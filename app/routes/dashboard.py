"""Dashboard overview and initial records required by the frontend."""
from flask import Blueprint, jsonify

from app.db import rows
from app.security import admin_required

bp = Blueprint("dashboard", __name__, url_prefix="/api")


@bp.get("/bootstrap")
@admin_required
def bootstrap():
    departments = rows("SELECT department_id AS id, department_name AS name, description, status FROM departments ORDER BY department_name")
    employees = rows("""SELECT employee_id AS id, employee_code AS code, first_name AS first,
        middle_name AS middle, last_name AS last, gender, date_of_birth AS dob, phone,
        email, address, city, state, postal_code AS postal, emergency_contact_name AS emergencyName,
        emergency_contact_phone AS emergencyPhone, designation, department_id AS departmentId,
        joining_date AS joining, employment_status AS status, basic_salary AS salary,
        profile_photo AS profilePhoto FROM employees ORDER BY first_name, last_name""")
    attendance = rows("""SELECT attendance_id AS id, a.employee_id AS employeeId,
        a.attendance_date AS date, a.status, TIME_FORMAT(a.check_in,'%H:%i') AS `in`,
        TIME_FORMAT(a.check_out,'%H:%i') AS `out`, a.marked_by AS markedBy,
        CONCAT_WS(' ', marker.first_name, marker.last_name) AS markedByName, remarks
        FROM attendance a LEFT JOIN users u ON u.user_id=a.marked_by
        LEFT JOIN employees marker ON marker.employee_id=u.employee_id
        ORDER BY attendance_date DESC, attendance_id DESC""")
    leaves = rows("""SELECT l.leave_id AS id, l.employee_id AS employeeId, l.leave_type AS type,
        l.start_date AS start, l.end_date AS end, l.total_days AS days, l.reason, l.status,
        l.applied_at AS applied, l.reviewed_by AS reviewerId,
        COALESCE(CONCAT_WS(' ', reviewer.first_name, reviewer.last_name), reviewer_user.username, '—') AS reviewer,
        review_remarks AS remarks FROM leave_requests l
        LEFT JOIN users reviewer_user ON reviewer_user.user_id=l.reviewed_by
        LEFT JOIN employees reviewer ON reviewer.employee_id=reviewer_user.employee_id
        ORDER BY applied_at DESC""")
    salaries = rows("""SELECT salary_id AS id, employee_id AS employeeId,
        DATE_FORMAT(salary_month,'%Y-%m') AS month, basic_salary AS basic,
        allowances, overtime_amount AS overtime, bonus, deductions, net_salary AS net,
        payment_status AS status, payment_date AS date, payment_method AS method,
        processed_by AS processedBy FROM salary_records ORDER BY salary_month DESC""")
    users = rows("""SELECT u.user_id AS id, u.username, u.employee_id AS employeeId,
        u.role, u.status, u.last_login AS lastLogin FROM users u ORDER BY u.username""")
    return jsonify(departments=departments, employees=employees, attendance=attendance,
                   leaves=leaves, salaries=salaries, users=users)