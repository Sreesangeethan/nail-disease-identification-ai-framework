from flask import Flask

from app.config import Config
from app.extensions import cors, db, jwt
from app.routes import register_blueprints
from app.utils.exceptions import AppError
from app.utils.logging import configure_logging
from app.utils.responses import error_response


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    config_class.init_app(app)

    configure_logging(app)
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    register_blueprints(app)
    register_error_handlers(app)
    return app


def register_error_handlers(app):
    @jwt.unauthorized_loader
    def handle_missing_token(message):
        return error_response(message, 401, "AUTH_REQUIRED")

    @jwt.invalid_token_loader
    def handle_invalid_token(message):
        return error_response(message, 422, "INVALID_TOKEN")

    @jwt.expired_token_loader
    def handle_expired_token(_header, _payload):
        return error_response("Token has expired", 401, "TOKEN_EXPIRED")

    @app.errorhandler(AppError)
    def handle_app_error(error):
        return error_response(
            message=error.message,
            status_code=error.status_code,
            error_code=error.error_code,
            details=error.details,
        )

    @app.errorhandler(404)
    def handle_not_found(_error):
        return error_response("Resource not found", 404, "NOT_FOUND")

    @app.errorhandler(413)
    def handle_large_file(_error):
        return error_response("Uploaded file is too large", 413, "FILE_TOO_LARGE")

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Unhandled application error: %s", error)
        return error_response("Internal server error", 500, "INTERNAL_SERVER_ERROR")
