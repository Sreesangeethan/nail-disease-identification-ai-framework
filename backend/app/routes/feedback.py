from flask import Blueprint, current_app, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.feedback_service import FeedbackService
from app.utils.exceptions import AppError
from app.utils.responses import error_response, success_response


feedback_bp = Blueprint("feedback", __name__)
feedback_service = FeedbackService()


@feedback_bp.post("/analysis/<int:analysis_id>/feedback")
@jwt_required()
def create_feedback(analysis_id):
    payload = request.get_json(silent=True) or {}
    try:
        feedback = feedback_service.create(int(get_jwt_identity()), analysis_id, payload)
    except AppError as exc:
        current_app.logger.warning("Feedback create failed: %s", exc.message)
        return error_response(exc.message, exc.status_code, exc.error_code, exc.details)
    return success_response(feedback.to_dict(), "Feedback saved", 201)


@feedback_bp.get("/analysis/<int:analysis_id>/feedback")
@jwt_required()
def list_feedback_for_analysis(analysis_id):
    try:
        feedback_items = feedback_service.list_for_analysis(
            int(get_jwt_identity()),
            analysis_id,
        )
    except AppError as exc:
        current_app.logger.warning("Feedback list failed: %s", exc.message)
        return error_response(exc.message, exc.status_code, exc.error_code, exc.details)
    return success_response({"items": [item.to_dict() for item in feedback_items]})


@feedback_bp.get("/feedback/<int:feedback_id>")
@jwt_required()
def get_feedback(feedback_id):
    try:
        feedback = feedback_service.get_for_user(int(get_jwt_identity()), feedback_id)
    except AppError as exc:
        current_app.logger.warning("Feedback lookup failed: %s", exc.message)
        return error_response(exc.message, exc.status_code, exc.error_code, exc.details)
    return success_response(feedback.to_dict())


@feedback_bp.patch("/feedback/<int:feedback_id>")
@jwt_required()
def update_feedback(feedback_id):
    payload = request.get_json(silent=True) or {}
    try:
        feedback = feedback_service.update(int(get_jwt_identity()), feedback_id, payload)
    except AppError as exc:
        current_app.logger.warning("Feedback update failed: %s", exc.message)
        return error_response(exc.message, exc.status_code, exc.error_code, exc.details)
    return success_response(feedback.to_dict(), "Feedback updated")


@feedback_bp.delete("/feedback/<int:feedback_id>")
@jwt_required()
def delete_feedback(feedback_id):
    try:
        deleted = feedback_service.delete(int(get_jwt_identity()), feedback_id)
    except AppError as exc:
        current_app.logger.warning("Feedback delete failed: %s", exc.message)
        return error_response(exc.message, exc.status_code, exc.error_code, exc.details)
    return success_response({"id": deleted.id}, "Feedback deleted")
