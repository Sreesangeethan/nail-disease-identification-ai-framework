class AppError(Exception):
    def __init__(self, message, status_code=400, error_code="APP_ERROR", details=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}


class ValidationError(AppError):
    def __init__(self, message, details=None):
        super().__init__(message, 400, "VALIDATION_ERROR", details)


class AuthError(AppError):
    def __init__(self, message="Authentication failed", details=None):
        super().__init__(message, 401, "AUTH_ERROR", details)


class ForbiddenError(AppError):
    def __init__(self, message="Forbidden", details=None):
        super().__init__(message, 403, "FORBIDDEN", details)


class NotFoundError(AppError):
    def __init__(self, message="Resource not found", details=None):
        super().__init__(message, 404, "NOT_FOUND", details)


class ModelUnavailableError(AppError):
    def __init__(self, message="AI model artifacts are not configured", details=None):
        super().__init__(message, 503, "MODEL_UNAVAILABLE", details)
