from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models.analysis import AnalysisFeedback, NailAnalysis
from app.utils.exceptions import DatabaseError, NotFoundError


class HistoryService:
    def list_for_user(self, user_id, limit=25, offset=0, status=None, condition=None):
        limit = self._bounded_int(limit, default=25, minimum=1, maximum=100)
        offset = self._bounded_int(offset, default=0, minimum=0)

        query = NailAnalysis.query.filter_by(user_id=user_id)
        if status:
            query = query.filter(NailAnalysis.status == status)
        if condition:
            query = query.filter(NailAnalysis.predicted_condition == condition)

        total = query.count()
        records = (
            query.order_by(NailAnalysis.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return {
            "items": records,
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    def get_for_user(self, user_id, analysis_id):
        analysis = NailAnalysis.query.filter_by(id=analysis_id, user_id=user_id).first()
        if not analysis:
            raise NotFoundError("Analysis record was not found")
        return analysis

    def delete_for_user(self, user_id, analysis_id):
        analysis = self.get_for_user(user_id, analysis_id)
        try:
            AnalysisFeedback.query.filter_by(analysis_id=analysis.id).delete(
                synchronize_session=False
            )
            db.session.delete(analysis)
            db.session.commit()
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise DatabaseError("Could not delete analysis record") from exc
        return analysis

    def _bounded_int(self, value, default, minimum=None, maximum=None):
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            parsed = default
        if minimum is not None:
            parsed = max(parsed, minimum)
        if maximum is not None:
            parsed = min(parsed, maximum)
        return parsed
