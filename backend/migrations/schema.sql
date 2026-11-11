-- ============================================================
-- Village Complaint Redressal System - MySQL Database Schema
-- Village: Gadepudi Village
-- Generated: 2026
-- ============================================================

CREATE DATABASE IF NOT EXISTS grampur_csp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE grampur_csp;

-- -------------------------------------------------------
-- Table: users
-- Stores all registered villagers, workers, and admins
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id      INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    mobile       VARCHAR(15) NOT NULL UNIQUE,
    village      VARCHAR(100) NOT NULL DEFAULT 'Gadepudi Village',
    password_hash VARCHAR(255) NOT NULL,
    role         ENUM('villager', 'worker', 'admin') NOT NULL DEFAULT 'villager',
    fcm_token    VARCHAR(255) DEFAULT NULL,   -- Firebase Cloud Messaging token for push notifications
    is_active    TINYINT(1) NOT NULL DEFAULT 1,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_mobile (mobile),
    INDEX idx_role   (role)
) ENGINE=InnoDB;

-- -------------------------------------------------------
-- Table: otp_sessions
-- Stores OTP codes for mobile number verification
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS otp_sessions (
    session_id   INT AUTO_INCREMENT PRIMARY KEY,
    mobile       VARCHAR(15) NOT NULL,
    otp_code     VARCHAR(10) NOT NULL,
    purpose      ENUM('registration', 'login', 'forgot_password') NOT NULL DEFAULT 'login',
    is_used      TINYINT(1) NOT NULL DEFAULT 0,
    attempts     INT NOT NULL DEFAULT 0,
    expires_at   DATETIME NOT NULL,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_mobile_otp (mobile, otp_code)
) ENGINE=InnoDB;

-- -------------------------------------------------------
-- Table: complaints
-- Core table for all village complaints
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS complaints (
    complaint_id    VARCHAR(15) PRIMARY KEY,          -- e.g. CMP2026001
    user_id         INT NOT NULL,
    title           VARCHAR(200) NOT NULL,
    category        ENUM(
                        'Road Issues',
                        'Streetlight Issues',
                        'Water Supply Problems',
                        'Drainage Problems',
                        'Garbage Collection Issues',
                        'Sanitation Issues'
                    ) NOT NULL,
    description     TEXT NOT NULL,
    image_url       VARCHAR(500) DEFAULT NULL,        -- Firebase Storage URL
    ai_category_suggestion VARCHAR(100) DEFAULT NULL, -- AI-suggested category
    location        VARCHAR(255) NOT NULL,
    latitude        DECIMAL(10, 8) DEFAULT NULL,
    longitude       DECIMAL(11, 8) DEFAULT NULL,
    status          ENUM(
                        'Submitted',
                        'Under Review',
                        'Assigned',
                        'In Progress',
                        'Resolved',
                        'Rejected'
                    ) NOT NULL DEFAULT 'Submitted',
    priority        ENUM('Low', 'Medium', 'High', 'Critical') NOT NULL DEFAULT 'Medium',
    worker_id       INT DEFAULT NULL,            -- Assigned maintenance worker
    lat             DECIMAL(10, 8) DEFAULT NULL, -- GPS Latitude
    lng             DECIMAL(11, 8) DEFAULT NULL, -- GPS Longitude
    escalation_level INT NOT NULL DEFAULT 0,  -- 0=Normal, 1=Village Officer, 2=Senior Officer, 3=District
    escalated_at    DATETIME DEFAULT NULL,       -- When the last escalation happened
    resolution_image_url VARCHAR(500) DEFAULT NULL,  -- Photo after resolution
    resolution_notes TEXT DEFAULT NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    resolved_at     DATETIME DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (worker_id) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_user_id   (user_id),
    INDEX idx_worker_id (worker_id),
    INDEX idx_status    (status),
    INDEX idx_category  (category),
    INDEX idx_created   (created_at)
) ENGINE=InnoDB;

