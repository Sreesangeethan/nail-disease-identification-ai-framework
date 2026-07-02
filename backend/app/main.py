from flask import Flask
from flask_cors import CORS

from app.config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    config_class.init_app(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

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


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])
