# API Documentation

Base URL:

```text
http://127.0.0.1:5000/api
```

All protected endpoints require:

```http
Authorization: Bearer <access_token>
```

## Health

### GET `/health`

Returns service status and model configuration state.

Response:

```json
{
  "success": true,
  "message": "success",
  "data": {
    "service": "nail-disease-identification-ai-framework",
    "status": "healthy",
    "model_version": "unconfigured",
    "demo_inference": false
  }
}
```

## Authentication

### POST `/auth/register`

Request:

```json
{
  "full_name": "Demo Patient",
  "email": "patient@example.com",
  "password": "Password123"
}
```

Response: `201 Created`

```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "id": 1,
    "full_name": "Demo Patient",
    "email": "patient@example.com",
    "role": "patient",
    "is_active": true,
    "created_at": "2026-07-02T10:00:00"
  }
}
```

### POST `/auth/login`

Request:

```json
{
  "email": "patient@example.com",
  "password": "Password123"
}
```

Response:

```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "<jwt>",
    "token_type": "Bearer",
    "user": {
      "id": 1,
      "full_name": "Demo Patient",
      "email": "patient@example.com"
    }
  }
}
```

### GET `/auth/profile`

Returns the authenticated user's profile.

## Upload Validation

### POST `/upload/validate`

Content-Type: `multipart/form-data`

Form field:

```text
image=<jpg|jpeg|png>
```

Response:

```json
{
  "success": true,
  "message": "Image quality validation completed",
  "data": {
    "metadata": {
      "file_size_bytes": 220115,
      "width": 1024,
      "height": 768,
      "blur_score": 85.41,
      "brightness": 132.8
    },
    "warnings": []
  }
}
```

## Analysis

### POST `/analyze`

Protected. Content-Type: `multipart/form-data`.

Form field:

```text
image=<jpg|jpeg|png>
```

Response:

```json
{
  "success": true,
  "message": "Analysis completed",
  "data": {
    "id": 10,
    "predicted_condition": "onychomycosis",
    "confidence": 0.91,
    "severity_score": 48.5,
    "severity_label": "moderate",
    "status": "completed",
    "model_version": "2026.07.01",
    "report": {
      "pipeline": [
        "preprocessing",
        "u_net_segmentation",
        "cnn_classification",
        "grad_cam_heatmap",
        "severity_scoring",
        "report_generation"
      ],
      "clinical_notice": "This software output is decision support only and is not a standalone medical diagnosis."
    }
  }
}
```

If model files are not configured and demo inference is disabled:

```json
{
  "success": false,
  "error": {
    "code": "MODEL_UNAVAILABLE",
    "message": "U-Net and CNN model files must be configured before clinical inference"
  }
}
```

## History

### GET `/history?limit=25&offset=0`

Returns the authenticated user's prior analyses.

### GET `/history/{analysis_id}`

Returns one analysis record owned by the authenticated user.

## Feedback

### POST `/analysis/{analysis_id}/feedback`

Request:

```json
{
  "rating": 4,
  "correction_label": "onychomycosis",
  "comment": "Clinician agrees with prediction but severity may be mild."
}
```

Response: `201 Created`

```json
{
  "success": true,
  "message": "Feedback saved",
  "data": {
    "id": 1,
    "analysis_id": 10,
    "rating": 4,
    "correction_label": "onychomycosis",
    "comment": "Clinician agrees with prediction but severity may be mild."
  }
}
```
