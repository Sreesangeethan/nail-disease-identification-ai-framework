from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.ai_pipeline import AIPipelineError, NailDiseaseAIPipeline


analyze_bp = Blueprint("analyze", __name__)


@analyze_bp.post("")
@analyze_bp.post("/")
@jwt_required()
def analyze_image():
    pipeline = NailDiseaseAIPipeline(
        config=current_app.config,
        logger=current_app.logger,
    )

    try:
        analysis = pipeline.analyze(
            user_id=int(get_jwt_identity()),
            file_storage=request.files.get("image"),
        )
    except AIPipelineError as exc:
        current_app.logger.warning("Analysis request failed: %s", exc.message)
        return _error(exc.message, exc.status_code, exc.code, exc.details)

    return _success(analysis.to_dict(), "Analysis completed", 201)


def _success(data=None, message="success", status_code=200):
    return jsonify({"success": True, "message": message, "data": data or {}}), status_code


def _error(message, status_code, code, details=None):
    return (
        jsonify(
            {
                "success": False,
                "error": {
                    "code": code,
                    "message": message,
                    "details": details or {},
                },
            }
        ),
        status_code,
    )
