-- ============================================================
-- Village Complaint Redressal System - Schema v2 Updates
-- Includes: Wards, Assets, SLAs, Escalations, Worker Tracking
-- ============================================================

USE grampur_csp;

-- 1. Wards Table
CREATE TABLE IF NOT EXISTS wards (
    ward_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    boundaries_json JSON DEFAULT NULL,
    population INT DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Insert default wards
INSERT IGNORE INTO wards (ward_id, name) VALUES
(1, 'North Ward'), (2, 'South Ward'), (3, 'East Ward'), (4, 'West Ward');

-- 2. Assets Table (Village Asset Registry)
CREATE TABLE IF NOT EXISTS assets (
    asset_id VARCHAR(50) PRIMARY KEY, -- e.g. AST-WL-001
    type ENUM('Streetlight', 'Water Tank', 'Drainage Line', 'Road Segment', 'Public Toilet') NOT NULL,
    ward_id INT NOT NULL,
    location_lat DECIMAL(10, 8) DEFAULT NULL,
    location_lng DECIMAL(11, 8) DEFAULT NULL,
    status ENUM('Active', 'Maintenance Required', 'Broken', 'Under Repair') NOT NULL DEFAULT 'Active',
    installed_date DATE DEFAULT NULL,
    last_maintained DATE DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ward_id) REFERENCES wards(ward_id)
) ENGINE=InnoDB;

-- 3. SLAs Table
CREATE TABLE IF NOT EXISTS slas (
    category VARCHAR(100) PRIMARY KEY,
    max_days_to_resolve INT NOT NULL,
    escalation_level_1_days INT NOT NULL,
    escalation_level_2_days INT NOT NULL
) ENGINE=InnoDB;

-- Insert SLA defaults
INSERT IGNORE INTO slas (category, max_days_to_resolve, escalation_level_1_days, escalation_level_2_days) VALUES
('Road Issues', 15, 7, 10),
('Water Supply Problems', 7, 3, 5),
('Streetlight Issues', 5, 2, 4),
('Drainage Problems', 10, 4, 7),
('Garbage Collection Issues', 3, 1, 2),
('Sanitation Issues', 5, 2, 4);

-- 4. Escalation Logs Table
CREATE TABLE IF NOT EXISTS escalations (
    escalation_id INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id VARCHAR(15) NOT NULL,
    level INT NOT NULL, -- 1=Village Secretary, 2=Panchayat Officer, 3=Mandal Authority
    escalated_to VARCHAR(100) NOT NULL,
    reason VARCHAR(255) NOT NULL,
    is_resolved TINYINT(1) DEFAULT 0,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (complaint_id) REFERENCES complaints(complaint_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 5. Worker Field Tracking Table
CREATE TABLE IF NOT EXISTS worker_tracking (
    tracking_id INT AUTO_INCREMENT PRIMARY KEY,
    worker_id INT NOT NULL,
    lat DECIMAL(10, 8) NOT NULL,
    lng DECIMAL(11, 8) NOT NULL,
    status ENUM('Checked-in', 'En-route', 'Working', 'Checked-out') NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (worker_id) REFERENCES workers(worker_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 6. Modify Existing Complaints Table
ALTER TABLE complaints
    ADD COLUMN ward_id INT DEFAULT NULL AFTER location,
    ADD COLUMN asset_id VARCHAR(50) DEFAULT NULL AFTER ward_id,
    ADD COLUMN duplicate_of VARCHAR(15) DEFAULT NULL AFTER asset_id,
    ADD COLUMN sla_breach_status ENUM('None', 'Warning', 'Breached') DEFAULT 'None' AFTER priority,
    ADD CONSTRAINT fk_complaints_ward FOREIGN KEY (ward_id) REFERENCES wards(ward_id) ON DELETE SET NULL,
    ADD CONSTRAINT fk_complaints_asset FOREIGN KEY (asset_id) REFERENCES assets(asset_id) ON DELETE SET NULL,
    ADD CONSTRAINT fk_complaints_duplicate FOREIGN KEY (duplicate_of) REFERENCES complaints(complaint_id) ON DELETE SET NULL;
