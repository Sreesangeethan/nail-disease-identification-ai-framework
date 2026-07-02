import re

from werkzeug.utils import secure_filename

from app.utils.exceptions import ValidationError


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_email(email):
    if not email:
        raise ValidationError("Email is required")
    normalized = email.strip().lower()
    if not EMAIL_PATTERN.match(normalized):
        raise ValidationError("Email format is invalid")
    return normalized


def validate_password(password):
    if not password or len(password) < 8:
        raise ValidationError("Password must contain at least 8 characters")
    if not any(char.isdigit() for char in password):
        raise ValidationError("Password must contain at least one number")
    if not any(char.isalpha() for char in password):
        raise ValidationError("Password must contain at least one letter")


def safe_filename(filename):
    cleaned = secure_filename(filename or "")
    if not cleaned:
        raise ValidationError("Filename is invalid")
    return cleaned
