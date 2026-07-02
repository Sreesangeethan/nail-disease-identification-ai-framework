# Architecture

## Design Goals

The backend follows a layered Flask architecture:

- Routes handle HTTP only.
- Services own business rules and orchestration.
- Models map database tables using SQLAlchemy.
- AI model loading and inference are isolated under `app/ai_models`.
- Utilities centralize validation, error handling, response formatting, logging, and security helpers.

This separation keeps the system testable and prevents API handlers from becoming medical AI business logic containers.

## Request Flow

```text
Flutter client
  -> Flask route
  -> service layer
  -> image validation and storage
  -> AI pipeline
  -> SQLAlchemy model persistence
  -> JSON response
```

## AI Pipeline

The inference pipeline is implemented in `backend/app/ai_models/pipeline.py`.

1. Preprocessing
   - Load image with Pillow.
   - Convert to RGB.
   - Resize and normalize for model inputs.

2. U-Net segmentation
   - Loads `UNET_MODEL_PATH`.
   - Produces a nail-region mask.
   - Falls back only when demo inference is enabled.

3. CNN classification
   - Loads `CLASSIFIER_MODEL_PATH`.
   - Produces class probabilities.
   - Class labels are defined in the pipeline module and should match training output order.

4. Grad-CAM compatible heatmap
   - Produces an explainability artifact for UI display and clinical review.
   - A validated production implementation should bind to the final convolutional layer through `GRADCAM_LAYER_NAME`.

5. Severity score
   - Combines mask coverage, heatmap intensity, and model confidence.
   - Returns low, moderate, or high.

6. Report generation
   - Stores structured JSON in `nail_analyses.report_json`.

## Database

Primary tables:

- `users`
- `nail_analyses`
- `analysis_feedback`
- `model_versions`
- `audit_logs`

Indexes are included for login lookup, history retrieval, condition filtering, and audit traceability.

## Security Practices

- JWT authentication for protected endpoints.
- Werkzeug password hashing.
- Extension allow-list for image uploads.
- Image verification using Pillow.
- Quality checks using OpenCV.
- File names are sanitized and replaced with UUID-based names.
- Centralized exception handling prevents leaking stack traces to API clients.

## Production Hardening Checklist

- Replace all `.env.example` secrets.
- Configure HTTPS at the reverse proxy.
- Store uploads outside the public web root.
- Use encrypted storage for medical data.
- Add database migrations with Alembic or Flask-Migrate.
- Add structured audit logging for all PHI access.
- Add model registry approval workflow.
- Add clinical validation datasets and drift monitoring.
- Add rate limiting and request throttling.
- Add automated tests for routes, services, and model adapters.
