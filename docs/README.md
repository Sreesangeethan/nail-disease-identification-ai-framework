# Nail Disease Identification AI Framework

Production-oriented Flask backend scaffold for nail disease image analysis.

This repository contains:

- Flask API backend with JWT authentication.
- MySQL persistence designed for XAMPP local development.
- Secure image upload and image quality validation.
- AI inference pipeline structure:
  preprocessing -> U-Net segmentation -> CNN classification -> Grad-CAM heatmap -> severity score -> report.
- Flutter client structure and API examples.

Important clinical note: this project is a software framework. It must not be used for real clinical decisions until the models are validated, versioned, audited, and approved through the required medical governance process.

## Repository Structure

```text
backend/
  app/
    ai_models/
    models/
    routes/
    services/
    utils/
    config.py
    extensions.py
    main.py
  run.py
  requirements.txt
  .env.example
database/
  schema.sql
  dummy_data.sql
docs/
  API_Documentation.md
  Architecture.md
  Flutter_Integration.md
```

## Local Setup

1. Start Apache and MySQL in XAMPP.
2. Open phpMyAdmin or MySQL CLI.
3. Run `database/schema.sql`.
4. Optionally run `database/dummy_data.sql`.
5. Create a Python virtual environment:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

6. Update `.env` with secure secrets and your MySQL password.
7. Run the API:

```bash
python run.py
```

The API runs at `http://127.0.0.1:5000`.

## Model Artifacts

Place trained CPU-compatible TensorFlow/Keras artifacts here when running from the
`backend` directory:

```text
model_artifacts/unet.keras
model_artifacts/classifier.keras
```

By default, `ALLOW_DEMO_INFERENCE=false`. This is intentional: production medical AI must not silently pretend to diagnose without validated model artifacts. For UI testing only, set `ALLOW_DEMO_INFERENCE=true`.

## Suggested Commit Commands

Because the current folder did not report as a git repository during scaffolding, first ensure this directory is the real clone. Once git is available:

```bash
git add backend
git commit -m "Add Flask backend framework"
git add database
git commit -m "Add MySQL database schema and seed data"
git add docs
git commit -m "Add project documentation"
```
