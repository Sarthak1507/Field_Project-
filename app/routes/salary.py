"""Salary record creation and payment processing."""
from datetime import date
from flask import Blueprint, jsonify, request, session
from app.db import execute, rows
from app.security import admin_required, csrf_protect
from app.validation import amount, enum_value, positive_id, text

bp = Blueprint("salary", __name__, url_prefix="/api/salaries")


@bp.get("")
@admin_required
def list_salaries():
    return jsonify(rows("""SELECT salary_id AS id,employee_id AS employeeId,
      DATE_FORMAT(salary_month,'%Y-%m') AS month,basic_salary AS basic,allowances,
      overtime_amount AS overtime,bonus,deductions,net_salary AS net,
      payment_status AS status,payment_date AS date,payment_method AS method,
      processed_by AS processedBy FROM salary_records ORDER BY salary_month DESC"""))


@bp.post("")
@admin_required
@csrf_protect
def create_salary():
    data = request.get_json(silent=True) or {}
    employee_id = positive_id(data, "employeeId", "employee", True)
    month_text = text(data, "month", "Salary month", True, 7)
    try:
        month = date.fromisoformat(month_text + "-01")
    except ValueError:
        raise ValueError("Salary month must use YYYY-MM format.")
    values = [amount(data, key, label, False) for key, label in
              (("allowances", "Allowances"), ("overtime", "Overtime"),
               ("bonus", "Bonus"), ("deductions", "Deductions"))]
    salary_id, _ = execute("""INSERT INTO salary_records(employee_id,salary_month,basic_salary,allowances,
      overtime_amount,bonus,deductions,payment_status,processed_by)
      SELECT %s,%s,basic_salary,%s,%s,%s,%s,'Pending',%s FROM employees WHERE employee_id=%s""",
            (employee_id, month, *values, session["user_id"], employee_id))
    return jsonify(id=salary_id, message="Salary record created."), 201


@bp.put("/<int:salary_id>/payment")
@admin_required
@csrf_protect
def update_payment(salary_id):
    data = request.get_json(silent=True) or {}
    status = enum_value(data, "status", "payment status", ("Pending", "Paid"))
    method = text(data, "method", "Payment method", status == "Paid", 60)
    payment_date = date.today() if status == "Paid" else None
    execute("UPDATE salary_records SET payment_status=%s,payment_method=%s,payment_date=%s,processed_by=%s WHERE salary_id=%s",
            (status, method, payment_date, session["user_id"], salary_id))
    return jsonify(message="Payment status updated.")


@bp.delete("/<int:salary_id>")
@admin_required
@csrf_protect
def delete_salary(salary_id):
    execute("DELETE FROM salary_records WHERE salary_id=%s", (salary_id,))
    return jsonify(message="Salary record deleted.")