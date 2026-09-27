"""Small parameterized MySQL helpers shared by route modules."""
from contextlib import contextmanager
from datetime import date, datetime, time
from decimal import Decimal

import mysql.connector
from flask import current_app


def connect():
    """Open a short-lived connection using the current app configuration."""
    return mysql.connector.connect(
        host=current_app.config["DB_HOST"],
        port=current_app.config["DB_PORT"],
        database=current_app.config["DB_NAME"],
        user=current_app.config["DB_USER"],
        password=current_app.config["DB_PASSWORD"],
        charset="utf8mb4",
        use_unicode=True,
    )


@contextmanager
def cursor(dictionary=True, commit=False):
    """Manage cursor/connection cleanup and commit only successful writes."""
    connection = connect()
    cur = connection.cursor(dictionary=dictionary)
    try:
        yield cur
        if commit:
            connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cur.close()
        connection.close()


def rows(sql, params=()):
    with cursor() as cur:
        cur.execute(sql, params)
        return [_json_safe(item) for item in cur.fetchall()]


def row(sql, params=()):
    with cursor() as cur:
        cur.execute(sql, params)
        return _json_safe(cur.fetchone())


def _json_safe(value):
    """Convert MySQL-specific values to predictable JSON-compatible values."""
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (date, datetime, time)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def execute(sql, params=()):
    with cursor(dictionary=False, commit=True) as cur:
        cur.execute(sql, params)
        return cur.lastrowid, cur.rowcount