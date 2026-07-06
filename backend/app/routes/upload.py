from flask import Blueprint, current_app, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.utils.exceptions import ValidationError
from app.utils.image_utils import save_image_upload, validate_image_file
from app.utils.responses import error_response
from app.utils.responses import success_response


upload_bp = Blueprint("upload", __name__)


@upload_bp.post("/validate")
@jwt_required()
def validate_upload():
    try:
        validation = validate_image_file(request.files.get("image"), current_app.config)
    except ValidationError as exc:
        return error_response(
            exc.message,
            exc.status_code,
            exc.error_code,
            exc.details,
        )

    return success_response(
        {
            "user_id": int(get_jwt_identity()),
            "metadata": validation.to_dict(),
            "warnings": validation.warnings,
        },
        "Image quality validation completed",
    )


@upload_bp.post("/store")
@jwt_required()
def store_upload():
    try:
        stored_image = save_image_upload(request.files.get("image"), current_app.config)
    except ValidationError as exc:
        return error_response(
            exc.message,
            exc.status_code,
            exc.error_code,
            exc.details,
        )

    return success_response(
        {
            "user_id": int(get_jwt_identity()),
            "upload": stored_image.to_dict(),
        },
        "Image uploaded successfully",
        201,
    )
