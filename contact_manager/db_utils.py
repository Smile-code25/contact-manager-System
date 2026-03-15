"""Database helpers for the contact_manager project.

This module provides a small utility to ensure that the configured database exists
before Django tries to connect to it. This is useful for backends like MySQL where
Django will fail to connect if the database does not already exist.

The intent is:
- If the database already exists, do nothing.
- If the database does not exist, create it using the configured connection info.
- If the server is unreachable or credentials are invalid, we let the resulting
  error bubble up (but emit a warning to stderr to help diagnose the issue).
"""

from __future__ import annotations

import sys

from django.conf import settings


def ensure_mysql_database_exists() -> None:
    """Create the configured MySQL database if it does not already exist."""

    db = settings.DATABASES.get("default") or {}
    engine = db.get("ENGINE", "")
    if "mysql" not in engine:
        return

    name = db.get("NAME")
    if not name:
        return

    try:
        import MySQLdb  # noqa: T001
    except ImportError:
        # If the MySQL client library isn't installed, let Django report it.
        return

    conn_kwargs = {
        "host": db.get("HOST", "localhost"),
        "user": db.get("USER", "root"),
        "passwd": db.get("PASSWORD", ""),
        "port": int(db.get("PORT") or 3306),
        "charset": db.get("OPTIONS", {}).get("charset", "utf8mb4"),
        "autocommit": True,
    }

    unix_socket = db.get("OPTIONS", {}).get("unix_socket")
    if unix_socket:
        conn_kwargs["unix_socket"] = unix_socket

    try:
        conn = MySQLdb.connect(**conn_kwargs)
        with conn.cursor() as cursor:
            cursor.execute(
                "CREATE DATABASE IF NOT EXISTS `{}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci".format(name)
            )
        conn.close()
    except MySQLdb.OperationalError as exc:
        # If we can't connect, we let Django raise the exception later, but
        # output a warning so it's easier to debug.
        print(
            "Warning: could not ensure MySQL database exists:",
            exc,
            file=sys.stderr,
        )
