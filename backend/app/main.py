from flask import Flask

from app.config import Config
from app.extensions import cors, db, jwt


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    config_class.init_app(app)

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    _register_jwt_handlers(jwt)

    from app.routes.analyze import analyze_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(analyze_bp, url_prefix="/api/analyze")

    @app.get("/api/health")
    def health_check():
        return {
            "success": True,
            "message": "API is running",
            "data": {
                "service": app.config["APP_NAME"],
                "model_version": app.config["MODEL_VERSION"],
                "demo_inference": app.config["ALLOW_DEMO_INFERENCE"],
            },
        }, 200

    return app


def _register_jwt_handlers(jwt_manager):
    @jwt_manager.unauthorized_loader
    def missing_token(message):
        return _auth_error("AUTH_REQUIRED", message, 401)

    @jwt_manager.invalid_token_loader
    def invalid_token(message):
        return _auth_error("INVALID_TOKEN", message, 422)

    @jwt_manager.expired_token_loader
    def expired_token(_jwt_header, _jwt_payload):
        return _auth_error("TOKEN_EXPIRED", "Token has expired", 401)


def _auth_error(code, message, status_code):
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
        },
    }, status_code


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])
