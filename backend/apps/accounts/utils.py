from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """Custom error response format consistent with API_SPEC.md §1.1."""
    response = exception_handler(exc, context)

    if response is not None:
        error_code = "validation_error"
        status_code = response.status_code

        if status_code == 400:
            error_code = "validation_error"
            # Check for specific error codes in response data
            if isinstance(response.data, dict):
                if "code" in response.data:
                    error_code = response.data.pop("code")
        elif status_code == 401:
            error_code = "unauthenticated"
            if isinstance(response.data, dict) and "detail" in response.data:
                if "credentials" in str(response.data["detail"]).lower():
                    error_code = "invalid_credentials"
        elif status_code == 403:
            error_code = "permission_denied"
        elif status_code == 404:
            error_code = "not_found"
        elif status_code == 405:
            error_code = "method_not_allowed"
        elif status_code == 409:
            error_code = "conflict"
        elif status_code == 429:
            error_code = "rate_limited"

        details = response.data
        if isinstance(details, dict) and "detail" in details:
            details = {"non_field_errors": [details["detail"]]}
        elif isinstance(details, list):
            details = {"non_field_errors": details}

        response.data = {
            "error": {
                "code": error_code,
                "message": str(response.data.get("detail", "Permintaan gagal.")),
                "details": details if isinstance(details, dict) else {},
            }
        }

    return response
