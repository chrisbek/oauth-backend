from typing import Optional
from app.config.config import Container
from fastapi import FastAPI, Request
from pydantic import ValidationError
from app.business_logic.exceptions import ResourceNotFoundException, BusinessLogicException, ServerException, \
    UnauthorizedException, InvalidRefreshToken, ResourceAlreadyExists, InvalidIdToken, InvalidState, \
    IdentityProviderGenericException, TimeoutException, BackendRepositoryException

serializer = Container.serializer()


def get_authentication_path_from_request(request: Request) -> Optional[str]:
    path = str(request.url).replace(str(request.base_url), '')
    path = path.split('?')[0].strip()   # remove any query parameters
    return path.replace(Container.authentication_route_prefix, '') \
        if Container.authentication_route_prefix in path \
        else None


async def _invalid_input_exception_handler(request, exc):
    return serializer.get_json_response_for_exception(exc, status_code=400)


async def _business_logic_exception_handler(request, exc):
    return serializer.get_json_response_for_exception(exc, status_code=409)


async def _server_exception_handler(request: Request, exc):
    path = get_authentication_path_from_request(request)
    if path in ['/stateful', '/login_redirect', '/signup_redirect']:
        return serializer.get_server_exception_response(exc)
    if path == '/exchange_refresh_for_access':
        response = serializer.get_server_exception_response(exc)
        serializer.delete_refresh_cookies_from_response(response, path_id='exchange_refresh_for_access_token')
        return response
    if path in ['/refresh_token', '/logout']:
        response = serializer.get_server_exception_response(exc)
        serializer.delete_refresh_cookies_from_response(response, path_id='refresh_token_grant')
        return response

    return serializer.get_json_response_for_exception(exc, status_code=500)


async def _request_validation_error_handler(request: Request, exc):
    return serializer.get_json_response_for_exception(exc, status_code=400)


async def _resource_not_found_exception_handler(request, exc):
    path = get_authentication_path_from_request(request)
    serializer.get_unauthorized_response()
    if path in ['/exchange_refresh_for_access', '/refresh_token', '/logout', '/login_redirect']:
        return serializer.get_unauthorized_response()

    return serializer.get_json_response_for_exception(exc, status_code=404)


async def _unauthorized_exception_handler(request, exc):
    path = get_authentication_path_from_request(request)
    if path in ['/login_redirect', '/signup_redirect']:
        return serializer.get_unauthorized_response()
    if path == '/exchange_refresh_for_access':
        response = serializer.get_unauthorized_response()
        serializer.delete_refresh_cookies_from_response(response, path_id='exchange_refresh_for_access_token')
        return response

    return serializer.get_json_response_for_exception(exc, status_code=401)


async def _invalid_refresh_token_handler(request, exc):
    path = get_authentication_path_from_request(request)
    if path in ['/refresh_token', '/logout']:
        return serializer.get_invalid_refresh_token_response()

    return serializer.get_json_response_for_exception(exc, status_code=401)


async def _resource_exists_exception_handler(request, exc):
    path = get_authentication_path_from_request(request)
    if path == '/signup_redirect':
        return serializer.get_user_already_exists_response()

    return serializer.get_json_response_for_exception(exc, status_code=422)


async def _invalid_id_token_handler(request, exc):
    path = get_authentication_path_from_request(request)
    if path == '/signup_redirect':
        return serializer.get_invalid_id_token_response()
    if path == '/exchange_refresh_for_access':
        response = serializer.get_invalid_id_token_response()
        serializer.delete_refresh_cookies_from_response(response, path_id='exchange_refresh_for_access_token')
        return response
    if path == '/refresh_token':
        response = serializer.get_invalid_id_token_response()
        serializer.delete_refresh_cookies_from_response(response, path_id='refresh_token_grant')
        return response

    return serializer.get_json_response_for_exception(exc, status_code=401)


async def _template(request, exc):
    path = get_authentication_path_from_request(request)
    if path == '':
        pass

    return serializer.get_json_response_for_exception(exc, status_code=401)


def add_exception_handlers_to_app(app: FastAPI):
    app.add_exception_handler(BusinessLogicException, _business_logic_exception_handler)
    app.add_exception_handler(ServerException, _server_exception_handler)
    app.add_exception_handler(ValidationError, _request_validation_error_handler)
    app.add_exception_handler(ResourceNotFoundException, _resource_not_found_exception_handler)
    app.add_exception_handler(UnauthorizedException, _unauthorized_exception_handler)
    app.add_exception_handler(InvalidRefreshToken, _invalid_refresh_token_handler)
    app.add_exception_handler(ResourceAlreadyExists, _resource_exists_exception_handler)
    app.add_exception_handler(InvalidIdToken, _invalid_id_token_handler)
    app.add_exception_handler(InvalidState, _unauthorized_exception_handler)
    app.add_exception_handler(IdentityProviderGenericException, _server_exception_handler)
    app.add_exception_handler(TimeoutException, _server_exception_handler)
    app.add_exception_handler(BackendRepositoryException, _server_exception_handler)
