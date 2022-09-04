from http.cookiejar import CookieJar, Cookie
from unittest.mock import Mock
import jwt
from requests import Response
from app.business_logic.models.authentication import UserInfo
from app.adapters.rest.dtos.cookies import StateCookie, RefreshTokenCookie
from tests.test_utils import TestUtils

session_id = '7bd70606-06b5-4160-a8ce-7e612fd8c6ad'  # only uuid4 are allowed
code = 'azoogue6eBaePoogeenga3ui'
google_private_key = 'ao5phei0ahH3oonoot7aas9C'
user_info = UserInfo(
    email='user@example.com',
    first_name='Christopher',
    external_identifier='10769150350006150715113082367'
)
access_token = 'XkhU2DFnMGIVL2hvsRHLM00hRWav'
refresh_token = 'ahD9sieS0rai2zah0uquiexoocha'
id_token = jwt.encode(
    {
        "iss": "https://accounts.google.com",
        "azp": "1234987819200.apps.googleusercontent.com",
        "aud": "1234987819200.apps.googleusercontent.com",
        "sub": user_info.external_identifier,
        "hd": "example.com",
        "email": user_info.email,
        "email_verified": "true",
        "iat": 1353601026,
        "exp": 1353604926,
        "nonce": "0394852-3190485-2490358",
        "name": user_info.first_name
    },
    google_private_key,
    StateCookie.algorithm
)
access_token_refreshed = 'Ookoh2gae3Piegha4paithaa'
refresh_token_refreshed = 'eu9hohng3naipheeZoojuagh'
id_token_refreshed = id_token


def _get_exchange_code_for_token_mocked_response():
    response = Mock()
    response.ok = Response.ok
    response.json.return_value = {
        'state': session_id,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'id_token': id_token
    }
    return response


def _get_refresh_token_mocked_response():
    response = Mock()
    response.ok = Response.ok
    response.json.return_value = {
        'access_token': access_token_refreshed,
        'refresh_token': refresh_token_refreshed,
        'id_token': id_token_refreshed
    }
    return response


def _get_revoke_token_mocked_response():
    response = Mock()
    response.ok = Response.ok
    return response


def _get_cookies_in_frontend(frontend_cookies) -> CookieJar:
    cookies = CookieJar()
    for cookie in frontend_cookies:
        cookies.set_cookie(Cookie(
            name=cookie['name'],
            path=cookie['path'].replace('/dev', ''),  # TODO: investigate why the root_path /dev is not supported
            value=cookie['value'],
            version=0,
            port='3000',
            port_specified=True,
            domain='localhost.local',
            domain_specified=True,
            path_specified=True,
            secure=False,
            expires=None,
            discard=False,
            comment=None,
            comment_url=None,
            rfc2109=False,
            rest={'HttpOnly': None, 'SameSite': 'strict'},
            domain_initial_dot=False,
        ))
    return cookies


_frontend_cookies_after_login = _get_cookies_in_frontend([
    {
        'name': StateCookie.cookie_name,
        'path': '/',
        'value': StateCookie(
            session_identifier='7bd70606-06b5-4160-a8ce-7e612fd8c6ad',
            refresh_token_is_set=True,
            user_info={'username': user_info.first_name}
        ).as_jwt(TestUtils.PRIVATE_KEY)
    },
    {
        'name': f'{RefreshTokenCookie.cookie_name}&path.{TestUtils.STAGE}'
                f'.{TestUtils.AUTHENTICATION_ROUTE_PREFIX}.logout',
        'path': f'/{TestUtils.STAGE}/{TestUtils.AUTHENTICATION_ROUTE_PREFIX}/logout',
        'value': refresh_token
    },
    {
        'name': f'{RefreshTokenCookie.cookie_name}&path.{TestUtils.STAGE}'
                f'.{TestUtils.AUTHENTICATION_ROUTE_PREFIX}.refresh_token',
        'path': f'/{TestUtils.STAGE}/{TestUtils.AUTHENTICATION_ROUTE_PREFIX}/refresh_token',
        'value': refresh_token
    },
])


