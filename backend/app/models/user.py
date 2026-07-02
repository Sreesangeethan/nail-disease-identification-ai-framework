from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    ROLE_PATIENT = "patient"
    ROLE_CLINICIAN = "clinician"
    ROLE_ADMIN = "admin"
    ALLOWED_ROLES = {ROLE_PATIENT, ROLE_CLINICIAN, ROLE_ADMIN}

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(40), nullable=False, default="patient")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    analyses = db.relationship("NailAnalysis", back_populates="user", lazy=True)
    feedback = db.relationship("AnalysisFeedback", back_populates="user", lazy=True)

    @classmethod
    def create(cls, full_name, email, password, role=ROLE_PATIENT):
        user = cls(
            full_name=full_name.strip(),
            email=email.strip().lower(),
            role=role if role in cls.ALLOWED_ROLES else cls.ROLE_PATIENT,
        )
        user.set_password(password)
        return user

    @classmethod
    def find_by_email(cls, email):
        if not email:
            return None
        return cls.query.filter_by(email=email.strip().lower()).first()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"
