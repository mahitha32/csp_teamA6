-- ============================================================
-- Village Complaint Redressal System
-- Village: Vemavaram, Krishna District, Andhra Pradesh
-- Schema Version: 2.0 (Unified — replaces schema.sql + schema_v2.sql)
-- Run this once: mysql -u root -p < schema_complete.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS vemavaram_csp
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE vemavaram_csp;

-- ═══════════════════════════════════════════════════════════
-- CORE USER TABLE
-- Roles: citizen | worker | admin
-- Workers: stored here for unified auth; profile detail
--          goes in the `worker_profiles` table below.
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS users (
    user_id       INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    mobile        VARCHAR(15)  NOT NULL UNIQUE,
    email         VARCHAR(150) DEFAULT NULL,
    village       VARCHAR(100) NOT NULL DEFAULT 'Vemavaram',
    password_hash VARCHAR(255) NOT NULL,
    role          ENUM('citizen', 'worker', 'admin') NOT NULL DEFAULT 'citizen',
    fcm_token     VARCHAR(255) DEFAULT NULL,   -- Firebase Cloud Messaging for push
    is_active     TINYINT(1)   NOT NULL DEFAULT 1,
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_mobile (mobile),
    INDEX idx_role   (role)
) ENGINE=InnoDB;

-- ═══════════════════════════════════════════════════════════
-- WORKER PROFILE
-- Extends users WHERE role='worker' with department details
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS worker_profiles (
    profile_id   INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT NOT NULL UNIQUE,
    department   ENUM(
                     'Roads & Infrastructure',
                     'Electrical & Streetlights',
                     'Water Supply',
                     'Drainage & Sanitation',
                     'Waste Management',
                     'General Services'
                 ) NOT NULL,
    employee_id  VARCHAR(20)  DEFAULT NULL,
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_department (department)
) ENGINE=InnoDB;

-- ═══════════════════════════════════════════════════════════
-- OTP SESSIONS (Mobile phone verification)
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS otp_sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    mobile     VARCHAR(15) NOT NULL,
    otp_code   VARCHAR(10) NOT NULL,
    purpose    ENUM('registration', 'login', 'forgot_password') NOT NULL DEFAULT 'login',
    is_used    TINYINT(1)  NOT NULL DEFAULT 0,
    attempts   INT         NOT NULL DEFAULT 0,
    expires_at DATETIME    NOT NULL,
    created_at DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_mobile_otp (mobile, otp_code)
) ENGINE=InnoDB;

