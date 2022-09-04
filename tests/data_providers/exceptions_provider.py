from unittest.mock import Mock

from requests import Response

from app.adapters.rest.dtos.cookies import StateCookie
from app.business_logic.exceptions import BackendRepositoryException, InvalidState, UnauthorizedException, \
    InvalidIdToken, ResourceAlreadyExists, IdentityProviderGenericException, ResourceNotFoundException, \
    InvalidRefreshToken
from tests.test_utils import TestUtils


def _get_failed_response_mock():
    response = Mock()
    response.ok.return_value = None
    return response


def _get_successful_post_code_response_mock():
    response = Mock()
    response.ok = Response.ok
    response.json.return_value = {
        'state': '2c38da8a-e6b4-42ba-9af6-ed857ff36095',
        'access_token': 'access_token',
        'refresh_token': 'refresh_token',
        'id_token': 'id_token'
    }
    return response


def get_data_for_home():
    error_message = 'error message'
    yield {
        'repository_exception': BackendRepositoryException(error_message),
        'expected_cookies': [
            {
                'name': StateCookie.cookie_name,
                'path': '/',
                'value': StateCookie(error_code=500, error_desc=error_message).as_jwt(TestUtils.PRIVATE_KEY)
            }
        ]
    }


def get_data_for_login_redirect_exceptions():
    session_id = '2c38da8a-e6b4-42ba-9af6-ed857ff36095'
    code = 'any'
    yield {
        'exchange_code_for_token_exception': InvalidState('invalid state'),
        'session_id': session_id,
        'code': code,
        'expected_cookies': [
            {
                'name': StateCookie.cookie_name,
                'path': '/',
                'value': StateCookie(error_code=401, error_desc='unauthorized').as_jwt(TestUtils.PRIVATE_KEY)
            }
        ]
    }
    yield {
        'exchange_code_for_token_exception': UnauthorizedException('some message'),
        'session_id': session_id,
        'code': code,
        'expected_cookies': [
            {
                'name': StateCookie.cookie_name,
                'path': '/',
                'value': StateCookie(error_code=401, error_desc='unauthorized').as_jwt(TestUtils.PRIVATE_KEY)
            }
        ]
    }
    yield {
        'temporarily_store_auth_state_exception': BackendRepositoryException('cannot store state'),
        'session_id': session_id,
        'code': code,
        'post_code_request_mock': _get_successful_post_code_response_mock(),
        'expected_cookies': [
            {
                'name': StateCookie.cookie_name,
                'path': '/',
                'value': StateCookie(error_code=500, error_desc='cannot store state').as_jwt(TestUtils.PRIVATE_KEY)
            }
        ]
    }


def get_data_for_signup_redirect_exceptions():
    session_id = '2c38da8a-e6b4-42ba-9af6-ed857ff36095'
    code = 'any'
    yield {
        'exchange_code_for_token_exception': InvalidState('invalid state'),
        'session_id': session_id,
        'code': code,
        'expected_cookies': [
            {
                'name': StateCookie.cookie_name,
                'path': '/',
                'value': StateCookie(error_code=401, error_desc='unauthorized').as_jwt(TestUtils.PRIVATE_KEY)
            }
        ]
    }
    yield {
        'exchange_code_for_token_exception': UnauthorizedException('some message'),
        'session_id': session_id,
        'code': code,
        'expected_cookies': [
            {
                'name': StateCookie.cookie_name,
                'path': '/',
                'value': StateCookie(error_code=401, error_desc='unauthorized').as_jwt(TestUtils.PRIVATE_KEY)
            }
        ]
    }
    yield {
        'create_user_exception': InvalidIdToken('invalid token'),
        'session_id': session_id,
        'code': code,
        'expected_cookies': [
            {
                'name': StateCookie.cookie_name,
                'path': '/',
                'value': StateCookie(
                    error_code=403,
                    error_desc='Failed to create user, unexpected id_token'
                ).as_jwt(TestUtils.PRIVATE_KEY)
            }
        ]
    }
    yield {
        'create_user_exception': ResourceAlreadyExists('user exists'),
        'session_id': session_id,
        'code': code,
        'expected_cookies': [
            {
                'name': StateCookie.cookie_name,
                'path': '/',
                'value': StateCookie(
                    error_code=402,
                    error_desc='user exists, please login'
                ).as_jwt(TestUtils.PRIVATE_KEY)
            }
        ]
    }
    yield {
        'create_user_exception': IdentityProviderGenericException('identity-provider generic exception'),
        'session_id': session_id,
        'code': code,
        'expected_cookies': [
            {
                'name': StateCookie.cookie_name,
                'path': '/',
                'value': StateCookie(
                    error_code=500,
                    error_desc='identity-provider generic exception'
                ).as_jwt(TestUtils.PRIVATE_KEY)
            }
        ]
    }
    yield {
        'temporarily_store_auth_state_exception': BackendRepositoryException('cannot store state'),
        'session_id': session_id,
        'code': code,
        'post_code_request_mock': _get_successful_post_code_response_mock(),
        'expected_cookies': [
            {
                'name': StateCookie.cookie_name,
                'path': '/',
                'value': StateCookie(error_code=500, error_desc='cannot store state').as_jwt(TestUtils.PRIVATE_KEY)
            }
        ]
    }


