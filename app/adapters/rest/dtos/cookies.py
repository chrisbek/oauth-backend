from dataclasses import dataclass, asdict
from typing import Optional, ClassVar
import jwt
from starlette.requests import Request
from starlette.responses import Response


@dataclass
class StateCookie:
    cookie_name: ClassVar[str] = 'sd'
    algorithm: ClassVar[str] = 'HS256'

    session_identifier: Optional[str] = None
    error_code: Optional[int] = None
    error_desc: Optional[str] = None
    refresh_token_is_set: bool = False
    user_info: Optional[dict] = None
    redirected_from_popup: bool = False
    code: Optional[str] = None
    session_state: Optional[str] = None

    def as_jwt(self, private_key: str) -> str:
        encoded = jwt.encode(asdict(self), private_key, algorithm=StateCookie.algorithm)
        return encoded

    def add_cookie_to_response(self, response: Response, private_key: str, path: str = "/"):
        response.set_cookie(
            key=StateCookie.cookie_name,
            path=path,
            value=self.as_jwt(private_key),
            secure=True,
            samesite='strict'
        )

    @staticmethod
    def get_cookie_from_request(request: Request) -> Optional['StateCookie']:
        raise NotImplementedError()

    @staticmethod
    def delete_cookie_from_response(response: Response, path: str = "/"):
        response.delete_cookie(key=StateCookie.cookie_name, path=path)


@dataclass
class RefreshTokenCookie:
    cookie_name: ClassVar[str] = 'rt'
    allowed_paths_mapping: ClassVar[dict] = {
        'exchange_refresh_for_access_token': ['/exchange_refresh_for_access'],
        'refresh_token_grant': ['/refresh_token', '/logout']
    }

    refresh_token: Optional[str] = None
    path_id: Optional[str] = None

    def __post_init__(self):
        if self.path_id is not None and self.path_id not in self.allowed_paths_mapping.keys():
            raise Exception(f'custom {self.path_id}')

    def as_jwt(self):
        return self.refresh_token

    def add_cookie_to_response(self, response: Response, stage: str, authentication_route_prefix: str):
        for path in self.allowed_paths_mapping[self.path_id]:
            response.set_cookie(
                key=self._get_unique_key_for_path(path, stage, authentication_route_prefix),
                value=self.refresh_token,
                secure=True,
                httponly=True,
                samesite='strict',
                path=f"/{stage}/{authentication_route_prefix}{path}"
            )

    def delete_cookie_from_response(self, response: Response, stage: str, authentication_route_prefix: str):
        for path in self.allowed_paths_mapping[self.path_id]:
            response.delete_cookie(
                key=self._get_unique_key_for_path(path, stage, authentication_route_prefix),
                path=f"/{stage}/{authentication_route_prefix}{path}"
            )

    @staticmethod
    def get_cookie_from_request(request: Request) -> Optional['RefreshTokenCookie']:
        for cookie_name, value in request.cookies.items():
            if f"{RefreshTokenCookie.cookie_name}&path." in cookie_name:
                return RefreshTokenCookie(refresh_token=value)

        return None

    @staticmethod
    def _get_unique_key_for_path(path: str, stage: str, authentication_route_prefix: str) -> str:
        return \
            f'{RefreshTokenCookie.cookie_name}&path.{stage}.{authentication_route_prefix}{path.replace("/", ".")}'
