from datetime import datetime

from app.extensions import db


class NailAnalysis(db.Model):
    __tablename__ = "nail_analyses"

    STATUS_PENDING = "pending"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    image_path = db.Column(db.String(500), nullable=False)
    segmentation_mask_path = db.Column(db.String(500), nullable=True)
    heatmap_path = db.Column(db.String(500), nullable=True)
    predicted_condition = db.Column(db.String(120), nullable=True)
    confidence = db.Column(db.Float, nullable=True)
    severity_score = db.Column(db.Float, nullable=True)
    severity_label = db.Column(db.String(60), nullable=True)
    status = db.Column(db.String(40), nullable=False, default="completed")
    model_version = db.Column(db.String(120), nullable=False, default="unconfigured")
    quality_metadata = db.Column(db.JSON, nullable=True)
    report_json = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", back_populates="analyses")
    feedback = db.relationship("AnalysisFeedback", back_populates="analysis", lazy=True)

    @classmethod
    def from_pipeline_result(cls, user_id, stored_image, pipeline_result):
        return cls(
            user_id=user_id,
            original_filename=stored_image["original_filename"],
            stored_filename=stored_image["stored_filename"],
            image_path=stored_image["image_path"],
            segmentation_mask_path=pipeline_result.get("segmentation_mask_path"),
            heatmap_path=pipeline_result.get("heatmap_path"),
            predicted_condition=pipeline_result.get("predicted_condition"),
            confidence=pipeline_result.get("confidence"),
            severity_score=pipeline_result.get("severity_score"),
            severity_label=pipeline_result.get("severity_label"),
            status=cls.STATUS_COMPLETED,
            model_version=pipeline_result.get("model_version", "unconfigured"),
            quality_metadata=stored_image.get("quality_metadata"),
            report_json=pipeline_result.get("report"),
        )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "original_filename": self.original_filename,
            "stored_filename": self.stored_filename,
            "predicted_condition": self.predicted_condition,
            "confidence": self.confidence,
            "severity_score": self.severity_score,
            "severity_label": self.severity_label,
            "status": self.status,
            "model_version": self.model_version,
            "quality_metadata": self.quality_metadata,
            "artifacts": {
                "image_path": self.image_path,
                "segmentation_mask_path": self.segmentation_mask_path,
                "heatmap_path": self.heatmap_path,
            },
            "report": self.report_json,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<NailAnalysis id={self.id} user_id={self.user_id} status={self.status}>"


class AnalysisFeedback(db.Model):
    __tablename__ = "analysis_feedback"

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(
        db.Integer,
        db.ForeignKey("nail_analyses.id"),
        nullable=False,
        index=True,
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=True)
    correction_label = db.Column(db.String(120), nullable=True)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    analysis = db.relationship("NailAnalysis", back_populates="feedback")
    user = db.relationship("User", back_populates="feedback")

    def to_dict(self):
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "rating": self.rating,
            "correction_label": self.correction_label,
            "comment": self.comment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ModelVersion(db.Model):
    __tablename__ = "model_versions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    version = db.Column(db.String(80), nullable=False)
    artifact_path = db.Column(db.String(500), nullable=False)
    model_type = db.Column(db.String(80), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
