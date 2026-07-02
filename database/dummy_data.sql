USE nail_disease_ai;

INSERT INTO model_versions (name, version, artifact_path, model_type, is_active)
VALUES
  ('U-Net Nail Segmentation', 'unconfigured', 'backend/model_artifacts/unet.keras', 'segmentation', TRUE),
  ('CNN Nail Disease Classifier', 'unconfigured', 'backend/model_artifacts/classifier.keras', 'classification', TRUE);

INSERT INTO users (full_name, email, password_hash, role, is_active)
VALUES
  (
    'Demo Patient',
    'patient@example.com',
    'replace-with-werkzeug-generated-password-hash',
    'patient',
    TRUE
  ),
  (
    'Demo Clinician',
    'clinician@example.com',
    'replace-with-werkzeug-generated-password-hash',
    'clinician',
    TRUE
  );

INSERT INTO audit_logs (user_id, action, entity_type, entity_id, metadata)
VALUES
  (NULL, 'seed_database', 'database', 'nail_disease_ai', JSON_OBJECT('source', 'database/dummy_data.sql'));