-- ═══════════════════════════════════════════════════════════
-- WARDS (Village ward divisions)
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS wards (
    ward_id         INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    boundaries_json JSON         DEFAULT NULL,
    population      INT          DEFAULT 0,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

INSERT IGNORE INTO wards (ward_id, name) VALUES
    (1, 'Ward 1'),
    (2, 'Ward 2'),
    (3, 'Ward 3'),
    (4, 'Ward 4');

-- ═══════════════════════════════════════════════════════════
-- COMPLAINTS (Core table)
-- image_url: Cloudinary URL for complaint evidence photo
-- resolution_image_url: Cloudinary URL for post-fix photo
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS complaints (
    complaint_id         VARCHAR(15)   PRIMARY KEY,          -- e.g. CMP2026001
    user_id              INT           NOT NULL,
    title                VARCHAR(200)  NOT NULL,
    category             ENUM(
                             'Road Issues',
                             'Streetlight Issues',
                             'Water Supply Problems',
                             'Drainage Problems',
                             'Garbage Collection Issues',
                             'Sanitation Issues'
                         ) NOT NULL,
    description          TEXT          NOT NULL,
    image_url            VARCHAR(500)  DEFAULT NULL,         -- Cloudinary URL
    ai_category_suggestion VARCHAR(100) DEFAULT NULL,
    location             VARCHAR(255)  NOT NULL,
    latitude             DECIMAL(10,8) DEFAULT NULL,
    longitude            DECIMAL(11,8) DEFAULT NULL,
    ward_id              INT           DEFAULT NULL,
    status               ENUM(
                             'Submitted',
                             'Under Review',
                             'Assigned',
                             'In Progress',
                             'Resolved',
                             'Rejected'
                         ) NOT NULL DEFAULT 'Submitted',
    priority             ENUM('Low', 'Medium', 'High', 'Critical') NOT NULL DEFAULT 'Medium',
    worker_id            INT           DEFAULT NULL,         -- FK to users (role=worker)
    escalation_level     INT           NOT NULL DEFAULT 0,
    escalated_at         DATETIME      DEFAULT NULL,
    resolution_image_url VARCHAR(500)  DEFAULT NULL,         -- Cloudinary URL
    resolution_notes     TEXT          DEFAULT NULL,
    created_at           DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    resolved_at          DATETIME      DEFAULT NULL,
    FOREIGN KEY (user_id)   REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (worker_id) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (ward_id)   REFERENCES wards(ward_id) ON DELETE SET NULL,
    INDEX idx_user_id    (user_id),
    INDEX idx_worker_id  (worker_id),
    INDEX idx_status     (status),
    INDEX idx_category   (category),
    INDEX idx_created    (created_at)
) ENGINE=InnoDB;

-- ═══════════════════════════════════════════════════════════
-- ASSIGNMENTS (Worker assignment history per complaint)
-- assigned_worker_id FK → users(user_id) where role='worker'
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS assignments (
    assignment_id INT          AUTO_INCREMENT PRIMARY KEY,
    complaint_id  VARCHAR(15)  NOT NULL,
    worker_id     INT          NOT NULL,     -- FK → users (role=worker)
    assigned_by   INT          NOT NULL,     -- FK → users (role=admin)
    notes         TEXT         DEFAULT NULL,
    is_current    TINYINT(1)   NOT NULL DEFAULT 1,
    assigned_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (complaint_id) REFERENCES complaints(complaint_id) ON DELETE CASCADE,
    FOREIGN KEY (worker_id)    REFERENCES users(user_id),
    FOREIGN KEY (assigned_by)  REFERENCES users(user_id),
    INDEX idx_complaint_id (complaint_id),
    INDEX idx_worker_id    (worker_id)
) ENGINE=InnoDB;

-- ═══════════════════════════════════════════════════════════
-- COMPLAINT STATUS HISTORY (Audit trail)
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS complaint_status_history (
    history_id   INT          AUTO_INCREMENT PRIMARY KEY,
    complaint_id VARCHAR(15)  NOT NULL,
    old_status   VARCHAR(50)  DEFAULT NULL,
    new_status   VARCHAR(50)  NOT NULL,
    changed_by   INT          NOT NULL,
    notes        TEXT         DEFAULT NULL,
    changed_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (complaint_id) REFERENCES complaints(complaint_id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by)   REFERENCES users(user_id),
    INDEX idx_complaint_id (complaint_id)
) ENGINE=InnoDB;

-- ═══════════════════════════════════════════════════════════
-- FEEDBACK (Post-resolution citizen ratings)
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS feedback (
    feedback_id  INT          AUTO_INCREMENT PRIMARY KEY,
    complaint_id VARCHAR(15)  NOT NULL UNIQUE,
    user_id      INT          NOT NULL,
    rating       TINYINT      NOT NULL CHECK (rating BETWEEN 1 AND 5),
    remarks      TEXT         DEFAULT NULL,
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (complaint_id) REFERENCES complaints(complaint_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)      REFERENCES users(user_id),
    INDEX idx_complaint_id (complaint_id),
    INDEX idx_rating       (rating)
) ENGINE=InnoDB;

-- ═══════════════════════════════════════════════════════════
-- NOTIFICATIONS (In-app alerts)
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INT          AUTO_INCREMENT PRIMARY KEY,
    user_id         INT          NOT NULL,
    complaint_id    VARCHAR(15)  DEFAULT NULL,
    title           VARCHAR(200) NOT NULL,
    message         TEXT         NOT NULL,
    type            ENUM(
                        'complaint_received',
                        'complaint_assigned',
                        'status_changed',
                        'complaint_resolved',
                        'general'
                    ) NOT NULL DEFAULT 'general',
    is_read         TINYINT(1)   NOT NULL DEFAULT 0,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)      REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (complaint_id) REFERENCES complaints(complaint_id) ON DELETE SET NULL,
    INDEX idx_user_id  (user_id),
    INDEX idx_is_read  (is_read)
) ENGINE=InnoDB;

-- ═══════════════════════════════════════════════════════════
-- ACTIVITY LOGS (Security audit trail)
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS activity_logs (
    log_id     INT          AUTO_INCREMENT PRIMARY KEY,
    user_id    INT          DEFAULT NULL,
    action     VARCHAR(100) NOT NULL,
    details    TEXT         DEFAULT NULL,
    ip_address VARCHAR(45)  DEFAULT NULL,
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_action  (action)
) ENGINE=InnoDB;