def get_data_for_exchange_refresh_for_access_exceptions():
    session_id = '2c38da8a-e6b4-42ba-9af6-ed857ff36095'
    refresh_cookie_mock = Mock()
    refresh_cookie_mock.refresh_cookie = 'ahD9sieS0rai2zah0uquiexoocha'
    yield {
        'get_refresh_cookie_exception': ResourceNotFoundException('invalid refresh token'),
        'session_id': session_id,
        'expected_cookies': [
            {
                'name': StateCookie.cookie_name,
                'path': '/',
                'value': StateCookie(error_code=401, error_desc='unauthorized').as_jwt(TestUtils.PRIVATE_KEY)
            }
        ]
    }
    yield {
        'session_id': session_id,
        'refresh_cookie_mock': refresh_cookie_mock,
        'get_temporarily_stored_access_token_exception': BackendRepositoryException('database exception'),
        'expected_cookies': [
            {
                'name': StateCookie.cookie_name,
                'path': '/',
                'value': StateCookie(error_code=500, error_desc='database exception').as_jwt(TestUtils.PRIVATE_KEY)
            }
        ]
    }
    yield {
        'session_id': session_id,
        'refresh_cookie_mock': refresh_cookie_mock,
        'get_temporarily_stored_access_token_exception': UnauthorizedException('no state-refresh_token pair found'),
        'expected_cookies': [
            {
                'name': StateCookie.cookie_name,
                'path': '/',
                'value': StateCookie(error_code=401, error_desc='unauthorized').as_jwt(TestUtils.PRIVATE_KEY)
            }
        ]
    }
    yield {
        'session_id': session_id,
        'refresh_cookie_mock': refresh_cookie_mock,
        'get_user_info_exception': InvalidIdToken('invalid id token'),
        'expected_cookies': [
            {
                'name': StateCookie.cookie_name,
                'path': '/',
                'value': StateCookie(
                    error_code=403,
                    error_desc='Failed to create user, unexpected id_token'
                ).as_jwt(TestUtils.PRIVATE_KEY)
            }
        ]
    }


def get_data_for_refresh_token_exceptions():
    session_id = '2c38da8a-e6b4-42ba-9af6-ed857ff36095'
    refresh_cookie_mock = Mock()
    refresh_cookie_mock.refresh_cookie = 'ahD9sieS0rai2zah0uquiexoocha'
    yield {
        'get_refresh_cookie_exception': ResourceNotFoundException('invalid refresh token'),
        'session_id': session_id,
        'expected_cookies': [
            {
                'name': StateCookie.cookie_name,
                'path': '/',
                'value': StateCookie(error_code=401, error_desc='unauthorized').as_jwt(TestUtils.PRIVATE_KEY)
            }
        ]
    }
    yield {
        'session_id': session_id,
        'refresh_cookie_mock': refresh_cookie_mock,
        'refresh_access_token_exception': InvalidRefreshToken('invalid refresh token'),
        'expected_cookies': [
            {
                'name': StateCookie.cookie_name,
                'path': '/',
                'value': StateCookie(
                    error_code=401,
                    error_desc='refresh_token invalid or expired'
                ).as_jwt(TestUtils.PRIVATE_KEY)
            }
        ]
    }
    yield {
        'session_id': session_id,
        'refresh_cookie_mock': refresh_cookie_mock,
        'get_user_info': InvalidIdToken('invalid id token'),
        'expected_cookies': [
            {
                'name': StateCookie.cookie_name,
                'path': '/',
                'value': StateCookie(
                    error_code=403,
                    error_desc='Failed to create user, unexpected id_token'
                ).as_jwt(TestUtils.PRIVATE_KEY)
            }
        ]
    }


def get_logout_exceptions():
    session_id = '2c38da8a-e6b4-42ba-9af6-ed857ff36095'
    refresh_cookie_mock = Mock()
    refresh_cookie_mock.refresh_cookie = 'ahD9sieS0rai2zah0uquiexoocha'
    yield {
        'get_refresh_cookie_exception': ResourceNotFoundException('invalid refresh token'),
        'session_id': session_id,
        'expected_cookies': [
            {
                'name': StateCookie.cookie_name,
                'path': '/',
                'value': StateCookie(error_code=401, error_desc='unauthorized').as_jwt(TestUtils.PRIVATE_KEY)
            }
        ]
    }
    yield {
        'session_id': session_id,
        'refresh_cookie_mock': refresh_cookie_mock,
        'revoke_refresh_token_exception': InvalidRefreshToken('invalid refresh token'),
        'expected_cookies': [
            {
                'name': StateCookie.cookie_name,
                'path': '/',
                'value': StateCookie(
                    error_code=401,
                    error_desc='refresh_token invalid or expired'
                ).as_jwt(TestUtils.PRIVATE_KEY)
            }
        ]
    }
