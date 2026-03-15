#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contact_manager.settings')

    try:
        from django.core.management import execute_from_command_line
        from contact_manager.db_utils import ensure_mysql_database_exists
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Ensure the configured MySQL database exists before Django attempts to
    # open a connection (e.g. during migrations, checks, etc.).
    ensure_mysql_database_exists()

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
