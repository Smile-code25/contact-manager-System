from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView

index_view = ensure_csrf_cookie(TemplateView.as_view(template_name='index.html'))

urlpatterns = [
    path('api/', include('contacts.urls')),
    path('', index_view),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
