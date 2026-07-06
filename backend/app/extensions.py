from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy(session_options={"expire_on_commit": False})
jwt = JWTManager()
cors = CORS()


def init_extensions(app):
    """Initialize Flask extensions in one place for the application factory."""
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    _register_jwt_error_handlers()


def _register_jwt_error_handlers():
    @jwt.unauthorized_loader
    def missing_token(message):
        return _auth_error("AUTH_REQUIRED", message, 401)

    @jwt.invalid_token_loader
    def invalid_token(message):
        return _auth_error("INVALID_TOKEN", message, 422)

    @jwt.expired_token_loader
    def expired_token(_jwt_header, _jwt_payload):
        return _auth_error("TOKEN_EXPIRED", "Token has expired", 401)


def _auth_error(code, message, status_code):
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": {},
        },
    }, status_code
