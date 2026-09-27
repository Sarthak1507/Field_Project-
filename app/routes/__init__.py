from app.routes.attendance import attendance_bp
from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.departments import departments_bp
from app.routes.employees import employees_bp
from app.routes.leaves import leaves_bp
from app.routes.reports import reports_bp
from app.routes.salary import salary_bp
from app.routes.users import users_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(departments_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(leaves_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(salary_bp)
    app.register_blueprint(users_bp)