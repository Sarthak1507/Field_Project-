"""Employee record CRUD routes with server-side checks."""
from flask import Blueprint, jsonify, request
from mysql.connector import IntegrityError

from app.db import execute, row, rows
from app.security import admin_required, csrf_protect
from app.validation import (amount, date_value, email_value, enum_value,
                            phone_value, positive_id, text)

bp = Blueprint("employees", __name__, url_prefix="/api/employees")
STATUSES = ("Active", "On leave", "Inactive")
GENDERS = ("Female", "Male", "Non-binary", "Prefer not to say")


def employee_values(data):
    return (
        text(data, "code", "Employee code", True, 30),
        text(data, "first", "First name", True, 80),
        text(data, "middle", "Middle name", False, 80),
        text(data, "last", "Last name", True, 80),
        enum_value(data, "gender", "gender", GENDERS),
        date_value(data, "dob", "Date of birth"),
        phone_value(data, "phone", "Phone", True),
        email_value(data, required=True),
        text(data, "address", "Address", False, 250),
        text(data, "city", "City", False, 80),
        text(data, "state", "State", False, 80),
        text(data, "postal", "Postal code", False, 15),
        text(data, "emergencyName", "Emergency contact name", False, 120),
        phone_value(data, "emergencyPhone", "Emergency contact phone"),
        text(data, "designation", "Designation", True, 100),
        positive_id(data, "departmentId", "department", True),
        date_value(data, "joining", "Joining date", True),
        enum_value(data, "status", "employment status", STATUSES, "Active"),
        amount(data, "salary", "Basic salary"),
        text(data, "profilePhoto", "Profile photo path", False, 255),
    )


@bp.get("")
@admin_required
def list_employees():
    return jsonify(rows("""SELECT employee_id AS id,employee_code AS code,first_name AS first,
      middle_name AS middle,last_name AS last,gender,date_of_birth AS dob,phone,email,address,
      city,state,postal_code AS postal,emergency_contact_name AS emergencyName,
      emergency_contact_phone AS emergencyPhone,designation,department_id AS departmentId,
      joining_date AS joining,employment_status AS status,basic_salary AS salary,
      profile_photo AS profilePhoto FROM employees ORDER BY first_name,last_name"""))


@bp.post("")
@admin_required
@csrf_protect
def create_employee():
    values = employee_values(request.get_json(silent=True) or {})
    employee_id, _ = execute("""INSERT INTO employees(employee_code,first_name,middle_name,last_name,gender,
        date_of_birth,phone,email,address,city,state,postal_code,emergency_contact_name,
        emergency_contact_phone,designation,department_id,joining_date,employment_status,
        basic_salary,profile_photo) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", values)
    return jsonify(id=employee_id, message="Employee created."), 201


@bp.put("/<int:employee_id>")
@admin_required
@csrf_protect
def update_employee(employee_id):
    if not row("SELECT employee_id FROM employees WHERE employee_id=%s", (employee_id,)):
        return jsonify(error="Employee not found."), 404
    values = employee_values(request.get_json(silent=True) or {}) + (employee_id,)
    execute("""UPDATE employees SET employee_code=%s,first_name=%s,middle_name=%s,last_name=%s,
        gender=%s,date_of_birth=%s,phone=%s,email=%s,address=%s,city=%s,state=%s,postal_code=%s,
        emergency_contact_name=%s,emergency_contact_phone=%s,designation=%s,department_id=%s,
        joining_date=%s,employment_status=%s,basic_salary=%s,profile_photo=%s WHERE employee_id=%s""", values)
    return jsonify(message="Employee updated.")


@bp.delete("/<int:employee_id>")
@admin_required
@csrf_protect
def delete_employee(employee_id):
    execute("DELETE FROM employees WHERE employee_id=%s", (employee_id,))
    return jsonify(message="Employee and dependent records removed.")