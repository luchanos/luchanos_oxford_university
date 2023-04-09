from prometheus_client import Counter
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class CustomPrometheusMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.responses_total = Counter(
            "starlette_http_responses_total",
            "Total number of HTTP responses by status code",
            ["method", "status_code"],
        )

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)
        self.responses_total.labels(
            method=request.method, status_code=response.status_code
        ).inc()
        return response