def get_authorization_server_redirect_data():
    yield {
        'session_id': session_id,
        'code': code,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'id_token': id_token,
        'expected_cookies': [
            {
                'name': StateCookie.cookie_name,
                'path': '/',
                'value': StateCookie(
                    session_identifier='7bd70606-06b5-4160-a8ce-7e612fd8c6ad',
                    refresh_token_is_set=True
                ).as_jwt(TestUtils.PRIVATE_KEY)
            },
            {
                'name': f'{RefreshTokenCookie.cookie_name}&path.{TestUtils.STAGE}'
                        f'.{TestUtils.AUTHENTICATION_ROUTE_PREFIX}.exchange_refresh_for_access',
                'path': f'/{TestUtils.STAGE}/{TestUtils.AUTHENTICATION_ROUTE_PREFIX}/exchange_refresh_for_access',
                'value': refresh_token
            }
        ],
        'user_info': user_info,
        'exchange_code_for_token_mocked_response': _get_exchange_code_for_token_mocked_response()
    }


def get_exchange_refresh_for_access_request_data():
    yield {
        'session_id': session_id,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'id_token': id_token,
        'user_info': user_info,
        'cookies_in_frontend': _get_cookies_in_frontend([
            {
                'name': StateCookie.cookie_name,
                'path': '/',
                'value': StateCookie(
                    session_identifier='7bd70606-06b5-4160-a8ce-7e612fd8c6ad',
                    refresh_token_is_set=True
                ).as_jwt(TestUtils.PRIVATE_KEY)
            },
            {
                'name': f'{RefreshTokenCookie.cookie_name}&path.{TestUtils.STAGE}'
                        f'.{TestUtils.AUTHENTICATION_ROUTE_PREFIX}.exchange_refresh_for_access',
                'path': f'/{TestUtils.STAGE}/{TestUtils.AUTHENTICATION_ROUTE_PREFIX}/exchange_refresh_for_access',
                'value': refresh_token
            }
        ]),
        'expected_cookies': [
            {
                'name': StateCookie.cookie_name,
                'path': '/',
                'value': StateCookie(
                    session_identifier='7bd70606-06b5-4160-a8ce-7e612fd8c6ad',
                    refresh_token_is_set=True,
                    user_info={'username': user_info.first_name}
                ).as_jwt(TestUtils.PRIVATE_KEY)
            },
            {
                'name': f'{RefreshTokenCookie.cookie_name}&path.{TestUtils.STAGE}'
                        f'.{TestUtils.AUTHENTICATION_ROUTE_PREFIX}.logout',
                'path': f'/{TestUtils.STAGE}/{TestUtils.AUTHENTICATION_ROUTE_PREFIX}/logout',
                'value': refresh_token
            },
            {
                'name': f'{RefreshTokenCookie.cookie_name}&path.{TestUtils.STAGE}'
                        f'.{TestUtils.AUTHENTICATION_ROUTE_PREFIX}.refresh_token',
                'path': f'/{TestUtils.STAGE}/{TestUtils.AUTHENTICATION_ROUTE_PREFIX}/refresh_token',
                'value': refresh_token
            },
        ]
    }


def get_refresh_token_request_data():
    yield {
        'session_id': session_id,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'id_token': id_token,
        'access_token_refreshed': access_token_refreshed,
        'refresh_token_refreshed': refresh_token_refreshed,
        'id_token_refreshed': id_token,
        'user_info': user_info,
        'cookies_in_frontend': _frontend_cookies_after_login,
        'expected_cookies': [
            {
                'name': StateCookie.cookie_name,
                'path': '/',
                'value': StateCookie(
                    refresh_token_is_set=True,
                    user_info={'username': user_info.first_name}
                ).as_jwt(TestUtils.PRIVATE_KEY)
            },
            {
                'name': f'{RefreshTokenCookie.cookie_name}&path.{TestUtils.STAGE}'
                        f'.{TestUtils.AUTHENTICATION_ROUTE_PREFIX}.logout',
                'path': f'/{TestUtils.STAGE}/{TestUtils.AUTHENTICATION_ROUTE_PREFIX}/logout',
                'value': refresh_token_refreshed
            },
            {
                'name': f'{RefreshTokenCookie.cookie_name}&path.{TestUtils.STAGE}'
                        f'.{TestUtils.AUTHENTICATION_ROUTE_PREFIX}.refresh_token',
                'path': f'/{TestUtils.STAGE}/{TestUtils.AUTHENTICATION_ROUTE_PREFIX}/refresh_token',
                'value': refresh_token_refreshed
            },
        ],
        'refresh_token_mocked_response': _get_refresh_token_mocked_response()
    }


def get_logout_request_data():
    yield {
        'session_id': session_id,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'cookies_in_frontend': _frontend_cookies_after_login,
        'expected_cookies': [],
        'refresh_token_mocked_response': _get_revoke_token_mocked_response()
    }
