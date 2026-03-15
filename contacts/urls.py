from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('register', views.register,     name='register'),
    path('login',    views.login_view,   name='login'),
    path('logout',   views.logout_view,  name='logout'),
    path('me',       views.me,           name='me'),

    # Contacts — search MUST come before <int:contact_id> (same reason as Flask)
    path('contacts/search',              views.search_contacts,      name='search_contacts'),
    path('contacts',                     views.contacts_list_create,  name='contacts'),
    path('contacts/<int:contact_id>',    views.contact_detail,        name='contact_detail'),

    # Export
    path('export/csv',  views.export_csv,  name='export_csv'),
    path('export/json', views.export_json, name='export_json'),
]
