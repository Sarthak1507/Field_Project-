"""Offline checks for page serving, CSRF protection, login, and role gates."""
import unittest
from unittest.mock import patch

from werkzeug.security import generate_password_hash

from app import create_app


class AppTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True, "SECRET_KEY": "unit-test-key"})
        self.client = self.app.test_client()

    def csrf(self):
        return self.client.get("/api/csrf").get_json()["csrf_token"]

    def login(self, role="ADMIN", status="Active"):
        token = self.csrf()
        user = {"user_id": 7, "username": "review-admin", "password_hash": generate_password_hash("correct-horse-battery"),
                "role": role, "status": status, "employee_id": None}
        with patch("app.routes.auth.row", return_value=user), patch("app.routes.auth.execute") as write:
            response = self.client.post("/api/login", json={"username": "review-admin", "password": "correct-horse-battery"},
                                        headers={"X-CSRF-Token": token})
        return response, write

    def test_frontend_pages_and_user_assets_are_served(self):
        for path in ("/", "/frontend/dashboard.html", "/frontend/reports.html",
                     "/assets/css/style.css", "/assets/js/app.js",
                     "/assets/images/LogoMaher.jpg", "/assets/images/background.webp"):
            with self.subTest(path=path):
                response = self.client.get(path)
                if path == "/":
                    self.assertIn("/frontend/index.html", response.headers["Location"])
                    response.close()
                    continue
                self.assertEqual(response.status_code, 200)
                response.close()

    def test_login_requires_csrf_token(self):
        with patch("app.routes.auth.row") as lookup:
            response = self.client.post("/api/login", json={"username": "admin", "password": "password"})
        self.assertEqual(response.status_code, 400)
        lookup.assert_not_called()

    def test_active_admin_login_creates_session_and_updates_last_login(self):
        response, write = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["user"]["role"], "ADMIN")
        self.assertTrue(response.get_json()["csrf_token"])
        write.assert_called_once()
        with patch("app.routes.dashboard.rows", return_value=[]):
            self.assertEqual(self.client.get("/api/bootstrap").status_code, 200)

    def test_inactive_user_cannot_log_in(self):
        token = self.csrf()
        user = {"user_id": 7, "username": "review-admin", "password_hash": generate_password_hash("correct-horse-battery"),
                "role": "ADMIN", "status": "Inactive", "employee_id": None}
        with patch("app.routes.auth.row", return_value=user), patch("app.routes.auth.execute") as write:
            response = self.client.post("/api/login", json={"username": "review-admin", "password": "correct-horse-battery"},
                                        headers={"X-CSRF-Token": token})
        self.assertEqual(response.status_code, 401)
        write.assert_not_called()

    def test_employee_role_is_denied_admin_bootstrap(self):
        response, _ = self.login(role="EMPLOYEE")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/api/bootstrap").status_code, 403)

    def test_protected_api_requires_login(self):
        self.assertEqual(self.client.get("/api/reports").status_code, 401)

    def test_employee_api_validates_before_writing(self):
        self.login()
        token = self.client.get("/api/session").get_json()["csrf_token"]
        invalid = self.client.post("/api/employees", json={"first": "Only a first name"},
                                   headers={"X-CSRF-Token": token})
        self.assertEqual(invalid.status_code, 400)
        with patch("app.routes.employees.execute", return_value=(31, 1)) as write:
            valid = self.client.post("/api/employees", json={
                "code": "OEMS-031", "first": "Asha", "last": "Rao", "gender": "Female",
                "phone": "+91 98765 43210", "email": "asha.rao@example.org",
                "designation": "Care Associate", "departmentId": 1,
                "joining": "2026-01-15", "status": "Active", "salary": "28000",
            }, headers={"X-CSRF-Token": token})
        self.assertEqual(valid.status_code, 201)
        self.assertEqual(valid.get_json()["id"], 31)
        write.assert_called_once()

    def test_schema_keeps_required_generated_salary_and_unique_keys(self):
        from pathlib import Path
        schema = (Path(__file__).parents[1] / "database" / "schema.sql").read_text(encoding="utf-8")
        self.assertIn("UNIQUE KEY uq_attendance_employee_date(employee_id,attendance_date)", schema)
        self.assertIn("UNIQUE KEY uq_salary_employee_month(employee_id,salary_month)", schema)
        self.assertIn("GENERATED ALWAYS AS", schema)
        self.assertIn("ON DELETE RESTRICT", schema)
        self.assertIn("ON DELETE CASCADE", schema)
        self.assertIn("ON DELETE SET NULL", schema)


if __name__ == "__main__":
    unittest.main()
