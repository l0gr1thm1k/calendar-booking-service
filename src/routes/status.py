import os

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, RedirectResponse
from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, CollectorRegistry, generate_latest
from prometheus_client.multiprocess import MultiProcessCollector
from starlette.responses import Response

from routes.router import CustomRoute

status_router = APIRouter(route_class=CustomRoute)


@status_router.get('/', summary='Redirect to docs', include_in_schema=False)
async def get_ui():
    """
    Redirects root to /ui

    :return: 301
    """

    return RedirectResponse('/ui')


@status_router.get('/healthcheck', summary='Healthcheck', description='Check if service is healthy.')
async def get_healthcheck():
    """
    Returns 200 for health checks

    :return: 200
    """

    return Response()


@status_router.get('/metrics', response_class=PlainTextResponse, summary='Prometheus metrics',
                   description='Get service metrics in Prometheus format.')
async def get_metrics():
    """
    Generates and returns Prometheus metrics

    :return: Prometheus metrics
    """

    if 'prometheus_multiproc_dir' in os.environ:
        registry = CollectorRegistry()
        MultiProcessCollector(registry)
    else:
        registry = REGISTRY

    return Response(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)
