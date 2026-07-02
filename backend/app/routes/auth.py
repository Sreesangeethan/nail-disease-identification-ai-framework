import re

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.user import User


auth_bp = Blueprint("auth", __name__)
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@auth_bp.post("/register")
def register():
    payload = request.get_json(silent=True) or {}
    validation_error = _validate_registration_payload(payload)
    if validation_error:
        return _error(validation_error, 400, "VALIDATION_ERROR")

    email = payload["email"].strip().lower()
    if User.find_by_email(email):
        return _error("Email is already registered", 409, "EMAIL_ALREADY_EXISTS")

    user = User.create(
        full_name=payload["full_name"],
        email=email,
        password=payload["password"],
        role=User.ROLE_PATIENT,
    )

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _error("Email is already registered", 409, "EMAIL_ALREADY_EXISTS")

    return _success(user.to_dict(), "User registered successfully", 201)


@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if not email or not password:
        return _error("Email and password are required", 400, "VALIDATION_ERROR")

    user = User.find_by_email(email)
    if not user or not user.check_password(password):
        return _error("Invalid email or password", 401, "INVALID_CREDENTIALS")

    if not user.is_active:
        return _error("User account is disabled", 403, "USER_DISABLED")

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role, "email": user.email},
    )
    return _success(
        {
            "access_token": token,
            "token_type": "Bearer",
            "user": user.to_dict(),
        },
        "Login successful",
    )


@auth_bp.get("/profile")
@jwt_required()
def profile():
    user = db.session.get(User, int(get_jwt_identity()))
    if not user:
        return _error("User profile was not found", 404, "USER_NOT_FOUND")
    return _success(user.to_dict())


def _validate_registration_payload(payload):
    full_name = (payload.get("full_name") or "").strip()
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if len(full_name) < 2:
        return "Full name must contain at least 2 characters"
    if not EMAIL_PATTERN.match(email):
        return "Email format is invalid"
    if len(password) < 8:
        return "Password must contain at least 8 characters"
    if not any(char.isalpha() for char in password):
        return "Password must contain at least one letter"
    if not any(char.isdigit() for char in password):
        return "Password must contain at least one number"
    return None


def _success(data=None, message="success", status_code=200):
    return jsonify({"success": True, "message": message, "data": data or {}}), status_code


def _error(message, status_code, code):
    return (
        jsonify(
            {
                "success": False,
                "error": {
                    "code": code,
                    "message": message,
                },
            }
        ),
        status_code,
    )
