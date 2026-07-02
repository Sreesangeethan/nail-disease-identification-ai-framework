from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.history_service import HistoryService
from app.utils.responses import success_response


history_bp = Blueprint("history", __name__)
history_service = HistoryService()


@history_bp.get("")
@jwt_required()
def list_history():
    limit = _parse_int_arg("limit", 25, minimum=1, maximum=100)
    offset = _parse_int_arg("offset", 0, minimum=0)
    records = history_service.list_for_user(int(get_jwt_identity()), limit, offset)
    return success_response(
        {
            "items": [record.to_dict() for record in records],
            "limit": limit,
            "offset": offset,
        }
    )


@history_bp.get("/<int:analysis_id>")
@jwt_required()
def get_history_item(analysis_id):
    analysis = history_service.get_for_user(int(get_jwt_identity()), analysis_id)
    return success_response(analysis.to_dict())


def _parse_int_arg(name, default, minimum=None, maximum=None):
    raw_value = request.args.get(name, default)
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        value = default
    if minimum is not None:
        value = max(value, minimum)
    if maximum is not None:
        value = min(value, maximum)
    return value
