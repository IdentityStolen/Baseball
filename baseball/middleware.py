from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse


class SimpleCORSMiddleware(MiddlewareMixin):
    """Very small CORS middleware for development.

    Allows origins listed in ALLOWED_CORS_ORIGINS in settings, or allows
    http://localhost:3000 and http://127.0.0.1:3000 by default.

    Note: This is intended for local development only. For production, use
    django-cors-headers or a proper CORS configuration at the proxy.
    """

    def process_request(self, request):
        # Handle preflight requests
        if request.method == "OPTIONS":
            response = HttpResponse()
            self._set_cors_headers(request, response)
            return response
        return None

    def process_response(self, request, response):
        self._set_cors_headers(request, response)
        return response

    def _set_cors_headers(self, request, response):
        allowed = getattr(
            __import__("django.conf").conf.settings, "ALLOWED_CORS_ORIGINS", None
        )
        origin = request.META.get("HTTP_ORIGIN")
        default_allowed = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://web:3000",
        ]
        allowed_origins = allowed if allowed is not None else default_allowed
        if origin and origin in allowed_origins:
            response["Access-Control-Allow-Origin"] = origin
            response["Vary"] = "Origin"
            response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response["Access-Control-Allow-Credentials"] = "true"
        return response
