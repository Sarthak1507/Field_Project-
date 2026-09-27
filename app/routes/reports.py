"""Small aggregate queries that power the reports page."""
from flask import Blueprint, jsonify
from app.db import rows, row
from app.security import admin_required

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


@reports_bp.get("")
@admin_required
def report_summary():
    departments = rows("""SELECT d.department_id AS id,d.department_name AS name,
      COUNT(e.employee_id) AS employeeCount FROM departments d LEFT JOIN employees e
      ON e.department_id=d.department_id GROUP BY d.department_id ORDER BY d.department_name""")
    attendance = rows("SELECT status,COUNT(*) AS total FROM attendance WHERE attendance_date=CURDATE() GROUP BY status")
    leaves = rows("SELECT status,COUNT(*) AS total FROM leave_requests GROUP BY status")
    salary = row("""SELECT COUNT(*) AS records,COALESCE(SUM(net_salary),0) AS netTotal,
      SUM(payment_status='Paid') AS paidRecords FROM salary_records
      WHERE salary_month=(SELECT MAX(salary_month) FROM salary_records)""")
    employees = row("SELECT COUNT(*) AS total,SUM(employment_status='Active') AS active FROM employees")
    return jsonify(departments=departments, attendance=attendance, leaves=leaves,
                   salary=salary, employees=employees)