from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.feedback_service import FeedbackService
from app.utils.responses import success_response


feedback_bp = Blueprint("feedback", __name__)
feedback_service = FeedbackService()


@feedback_bp.post("/analysis/<int:analysis_id>/feedback")
@jwt_required()
def create_feedback(analysis_id):
    payload = request.get_json(silent=True) or {}
    feedback = feedback_service.create(int(get_jwt_identity()), analysis_id, payload)
    return success_response(feedback.to_dict(), "Feedback saved", 201)
