"""Session authorization and same-origin request protection."""
from functools import wraps
import hmac
import secrets

from flask import jsonify, request, session


def csrf_token():
    """Create one CSRF token per browser session for mutating API calls."""
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


def csrf_protect(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        expected = session.get("csrf_token", "")
        supplied = request.headers.get("X-CSRF-Token", "")
        if not expected or not hmac.compare_digest(expected, supplied):
            return jsonify(error="The request token expired. Refresh the page and try again."), 400
        return fn(*args, **kwargs)
    return wrapped


def login_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify(error="Please sign in to continue."), 401
        return fn(*args, **kwargs)
    return wrapped


def admin_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify(error="Please sign in to continue."), 401
        if session.get("role") != "ADMIN":
            return jsonify(error="Administrator access is required."), 403
        return fn(*args, **kwargs)
    return wrapped