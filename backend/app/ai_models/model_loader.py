import os
from dataclasses import dataclass
from pathlib import Path


os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")


@dataclass
class ModelBundle:
    name: str
    path: Path
    model: object | None
    version: str


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

    def _load_model(self, name, path):
        model_path = Path(path)
        if not model_path.exists():
            self.logger.warning("%s model artifact not found at %s", name, model_path)
            return ModelBundle(name, model_path, None, self.config["MODEL_VERSION"])

        try:
            from tensorflow.keras.models import load_model

            model = load_model(model_path, compile=False)
            self.logger.info("Loaded %s model from %s", name, model_path)
            return ModelBundle(name, model_path, model, self.config["MODEL_VERSION"])
        except Exception as exc:
            self.logger.exception("Failed to load %s model: %s", name, exc)
            return ModelBundle(name, model_path, None, self.config["MODEL_VERSION"])
