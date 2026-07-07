from dataclasses import dataclass

from flask import current_app

from app.utils.image_utils import save_image_upload, validate_image_file


@dataclass(frozen=True)
class StoredImage:
    original_filename: str
    stored_filename: str
    image_path: str
    metadata: dict


class ImageService:
    def validate(self, file_storage):
        return validate_image_file(file_storage, current_app.config)

    def store(self, file_storage):
        stored_image = save_image_upload(file_storage, current_app.config)
        return StoredImage(
            original_filename=stored_image.original_filename,
            stored_filename=stored_image.stored_filename,
            image_path=stored_image.image_path,
            metadata=stored_image.validation.to_dict(),
        )
