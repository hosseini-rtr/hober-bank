from typing import Any


class CustomHeaderMiddleware:
    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request) -> Any:
        response = self.get_response(request)
        if request.user.is_authenticated:
            response["X-Django-User"] = request.user.email
        return response
