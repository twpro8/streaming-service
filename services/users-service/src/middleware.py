from time import time

from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram


REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint"])

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "HTTP request latency", ["method", "endpoint"]
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        method = request.method
        endpoint = request.url.path
        REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()

        start_time = time()
        response = await call_next(request)
        duration = time() - start_time
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)

        return response
