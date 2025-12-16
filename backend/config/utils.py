from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return None


    response.data = format_response(
        success=False,
        message="خطایی رخ داده است.",
        errors=response.data
    )

    return response

def format_response(success, message, errors=None):
    return {
        "success": success,
        "message": message,
        "errors": errors
    }
