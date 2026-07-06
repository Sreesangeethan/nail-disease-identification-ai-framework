import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")


@dataclass
class ModelBundle:
    name: str
    path: Path
    model: object | None
    version: str
    loaded_at: datetime | None = None
    error: str | None = None

    @property
    def is_loaded(self):
        return self.model is not None


class AIModelRegistry:
    def __init__(self, app_config, logger):
        self.config = app_config
        self.logger = logger
        self._unet = None
        self._classifier = None

    def get_unet(self):
        if self._unet is None:
            self._unet = self._load_model("unet", self.config["UNET_MODEL_PATH"])
        return self._unet

    def get_classifier(self):
        if self._classifier is None:
            self._classifier = self._load_model(
                "classifier",
                self.config["CLASSIFIER_MODEL_PATH"],
            )
        return self._classifier

    def has_required_models(self):
        return Path(self.config["UNET_MODEL_PATH"]).exists() and Path(
            self.config["CLASSIFIER_MODEL_PATH"]
        ).exists()

    def models_ready(self):
        return self.get_unet().is_loaded and self.get_classifier().is_loaded

    def reload(self):
        self._unet = None
        self._classifier = None
        return {
            "unet": self.get_unet(),
            "classifier": self.get_classifier(),
        }

    def status(self):
        unet = self.get_unet()
        classifier = self.get_classifier()
        return {
            "model_version": self.config["MODEL_VERSION"],
            "unet": self._bundle_status(unet),
            "classifier": self._bundle_status(classifier),
        }

    def _load_model(self, name, path):
        model_path = Path(path)
        if not model_path.exists():
            message = f"{name} model artifact not found at {model_path}"
            self.logger.warning(message)
            return ModelBundle(
                name=name,
                path=model_path,
                model=None,
                version=self.config["MODEL_VERSION"],
                error=message,
            )

        try:
            from tensorflow.keras.models import load_model

            model = load_model(model_path, compile=False)
            self.logger.info("Loaded %s model from %s", name, model_path)
            return ModelBundle(
                name=name,
                path=model_path,
                model=model,
                version=self.config["MODEL_VERSION"],
                loaded_at=datetime.utcnow(),
            )
        except Exception as exc:
            message = f"Failed to load {name} model: {exc}"
            self.logger.exception(message)
            return ModelBundle(
                name=name,
                path=model_path,
                model=None,
                version=self.config["MODEL_VERSION"],
                error=message,
            )

    def _bundle_status(self, bundle):
        return {
            "name": bundle.name,
            "path": str(bundle.path),
            "version": bundle.version,
            "is_loaded": bundle.is_loaded,
            "loaded_at": bundle.loaded_at.isoformat() if bundle.loaded_at else None,
            "error": bundle.error,
        }
