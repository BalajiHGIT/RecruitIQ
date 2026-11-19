"""Custom project exceptions."""
class ProjectError(Exception):
    """Base exception for expected project errors."""

class ValidationError(ProjectError):
    """Raised when input validation fails."""

class DuplicateApplicationError(ProjectError):
    """Raised when a candidate applies to the same job more than once."""
