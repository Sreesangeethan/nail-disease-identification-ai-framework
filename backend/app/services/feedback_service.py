from app.extensions import db
from app.models.analysis import AnalysisFeedback, NailAnalysis
from app.utils.exceptions import NotFoundError, ValidationError


class FeedbackService:
    def create(self, user_id, analysis_id, payload):
        analysis = NailAnalysis.query.filter_by(id=analysis_id, user_id=user_id).first()
        if not analysis:
            raise NotFoundError("Analysis record was not found")

        rating = payload.get("rating")
        if rating is not None:
            try:
                rating = int(rating)
            except (TypeError, ValueError) as exc:
                raise ValidationError("Rating must be a number between 1 and 5") from exc
            if rating < 1 or rating > 5:
                raise ValidationError("Rating must be between 1 and 5")

        feedback = AnalysisFeedback(
            analysis_id=analysis_id,
            user_id=user_id,
            rating=rating,
            correction_label=payload.get("correction_label"),
            comment=payload.get("comment"),
        )
        db.session.add(feedback)
        db.session.commit()
        return feedback
