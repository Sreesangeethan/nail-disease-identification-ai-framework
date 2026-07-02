from app.models.analysis import NailAnalysis
from app.utils.exceptions import NotFoundError


class HistoryService:
    def list_for_user(self, user_id, limit=25, offset=0):
        query = NailAnalysis.query.filter_by(user_id=user_id).order_by(
            NailAnalysis.created_at.desc()
        )
        return query.offset(offset).limit(limit).all()

    def get_for_user(self, user_id, analysis_id):
        analysis = NailAnalysis.query.filter_by(id=analysis_id, user_id=user_id).first()
        if not analysis:
            raise NotFoundError("Analysis record was not found")
        return analysis
