"""Department maintenance endpoints."""
from flask import Blueprint, jsonify, request
from app.db import execute, row, rows
from app.security import admin_required, csrf_protect
from app.validation import enum_value, text

departments_bp = Blueprint("departments", __name__, url_prefix="/api/departments")


@departments_bp.get("")
@admin_required
def list_departments():
    return jsonify(rows("""SELECT d.department_id AS id, d.department_name AS name,
        d.description, d.status, COUNT(e.employee_id) AS employeeCount FROM departments d
        LEFT JOIN employees e ON e.department_id=d.department_id
        GROUP BY d.department_id ORDER BY d.department_name"""))


@departments_bp.post("")
@admin_required
@csrf_protect
def create_department():
    data = request.get_json(silent=True) or {}
    name = text(data, "name", "Department name", True, 100)
    description = text(data, "description", "Description", False, 255)
    department_id, _ = execute("INSERT INTO departments(department_name,description,status) VALUES(%s,%s,'Active')", (name, description))
    return jsonify(id=department_id, message="Department created."), 201


@departments_bp.put("/<int:department_id>")
@admin_required
@csrf_protect
def update_department(department_id):
    data = request.get_json(silent=True) or {}
    name = text(data, "name", "Department name", True, 100)
    description = text(data, "description", "Description", False, 255)
    status = enum_value(data, "status", "department status", ("Active", "Inactive"), "Active")
    execute("UPDATE departments SET department_name=%s,description=%s,status=%s WHERE department_id=%s", (name, description, status, department_id))
    return jsonify(message="Department updated.")


@departments_bp.delete("/<int:department_id>")
@admin_required
@csrf_protect
def delete_department(department_id):
    if row("SELECT employee_id FROM employees WHERE department_id=%s LIMIT 1", (department_id,)):
        return jsonify(error="Reassign employees before deleting this department."), 409
    execute("DELETE FROM departments WHERE department_id=%s", (department_id,))
    return jsonify(message="Department deleted.")