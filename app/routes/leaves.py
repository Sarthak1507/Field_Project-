"""Leave request listing and administrator review."""
from datetime import datetime
from flask import Blueprint, jsonify, request, session
from app.db import execute, rows
from app.security import admin_required, csrf_protect
from app.validation import enum_value, text

bp = Blueprint("leaves", __name__, url_prefix="/api/leaves")


@bp.get("")
@admin_required
def list_leaves():
    return jsonify(rows("""SELECT leave_id AS id, employee_id AS employeeId, leave_type AS type,
      start_date AS start,end_date AS end,total_days AS days,reason,status,applied_at AS applied,
      reviewed_by AS reviewerId,review_remarks AS remarks FROM leave_requests ORDER BY applied_at DESC"""))


@bp.post("")
@admin_required
@csrf_protect
def create_leave():
    data = request.get_json(silent=True) or {}
    from app.validation import date_value, positive_id
    employee_id = positive_id(data, "employeeId", "employee", True)
    start = date_value(data, "start", "Start date", True)
    end = date_value(data, "end", "End date", True)
    if end < start:
        raise ValueError("End date must not be before start date.")
    leave_type = text(data, "type", "Leave type", True, 50)
    reason = text(data, "reason", "Reason", True, 1000)
    days = (end - start).days + 1
    leave_id, _ = execute("INSERT INTO leave_requests(employee_id,leave_type,start_date,end_date,total_days,reason,status) VALUES(%s,%s,%s,%s,%s,%s,'Pending')",
            (employee_id, leave_type, start, end, days, reason))
    return jsonify(id=leave_id, message="Leave request submitted."), 201


@bp.put("/<int:leave_id>/review")
@admin_required
@csrf_protect
def review_leave(leave_id):
    data = request.get_json(silent=True) or {}
    status = enum_value(data, "status", "review decision", ("Approved", "Rejected"))
    remarks = text(data, "remarks", "Review remarks", False, 1000)
    execute("UPDATE leave_requests SET status=%s,reviewed_by=%s,review_remarks=%s,reviewed_at=%s WHERE leave_id=%s AND status='Pending'",
            (status, session["user_id"], remarks, datetime.now(), leave_id))
    return jsonify(message=f"Leave request {status.lower()}.")


@bp.delete("/<int:leave_id>")
@admin_required
@csrf_protect
def delete_leave(leave_id):
    execute("DELETE FROM leave_requests WHERE leave_id=%s", (leave_id,))
    return jsonify(message="Leave request deleted.")