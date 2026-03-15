import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contact_manager.settings')

# Ensure the database exists before Django tries to connect (useful for MySQL).
# This allows the project to start even when the DB has not yet been created.
try:
    from contact_manager.db_utils import ensure_mysql_database_exists

    ensure_mysql_database_exists()
except ImportError:
    # If the helper can't be imported, fall back to the default behavior.
    pass

application = get_wsgi_application()
