from app.routes.analyze import analyze_bp
from app.routes.auth import auth_bp
from app.routes.feedback import feedback_bp
from app.routes.health import health_bp
from app.routes.history import history_bp
from app.routes.upload import upload_bp


def register_blueprints(app):
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(upload_bp, url_prefix="/api/upload")
    app.register_blueprint(analyze_bp, url_prefix="/api/analyze")
    app.register_blueprint(history_bp, url_prefix="/api/history")
    app.register_blueprint(feedback_bp, url_prefix="/api")
