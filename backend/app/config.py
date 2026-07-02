import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent
load_dotenv(BACKEND_DIR / ".env")


def _as_bool(value, default=False):
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _as_int(name, default):
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


def _as_float(name, default):
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


class Config:
    APP_NAME = "nail-disease-identification-ai-framework"
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = _as_bool(os.getenv("FLASK_DEBUG"), default=False)

    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-jwt-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=_as_int("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", 60)
    )

    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "nail_disease_ai")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    MAX_CONTENT_LENGTH = _as_int("MAX_UPLOAD_MB", 10) * 1024 * 1024
    UPLOAD_FOLDER = Path(os.getenv("UPLOAD_FOLDER", BACKEND_DIR / "uploads")).resolve()
    ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}
    MIN_IMAGE_WIDTH = _as_int("MIN_IMAGE_WIDTH", 224)
    MIN_IMAGE_HEIGHT = _as_int("MIN_IMAGE_HEIGHT", 224)
    MIN_BLUR_SCORE = _as_float("MIN_BLUR_SCORE", 30.0)

    MODEL_DIR = Path(os.getenv("MODEL_DIR", BACKEND_DIR / "model_artifacts")).resolve()
    UNET_MODEL_PATH = Path(os.getenv("UNET_MODEL_PATH", MODEL_DIR / "unet.keras"))
    CLASSIFIER_MODEL_PATH = Path(
        os.getenv("CLASSIFIER_MODEL_PATH", MODEL_DIR / "classifier.keras")
    )
    GRADCAM_LAYER_NAME = os.getenv("GRADCAM_LAYER_NAME", "")
    MODEL_VERSION = os.getenv("MODEL_VERSION", "unconfigured")
    ALLOW_DEMO_INFERENCE = _as_bool(os.getenv("ALLOW_DEMO_INFERENCE"), default=False)

    JSON_SORT_KEYS = False

    @classmethod
    def init_app(cls, app):
        cls.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        cls.MODEL_DIR.mkdir(parents=True, exist_ok=True)
