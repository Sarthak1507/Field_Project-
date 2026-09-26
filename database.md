-- ============================================================
-- ORPHANAGE EMPLOYEE MANAGEMENT SYSTEM
-- PostgreSQL Database Schema
-- ============================================================

-- ------------------------------------------------------------
-- 1. CREATE DATABASE
-- ------------------------------------------------------------
-- Run this separately if the database does not already exist:
--
-- CREATE DATABASE orphanage_employee_management;
--
-- Then connect to that database and run the rest of this script.


-- ============================================================
-- 2. ENUM TYPES
-- ============================================================

CREATE TYPE user_role AS ENUM (
    'ADMIN',
    'EMPLOYEE'
);

CREATE TYPE employee_gender AS ENUM (
    'MALE',
    'FEMALE',
    'OTHER'
);

CREATE TYPE employment_status AS ENUM (
    'ACTIVE',
    'INACTIVE',
    'RESIGNED',
    'TERMINATED'
);

CREATE TYPE attendance_status AS ENUM (
    'PRESENT',
    'ABSENT',
    'HALF_DAY',
    'LEAVE'
);

CREATE TYPE leave_status AS ENUM (
    'PENDING',
    'APPROVED',
    'REJECTED',
    'CANCELLED'
);

CREATE TYPE leave_type AS ENUM (
    'CASUAL',
    'SICK',
    'ANNUAL',
    'EMERGENCY',
    'OTHER'
);

CREATE TYPE payment_status AS ENUM (
    'PENDING',
    'PAID',
    'PARTIAL'
);


-- ============================================================
-- 3. DEPARTMENTS
-- ============================================================

