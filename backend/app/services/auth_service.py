from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.user import User
from app.utils.exceptions import AuthError, ValidationError
from app.utils.security import normalize_email, validate_password


class AuthService:
    def register(self, full_name, email, password):
        if not full_name or len(full_name.strip()) < 2:
            raise ValidationError("Full name must contain at least 2 characters")
        normalized_email = normalize_email(email)
        validate_password(password)

        if User.find_by_email(normalized_email):
            raise ValidationError("Email is already registered")

        user = User.create(
            full_name=full_name,
            email=normalized_email,
            password=password,
            role=User.ROLE_PATIENT,
        )
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            raise ValidationError("Email is already registered") from exc
        return user

    def login(self, email, password):
        normalized_email = normalize_email(email)
        user = User.find_by_email(normalized_email)
        if not user or not user.check_password(password):
            raise AuthError("Invalid email or password")
        if not user.is_active:
            raise AuthError("User account is disabled")

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role, "email": user.email},
        )
        return user, access_token

    def get_profile(self, user_id):
        user = db.session.get(User, int(user_id))
        if not user:
            raise AuthError("User account was not found")
        if not user.is_active:
            raise AuthError("User account is disabled")
        return user
