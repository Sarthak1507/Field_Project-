"""Insert required OEMS departments and the first administrator account."""
from werkzeug.security import generate_password_hash

from app import create_app
from app.db import cursor, row

DEPARTMENTS = (
    "Administration", "Care and Support", "Education", "Kitchen",
    "Maintenance", "Security",
)


def seed():
    app = create_app()
    with app.app_context():
        with cursor(dictionary=False, commit=True) as cur:
            cur.executemany(
                "INSERT INTO departments(department_name) VALUES(%s) "
                "ON DUPLICATE KEY UPDATE department_name=VALUES(department_name)",
                [(name,) for name in DEPARTMENTS],
            )
        username = app.config["ADMIN_USERNAME"].strip()
        password = app.config["ADMIN_PASSWORD"]
        if not username or len(username) > 80 or len(password) < 12:
            raise ValueError("Set ADMIN_USERNAME and an ADMIN_PASSWORD of at least 12 characters in .env.")
        if row("SELECT user_id FROM users WHERE username=%s", (username,)):
            print(f"Administrator '{username}' already exists; its password was left unchanged.")
        else:
            with cursor(dictionary=False, commit=True) as cur:
                cur.execute(
                    "INSERT INTO users(username,password_hash,role,status) VALUES(%s,%s,'ADMIN','Active')",
                    (username, generate_password_hash(password)),
                )
            print(f"Created administrator '{username}'. Store its password securely.")
        print("Seeded the six required departments.")


if __name__ == "__main__":
    seed()