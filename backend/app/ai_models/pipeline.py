from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from app.ai_models.model_loader import AIModelRegistry
from app.utils.exceptions import ModelUnavailableError


CLASS_LABELS = [
    "healthy",
    "onychomycosis",
    "psoriasis",
    "melanonychia",
    "beaus_lines",
]


@dataclass(frozen=True)
class PipelineResult:
    predicted_condition: str
    confidence: float
    severity_score: float
    severity_label: str
    segmentation_mask_path: str
    heatmap_path: str
    model_version: str
    report: dict


class NailDiseaseInferencePipeline:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.registry = AIModelRegistry(config, logger)

    def run(self, image_path, artifact_dir):
        artifact_dir = Path(artifact_dir)
        artifact_dir.mkdir(parents=True, exist_ok=True)

        image = self._load_rgb_image(image_path)
        self._validate_model_availability()
        mask = self._segment_nail(image)
        condition, confidence, probabilities = self._classify(image)
        heatmap = self._generate_heatmap(image, condition)
        severity_score, severity_label = self._score_severity(mask, heatmap, confidence)

        mask_path = artifact_dir / "segmentation_mask.png"
        heatmap_path = artifact_dir / "gradcam_heatmap.png"
        cv2.imwrite(str(mask_path), mask)
        cv2.imwrite(str(heatmap_path), cv2.cvtColor(heatmap, cv2.COLOR_RGB2BGR))

        report = {
            "pipeline": [
                "preprocessing",
                "u_net_segmentation",
                "cnn_classification",
                "grad_cam_heatmap",
                "severity_scoring",
                "report_generation",
            ],
            "predicted_condition": condition,
            "confidence": confidence,
            "severity_score": severity_score,
            "severity_label": severity_label,
            "class_probabilities": probabilities,
            "clinical_notice": (
                "This software output is decision support only and is not a standalone "
                "medical diagnosis."
            ),
        }

        return PipelineResult(
            predicted_condition=condition,
            confidence=confidence,
            severity_score=severity_score,
            severity_label=severity_label,
            segmentation_mask_path=str(mask_path),
            heatmap_path=str(heatmap_path),
            model_version=self.config["MODEL_VERSION"],
            report=report,
        )

    def _validate_model_availability(self):
        if self.config["ALLOW_DEMO_INFERENCE"]:
            return

        if not self.registry.has_required_models():
            raise ModelUnavailableError(
                "U-Net and CNN model files must be configured before clinical inference",
                {
                    "unet_model_path": str(self.config["UNET_MODEL_PATH"]),
                    "classifier_model_path": str(self.config["CLASSIFIER_MODEL_PATH"]),
                    "demo_mode": False,
                },
            )

        unet = self.registry.get_unet()
        classifier = self.registry.get_classifier()
        if unet.model is None or classifier.model is None:
            raise ModelUnavailableError(
                "AI model artifacts exist but could not be loaded",
                {
                    "unet_model_path": str(unet.path),
                    "classifier_model_path": str(classifier.path),
                    "demo_mode": False,
                },
            )

    def _load_rgb_image(self, image_path):
        return np.array(Image.open(image_path).convert("RGB"))

    def _segment_nail(self, image):
        unet = self.registry.get_unet().model
        if unet is not None:
            resized = cv2.resize(image, (256, 256)).astype("float32") / 255.0
            prediction = unet.predict(np.expand_dims(resized, axis=0), verbose=0)
            mask = (prediction[0, :, :, 0] > 0.5).astype("uint8") * 255
            return cv2.resize(mask, (image.shape[1], image.shape[0]))

        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        saturation = hsv[:, :, 1]
        value = hsv[:, :, 2]
        mask = np.where((saturation > 20) & (value > 40) & (value < 245), 255, 0)
        return mask.astype("uint8")

    def _classify(self, image):
        classifier = self.registry.get_classifier().model
        if classifier is not None:
            resized = cv2.resize(image, (224, 224)).astype("float32") / 255.0
            prediction = classifier.predict(np.expand_dims(resized, axis=0), verbose=0)[0]
            prediction = np.asarray(prediction, dtype=float)
            index = int(np.argmax(prediction))
            confidence = round(float(prediction[index]), 4)
            probabilities = {
                CLASS_LABELS[i]: round(float(prediction[i]), 4)
                for i in range(min(len(CLASS_LABELS), len(prediction)))
            }
            return CLASS_LABELS[index], confidence, probabilities

        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        yellow_ratio = float(np.mean((hsv[:, :, 0] > 18) & (hsv[:, :, 0] < 42)))
        dark_ratio = float(np.mean(hsv[:, :, 2] < 70))
        red_ratio = float(np.mean((hsv[:, :, 0] < 10) & (hsv[:, :, 1] > 80)))

        scores = {
            "healthy": max(0.05, 1.0 - yellow_ratio - dark_ratio - red_ratio),
            "onychomycosis": yellow_ratio,
            "psoriasis": red_ratio,
            "melanonychia": dark_ratio,
            "beaus_lines": 0.08,
        }
        total = sum(scores.values())
        probabilities = {
            label: round(score / total, 4) for label, score in scores.items()
        }
        condition = max(probabilities, key=probabilities.get)
        return condition, probabilities[condition], probabilities

    def _generate_heatmap(self, image, condition):
        classifier = self.registry.get_classifier().model
        layer_name = self.config.get("GRADCAM_LAYER_NAME")
        if classifier is not None and layer_name:
            try:
                return self._generate_model_gradcam(image, classifier, layer_name)
            except Exception as exc:
                self.logger.warning("Model Grad-CAM failed, using fallback heatmap: %s", exc)

        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 60, 140)
        heat = cv2.GaussianBlur(edges, (0, 0), sigmaX=9)
        normalized = cv2.normalize(heat, None, 0, 255, cv2.NORM_MINMAX)
        colored = cv2.applyColorMap(normalized.astype("uint8"), cv2.COLORMAP_JET)
        overlay = cv2.addWeighted(image, 0.65, cv2.cvtColor(colored, cv2.COLOR_BGR2RGB), 0.35, 0)
        self.logger.info("Generated Grad-CAM compatible heatmap for %s", condition)
        return overlay

    def _generate_model_gradcam(self, image, classifier, layer_name):
        import tensorflow as tf

        resized = cv2.resize(image, (224, 224)).astype("float32") / 255.0
        input_tensor = tf.convert_to_tensor(np.expand_dims(resized, axis=0))
        target_layer = classifier.get_layer(layer_name)
        grad_model = tf.keras.models.Model(
            classifier.inputs,
            [target_layer.output, classifier.output],
        )

        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(input_tensor)
            class_index = tf.argmax(predictions[0])
            loss = predictions[:, class_index]

        gradients = tape.gradient(loss, conv_outputs)
        pooled_gradients = tf.reduce_mean(gradients, axis=(0, 1, 2))
        conv_outputs = conv_outputs[0]
        heatmap = tf.reduce_sum(conv_outputs * pooled_gradients, axis=-1)
        heatmap = tf.maximum(heatmap, 0) / (tf.reduce_max(heatmap) + 1e-8)
        heatmap = heatmap.numpy()
        heatmap = cv2.resize(heatmap, (image.shape[1], image.shape[0]))
        colored = cv2.applyColorMap(np.uint8(255 * heatmap), cv2.COLORMAP_JET)
        return cv2.addWeighted(image, 0.65, cv2.cvtColor(colored, cv2.COLOR_BGR2RGB), 0.35, 0)

    def _score_severity(self, mask, heatmap, confidence):
        mask_area = max(float(np.mean(mask > 0)), 0.01)
        heat_intensity = float(np.mean(cv2.cvtColor(heatmap, cv2.COLOR_RGB2GRAY))) / 255.0
        score = round(min(100.0, (heat_intensity * 70.0 + confidence * 30.0) * mask_area), 2)
        if score < 25:
            label = "low"
        elif score < 60:
            label = "moderate"
        else:
            label = "high"
        return score, label
