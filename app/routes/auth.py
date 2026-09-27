"""Login, logout, and current-session endpoints."""
from datetime import datetime

from flask import Blueprint, jsonify, request, session
from werkzeug.security import check_password_hash

from app.db import row, execute
from app.security import csrf_protect, csrf_token, login_required

bp = Blueprint("auth", __name__, url_prefix="/api")


@bp.get("/csrf")
def get_csrf():
    return jsonify(csrf_token=csrf_token())


@bp.post("/login")
@csrf_protect
def login():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))
    if not username or not password or len(username) > 80:
        return jsonify(error="Enter a valid username and password."), 400
    user = row("""SELECT user_id, username, password_hash, role, status, employee_id
                  FROM users WHERE username = %s""", (username,))
    if not user or user["status"] != "Active" or not check_password_hash(user["password_hash"], password):
        return jsonify(error="The username or password is incorrect, or this account is inactive."), 401
    session.clear()
    session["user_id"] = user["user_id"]
    session["role"] = user["role"]
    session["username"] = user["username"]
    session.permanent = bool(data.get("remember", False))
    # Updating login time is part of the audit trail for successful sign-ins.
    execute("UPDATE users SET last_login = %s WHERE user_id = %s", (datetime.now(), user["user_id"]))
    return jsonify(user={"id": user["user_id"], "username": user["username"],
                         "role": user["role"]}, csrf_token=csrf_token())


@bp.post("/logout")
@csrf_protect
@login_required
def logout():
    session.clear()
    return jsonify(message="Signed out.")


@bp.get("/session")
@login_required
def current_session():
    return jsonify(user={"id": session["user_id"], "username": session["username"],
                         "role": session["role"]}, csrf_token=csrf_token())