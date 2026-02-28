from flask import jsonify
from typing import Any, Optional, List


def success_response(data: Any = None, message: str = "Success", status_code: int = 200):
    """Create a standardized success response"""
    response = {
        "success": True,
        "message": message,
        "data": data
    }
    return jsonify(response), status_code


def error_response(message: str = "Error", errors: Optional[List[str]] = None, status_code: int = 400):
    """Create a standardized error response"""
    response = {
        "success": False,
        "message": message,
        "errors": errors or []
    }
    return jsonify(response), status_code


def validation_error_response(errors: List[str], message: str = "Validation failed"):
    """Create a validation error response"""
    return error_response(message=message, errors=errors, status_code=422)
