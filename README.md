# Orphanage Employee Management System (OEMS)

OEMS is a Flask and MySQL employee management system with a plain HTML, CSS, and vanilla JavaScript interface. It includes an administrator dashboard and employee, department, attendance, leave, salary, user, and report modules. The Maher logo and community photo supplied for this project are stored unchanged in `assets/images`.

## Requirements

- Windows 10/11 with Python 3.10 or newer
- MySQL 8.0 or newer
- VS Code (optional)

The frontend needs no Node.js, npm, or build step.

## Setup on Windows

Open PowerShell in the project folder and run:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env`: set a long random `SECRET_KEY`, your MySQL connection values, and a unique administrator username and password. The seed command requires the administrator password to be at least 12 characters. Keep `.env` private; it is excluded from Git.

Create a restricted MySQL application account (run in a MySQL client as an administrator):

```sql
CREATE USER IF NOT EXISTS 'oems_app'@'localhost' IDENTIFIED BY 'use-a-unique-database-password';
ALTER USER 'oems_app'@'localhost' IDENTIFIED BY 'use-a-unique-database-password';
GRANT SELECT, INSERT, UPDATE, DELETE ON orphanage_employee_management.* TO 'oems_app'@'localhost';
```

Set `DB_USER=oems_app` and `DB_PASSWORD` to the same password in `.env`. If the account already exists, the `ALTER USER` statement resets its password so it matches the application settings.

Apply the schema from PowerShell:

```powershell
cmd /c "mysql -u root -p < database\schema.sql"
```

The provided prompt specified the database and six table names, generated salary formula, foreign-key behavior, and two unique constraints, but did not include a column-by-column SQL schema. `database/schema.sql` therefore documents a conservative schema inferred from the fields in the prompt and the Phase 1 interface. Review that inferred column definition against your instructor's schema before applying it if they have a separate schema file.

Seed the required departments and administrator, then start Flask:

```powershell
python -m database.seed
python run.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) and sign in using the administrator values from `.env`. The seed script hashes the initial password and does not replace the password on later runs.

## Project layout

```text
app/                 Flask configuration, MySQL helpers, and route groups
assets/css/          Shared responsive design system
assets/js/           Vanilla JavaScript views and API integration
assets/images/       Only the two user-provided images
database/schema.sql  MySQL 8 schema and relationships
database/seed.py     Idempotent department/admin seed
frontend/            Static HTML entry points, served by Flask
```

## Security and behavior

- Passwords are stored as Werkzeug password hashes; successful logins update `last_login`.
- Flask sessions are HTTP-only and same-site; mutating API calls require a session CSRF token.
- Admin-only routes guard staff management and reports. Inactive users cannot sign in.
- Server-side validation complements browser validation. SQL statements use parameters.
- MySQL enforces employee/department relationships, attendance and payroll uniqueness, and the generated `net_salary` value.
- Deleting an employee cascades to attendance, leave, and salary records. Its linked user's employee association is set to `NULL`. Departments with employees are restricted from deletion; user references in audit fields are set to `NULL` when that user is removed.
- Employee photos are not uploaded or stored; no employee photo assets were supplied.

## Run the offline checks

```powershell
python -m unittest discover -s tests -v
```

These checks cover page and asset serving, session login behavior, CSRF enforcement, role restrictions, server-side employee validation, and required schema constraints. They do not replace an integration run against a configured MySQL 8 server.

## Phase boundary

Phase 2 is implemented here. No Node.js, npm, React, or frontend framework is used. Use the virtual environment commands above to run the application; the earlier static-only preview command is no longer the application entry point.
