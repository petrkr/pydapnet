"""DAPNET client exceptions."""


class DapnetError(Exception):
    """Base class for DAPNET errors."""


class DapnetRequestError(DapnetError):
    """Raised when the HTTP request fails before receiving a response."""


class DapnetAuthError(DapnetError):
    """Raised when credentials are required but missing."""

    def __init__(self, message: str = "login required"):
        super().__init__(message)
        self.message = message

    def __repr__(self) -> str:
        return "%s(message=%r)" % (self.__class__.__name__, self.message)


class DapnetApiError(DapnetError):
    """Raised when the DAPNET API returns an error response."""

    def __init__(self, status_code: int, message: str, payload: object | None = None):
        super().__init__("DAPNET API error %s: %s" % (status_code, message))
        self.status_code = status_code
        self.message = message
        self.payload = payload

    def __repr__(self) -> str:
        return "%s(status_code=%r, message=%r)" % (
            self.__class__.__name__,
            self.status_code,
            self.message,
        )


class DapnetNotFoundError(DapnetApiError):
    """Raised when the DAPNET API returns 404."""


class DapnetPermissionError(DapnetApiError):
    """Raised when the DAPNET API returns 403."""
