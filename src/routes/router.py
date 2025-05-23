import gzip
import json
import uuid
from copy import deepcopy
from typing import Callable, Optional

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from prometheus_client import Counter
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from structlog import BoundLogger, get_logger
from structlog.threadlocal import bind_threadlocal, clear_threadlocal

MAX_LOG_LENGTH = 1000000


class GzipRequest(Request):
    async def body(self) -> bytes:
        if not hasattr(self, "_body"):
            body = await super().body()
            if "gzip" in self.headers.getlist("Content-Encoding"):
                body = gzip.decompress(body)
            self._body = body
        return self._body


async def _get_request_data(request: Request) -> Optional[str]:
    """
    Get JSON request data (if applicable) as a string
    :param request: Request object
    :return: request data string
    """
    if 'application/json' in request.headers.get('content-type', '').lower():
        try:
            request_data = str(await request.json())[:MAX_LOG_LENGTH]
        except:
            request_data = 'error retrieving JSON'
    else:
        request_data = None
    return request_data


def get_logging_route(application_name: str, log_requests: bool, log_responses: bool) -> Callable:
    """
    Closure for setting request/response logging in custom APIRoute class
    :param application_name: name of microservice
    :param log_requests: whether to log application requests
    :param log_responses: whether to log application responses
    :return: logging APIRoute class
    """

    class LoggingRoute(APIRoute):
        """
        Custom APIRoute for logging requests and responses and attaching relevant request data to logger
        """

        def get_route_handler(self) -> Callable:
            """
            Get custom route handler
            :return: custom route handler
            """
            original_route_handler = super().get_route_handler()

            async def custom_route_handler(request: Request) -> Response:
                """
                Handle route and logging
                :param request: Application request
                :return: Response
                """
                # Set request metadata for logging
                request_id = get_new_request_id()
                request_uuid = request.headers.get('uuid')
                path_variables = deepcopy(request.path_params)
                # Remove filename key to prevent it from sticking around
                path_variables.pop('filename', None)
                query_parameters = request.query_params
                clear_threadlocal()
                bind_threadlocal(requestId=request_id,
                                 requestMethod=request.method,
                                 requestPath=request.url.path,
                                 remoteIPAddress=request.headers.get('X-Forwarded-For', request.client.host),
                                 consumer=request.headers.get('X-WW-Consumer', 'unknown'),
                                 uuid=request_uuid,
                                 **path_variables,
                                 **query_parameters)
                logger = get_logger('application')
                if log_requests:
                    logger.info(f'{application_name} request', applicationRequest=await _get_request_data(request))
                try:
                    if 'gzip' in request.headers.getlist("Content-Encoding"):
                        request = GzipRequest(request.scope, request.receive)
                    response: Response = await original_route_handler(request)
                except RequestValidationError as ex:
                    log_exception(ex, 'Validation error', logger=logger,
                                  applicationRequest=await _get_request_data(request))
                    response = generate_error_response({'detail': ex.errors()}, 400)
                except HTTPException as ex:
                    response = generate_error_response({'detail': ex.detail}, ex.status_code)
                except Exception as ex:
                    # Handle JSON parsing errors
                    if isinstance(ex, HTTPException) and getattr(ex, 'status_code', None) == 400:
                        status_code = 400
                        message = 'Request body is not valid JSON'
                    else:
                        log_exception(ex, logger=logger, applicationRequest=await _get_request_data(request),
                                      **request.state._state)
                        status_code = 500
                        message = f'Unhandled exception in application: {type(ex).__name__}({ex})'
                    response = generate_error_response({'message': message}, status_code)
                if log_responses:
                    if response.media_type == 'application/json':
                        response_data = str(json.loads(response.body))[:MAX_LOG_LENGTH]
                    else:
                        if response.body:
                            response_data = str(response.body)[:MAX_LOG_LENGTH]
                        else:
                            response_data = None
                    logger.info(f'{application_name} response', statusCode=response.status_code,
                                applicationResponse=response_data)
                clear_threadlocal()
                return response

            return custom_route_handler

    return LoggingRoute


def generate_error_response(response_data: dict, status_code: int = 500) -> JSONResponse:
    """
    Helper function for generating Starlette responses using orjson

    :param response_data: response data
    :param status_code: HTTP status code
    :return: Response
    """

    return JSONResponse(response_data, status_code=status_code)


def get_new_request_id() -> str:
    """
    gets a new UUID string for a request

    :return: UUID string
    """

    return str(uuid.uuid4()).replace('-', '')


def log_exception(ex: Exception = None, message: str = 'Unhandled exception', logger: BoundLogger = None,
                  **kwargs):
    """
    log an exception with a traceback

    :param ex: Exception
    :param message: optional message
    :param logger: logger, if needed to surface bound kwargs
    :param kwargs: additional fields for log entry
    """

    if logger is None:
        logger = get_logger()
    logger.exception(message, exceptionType=type(ex).__name__, exceptionMessage=str(ex), exc_info=True, **kwargs)


# Get custom APIRoute class to handle request/response logging and exception handling
CustomRoute = get_logging_route('Calendar Booking', True, True)