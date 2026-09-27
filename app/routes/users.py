"""Account administration with hashed passwords and role checks."""
import re
from flask import Blueprint, jsonify, request, session
from werkzeug.security import generate_password_hash

from app.db import execute, row, rows
from app.security import admin_required, csrf_protect
from app.validation import enum_value, positive_id, text

bp = Blueprint("users", __name__, url_prefix="/api/users")


@bp.get("")
@admin_required
def list_users():
    return jsonify(rows("""SELECT user_id AS id,username,employee_id AS employeeId,role,status,
      last_login AS lastLogin FROM users ORDER BY username"""))


@bp.post("")
@admin_required
@csrf_protect
def create_user():
    data = request.get_json(silent=True) or {}
    username = text(data, "username", "Username", True, 80)
    if not re.fullmatch(r"[A-Za-z0-9._-]+", username):
        raise ValueError("Username may contain letters, numbers, periods, underscores, and hyphens.")
    password = str(data.get("password", ""))
    if len(password) < 8 or len(password) > 128:
        raise ValueError("Password must be between 8 and 128 characters.")
    employee_id = positive_id(data, "employeeId", "employee")
    role = enum_value(data, "role", "role", ("ADMIN", "EMPLOYEE"))
    status = enum_value(data, "status", "user status", ("Active", "Inactive"), "Active")
    user_id, _ = execute("INSERT INTO users(username,password_hash,role,employee_id,status) VALUES(%s,%s,%s,%s,%s)",
            (username, generate_password_hash(password), role, employee_id, status))
    return jsonify(id=user_id, message="User created."), 201


@bp.put("/<int:user_id>")
@admin_required
@csrf_protect
def update_user(user_id):
    data = request.get_json(silent=True) or {}
    status = enum_value(data, "status", "user status", ("Active", "Inactive"))
    role = enum_value(data, "role", "role", ("ADMIN", "EMPLOYEE"))
    employee_id = positive_id(data, "employeeId", "employee")
    if user_id == session["user_id"] and (status != "Active" or role != "ADMIN"):
        return jsonify(error="You cannot deactivate or remove administrator access from your own account."), 409
    password = str(data.get("password", ""))
    if password:
        if len(password) < 8 or len(password) > 128:
            raise ValueError("Password must be between 8 and 128 characters.")
        execute("UPDATE users SET status=%s,role=%s,employee_id=%s,password_hash=%s WHERE user_id=%s",
                (status, role, employee_id, generate_password_hash(password), user_id))
    else:
        execute("UPDATE users SET status=%s,role=%s,employee_id=%s WHERE user_id=%s",
                (status, role, employee_id, user_id))
    return jsonify(message="User updated.")


@bp.delete("/<int:user_id>")
@admin_required
@csrf_protect
def delete_user(user_id):
    if user_id == session["user_id"]:
        return jsonify(error="You cannot delete the account you are signed in with."), 409
    if row("SELECT COUNT(*) AS total FROM users WHERE role='ADMIN' AND status='Active'")["total"] <= 1:
        return jsonify(error="Keep at least one active administrator account."), 409
    execute("DELETE FROM users WHERE user_id=%s", (user_id,))
    return jsonify(message="User deleted.")