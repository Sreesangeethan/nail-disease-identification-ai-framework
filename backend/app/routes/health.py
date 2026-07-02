from flask import Blueprint, current_app

from app.utils.responses import success_response


health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health_check():
    return success_response(
        {
            "service": "nail-disease-identification-ai-framework",
            "status": "healthy",
            "model_version": current_app.config["MODEL_VERSION"],
            "demo_inference": current_app.config["ALLOW_DEMO_INFERENCE"],
        }
    )
