-- OEMS MySQL 8 schema inferred from the supplied project requirements.
-- The prompt names the tables, key relationships, and unique constraints,
-- but it does not include a separate column-by-column schema to reproduce.
CREATE DATABASE IF NOT EXISTS orphanage_employee_management
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE orphanage_employee_management;

CREATE TABLE IF NOT EXISTS departments (
  department_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  department_name VARCHAR(100) NOT NULL UNIQUE,
  description VARCHAR(255) NULL,
  status ENUM('Active','Inactive') NOT NULL DEFAULT 'Active',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS employees (
  employee_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  employee_code VARCHAR(30) NOT NULL UNIQUE,
  first_name VARCHAR(80) NOT NULL,
  middle_name VARCHAR(80) NULL,
  last_name VARCHAR(80) NOT NULL,
  gender ENUM('Female','Male','Non-binary','Prefer not to say') NOT NULL,
  date_of_birth DATE NULL,
  phone VARCHAR(25) NOT NULL,
  email VARCHAR(254) NOT NULL UNIQUE,
  address VARCHAR(250) NULL,
  city VARCHAR(80) NULL,
  state VARCHAR(80) NULL,
  postal_code VARCHAR(15) NULL,
  emergency_contact_name VARCHAR(120) NULL,
  emergency_contact_phone VARCHAR(25) NULL,
  designation VARCHAR(100) NOT NULL,
  department_id INT UNSIGNED NOT NULL,
  joining_date DATE NOT NULL,
  employment_status ENUM('Active','On leave','Inactive') NOT NULL DEFAULT 'Active',
  basic_salary DECIMAL(10,2) UNSIGNED NOT NULL,
  profile_photo VARCHAR(255) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_employees_department FOREIGN KEY(department_id)
    REFERENCES departments(department_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS users (
  user_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(80) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('ADMIN','EMPLOYEE') NOT NULL DEFAULT 'EMPLOYEE',
  employee_id INT UNSIGNED NULL UNIQUE,
  status ENUM('Active','Inactive') NOT NULL DEFAULT 'Active',
  last_login DATETIME NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_users_employee FOREIGN KEY(employee_id)
    REFERENCES employees(employee_id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS attendance (
  attendance_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  employee_id INT UNSIGNED NOT NULL,
  attendance_date DATE NOT NULL,
  status ENUM('PRESENT','ABSENT','HALF DAY','LEAVE') NOT NULL,
  check_in TIME NULL,
  check_out TIME NULL,
  marked_by INT UNSIGNED NULL,
  remarks VARCHAR(500) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_attendance_employee_date(employee_id,attendance_date),
  CONSTRAINT fk_attendance_employee FOREIGN KEY(employee_id)
    REFERENCES employees(employee_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_attendance_marker FOREIGN KEY(marked_by)
    REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS leave_requests (
  leave_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  employee_id INT UNSIGNED NOT NULL,
  leave_type VARCHAR(50) NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  total_days SMALLINT UNSIGNED NOT NULL,
  reason VARCHAR(1000) NOT NULL,
  status ENUM('Pending','Approved','Rejected') NOT NULL DEFAULT 'Pending',
  applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  reviewed_by INT UNSIGNED NULL,
  reviewed_at DATETIME NULL,
  review_remarks VARCHAR(1000) NULL,
  CONSTRAINT fk_leave_employee FOREIGN KEY(employee_id)
    REFERENCES employees(employee_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_leave_reviewer FOREIGN KEY(reviewed_by)
    REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT chk_leave_dates CHECK(end_date >= start_date),
  CONSTRAINT chk_leave_days CHECK(total_days > 0)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS salary_records (
  salary_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  employee_id INT UNSIGNED NOT NULL,
  salary_month DATE NOT NULL,
  basic_salary DECIMAL(10,2) UNSIGNED NOT NULL,
  allowances DECIMAL(10,2) NOT NULL DEFAULT 0,
  overtime_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
  bonus DECIMAL(10,2) NOT NULL DEFAULT 0,
  deductions DECIMAL(10,2) NOT NULL DEFAULT 0,
  net_salary DECIMAL(12,2) GENERATED ALWAYS AS
    (basic_salary + allowances + overtime_amount + bonus - deductions) STORED,
  payment_status ENUM('Pending','Paid') NOT NULL DEFAULT 'Pending',
  payment_date DATE NULL,
  payment_method VARCHAR(60) NULL,
  processed_by INT UNSIGNED NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_salary_employee_month(employee_id,salary_month),
  CONSTRAINT fk_salary_employee FOREIGN KEY(employee_id)
    REFERENCES employees(employee_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_salary_processor FOREIGN KEY(processed_by)
    REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT chk_salary_nonnegative CHECK(basic_salary >= 0 AND allowances >= 0
    AND overtime_amount >= 0 AND bonus >= 0 AND deductions >= 0),
  CONSTRAINT chk_salary_month_start CHECK(DAY(salary_month) = 1)
) ENGINE=InnoDB;

CREATE INDEX idx_attendance_date ON attendance(attendance_date);
CREATE INDEX idx_leave_status ON leave_requests(status);
CREATE INDEX idx_salary_month ON salary_records(salary_month);