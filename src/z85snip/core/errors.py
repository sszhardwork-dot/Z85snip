class Z85snipError(Exception):
    """Base error for the project."""


class ValidationError(Z85snipError):
    """Input validation error."""


class SnipLibraryError(Z85snipError):
    """Ошибки работы с библиотекой СНиП."""
