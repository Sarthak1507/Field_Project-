"""Attendance review and capture endpoints."""
import re
from flask import Blueprint, jsonify, request
from app.db import execute, row, rows
from app.security import admin_required, csrf_protect
from app.validation import date_value, enum_value, positive_id, text

bp = Blueprint("attendance", __name__, url_prefix="/api/attendance")
STATUSES = ("PRESENT", "ABSENT", "HALF DAY", "LEAVE")


@bp.get("")
@admin_required
def list_attendance():
    return jsonify(rows("""SELECT attendance_id AS id, employee_id AS employeeId,
      attendance_date AS date,status,TIME_FORMAT(check_in,'%H:%i') AS `in`,
      TIME_FORMAT(check_out,'%H:%i') AS `out`,marked_by AS markedBy,remarks
      FROM attendance ORDER BY attendance_date DESC"""))


def attendance_values(data):
    employee_id = positive_id(data, "employeeId", "employee", True)
    date = date_value(data, "date", "Attendance date", True)
    status = enum_value(data, "status", "attendance status", STATUSES)
    check_in = text(data, "in", "Check in", False, 8)
    check_out = text(data, "out", "Check out", False, 8)
    for label, value in (("Check in", check_in), ("Check out", check_out)):
        if value and not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d)?", value):
            raise ValueError(f"{label} must use HH:MM format.")
    remarks = text(data, "remarks", "Remarks", False, 500)
    return employee_id, date, status, check_in or None, check_out or None, remarks


@bp.post("")
@admin_required
@csrf_protect
def create_attendance():
    employee_id, date, status, start, end, remarks = attendance_values(request.get_json(silent=True) or {})
    attendance_id, _ = execute("INSERT INTO attendance(employee_id,attendance_date,status,check_in,check_out,marked_by,remarks) VALUES(%s,%s,%s,%s,%s,%s,%s)",
            (employee_id, date, status, start, end, request_user_id(), remarks))
    return jsonify(id=attendance_id, message="Attendance record created."), 201


def request_user_id():
    from flask import session
    return session["user_id"]


@bp.put("/<int:attendance_id>")
@admin_required
@csrf_protect
def update_attendance(attendance_id):
    employee_id, date, status, start, end, remarks = attendance_values(request.get_json(silent=True) or {})
    execute("UPDATE attendance SET employee_id=%s,attendance_date=%s,status=%s,check_in=%s,check_out=%s,marked_by=%s,remarks=%s WHERE attendance_id=%s",
            (employee_id, date, status, start, end, request_user_id(), remarks, attendance_id))
    return jsonify(message="Attendance record updated.")


@bp.delete("/<int:attendance_id>")
@admin_required
@csrf_protect
def delete_attendance(attendance_id):
    execute("DELETE FROM attendance WHERE attendance_id=%s", (attendance_id,))
    return jsonify(message="Attendance record deleted.")