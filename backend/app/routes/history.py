from flask import Blueprint, current_app, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.history_service import HistoryService
from app.utils.exceptions import AppError
from app.utils.responses import error_response, success_response


history_bp = Blueprint("history", __name__)
history_service = HistoryService()


@history_bp.get("")
@history_bp.get("/")
@jwt_required()
def list_history():
    result = history_service.list_for_user(
        user_id=int(get_jwt_identity()),
        limit=request.args.get("limit", 25),
        offset=request.args.get("offset", 0),
        status=request.args.get("status"),
        condition=request.args.get("condition"),
    )
    return success_response(
        {
            "items": [record.to_dict() for record in result["items"]],
            "total": result["total"],
            "limit": result["limit"],
            "offset": result["offset"],
        }
    )


@history_bp.get("/<int:analysis_id>")
@jwt_required()
def get_history_item(analysis_id):
    try:
        analysis = history_service.get_for_user(int(get_jwt_identity()), analysis_id)
    except AppError as exc:
        current_app.logger.warning("History lookup failed: %s", exc.message)
        return error_response(exc.message, exc.status_code, exc.error_code, exc.details)
    return success_response(analysis.to_dict())


@history_bp.delete("/<int:analysis_id>")
@jwt_required()
def delete_history_item(analysis_id):
    try:
        deleted = history_service.delete_for_user(int(get_jwt_identity()), analysis_id)
    except AppError as exc:
        current_app.logger.warning("History delete failed: %s", exc.message)
        return error_response(exc.message, exc.status_code, exc.error_code, exc.details)
    return success_response(
        {"id": deleted.id},
        "Analysis record deleted",
    )
