import json
import time
import csv
import io

from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.db.models import Q

from .models import AppUser, Contact
from .validators import (
    validate_username, validate_password,
    validate_name, validate_phone, validate_email,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def json_body(request):
    """Parse JSON body safely."""
    try:
        return json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return {}


def login_required(view_func):
    """Decorator — mirrors Flask's login_required."""
    from functools import wraps

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'username' not in request.session:
            return JsonResponse(
                {'success': False, 'message': 'Unauthorized — please log in'}, status=401
            )
        return view_func(request, *args, **kwargs)
    return wrapper


def get_current_user(request):
    """Return AppUser for the session, or None."""
    username = request.session.get('username')
    if not username:
        return None
    try:
        return AppUser.objects.get(username=username)
    except AppUser.DoesNotExist:
        return None


# ─── Auth Views ───────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(['POST'])
def register(request):
    """
    POST /api/register
    Create a new user account.
    """
    data = json_body(request)
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()

    u_ok, u_msg = validate_username(username)
    if not u_ok:
        return JsonResponse({'success': False, 'message': u_msg}, status=400)

    p_ok, p_msg = validate_password(password)
    if not p_ok:
        return JsonResponse({'success': False, 'message': p_msg}, status=400)

    if AppUser.objects.filter(username=username).exists():
        return JsonResponse({
            'success': False,
            'message': 'Username already exists. Please choose another username.'
        }, status=400)

    AppUser.objects.create(username=username, password=password)
    return JsonResponse({
        'success': True,
        'message': f'Account created successfully! Welcome, {username}.'
    }, status=201)


@csrf_exempt
@require_http_methods(['POST'])
def login_view(request):
    """
    POST /api/login
    Authenticate a user with granular error messages + account lockout.
    """
    data = json_body(request)
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()

    if not username or not password:
        return JsonResponse({
            'success': False,
            'message': 'Username and password are required.'
        }, status=400)

    attempts_key = f'attempts_{username}'
    lock_key = f'locked_{username}'

    # Check lock first
    lock_until = request.session.get(lock_key)
    if lock_until and time.time() < lock_until:
        seconds_remaining = int(lock_until - time.time()) + 1
        return JsonResponse({
            'success': False,
            'locked': True,
            'seconds_remaining': seconds_remaining,
            'message': (
                f'Account locked due to multiple failed attempts. '
                f'Please try again in {seconds_remaining} seconds.'
            )
        }, status=403)

    # Check if user exists
    try:
        user = AppUser.objects.get(username=username)
    except AppUser.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'User does not exist. Please register first.'
        }, status=401)

    # Verify password
    if user.password == password:
        request.session.set_expiry(7200)  # 2 hours
        request.session['username'] = username
        request.session.pop(attempts_key, None)
        request.session.pop(lock_key, None)
        return JsonResponse({
            'success': True,
            'message': 'Login successful',
            'username': username
        }, status=200)

    # Wrong password
    attempts = request.session.get(attempts_key, 0) + 1
    request.session[attempts_key] = attempts

    if attempts >= 3:
        lock_until = time.time() + 60
        request.session[lock_key] = lock_until
        return JsonResponse({
            'success': False,
            'locked': True,
            'seconds_remaining': 60,
            'message': (
                'Account locked due to multiple failed attempts. '
                'Please try again in 60 seconds.'
            )
        }, status=403)

    remaining = 3 - attempts
    return JsonResponse({
        'success': False,
        'message': f'Incorrect password. {remaining} attempt(s) remaining before lockout.'
    }, status=401)


@csrf_exempt
@require_http_methods(['POST'])
@login_required
def logout_view(request):
    """POST /api/logout"""
    request.session.flush()
    return JsonResponse({'success': True, 'message': 'Logged out successfully'})


@require_http_methods(['GET'])
def me(request):
    """GET /api/me"""
    if 'username' in request.session:
        return JsonResponse({'username': request.session['username']})
    return JsonResponse({'success': False, 'message': 'Not logged in'}, status=401)


# ─── Contact Views ────────────────────────────────────────────────────────────

