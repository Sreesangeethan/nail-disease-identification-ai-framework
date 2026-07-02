from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.models.user import User
from app.services.auth_service import AuthService
from app.utils.exceptions import NotFoundError
from app.utils.responses import success_response


auth_bp = Blueprint("auth", __name__)
auth_service = AuthService()


@auth_bp.post("/register")
def register():
    payload = request.get_json(silent=True) or {}
    user = auth_service.register(
        payload.get("full_name"),
        payload.get("email"),
        payload.get("password"),
    )
    return success_response(user.to_dict(), "User registered successfully", 201)


@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    user, access_token = auth_service.login(payload.get("email"), payload.get("password"))
    return success_response(
        {
            "access_token": access_token,
            "token_type": "Bearer",
            "user": user.to_dict(),
        },
        "Login successful",
    )


@auth_bp.get("/profile")
@jwt_required()
def profile():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        raise NotFoundError("User profile was not found")
    return success_response(user.to_dict())
