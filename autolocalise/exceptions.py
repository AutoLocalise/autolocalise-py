"""Custom exceptions for AutoLocalise SDK"""


class AutoLocaliseError(Exception):
    """Base exception for AutoLocalise SDK"""

    pass


class APIError(AutoLocaliseError):
    """Raised when API returns an error response"""

    def __init__(self, message, status_code=None, response_data=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class NetworkError(AutoLocaliseError):
    """Raised when network request fails"""

    pass


class ConfigurationError(AutoLocaliseError):
    """Raised when SDK is misconfigured"""

    pass
