class AppError(Exception):
    def __init__(self, message, status_code=400, error_code="APP_ERROR", details=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}

    def to_dict(self):
        return {
            "code": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class ValidationError(AppError):
    def __init__(self, message, details=None):
        super().__init__(message, 400, "VALIDATION_ERROR", details)


class AuthError(AppError):
    def __init__(self, message="Authentication failed", details=None):
        super().__init__(message, 401, "AUTH_ERROR", details)


class ForbiddenError(AppError):
    def __init__(self, message="Forbidden", details=None):
        super().__init__(message, 403, "FORBIDDEN", details)


class ConflictError(AppError):
    def __init__(self, message="Resource conflict", details=None):
        super().__init__(message, 409, "CONFLICT", details)


class NotFoundError(AppError):
    def __init__(self, message="Resource not found", details=None):
        super().__init__(message, 404, "NOT_FOUND", details)


class StorageError(AppError):
    def __init__(self, message="File storage failed", details=None):
        super().__init__(message, 500, "STORAGE_ERROR", details)


class DatabaseError(AppError):
    def __init__(self, message="Database operation failed", details=None):
        super().__init__(message, 500, "DATABASE_ERROR", details)


class ModelUnavailableError(AppError):
    def __init__(self, message="AI model artifacts are not configured", details=None):
        super().__init__(message, 503, "MODEL_UNAVAILABLE", details)
