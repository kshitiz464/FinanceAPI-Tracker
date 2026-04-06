"""
Custom utilities for the API app.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    Wraps DRF's default handler with a standardized error format.
    """
    response = exception_handler(exc, context)

    if response is not None:
        custom_response = {
            'success': False,
            'status_code': response.status_code,
            'errors': response.data,
        }

        # Add human-readable message for common status codes
        messages = {
            400: 'Bad request. Please check your input.',
            401: 'Authentication credentials were not provided or are invalid.',
            403: 'You do not have permission to perform this action.',
            404: 'The requested resource was not found.',
            405: 'Method not allowed.',
            429: 'Too many requests. Please slow down.',
        }
        custom_response['message'] = messages.get(
            response.status_code, 'An error occurred.'
        )

        response.data = custom_response

    return response
