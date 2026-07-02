from flask_jwt_extended import create_access_token

from app.extensions import db
from app.models.user import User
from app.utils.exceptions import AuthError, ValidationError
from app.utils.security import normalize_email, validate_password


class AuthService:
    def register(self, full_name, email, password):
        if not full_name or len(full_name.strip()) < 2:
            raise ValidationError("Full name is required")
        normalized_email = normalize_email(email)
        validate_password(password)

        existing_user = User.query.filter_by(email=normalized_email).first()
        if existing_user:
            raise ValidationError("Email is already registered")

        user = User(full_name=full_name.strip(), email=normalized_email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    def login(self, email, password):
        normalized_email = normalize_email(email)
        user = User.query.filter_by(email=normalized_email).first()
        if not user or not user.check_password(password):
            raise AuthError("Invalid email or password")
        if not user.is_active:
            raise AuthError("User account is disabled")

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role, "email": user.email},
        )
        return user, access_token
