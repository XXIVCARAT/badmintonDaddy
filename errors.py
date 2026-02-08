"""
Error handling and HTTP responses for the application.
"""
from flask import jsonify
from typing import Dict, Any, Tuple
import logging


logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base application error."""
    
    def __init__(self, message: str, status_code: int = 400, data: Dict[str, Any] = None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.data = data or {}


class ValidationError(AppError):
    """Validation error (400)."""
    
    def __init__(self, message: str, data: Dict[str, Any] = None):
        super().__init__(message, 400, data)


class NotFoundError(AppError):
    """Resource not found error (404)."""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)


class DatabaseError(AppError):
    """Database operation error (500)."""
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, 500)


def success_response(
    data: Any = None,
    message: str = "Success",
    code: int = 200
) -> Tuple[Dict[str, Any], int]:
    """
    Create a standardized success response.
    
    Args:
        data: Response data payload
        message: Success message
        code: HTTP status code
    
    Returns:
        Tuple of (response dict, status code)
    """
    return {
        'status': 'success',
        'message': message,
        'data': data,
        'code': code
    }, code


def error_response(
    message: str,
    code: int = 400,
    data: Dict[str, Any] = None
) -> Tuple[Dict[str, Any], int]:
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        code: HTTP status code
        data: Additional error data
    
    Returns:
        Tuple of (response dict, status code)
    """
    return {
        'status': 'error',
        'message': message,
        'data': data or {},
        'code': code
    }, code


def json_response(data: Any = None, status_code: int = 200) -> Tuple[Dict, int]:
    """Create a JSON response with proper status code."""
    if isinstance(data, dict) and 'status' in data:
        return data, status_code
    return success_response(data, code=status_code)