CREATE TABLE departments (
    department_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    department_name VARCHAR(100) NOT NULL UNIQUE,

    description TEXT,

    status BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- 4. EMPLOYEES
-- ============================================================

CREATE TABLE employees (
    employee_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    employee_code VARCHAR(30) NOT NULL UNIQUE,

    first_name VARCHAR(50) NOT NULL,

    middle_name VARCHAR(50),

    last_name VARCHAR(50) NOT NULL,

    gender employee_gender NOT NULL,

    date_of_birth DATE,

    phone VARCHAR(15) NOT NULL,

    email VARCHAR(150) UNIQUE,

    address_line1 VARCHAR(200),

    address_line2 VARCHAR(200),

    city VARCHAR(100),

    state VARCHAR(100),

    postal_code VARCHAR(10),

    emergency_contact_name VARCHAR(100),

    emergency_contact_phone VARCHAR(15),

    designation VARCHAR(100) NOT NULL,

    department_id BIGINT NOT NULL,

    joining_date DATE NOT NULL,

    employment_status employment_status NOT NULL DEFAULT 'ACTIVE',

    basic_salary NUMERIC(12,2) NOT NULL DEFAULT 0.00,

    profile_photo_url TEXT,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_employee_department
        FOREIGN KEY (department_id)
        REFERENCES departments(department_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_basic_salary
        CHECK (basic_salary >= 0)
);


-- ============================================================
-- 5. USERS / LOGIN ACCOUNTS
-- ============================================================

CREATE TABLE users (
    user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    username VARCHAR(50) NOT NULL UNIQUE,

    password_hash TEXT NOT NULL,

    role user_role NOT NULL DEFAULT 'EMPLOYEE',

    employee_id BIGINT UNIQUE,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    last_login TIMESTAMP,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_user_employee
        FOREIGN KEY (employee_id)
        REFERENCES employees(employee_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);


-- ============================================================
-- 6. ATTENDANCE
-- ============================================================

CREATE TABLE attendance (
    attendance_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    employee_id BIGINT NOT NULL,

    attendance_date DATE NOT NULL,

    status attendance_status NOT NULL,

    check_in_time TIME,

    check_out_time TIME,

    remarks TEXT,

    marked_by BIGINT,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_attendance_employee
        FOREIGN KEY (employee_id)
        REFERENCES employees(employee_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_attendance_marked_by
        FOREIGN KEY (marked_by)
        REFERENCES users(user_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT unique_employee_attendance
        UNIQUE (employee_id, attendance_date),

    CONSTRAINT chk_attendance_time
        CHECK (
            check_out_time IS NULL
            OR check_in_time IS NULL
            OR check_out_time >= check_in_time
        )
);


-- ============================================================
-- 7. LEAVE REQUESTS
-- ============================================================

CREATE TABLE leave_requests (
    leave_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    employee_id BIGINT NOT NULL,

    leave_type leave_type NOT NULL,

    start_date DATE NOT NULL,

    end_date DATE NOT NULL,

    total_days NUMERIC(5,1) NOT NULL,

    reason TEXT NOT NULL,

    status leave_status NOT NULL DEFAULT 'PENDING',

    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    reviewed_by BIGINT,

    reviewed_at TIMESTAMP,

    review_remarks TEXT,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_leave_employee
        FOREIGN KEY (employee_id)
        REFERENCES employees(employee_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_leave_reviewer
        FOREIGN KEY (reviewed_by)
        REFERENCES users(user_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT chk_leave_dates
        CHECK (end_date >= start_date),

    CONSTRAINT chk_leave_days
        CHECK (total_days > 0)
);


-- ============================================================
-- 8. SALARY RECORDS
-- ============================================================

CREATE TABLE salary_records (
    salary_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    employee_id BIGINT NOT NULL,

    salary_month DATE NOT NULL,

    basic_salary NUMERIC(12,2) NOT NULL DEFAULT 0.00,

    allowances NUMERIC(12,2) NOT NULL DEFAULT 0.00,

    overtime_amount NUMERIC(12,2) NOT NULL DEFAULT 0.00,

    bonus NUMERIC(12,2) NOT NULL DEFAULT 0.00,

    deductions NUMERIC(12,2) NOT NULL DEFAULT 0.00,

    net_salary NUMERIC(12,2)
        GENERATED ALWAYS AS (
            basic_salary
            + allowances
            + overtime_amount
            + bonus
            - deductions
        ) STORED,

    payment_status payment_status NOT NULL DEFAULT 'PENDING',

    payment_date DATE,

    payment_method VARCHAR(50),

    transaction_reference VARCHAR(100),

    remarks TEXT,

    processed_by BIGINT,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_salary_employee
        FOREIGN KEY (employee_id)
        REFERENCES employees(employee_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_salary_processor
        FOREIGN KEY (processed_by)
        REFERENCES users(user_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT unique_employee_salary_month
        UNIQUE (employee_id, salary_month),

    CONSTRAINT chk_basic_salary_positive
        CHECK (basic_salary >= 0),

    CONSTRAINT chk_allowances_positive
        CHECK (allowances >= 0),

    CONSTRAINT chk_overtime_positive
        CHECK (overtime_amount >= 0),

    CONSTRAINT chk_bonus_positive
        CHECK (bonus >= 0),

    CONSTRAINT chk_deductions_positive
        CHECK (deductions >= 0)
);


-- ============================================================
-- 9. INDEXES
-- ============================================================

CREATE INDEX idx_employee_department
ON employees(department_id);

CREATE INDEX idx_employee_status
ON employees(employment_status);

CREATE INDEX idx_employee_name
ON employees(last_name, first_name);

CREATE INDEX idx_attendance_employee
ON attendance(employee_id);

CREATE INDEX idx_attendance_date
ON attendance(attendance_date);

CREATE INDEX idx_attendance_status
ON attendance(status);

CREATE INDEX idx_leave_employee
ON leave_requests(employee_id);

CREATE INDEX idx_leave_status
ON leave_requests(status);

CREATE INDEX idx_leave_dates
ON leave_requests(start_date, end_date);

CREATE INDEX idx_salary_employee
ON salary_records(employee_id);

CREATE INDEX idx_salary_month
ON salary_records(salary_month);


-- ============================================================
-- 10. TRIGGER FUNCTION FOR updated_at
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- 11. UPDATED_AT TRIGGERS
-- ============================================================

CREATE TRIGGER update_departments_updated_at
BEFORE UPDATE ON departments
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


CREATE TRIGGER update_employees_updated_at
BEFORE UPDATE ON employees
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


CREATE TRIGGER update_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


CREATE TRIGGER update_attendance_updated_at
BEFORE UPDATE ON attendance
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


CREATE TRIGGER update_leave_updated_at
BEFORE UPDATE ON leave_requests
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


CREATE TRIGGER update_salary_updated_at
BEFORE UPDATE ON salary_records
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- ============================================================
-- 12. INITIAL DEPARTMENTS
-- ============================================================

INSERT INTO departments
    (department_name, description)
VALUES
    ('Administration', 'Administrative and management staff'),
    ('Care and Support', 'Staff responsible for child care and support'),
    ('Education', 'Teaching and educational support staff'),
    ('Kitchen', 'Kitchen and food management staff'),
    ('Maintenance', 'Maintenance and facility support staff'),
    ('Security', 'Security and safety staff');


-- ============================================================
-- DATABASE COMPLETE
-- ============================================================
