from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models.analysis import AnalysisFeedback, NailAnalysis
from app.utils.exceptions import DatabaseError, NotFoundError, ValidationError


class FeedbackService:
    def create(self, user_id, analysis_id, payload):
        self._get_analysis_for_user(user_id, analysis_id)
        values = self._validate_payload(payload, require_content=True)

        feedback = AnalysisFeedback(
            analysis_id=analysis_id,
            user_id=user_id,
            rating=values.get("rating"),
            correction_label=values.get("correction_label"),
            comment=values.get("comment"),
        )
        try:
            db.session.add(feedback)
            db.session.commit()
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise DatabaseError("Could not save feedback") from exc
        return feedback

    def list_for_analysis(self, user_id, analysis_id):
        self._get_analysis_for_user(user_id, analysis_id)
        return (
            AnalysisFeedback.query.filter_by(analysis_id=analysis_id, user_id=user_id)
            .order_by(AnalysisFeedback.created_at.desc())
            .all()
        )

    def get_for_user(self, user_id, feedback_id):
        feedback = AnalysisFeedback.query.filter_by(
            id=feedback_id,
            user_id=user_id,
        ).first()
        if not feedback:
            raise NotFoundError("Feedback record was not found")
        return feedback

    def update(self, user_id, feedback_id, payload):
        feedback = self.get_for_user(user_id, feedback_id)
        values = self._validate_payload(payload, require_content=True)
        for field, value in values.items():
            setattr(feedback, field, value)
        try:
            db.session.commit()
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise DatabaseError("Could not update feedback") from exc
        return feedback

    def delete(self, user_id, feedback_id):
        feedback = self.get_for_user(user_id, feedback_id)
        try:
            db.session.delete(feedback)
            db.session.commit()
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise DatabaseError("Could not delete feedback") from exc
        return feedback

    def _get_analysis_for_user(self, user_id, analysis_id):
        analysis = NailAnalysis.query.filter_by(id=analysis_id, user_id=user_id).first()
        if not analysis:
            raise NotFoundError("Analysis record was not found")
        return analysis

    def _validate_payload(self, payload, require_content=False):
        payload = payload or {}
        values = {}

        if "rating" in payload and payload.get("rating") is not None:
            values["rating"] = self._validate_rating(payload.get("rating"))
        if "correction_label" in payload:
            values["correction_label"] = self._clean_optional_text(
                payload.get("correction_label"),
                "correction_label",
                120,
            )
        if "comment" in payload:
            values["comment"] = self._clean_optional_text(
                payload.get("comment"),
                "comment",
                1000,
            )

        if require_content and not values:
            raise ValidationError("At least one feedback field is required")
        return values

    def _validate_rating(self, rating):
        try:
            parsed = int(rating)
        except (TypeError, ValueError) as exc:
            raise ValidationError("Rating must be a number between 1 and 5") from exc
        if parsed < 1 or parsed > 5:
            raise ValidationError("Rating must be between 1 and 5")
        return parsed

    def _clean_optional_text(self, value, field_name, max_length):
        if value is None:
            return None
        cleaned = str(value).strip()
        if len(cleaned) > max_length:
            raise ValidationError(
                f"{field_name} is too long",
                {"max_length": max_length},
            )
        return cleaned or None
