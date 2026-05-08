from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return Response(
            {
                'success': False,
                'error': str(exc),
                'details': None,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    details = response.data
    error = None

    if isinstance(response.data, dict):
        error = response.data.get('detail')
        if error is None:
            error = 'Validation error'
    elif isinstance(response.data, list):
        error = response.data[0] if response.data else 'Error'
    else:
        error = str(response.data)

    payload = {
        'success': False,
        'error': error,
        'details': details,
    }

    return Response(payload, status=response.status_code)
