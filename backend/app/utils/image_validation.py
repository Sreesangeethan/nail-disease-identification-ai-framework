from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError


@dataclass(frozen=True)
class ImageValidationResult:
    is_valid: bool
    errors: list[str]
    warnings: list[str]
    metadata: dict


class ImageValidator:
    def __init__(
        self,
        allowed_extensions,
        max_bytes,
        min_width,
        min_height,
        min_blur_score,
    ):
        self.allowed_extensions = allowed_extensions
        self.max_bytes = max_bytes
        self.min_width = min_width
        self.min_height = min_height
        self.min_blur_score = min_blur_score

    def validate(self, filename, content):
        errors = []
        warnings = []
        metadata = {"file_size_bytes": len(content)}

        extension = Path(filename or "").suffix.lower().replace(".", "")
        if extension not in self.allowed_extensions:
            errors.append("Only JPG, JPEG, and PNG images are allowed")

        if len(content) > self.max_bytes:
            errors.append("Image exceeds the configured maximum upload size")

        try:
            image = Image.open(BytesIO(content))
            image_format = image.format
            image.verify()
            image = Image.open(BytesIO(content)).convert("RGB")
        except (UnidentifiedImageError, OSError):
            errors.append("File is not a valid image")
            return ImageValidationResult(False, errors, warnings, metadata)

        width, height = image.size
        metadata.update(
            {
                "width": width,
                "height": height,
                "format": image_format,
                "mode": image.mode,
            }
        )

        if width < self.min_width or height < self.min_height:
            errors.append(
                f"Image resolution must be at least {self.min_width}x{self.min_height}"
            )

        array = np.array(image)
        gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
        blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        brightness = float(gray.mean())
        metadata.update(
            {
                "blur_score": round(blur_score, 2),
                "brightness": round(brightness, 2),
            }
        )

        if blur_score < self.min_blur_score:
            warnings.append("Image appears blurry; capture a sharper nail image")
        if brightness < 35:
            warnings.append("Image appears underexposed")
        if brightness > 235:
            warnings.append("Image appears overexposed")

        return ImageValidationResult(not errors, errors, warnings, metadata)
