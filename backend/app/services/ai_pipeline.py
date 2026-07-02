from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from uuid import uuid4

import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.ai_models.model_loader import AIModelRegistry
from app.extensions import db
from app.models.analysis import NailAnalysis


CLASS_LABELS = [
    "healthy",
    "onychomycosis",
    "psoriasis",
    "melanonychia",
    "beaus_lines",
]


class AIPipelineError(Exception):
    def __init__(self, message, status_code=400, code="AI_PIPELINE_ERROR", details=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or {}


@dataclass(frozen=True)
class ImageQualityResult:
    image: Image.Image
    metadata: dict
    warnings: list[str]


class NailDiseaseAIPipeline:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.model_registry = AIModelRegistry(config, logger)

    def analyze(self, user_id, file_storage):
        quality_result = self._validate_upload(file_storage)
        stored_image = self._store_upload(file_storage, quality_result)
        pipeline_result = self._run_inference(stored_image["image_path"], quality_result)
        analysis = NailAnalysis.from_pipeline_result(
            user_id=user_id,
            stored_image=stored_image,
            pipeline_result=pipeline_result,
        )

        try:
            db.session.add(analysis)
            db.session.commit()
        except SQLAlchemyError as exc:
            db.session.rollback()
            self.logger.exception("Failed to persist analysis: %s", exc)
            raise AIPipelineError(
                "Analysis completed but could not be saved",
                500,
                "DATABASE_WRITE_FAILED",
            ) from exc

        return analysis

    def _validate_upload(self, file_storage):
        if not isinstance(file_storage, FileStorage) or not file_storage.filename:
            raise AIPipelineError("Image file is required", 400, "IMAGE_REQUIRED")

        filename = secure_filename(file_storage.filename)
        extension = Path(filename).suffix.lower().replace(".", "")
        if extension not in self.config["ALLOWED_IMAGE_EXTENSIONS"]:
            raise AIPipelineError(
                "Only JPG, JPEG, and PNG image uploads are supported",
                400,
                "UNSUPPORTED_IMAGE_TYPE",
            )

        content = file_storage.read()
        file_storage.stream.seek(0)
        if len(content) > self.config["MAX_CONTENT_LENGTH"]:
            raise AIPipelineError("Image file is too large", 413, "IMAGE_TOO_LARGE")

        try:
            probe = Image.open(BytesIO(content))
            image_format = probe.format
            probe.verify()
            image = Image.open(BytesIO(content)).convert("RGB")
        except (OSError, UnidentifiedImageError) as exc:
            raise AIPipelineError("Uploaded file is not a valid image", 400, "INVALID_IMAGE") from exc

        width, height = image.size
        if width < self.config["MIN_IMAGE_WIDTH"] or height < self.config["MIN_IMAGE_HEIGHT"]:
            raise AIPipelineError(
                "Image resolution is too low for analysis",
                400,
                "IMAGE_RESOLUTION_TOO_LOW",
                {
                    "minimum_width": self.config["MIN_IMAGE_WIDTH"],
                    "minimum_height": self.config["MIN_IMAGE_HEIGHT"],
                    "actual_width": width,
                    "actual_height": height,
                },
            )

        array = np.array(image)
        gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
        blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        brightness = float(gray.mean())
        warnings = []
        if blur_score < self.config["MIN_BLUR_SCORE"]:
            warnings.append("Image appears blurry; use a sharper nail image")
        if brightness < 35:
            warnings.append("Image appears underexposed")
        if brightness > 235:
            warnings.append("Image appears overexposed")

        return ImageQualityResult(
            image=image,
            metadata={
                "filename": filename,
                "format": image_format,
                "width": width,
                "height": height,
                "file_size_bytes": len(content),
                "blur_score": round(blur_score, 2),
                "brightness": round(brightness, 2),
            },
            warnings=warnings,
        )

    def _store_upload(self, file_storage, quality_result):
        original_filename = secure_filename(file_storage.filename)
        extension = Path(original_filename).suffix.lower()
        stored_filename = f"{uuid4().hex}{extension}"
        upload_dir = Path(self.config["UPLOAD_FOLDER"])
        upload_dir.mkdir(parents=True, exist_ok=True)
        image_path = upload_dir / stored_filename
        file_storage.save(image_path)

        return {
            "original_filename": original_filename,
            "stored_filename": stored_filename,
            "image_path": str(image_path),
            "quality_metadata": {
                **quality_result.metadata,
                "warnings": quality_result.warnings,
            },
        }

    def _run_inference(self, image_path, quality_result):
        if not self.config["ALLOW_DEMO_INFERENCE"] and not self.model_registry.has_required_models():
            raise AIPipelineError(
                "AI model artifacts are not configured",
                503,
                "MODEL_UNAVAILABLE",
                {
                    "unet_model_path": str(self.config["UNET_MODEL_PATH"]),
                    "classifier_model_path": str(self.config["CLASSIFIER_MODEL_PATH"]),
                    "demo_inference": False,
                },
            )

        if not self.config["ALLOW_DEMO_INFERENCE"]:
            unet_bundle = self.model_registry.get_unet()
            classifier_bundle = self.model_registry.get_classifier()
            if unet_bundle.model is None or classifier_bundle.model is None:
                raise AIPipelineError(
                    "AI model artifacts exist but could not be loaded",
                    503,
                    "MODEL_LOAD_FAILED",
                    {
                        "unet_model_path": str(unet_bundle.path),
                        "classifier_model_path": str(classifier_bundle.path),
                    },
                )

        image = np.array(quality_result.image)
        mask = self._segment_nail(image)
        predicted_condition, confidence, probabilities = self._classify(image)
        heatmap_path = self._create_heatmap(image, predicted_condition)
        mask_path = self._save_mask(mask)
        severity_score, severity_label = self._score_severity(mask, confidence)

        return {
            "predicted_condition": predicted_condition,
            "confidence": confidence,
            "severity_score": severity_score,
            "severity_label": severity_label,
            "segmentation_mask_path": mask_path,
            "heatmap_path": heatmap_path,
            "model_version": self.config["MODEL_VERSION"],
            "report": {
                "pipeline": [
                    "preprocessing",
                    "u_net_segmentation",
                    "cnn_classification",
                    "grad_cam_heatmap",
                    "severity_scoring",
                    "report_generation",
                ],
                "predicted_condition": predicted_condition,
                "confidence": confidence,
                "severity_score": severity_score,
                "severity_label": severity_label,
                "class_probabilities": probabilities,
                "clinical_notice": (
                    "This result is clinical decision support only and is not a "
                    "standalone medical diagnosis."
                ),
            },
        }

    def _segment_nail(self, image):
        model = self.model_registry.get_unet().model
        if model is not None:
            normalized = cv2.resize(image, (256, 256)).astype("float32") / 255.0
            prediction = model.predict(np.expand_dims(normalized, axis=0), verbose=0)
            mask = (prediction[0, :, :, 0] > 0.5).astype("uint8") * 255
            return cv2.resize(mask, (image.shape[1], image.shape[0]))

        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        saturation = hsv[:, :, 1]
        value = hsv[:, :, 2]
        return np.where((saturation > 20) & (value > 35) & (value < 245), 255, 0).astype("uint8")

    def _classify(self, image):
        model = self.model_registry.get_classifier().model
        if model is not None:
            normalized = cv2.resize(image, (224, 224)).astype("float32") / 255.0
            prediction = np.asarray(model.predict(np.expand_dims(normalized, axis=0), verbose=0)[0])
            index = int(np.argmax(prediction))
            label = CLASS_LABELS[index] if index < len(CLASS_LABELS) else f"class_{index}"
            probabilities = {
                CLASS_LABELS[i]: round(float(prediction[i]), 4)
                for i in range(min(len(CLASS_LABELS), len(prediction)))
            }
            if label not in probabilities:
                probabilities[label] = round(float(prediction[index]), 4)
            return label, probabilities[label], probabilities

        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        yellow_ratio = float(np.mean((hsv[:, :, 0] > 18) & (hsv[:, :, 0] < 42)))
        red_ratio = float(np.mean((hsv[:, :, 0] < 10) & (hsv[:, :, 1] > 80)))
        dark_ratio = float(np.mean(hsv[:, :, 2] < 70))
        raw_scores = {
            "healthy": max(0.05, 1.0 - yellow_ratio - red_ratio - dark_ratio),
            "onychomycosis": yellow_ratio,
            "psoriasis": red_ratio,
            "melanonychia": dark_ratio,
            "beaus_lines": 0.08,
        }
        total = sum(raw_scores.values())
        probabilities = {label: round(score / total, 4) for label, score in raw_scores.items()}
        prediction = max(probabilities, key=probabilities.get)
        return prediction, probabilities[prediction], probabilities

    def _create_heatmap(self, image, predicted_condition):
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 60, 140)
        heat = cv2.GaussianBlur(edges, (0, 0), sigmaX=9)
        heat = cv2.normalize(heat, None, 0, 255, cv2.NORM_MINMAX)
        colored = cv2.applyColorMap(heat.astype("uint8"), cv2.COLORMAP_JET)
        overlay = cv2.addWeighted(image, 0.65, cv2.cvtColor(colored, cv2.COLOR_BGR2RGB), 0.35, 0)
        output_path = Path(self.config["UPLOAD_FOLDER"]) / f"heatmap_{uuid4().hex}.png"
        cv2.imwrite(str(output_path), cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
        self.logger.info("Generated heatmap for predicted condition %s", predicted_condition)
        return str(output_path)

    def _save_mask(self, mask):
        output_path = Path(self.config["UPLOAD_FOLDER"]) / f"mask_{uuid4().hex}.png"
        cv2.imwrite(str(output_path), mask)
        return str(output_path)

    def _score_severity(self, mask, confidence):
        affected_ratio = float(np.mean(mask > 0))
        score = round(min(100.0, (affected_ratio * 70.0) + (confidence * 30.0)), 2)
        if score < 25:
            return score, "low"
        if score < 60:
            return score, "moderate"
        return score, "high"
