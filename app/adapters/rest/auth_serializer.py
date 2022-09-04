from fastapi import Request
from fastapi.encoders import jsonable_encoder
from starlette.responses import Response, RedirectResponse, JSONResponse
from app.adapters.rest.dtos.access_token import AccessTokenDTO
from app.adapters.rest.dtos.exceptions import get_error_code_for_exception
from app.business_logic.exceptions import ResourceNotFoundException, ServerException
from app.adapters.rest.dtos.cookies import RefreshTokenCookie, StateCookie
from app.business_logic.models.authentication import AuthenticationState, UserInfo


class Serializer:
    """
    This service is responsible for:
        - Deserialize RefreshTokenCookie from request: Request
        - Serialize and return Response for each endpoint or exception thrown in auth_controller.
        Serialization also includes adding the appropriate cookies to the redirect requests.
    """

    def __init__(self, backend_url: str, private_key: str, stage: str, authentication_route_prefix: str):
        self.backend_url = backend_url
        self.private_key = private_key
        self.stage = stage
        self.authentication_route_prefix = authentication_route_prefix

    @staticmethod
    def get_refresh_cookie_from_request(request: Request) -> RefreshTokenCookie:
        """
        :raises ResourceNotFoundException
        """
        refresh_cookie = RefreshTokenCookie.get_cookie_from_request(request)
        if not refresh_cookie:
            raise ResourceNotFoundException('invalid refresh token')

        return refresh_cookie

    @staticmethod
    def get_json_response_for_exception(exc: Exception, status_code: int):
        return JSONResponse(
            {'message': str(exc), 'error_code': get_error_code_for_exception(exc)}, status_code=status_code)

    def redirect_to_home_with_state(self, state: str) -> Response:
        response = RedirectResponse(self.backend_url, 302)
        session_cookie = StateCookie(session_identifier=state)
        session_cookie.add_cookie_to_response(response, self.private_key)
        return response

    def redirect_to_home_with_refresh_token(self, auth_data: AuthenticationState) -> Response:
        response = RedirectResponse(self.backend_url, 302)
        session_cookie = StateCookie(
            session_identifier=auth_data.state,
            refresh_token_is_set=True
        )
        session_cookie.add_cookie_to_response(response, self.private_key)
        refresh_cookie = RefreshTokenCookie(
            refresh_token=auth_data.refresh_token,
            path_id='exchange_refresh_for_access_token'
        )
        refresh_cookie.add_cookie_to_response(response, self.stage, self.authentication_route_prefix)
        return response

    def get_user_already_exists_response(self) -> Response:
        response = RedirectResponse(self.backend_url, 302)
        session_cookie = StateCookie(
            error_code=402,
            error_desc='user exists, please login'
        )
        session_cookie.add_cookie_to_response(response, self.private_key)
        return response

    def get_invalid_id_token_response(self) -> Response:
        response = RedirectResponse(self.backend_url, 302)
        session_cookie = StateCookie(
            error_code=403,
            error_desc='Failed to create user, unexpected id_token'
        )
        session_cookie.add_cookie_to_response(response, self.private_key)
        return response

    def redirect_after_user_creation(self, auth_data: AuthenticationState, user_info: UserInfo) -> Response:
        response = RedirectResponse(self.backend_url, 302)
        session_cookie = StateCookie(
            session_identifier=auth_data.state,
            refresh_token_is_set=True,
            user_info={  # TODO: make this dict a pydantic object
                'username': user_info.first_name
            }
        )
        session_cookie.add_cookie_to_response(response, self.private_key)
        refresh_cookie = RefreshTokenCookie(
            refresh_token=auth_data.refresh_token,
            path_id='refresh_token_grant'
        )
        refresh_cookie.add_cookie_to_response(response, self.stage, self.authentication_route_prefix)
        return response

    def redirect_with_access_refresh_token(self, auth_data: AuthenticationState, user_info: UserInfo) -> Response:
        response = JSONResponse(content=jsonable_encoder(AccessTokenDTO.get_dto(auth_data.access_token)))
        refresh_cookie = RefreshTokenCookie(refresh_token=auth_data.refresh_token, path_id='refresh_token_grant')
        refresh_cookie.delete_cookie_from_response(response, self.stage, self.authentication_route_prefix)
        refresh_cookie.add_cookie_to_response(response, self.stage, self.authentication_route_prefix)
        session_cookie = StateCookie(
            refresh_token_is_set=True,
            user_info={
                'username': user_info.first_name
            }
        )
        session_cookie.add_cookie_to_response(response, self.private_key)
        return response

    def get_unauthorized_response(self) -> Response:
        response = RedirectResponse(self.backend_url, 302)
        session_cookie = StateCookie(
            error_code=401,
            error_desc='unauthorized'
        )
        session_cookie.add_cookie_to_response(response, self.private_key)
        return response

    def get_invalid_refresh_token_response(self) -> Response:
        response = RedirectResponse(self.backend_url, 302)
        session_cookie = StateCookie(
            error_code=401,
            error_desc='refresh_token invalid or expired'
        )
        session_cookie.add_cookie_to_response(response, self.private_key)
        self.delete_refresh_cookies_from_response(response, path_id='refresh_token_grant')
        return response

    def get_refresh_token_response(self, auth_data: AuthenticationState, user_info: UserInfo) -> Response:
        response = JSONResponse(content=jsonable_encoder(AccessTokenDTO.get_dto(auth_data.access_token)))
        session_cookie = StateCookie(
            refresh_token_is_set=True,
            user_info={
                'username': user_info.first_name
            }
        )
        session_cookie.add_cookie_to_response(response, self.private_key)
        refresh_cookie = RefreshTokenCookie(
            refresh_token=auth_data.refresh_token,
            path_id='refresh_token_grant'
        )
        refresh_cookie.add_cookie_to_response(response, self.stage, self.authentication_route_prefix)
        return response

    def get_logout_response(self):
        response = RedirectResponse(self.backend_url, status_code=303)
        self.delete_refresh_cookies_from_response(response, path_id='refresh_token_grant')
        session_cookie = StateCookie()
        session_cookie.delete_cookie_from_response(response)
        return response

    def delete_refresh_cookies_from_response(self, response: Response, path_id: str):
        refresh_cookie = RefreshTokenCookie(path_id=path_id)
        refresh_cookie.delete_cookie_from_response(response, self.stage, self.authentication_route_prefix)

    def get_server_exception_response(self, exception: ServerException) -> Response:
        response = RedirectResponse(self.backend_url, 302)
        session_cookie = StateCookie(
            error_code=500,
            error_desc=str(exception)
        )
        session_cookie.add_cookie_to_response(response, self.private_key)
        return response

    def redirect_after_popup_window_gets_code(self, code: str):
        response = RedirectResponse(self.backend_url, 302)
        session_cookie = StateCookie(
            redirected_from_popup=True,
            code=code
        )
        session_cookie.add_cookie_to_response(response, self.private_key)
        return response

    def redirect_after_popup_window_gets_code_during_signup(self, code: str):
        response = RedirectResponse(self.backend_url, 302)
        session_cookie = StateCookie(
            redirected_from_popup=True,
            code=code,
            session_state='signup'
        )
        session_cookie.add_cookie_to_response(response, self.private_key)
        return response
