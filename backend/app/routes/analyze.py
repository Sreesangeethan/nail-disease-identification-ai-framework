from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.analysis_service import AnalysisService
from app.utils.responses import success_response


analyze_bp = Blueprint("analyze", __name__)
analysis_service = AnalysisService()


@analyze_bp.post("")
@jwt_required()
def analyze_image():
    analysis = analysis_service.analyze_upload(
        user_id=int(get_jwt_identity()),
        file_storage=request.files.get("image"),
    )
    return success_response(analysis.to_dict(), "Analysis completed", 201)
