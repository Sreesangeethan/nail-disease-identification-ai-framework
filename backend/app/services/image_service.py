from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from flask import current_app

from app.utils.exceptions import ValidationError
from app.utils.image_validation import ImageValidator
from app.utils.security import safe_filename


@dataclass(frozen=True)
class StoredImage:
    original_filename: str
    stored_filename: str
    image_path: str
    metadata: dict


class ImageService:
    def validate(self, file_storage):
        if not file_storage:
            raise ValidationError("Image file is required")

        original_filename = safe_filename(file_storage.filename)
        content = file_storage.read()
        file_storage.stream.seek(0)
        validator = self._build_validator()
        result = validator.validate(original_filename, content)
        if not result.is_valid:
            raise ValidationError("Image validation failed", {"errors": result.errors})
        return result

    def store(self, file_storage):
        result = self.validate(file_storage)
        original_filename = safe_filename(file_storage.filename)
        extension = Path(original_filename).suffix.lower()
        date_path = datetime.utcnow().strftime("%Y/%m/%d")
        upload_dir = Path(current_app.config["UPLOAD_FOLDER"]) / date_path
        upload_dir.mkdir(parents=True, exist_ok=True)

        stored_filename = f"{uuid4().hex}{extension}"
        destination = upload_dir / stored_filename
        file_storage.save(destination)

        return StoredImage(
            original_filename=original_filename,
            stored_filename=stored_filename,
            image_path=str(destination),
            metadata={
                **result.metadata,
                "warnings": result.warnings,
            },
        )

    def _build_validator(self):
        return ImageValidator(
            allowed_extensions=current_app.config["ALLOWED_IMAGE_EXTENSIONS"],
            max_bytes=current_app.config["MAX_CONTENT_LENGTH"],
            min_width=current_app.config["MIN_IMAGE_WIDTH"],
            min_height=current_app.config["MIN_IMAGE_HEIGHT"],
            min_blur_score=current_app.config["MIN_BLUR_SCORE"],
        )
