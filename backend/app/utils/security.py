import re

from werkzeug.utils import secure_filename

from app.utils.exceptions import ValidationError


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8
MAX_NAME_LENGTH = 120
MAX_FILENAME_LENGTH = 255


def normalize_email(email):
    if not email:
        raise ValidationError("Email is required")
    normalized = email.strip().lower()
    if not EMAIL_PATTERN.match(normalized):
        raise ValidationError("Email format is invalid")
    return normalized


def validate_full_name(full_name):
    normalized = (full_name or "").strip()
    if len(normalized) < 2:
        raise ValidationError("Full name must contain at least 2 characters")
    if len(normalized) > MAX_NAME_LENGTH:
        raise ValidationError(
            "Full name is too long",
            {"max_length": MAX_NAME_LENGTH},
        )
    return normalized


def validate_password(password):
    if not password or len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(
            "Password must contain at least 8 characters",
            {"min_length": MIN_PASSWORD_LENGTH},
        )
    if any(char.isspace() for char in password):
        raise ValidationError("Password must not contain whitespace")
    if not any(char.isdigit() for char in password):
        raise ValidationError("Password must contain at least one number")
    if not any(char.isalpha() for char in password):
        raise ValidationError("Password must contain at least one letter")
    return password


def safe_filename(filename):
    cleaned = secure_filename(filename or "")
    if not cleaned:
        raise ValidationError("Filename is invalid")
    if len(cleaned) > MAX_FILENAME_LENGTH:
        raise ValidationError(
            "Filename is too long",
            {"max_length": MAX_FILENAME_LENGTH},
        )
    return cleaned


def build_access_token_claims(user):
    return {
        "role": user.role,
        "email": user.email,
        "is_active": user.is_active,
    }
