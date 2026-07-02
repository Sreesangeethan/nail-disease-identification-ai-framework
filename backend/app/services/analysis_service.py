from pathlib import Path
from uuid import uuid4

from flask import current_app

from app.ai_models.pipeline import NailDiseaseInferencePipeline
from app.extensions import db
from app.models.analysis import NailAnalysis
from app.services.image_service import ImageService


class AnalysisService:
    def __init__(self):
        self.image_service = ImageService()

    def analyze_upload(self, user_id, file_storage):
        stored_image = self.image_service.store(file_storage)
        artifact_dir = Path(current_app.config["UPLOAD_FOLDER"]) / "artifacts" / uuid4().hex
        pipeline = NailDiseaseInferencePipeline(current_app.config, current_app.logger)
        result = pipeline.run(stored_image.image_path, artifact_dir)

        analysis = NailAnalysis(
            user_id=user_id,
            original_filename=stored_image.original_filename,
            stored_filename=stored_image.stored_filename,
            image_path=stored_image.image_path,
            segmentation_mask_path=result.segmentation_mask_path,
            heatmap_path=result.heatmap_path,
            predicted_condition=result.predicted_condition,
            confidence=result.confidence,
            severity_score=result.severity_score,
            severity_label=result.severity_label,
            model_version=result.model_version,
            quality_metadata=stored_image.metadata,
            report_json=result.report,
            status="completed",
        )
        db.session.add(analysis)
        db.session.commit()
        return analysis
