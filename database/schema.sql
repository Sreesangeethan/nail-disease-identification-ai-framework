CREATE DATABASE IF NOT EXISTS nail_disease_ai
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE nail_disease_ai;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  full_name VARCHAR(120) NOT NULL,
  email VARCHAR(180) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(40) NOT NULL DEFAULT 'patient',
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_users_email (email)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS model_versions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  version VARCHAR(80) NOT NULL,
  artifact_path VARCHAR(500) NOT NULL,
  model_type VARCHAR(80) NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_model_versions_active (model_type, is_active)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS nail_analyses (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  original_filename VARCHAR(255) NOT NULL,
  stored_filename VARCHAR(255) NOT NULL,
  image_path VARCHAR(500) NOT NULL,
  segmentation_mask_path VARCHAR(500) NULL,
  heatmap_path VARCHAR(500) NULL,
  predicted_condition VARCHAR(120) NULL,
  confidence DOUBLE NULL,
  severity_score DOUBLE NULL,
  severity_label VARCHAR(60) NULL,
  status VARCHAR(40) NOT NULL DEFAULT 'completed',
  model_version VARCHAR(120) NOT NULL DEFAULT 'unconfigured',
  quality_metadata JSON NULL,
  report_json JSON NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_nail_analyses_user
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE,
  INDEX idx_nail_analyses_user_created (user_id, created_at),
  INDEX idx_nail_analyses_condition (predicted_condition),
  INDEX idx_nail_analyses_status (status)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS analysis_feedback (
  id INT AUTO_INCREMENT PRIMARY KEY,
  analysis_id INT NOT NULL,
  user_id INT NOT NULL,
  rating INT NULL,
  correction_label VARCHAR(120) NULL,
  comment TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_feedback_analysis
    FOREIGN KEY (analysis_id) REFERENCES nail_analyses(id)
    ON DELETE CASCADE,
  CONSTRAINT fk_feedback_user
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE,
  CONSTRAINT chk_feedback_rating
    CHECK (rating IS NULL OR rating BETWEEN 1 AND 5),
  INDEX idx_feedback_analysis (analysis_id),
  INDEX idx_feedback_user (user_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS audit_logs (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NULL,
  action VARCHAR(120) NOT NULL,
  entity_type VARCHAR(120) NULL,
  entity_id VARCHAR(80) NULL,
  ip_address VARCHAR(80) NULL,
  user_agent VARCHAR(500) NULL,
  metadata JSON NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_audit_logs_user
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE SET NULL,
  INDEX idx_audit_logs_user_created (user_id, created_at),
  INDEX idx_audit_logs_action (action)
) ENGINE=InnoDB;
