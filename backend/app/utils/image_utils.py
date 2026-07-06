from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from pathlib import Path
from uuid import uuid4

import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError
from werkzeug.datastructures import FileStorage

from app.utils.exceptions import ValidationError
from app.utils.security import safe_filename


@dataclass(frozen=True)
class ImageValidationReport:
    original_filename: str
    safe_filename: str
    content_type: str
    extension: str
    file_size_bytes: int
    width: int
    height: int
    image_format: str | None
    color_mode: str
    blur_score: float
    brightness: float
    warnings: list[str]

    def to_dict(self):
        return {
            "original_filename": self.original_filename,
            "safe_filename": self.safe_filename,
            "content_type": self.content_type,
            "extension": self.extension,
            "file_size_bytes": self.file_size_bytes,
            "width": self.width,
            "height": self.height,
            "image_format": self.image_format,
            "color_mode": self.color_mode,
            "blur_score": self.blur_score,
            "brightness": self.brightness,
            "warnings": self.warnings,
        }


@dataclass(frozen=True)
class StoredImage:
    original_filename: str
    stored_filename: str
    image_path: str
    validation: ImageValidationReport

    def to_dict(self):
        return {
            "original_filename": self.original_filename,
            "stored_filename": self.stored_filename,
            "image_path": self.image_path,
            "quality_metadata": self.validation.to_dict(),
        }


def validate_image_file(file_storage, config):
    """Validate an uploaded nail image without persisting it."""
    if not isinstance(file_storage, FileStorage) or not file_storage.filename:
        raise ValidationError("Image file is required")

    original_filename = file_storage.filename
    cleaned_filename = safe_filename(original_filename)
    extension = Path(cleaned_filename).suffix.lower().replace(".", "")
    allowed_extensions = config["ALLOWED_IMAGE_EXTENSIONS"]
    if extension not in allowed_extensions:
        raise ValidationError(
            "Unsupported image type",
            {
                "allowed_extensions": sorted(allowed_extensions),
                "received_extension": extension,
            },
        )

    content = _read_upload_bytes(file_storage)
    max_bytes = config["MAX_CONTENT_LENGTH"]
    if len(content) > max_bytes:
        raise ValidationError(
            "Image exceeds maximum upload size",
            {
                "max_bytes": max_bytes,
                "actual_bytes": len(content),
            },
        )

    image, image_format = _open_verified_rgb_image(content)
    if image_format and image_format.lower() not in {"jpeg", "jpg", "png"}:
        raise ValidationError(
            "Unsupported image content",
            {
                "allowed_formats": ["JPEG", "PNG"],
                "actual_format": image_format,
            },
        )

    width, height = image.size
    if width < config["MIN_IMAGE_WIDTH"] or height < config["MIN_IMAGE_HEIGHT"]:
        raise ValidationError(
            "Image resolution is too low",
            {
                "minimum_width": config["MIN_IMAGE_WIDTH"],
                "minimum_height": config["MIN_IMAGE_HEIGHT"],
                "actual_width": width,
                "actual_height": height,
            },
        )

    blur_score, brightness = calculate_quality_scores(image)
    warnings = build_quality_warnings(
        blur_score=blur_score,
        brightness=brightness,
        min_blur_score=config["MIN_BLUR_SCORE"],
    )

    return ImageValidationReport(
        original_filename=original_filename,
        safe_filename=cleaned_filename,
        content_type=file_storage.mimetype or "application/octet-stream",
        extension=extension,
        file_size_bytes=len(content),
        width=width,
        height=height,
        image_format=image_format,
        color_mode=image.mode,
        blur_score=round(blur_score, 2),
        brightness=round(brightness, 2),
        warnings=warnings,
    )


def save_image_upload(file_storage, config, validation=None):
    """Validate and persist an uploaded image under the configured upload root."""
    validation = validation or validate_image_file(file_storage, config)
    upload_dir = Path(config["UPLOAD_FOLDER"]).resolve()
    dated_dir = upload_dir / datetime.utcnow().strftime("%Y/%m/%d")
    upload_dir.mkdir(parents=True, exist_ok=True)
    dated_dir.mkdir(parents=True, exist_ok=True)

    extension = Path(validation.safe_filename).suffix.lower()
    stored_filename = f"{uuid4().hex}{extension}"
    destination = (dated_dir / stored_filename).resolve()
    try:
        destination.relative_to(upload_dir)
    except ValueError as exc:
        raise ValidationError("Resolved upload path is invalid") from exc

    file_storage.stream.seek(0)
    file_storage.save(destination)

    return StoredImage(
        original_filename=validation.original_filename,
        stored_filename=stored_filename,
        image_path=str(destination),
        validation=validation,
    )


def load_rgb_image(image_path):
    try:
        return Image.open(image_path).convert("RGB")
    except (OSError, UnidentifiedImageError) as exc:
        raise ValidationError("Stored image could not be opened") from exc


def calculate_quality_scores(image):
    image_array = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness = float(gray.mean())
    return blur_score, brightness


def build_quality_warnings(blur_score, brightness, min_blur_score):
    warnings = []
    if blur_score < min_blur_score:
        warnings.append("Image appears blurry; capture a sharper nail image")
    if brightness < 35:
        warnings.append("Image appears underexposed")
    if brightness > 235:
        warnings.append("Image appears overexposed")
    return warnings


def _read_upload_bytes(file_storage):
    content = file_storage.read()
    file_storage.stream.seek(0)
    if not content:
        raise ValidationError("Uploaded image is empty")
    return content


def _open_verified_rgb_image(content):
    try:
        probe = Image.open(BytesIO(content))
        image_format = probe.format
        probe.verify()
        image = Image.open(BytesIO(content)).convert("RGB")
        return image, image_format
    except (OSError, UnidentifiedImageError) as exc:
        raise ValidationError("Uploaded file is not a valid image") from exc