-- -------------------------------------------------------
-- Table: activity_logs
-- Security logging for sensitive actions
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS activity_logs (
    log_id      INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT DEFAULT NULL,
    action      VARCHAR(255) NOT NULL,
    details     TEXT,
    ip_address  VARCHAR(45),
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- -------------------------------------------------------
-- Table: complaint_status_history
-- Tracks every status change for audit trail
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS complaint_status_history (
    history_id      INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id    VARCHAR(15) NOT NULL,
    old_status      VARCHAR(50) DEFAULT NULL,
    new_status      VARCHAR(50) NOT NULL,
    changed_by      INT NOT NULL,                    -- user_id of admin/worker
    notes           VARCHAR(500) DEFAULT NULL,
    changed_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (complaint_id) REFERENCES complaints(complaint_id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by)   REFERENCES users(user_id),
    INDEX idx_complaint_id (complaint_id)
) ENGINE=InnoDB;

-- -------------------------------------------------------
-- Table: workers
-- Village maintenance and service workers
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS workers (
    worker_id    INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT DEFAULT NULL,                   -- linked user account (optional)
    worker_name  VARCHAR(100) NOT NULL,
    mobile       VARCHAR(15) NOT NULL UNIQUE,
    department   ENUM(
                     'Roads & Infrastructure',
                     'Electrical & Streetlights',
                     'Water Supply',
                     'Drainage & Sanitation',
                     'Waste Management',
                     'General Services'
                 ) NOT NULL,
    is_active    TINYINT(1) NOT NULL DEFAULT 1,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_department (department),
    INDEX idx_active (is_active)
) ENGINE=InnoDB;

-- -------------------------------------------------------
-- Table: assignments
-- Linking complaints to workers
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS assignments (
    assignment_id   INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id    VARCHAR(15) NOT NULL,
    worker_id       INT NOT NULL,
    assigned_by     INT NOT NULL,                    -- admin user_id
    assigned_date   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expected_date   DATE DEFAULT NULL,
    notes           TEXT DEFAULT NULL,
    is_current      TINYINT(1) NOT NULL DEFAULT 1,   -- only one active assignment per complaint
    FOREIGN KEY (complaint_id) REFERENCES complaints(complaint_id) ON DELETE CASCADE,
    FOREIGN KEY (worker_id)    REFERENCES workers(worker_id),
    FOREIGN KEY (assigned_by)  REFERENCES users(user_id),
    INDEX idx_complaint_id (complaint_id),
    INDEX idx_worker_id    (worker_id)
) ENGINE=InnoDB;

-- -------------------------------------------------------
-- Table: feedback
-- Post-resolution ratings from villagers
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS feedback (
    feedback_id     INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id    VARCHAR(15) NOT NULL UNIQUE,
    user_id         INT NOT NULL,
    rating          TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    remarks         TEXT DEFAULT NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (complaint_id) REFERENCES complaints(complaint_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)      REFERENCES users(user_id),
    INDEX idx_complaint_id (complaint_id),
    INDEX idx_rating       (rating)
) ENGINE=InnoDB;

-- -------------------------------------------------------
-- Table: notifications
-- In-app notifications for users
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    complaint_id    VARCHAR(15) DEFAULT NULL,
    title           VARCHAR(200) NOT NULL,
    message         TEXT NOT NULL,
    type            ENUM(
                        'complaint_received',
                        'complaint_assigned',
                        'status_changed',
                        'complaint_resolved',
                        'general'
                    ) NOT NULL DEFAULT 'general',
    is_read         TINYINT(1) NOT NULL DEFAULT 0,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)      REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (complaint_id) REFERENCES complaints(complaint_id) ON DELETE SET NULL,
    INDEX idx_user_id  (user_id),
    INDEX idx_is_read  (is_read)
) ENGINE=InnoDB;

-- -------------------------------------------------------
-- Table: survey_insights
-- Village survey results (pre-loaded from field survey)
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS survey_insights (
    insight_id      INT AUTO_INCREMENT PRIMARY KEY,
    category        VARCHAR(100) NOT NULL,
    response_count  INT NOT NULL DEFAULT 0,
    percentage      DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    severity        ENUM('Critical', 'High', 'Medium', 'Low') NOT NULL DEFAULT 'Medium',
    description     TEXT DEFAULT NULL,
    survey_year     YEAR NOT NULL DEFAULT 2025,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- -------------------------------------------------------
-- Stored Procedure: Generate unique complaint ID
-- Format: CMP + YEAR + 3-digit sequence
-- -------------------------------------------------------
DELIMITER $$

CREATE PROCEDURE IF NOT EXISTS generate_complaint_id(OUT new_id VARCHAR(15))
BEGIN
    DECLARE current_year CHAR(4);
    DECLARE seq INT;
    SET current_year = YEAR(CURDATE());
    SELECT COUNT(*) + 1 INTO seq
    FROM complaints
    WHERE complaint_id LIKE CONCAT('CMP', current_year, '%');
    SET new_id = CONCAT('CMP', current_year, LPAD(seq, 3, '0'));
END$$

DELIMITER ;

-- -------------------------------------------------------
-- Seed Data: Default admin user
-- Password: Admin@123 (bcrypt hashed)
-- -------------------------------------------------------
INSERT INTO users (name, mobile, village, password_hash, role)
VALUES ('Village Admin', '9999900000', 'Grampur Village',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMUBqnOVQzq.lMXJRjcT1vLZW2', 'admin')
ON DUPLICATE KEY UPDATE name = name;

-- -------------------------------------------------------
-- Seed Data: Village Survey Insights (from field survey)
-- -------------------------------------------------------
INSERT INTO survey_insights (category, response_count, percentage, severity, description, survey_year) VALUES
('Road Issues',              87, 34.80, 'Critical', 'Potholed and unmaintained village roads causing accidents and vehicle damage', 2025),
('Water Supply Problems',    65, 26.00, 'Critical', 'Irregular water supply; taps dry for 3+ days per week in summer months', 2025),
('Streetlight Issues',       45, 18.00, 'High',     'Non-functioning streetlights creating safety hazards at night', 2025),
('Drainage Problems',        38, 15.20, 'High',     'Blocked drains causing waterlogging during monsoon season', 2025),
('Garbage Collection Issues',32, 12.80, 'Medium',   'Irregular garbage pickup; waste accumulating near common areas', 2025),
('Sanitation Issues',        23,  9.20, 'Medium',   'Public toilet maintenance and cleanliness issues', 2025)
ON DUPLICATE KEY UPDATE response_count = response_count;
