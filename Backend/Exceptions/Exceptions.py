class AppException(Exception):
    def __init__(self, message, status_code=500, error_code="APP_ERROR"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)

class AuthenticationError(AppException):
    def __init__(self, message="Authentication failed."):
        super().__init__(
            message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR"
        )

class AuthorizationError(AppException):
    def __init__(self, message="You are not authorized to perform this action."):
        super().__init__(
            message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR"
        )

class ResourceNotFoundError(AppException):
    def __init__(self, message="Resource not found."):
        super().__init__(
            message,
            status_code=404,
            error_code="RESOURCE_NOT_FOUND"
        )

class BadRequestError(AppException):
    def __init__(self, message="Invalid request."):
        super().__init__(
            message,
            status_code=400,
            error_code="BAD_REQUEST"
        )