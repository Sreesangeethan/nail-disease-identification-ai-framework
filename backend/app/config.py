import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-jwt-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "60"))
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

    MAX_CONTENT_LENGTH = int(os.getenv("MAX_UPLOAD_MB", "10")) * 1024 * 1024
    UPLOAD_FOLDER = Path(os.getenv("UPLOAD_FOLDER", BASE_DIR / "uploads")).resolve()
    ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}
    MIN_IMAGE_WIDTH = int(os.getenv("MIN_IMAGE_WIDTH", "224"))
    MIN_IMAGE_HEIGHT = int(os.getenv("MIN_IMAGE_HEIGHT", "224"))
    MIN_BLUR_SCORE = float(os.getenv("MIN_BLUR_SCORE", "30"))

    MODEL_DIR = Path(os.getenv("MODEL_DIR", BASE_DIR / "model_artifacts")).resolve()
    UNET_MODEL_PATH = Path(os.getenv("UNET_MODEL_PATH", MODEL_DIR / "unet.keras"))
    CLASSIFIER_MODEL_PATH = Path(
        os.getenv("CLASSIFIER_MODEL_PATH", MODEL_DIR / "classifier.keras")
    )
    GRADCAM_LAYER_NAME = os.getenv("GRADCAM_LAYER_NAME", "")
    MODEL_VERSION = os.getenv("MODEL_VERSION", "unconfigured")
    ALLOW_DEMO_INFERENCE = os.getenv("ALLOW_DEMO_INFERENCE", "false").lower() == "true"

    JSON_SORT_KEYS = False

    @classmethod
    def init_app(cls, app):
        cls.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        cls.MODEL_DIR.mkdir(parents=True, exist_ok=True)
