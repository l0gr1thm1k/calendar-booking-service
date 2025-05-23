import time

from prometheus_client import Counter, Gauge, Histogram
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Match


REQUESTS = Counter(
        'http_requests_total',
        'Total number of HTTP requests by method, endpoint, and consumer',
        ('method', 'endpoint', 'consumer')
)
RESPONSES = Counter(
        'http_responses_total',
        'Total number of HTTP responses by method, endpoint, status code, and consumer.',
        ('method', 'endpoint', 'status', 'consumer'),
)
REQUESTS_PROCESSING_TIME = Histogram(
        'http_request_duration_seconds',
        'Request duration in seconds by method, endpoint, and status code',
        ('method', 'endpoint', 'status'),
        buckets=(0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, 15.0, 20.0, 25.0, 30.0, 60.0, 90.0, 120.0, '+Inf')
)
REQUESTS_IN_PROGRESS = Gauge(
        'http_requests_in_progress',
        'Gauge of requests by method and endpoint currently being processed',
        ('method', 'endpoint')
)

IGNORED_ENDPOINTS = ('/ui', '/(ui)', 'swagger', 'openapi', '.ico', '/healthcheck', '/metrics')
# Add one hit to ensure metrics available on service startup for HPAs
REQUESTS.labels('GET', '/', 'unknown').inc()


class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware class for Prometheus metrics logging
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        Tabulate metrics, ignoring healthcheck, metrics, and docs endpoints

        :param request: request object
        :param call_next: next middleware
        :return: response object
        """

        method = request.method
        endpoint = self.get_path_template(request)

        # Skip metrics for ignored endpoints
        if not endpoint == '/' and not any(ignored_endpoint in endpoint for ignored_endpoint in IGNORED_ENDPOINTS):
            # Get consumer header for usage tracking
            consumer = request.headers.get('X-Consumer', 'unknown')

            REQUESTS_IN_PROGRESS.labels(method=method, endpoint=endpoint).inc()
            REQUESTS.labels(method=method, endpoint=endpoint, consumer=consumer).inc()

            before_time = time.time()
            response = await call_next(request)
            after_time = time.time()

            REQUESTS_PROCESSING_TIME.labels(method=method, endpoint=endpoint, status=response.status_code).observe(
                    after_time - before_time)
            RESPONSES.labels(method=method, endpoint=endpoint, status=response.status_code, consumer=consumer).inc()
            REQUESTS_IN_PROGRESS.labels(method=method, endpoint=endpoint).dec()
        else:
            response = await call_next(request)

        return response

    @staticmethod
    def get_path_template(request: Request) -> str:
        """
        Get path from request

        :param request: request object
        :return: path
        """

        for route in request.app.routes:
            match, child_scope = route.matches(request.scope)
            if match == Match.FULL:
                return route.path

        return request.url.path