-- ═══════════════════════════════════════════════════════════
-- SURVEY INSIGHTS (Pre-loaded Vemavaram field survey data)
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS survey_insights (
    insight_id      INT            AUTO_INCREMENT PRIMARY KEY,
    category        VARCHAR(100)   NOT NULL,
    response_count  INT            NOT NULL DEFAULT 0,
    percentage      DECIMAL(5,2)   NOT NULL DEFAULT 0.00,
    severity        ENUM('Critical', 'High', 'Medium', 'Low') NOT NULL DEFAULT 'Medium',
    description     TEXT           DEFAULT NULL,
    survey_year     YEAR           NOT NULL DEFAULT 2025,
    created_at      DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ═══════════════════════════════════════════════════════════
-- CONTACT MESSAGES (Landing page contact form submissions)
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS contact_messages (
    message_id  INT          AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(150) NOT NULL,
    phone       VARCHAR(15)  DEFAULT NULL,
    message     TEXT         NOT NULL,
    is_read     TINYINT(1)   NOT NULL DEFAULT 0,
    replied_at  DATETIME     DEFAULT NULL,
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at),
    INDEX idx_is_read    (is_read)
) ENGINE=InnoDB;

-- ═══════════════════════════════════════════════════════════
-- ASSETS (Village infrastructure asset registry)
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS assets (
    asset_id        VARCHAR(50)  PRIMARY KEY,
    type            ENUM('Streetlight', 'Water Tank', 'Drainage Line', 'Road Segment', 'Public Toilet') NOT NULL,
    ward_id         INT          NOT NULL,
    location_lat    DECIMAL(10,8) DEFAULT NULL,
    location_lng    DECIMAL(11,8) DEFAULT NULL,
    status          ENUM('Active', 'Maintenance Required', 'Broken', 'Under Repair') NOT NULL DEFAULT 'Active',
    installed_date  DATE         DEFAULT NULL,
    last_maintained DATE         DEFAULT NULL,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ward_id) REFERENCES wards(ward_id)
) ENGINE=InnoDB;

-- ═══════════════════════════════════════════════════════════
-- SLAs (Service Level Agreements per category)
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS slas (
    category                VARCHAR(100) PRIMARY KEY,
    max_days_to_resolve     INT NOT NULL,
    escalation_level_1_days INT NOT NULL,
    escalation_level_2_days INT NOT NULL
) ENGINE=InnoDB;

INSERT IGNORE INTO slas VALUES
    ('Road Issues',               15, 7, 10),
    ('Water Supply Problems',      7, 3,  5),
    ('Streetlight Issues',         5, 2,  4),
    ('Drainage Problems',         10, 4,  7),
    ('Garbage Collection Issues',  3, 1,  2),
    ('Sanitation Issues',          5, 2,  4);

-- ═══════════════════════════════════════════════════════════
-- ESCALATION LOGS
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS escalations (
    escalation_id INT          AUTO_INCREMENT PRIMARY KEY,
    complaint_id  VARCHAR(15)  NOT NULL,
    level         INT          NOT NULL,
    escalated_to  VARCHAR(100) NOT NULL,
    reason        VARCHAR(255) NOT NULL,
    is_resolved   TINYINT(1)   DEFAULT 0,
    timestamp     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (complaint_id) REFERENCES complaints(complaint_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ═══════════════════════════════════════════════════════════
-- SEED DATA
-- ═══════════════════════════════════════════════════════════

-- Default admin user
-- Mobile: 9999900000 | Password: Admin@123
-- bcrypt hash of "Admin@123" (12 rounds)
INSERT INTO users (name, mobile, village, password_hash, role)
VALUES ('Village Admin', '9999900000', 'Vemavaram',
        '$2b$12$WB.H6JKaCfcsOeugjW3y9OUgxDT4k6pWfe1c3FGlCDZzusRUlxxB.', 'admin')
ON DUPLICATE KEY UPDATE password_hash = VALUES(password_hash), name = VALUES(name), village = VALUES(village);

-- Vemavaram Village Survey Insights (from field survey 2025)
INSERT INTO survey_insights (category, response_count, percentage, severity, description, survey_year) VALUES
('Road Issues',               87, 34.80, 'Critical', 'Potholed and unmaintained village roads causing accidents and vehicle damage', 2025),
('Water Supply Problems',     65, 26.00, 'Critical', 'Irregular water supply; taps dry for 3+ days per week in summer months', 2025),
('Streetlight Issues',        45, 18.00, 'High',     'Non-functioning streetlights creating safety hazards at night', 2025),
('Drainage Problems',         38, 15.20, 'High',     'Blocked drains causing waterlogging during monsoon season', 2025),
('Garbage Collection Issues', 32, 12.80, 'Medium',   'Irregular garbage pickup; waste accumulating near common areas', 2025),
('Sanitation Issues',         23,  9.20, 'Medium',   'Public toilet maintenance and cleanliness issues', 2025)
ON DUPLICATE KEY UPDATE response_count = response_count;
