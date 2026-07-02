from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.services.image_service import ImageService
from app.utils.responses import success_response


upload_bp = Blueprint("upload", __name__)
image_service = ImageService()


@upload_bp.post("/validate")
@jwt_required()
def validate_upload():
    result = image_service.validate(request.files.get("image"))
    return success_response(
        {
            "metadata": result.metadata,
            "warnings": result.warnings,
        },
        "Image quality validation completed",
    )