@csrf_exempt
@login_required
def contacts_list_create(request):
    """
    GET  /api/contacts   — list all contacts
    POST /api/contacts   — create a contact
    """
    user = get_current_user(request)
    if not user:
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=401)

    if request.method == 'GET':
        contacts = user.contacts.all().order_by('-date_added')
        return JsonResponse([c.to_dict() for c in contacts], safe=False)

    # POST
    data = json_body(request)
    name = (data.get('name') or '').strip()
    phone = (data.get('phone') or '').strip()
    email = (data.get('email') or '').strip()

    if not name:
        return JsonResponse({'error': 'Name is required'}, status=400)
    if not phone:
        return JsonResponse({'error': 'Phone is required'}, status=400)

    n_ok, n_msg = validate_name(name)
    if not n_ok:
        return JsonResponse({'error': n_msg}, status=400)

    p_ok, cleaned_phone = validate_phone(phone)
    if not p_ok:
        return JsonResponse({'error': cleaned_phone}, status=400)

    e_ok, cleaned_email = validate_email(email)
    if not e_ok:
        return JsonResponse({'error': cleaned_email}, status=400)

    # Check duplicate phone
    if user.contacts.filter(phone=cleaned_phone).exists():
        return JsonResponse({'error': 'Phone number already exists in your contacts'}, status=400)

    # Check duplicate email
    if cleaned_email and user.contacts.filter(email=cleaned_email).exists():
        return JsonResponse({'error': 'Email address already exists in your contacts'}, status=400)

    contact = Contact.objects.create(
        user=user, name=name, phone=cleaned_phone, email=cleaned_email
    )
    return JsonResponse({'message': 'Contact added successfully', 'id': contact.id}, status=201)


@csrf_exempt
@login_required
def contact_detail(request, contact_id):
    """
    PUT    /api/contacts/<id>  — update
    DELETE /api/contacts/<id>  — delete
    """
    user = get_current_user(request)
    if not user:
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=401)

    try:
        contact = user.contacts.get(id=contact_id)
    except Contact.DoesNotExist:
        return JsonResponse({'error': 'Contact not found'}, status=404)

    if request.method == 'PUT':
        data = json_body(request)
        name = (data.get('name') or '').strip()
        phone = (data.get('phone') or '').strip()
        email = (data.get('email') or '').strip()

        if not name:
            return JsonResponse({'error': 'Name is required'}, status=400)
        if not phone:
            return JsonResponse({'error': 'Phone is required'}, status=400)

        n_ok, n_msg = validate_name(name)
        if not n_ok:
            return JsonResponse({'error': n_msg}, status=400)

        p_ok, cleaned_phone = validate_phone(phone)
        if not p_ok:
            return JsonResponse({'error': cleaned_phone}, status=400)

        e_ok, cleaned_email = validate_email(email)
        if not e_ok:
            return JsonResponse({'error': cleaned_email}, status=400)

        # Duplicate checks (exclude current contact)
        if user.contacts.filter(phone=cleaned_phone).exclude(id=contact_id).exists():
            return JsonResponse({'error': 'Phone number already exists for another contact'}, status=400)

        if cleaned_email and user.contacts.filter(email=cleaned_email).exclude(id=contact_id).exists():
            return JsonResponse({'error': 'Email already exists for another contact'}, status=400)

        contact.name = name
        contact.phone = cleaned_phone
        contact.email = cleaned_email
        contact.save()
        return JsonResponse({'message': 'Contact updated successfully'})

    if request.method == 'DELETE':
        contact.delete()
        return JsonResponse({'message': 'Contact deleted successfully'})

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@require_http_methods(['GET'])
@login_required
def search_contacts(request):
    """GET /api/contacts/search?q=<term>&field=<all|name|phone|email>"""
    user = get_current_user(request)
    if not user:
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=401)

    term = request.GET.get('q', '').strip()
    field = request.GET.get('field', 'all')

    if not term:
        return JsonResponse([], safe=False)

    qs = user.contacts.all()

    if field == 'name':
        qs = qs.filter(name__icontains=term)
    elif field == 'phone':
        qs = qs.filter(phone__icontains=term)
    elif field == 'email':
        qs = qs.filter(email__icontains=term)
    else:
        qs = qs.filter(
            Q(name__icontains=term) |
            Q(phone__icontains=term) |
            Q(email__icontains=term)
        )

    return JsonResponse([c.to_dict() for c in qs], safe=False)


# ─── Export Views ─────────────────────────────────────────────────────────────

@require_http_methods(['GET'])
@login_required
def export_csv(request):
    """GET /api/export/csv"""
    user = get_current_user(request)
    if not user:
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=401)

    contacts = list(user.contacts.all().order_by('-date_added'))

    if not contacts:
        return JsonResponse({'error': 'No contacts to export'}, status=404)

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['id', 'name', 'phone', 'email', 'date_added'])
    writer.writeheader()
    for c in contacts:
        writer.writerow(c.to_dict())

    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=contacts.csv'
    return response


@require_http_methods(['GET'])
@login_required
def export_json(request):
    """GET /api/export/json"""
    user = get_current_user(request)
    if not user:
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=401)

    contacts = list(user.contacts.all().order_by('-date_added'))

    if not contacts:
        return JsonResponse({'error': 'No contacts to export'}, status=404)

    data = json.dumps([c.to_dict() for c in contacts], indent=2)
    response = HttpResponse(data, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename=contacts.json'
    return response
