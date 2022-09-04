from typing import Optional

from fastapi import APIRouter, Request
from app.adapters.rest.dtos.access_token import AccessTokenDTO
from app.adapters.rest.dtos.authentication_data import AuthenticationDataDTO
from app.config.config import Container

router = APIRouter()


@router.get("/stateful")
def get_frontend_with_state():
    """
    :raises BackendRepositoryException
    """
    Container.logger.info("GET /stateful")

    state = Container.auth_service().create_state()
    return Container.serializer().redirect_to_home_with_state(state)


@router.get("/login_redirect")
def code_redirect_for_frontend(state: str, code: str, redirected_from_popup: Optional[bool] = True):
    """
    :raises InvalidState
    :raises UnauthorizedException
    :raises BackendRepositoryException
    """
    Container.logger.info("GET /code-redirect-for-frontend")
    if redirected_from_popup:
        Container.auth_service().validate_state(state)
        return Container.serializer().redirect_after_popup_window_gets_code(code)

    auth_state = Container.auth_service().exchange_code_for_token(state, code, endpoint_uri='/login_redirect')
    user_info = Container.auth_service().get_user_info(auth_state.id_token)
    Container.auth_service().ensure_user_exists(user_info.external_identifier)
    Container.auth_service().temporarily_store_auth_state(auth_state)

    return Container.serializer().redirect_to_home_with_refresh_token(auth_state)


@router.get("/signup_redirect")
def code_redirect_for_signup(state: str, code: str, redirected_from_popup: Optional[bool] = True):
    """
    :raises InvalidState
    :raises UnauthorizedException
    :raises InvalidIdToken
    :raises ResourceAlreadyExists
    :raises IdentityProviderGenericException
    :raises BackendRepositoryException
    """
    Container.logger.error("GET /code-redirect-for-signup")

    if redirected_from_popup:
        Container.auth_service().validate_state(state)
        return Container.serializer().redirect_after_popup_window_gets_code_during_signup(code)

    auth_state = Container.auth_service().exchange_code_for_token(state, code, endpoint_uri='/signup_redirect')
    user_info = Container.auth_service().create_user(auth_state.id_token)
    Container.auth_service().temporarily_store_auth_state(auth_state)
    # return Container.serializer().redirect_after_user_creation(auth_state, user_info)
    return Container.serializer().redirect_to_home_with_refresh_token(auth_state)


@router.put("/exchange_refresh_for_access", response_model=AccessTokenDTO)
def exchange_refresh_for_access(authentication_dto: AuthenticationDataDTO, request: Request):
    """
    :raises InvalidState
    :raises ResourceNotFoundException
    :raises BackendRepositoryException
    :raises UnauthorizedException
    :raises InvalidIdToken
    """
    Container.logger.info("PUT /exchange-refresh-for-access")

    refresh_token = Container.serializer().get_refresh_cookie_from_request(request).refresh_token
    auth_state = Container.auth_service().get_temporarily_stored_access_token(authentication_dto.state, refresh_token)
    user_info = Container.auth_service().get_user_info(auth_state.id_token)
    return Container.serializer().redirect_with_access_refresh_token(auth_state, user_info)


@router.put('/refresh_token')
def refresh_token_endpoint(request: Request):
    """
    :raises ResourceNotFoundException
    :raises InvalidRefreshToken
    :raises InvalidIdToken
    """
    Container.logger.error('PUT /refresh_token')

    refresh_token = Container.serializer().get_refresh_cookie_from_request(request).refresh_token
    auth_state = Container.auth_service().refresh_access_token(refresh_token=refresh_token)
    user_info = Container.auth_service().get_user_info(auth_state.id_token)
    return Container.serializer().get_refresh_token_response(auth_state, user_info)


@router.put('/logout')
def logout(request: Request):
    """
    :raises ResourceNotFoundException
    :raises InvalidRefreshToken
    """
    Container.logger.error("PUT /logout")

    refresh_token = Container.serializer().get_refresh_cookie_from_request(request).refresh_token
    Container.auth_service().revoke_refresh_token(refresh_token)
    return Container.serializer().get_logout_response()
