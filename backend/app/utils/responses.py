from flask import jsonify


def success_response(data=None, message="success", status_code=200):
    payload = {
        "success": True,
        "message": message,
        "data": data or {},
    }
    return jsonify(payload), status_code


def error_response(message, status_code=400, error_code="APP_ERROR", details=None):
    payload = {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
            "details": details or {},
        },
    }
    return jsonify(payload), status_code
