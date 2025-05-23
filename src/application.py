import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CollectorRegistry
from prometheus_client.multiprocess import MultiProcessCollector

from models.base_models import ErrorResponse
from prometheus_middleware import PrometheusMiddleware
from routes import status_router, booking_router

HOST_ADDRESS = '0.0.0.0'
HOST_PORT = 7100
LOGGING_CONFIG = None
TIMEOUT = 60


# Prometheus multiprocess setup (if needed)
if 'prometheus_multiproc_dir' in os.environ:
    registry = CollectorRegistry()
    MultiProcessCollector(registry)

application = FastAPI(
        title='Calendar Booking Service',
        description='A service to book calendar appointments',
        version='1.0.0',
        docs_url='/ui',
        openapi_url='/api/v1/openapi.json'
)

application.include_router(booking_router, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
                           tags=['Booking'])
application.include_router(status_router, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
                           tags=['Status'])
application.add_middleware(PrometheusMiddleware)
application.add_middleware(CORSMiddleware,
                           allow_origins=["*"],
                           allow_credentials=True,
                           allow_methods=["*"],
                           allow_headers=["*"]
                           )

if __name__ == '__main__':
    current_file_path = Path(__file__).parent
    uvicorn.run(application, host=HOST_ADDRESS, port=HOST_PORT, log_config=LOGGING_CONFIG, access_log=False,
                timeout_keep_alive=TIMEOUT)
