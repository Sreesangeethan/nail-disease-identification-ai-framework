from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.extensions import db
from app.models.user import User
from app.utils.exceptions import (
    AuthError,
    ConflictError,
    DatabaseError,
    ForbiddenError,
    NotFoundError,
)
from app.utils.security import (
    build_access_token_claims,
    normalize_email,
    validate_full_name,
    validate_password,
)


class AuthService:
    def register(self, full_name, email, password):
        normalized_name = validate_full_name(full_name)
        normalized_email = normalize_email(email)
        validate_password(password)

        if User.find_by_email(normalized_email):
            raise ConflictError("Email is already registered")

        user = User.create(
            full_name=normalized_name,
            email=normalized_email,
            password=password,
            role=User.ROLE_PATIENT,
        )
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            raise ConflictError("Email is already registered") from exc
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise DatabaseError("Could not create user account") from exc
        return user

    def login(self, email, password):
        normalized_email = normalize_email(email)
        user = User.find_by_email(normalized_email)
        if not user or not user.check_password(password):
            raise AuthError("Invalid email or password")
        if not user.is_active:
            raise ForbiddenError("User account is disabled")

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims=build_access_token_claims(user),
        )
        return user, access_token

    def get_profile(self, user_id):
        user = db.session.get(User, int(user_id))
        if not user:
            raise NotFoundError("User account was not found")
        if not user.is_active:
            raise ForbiddenError("User account is disabled")
        return user
