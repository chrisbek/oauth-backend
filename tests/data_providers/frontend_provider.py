from app.adapters.rest.dtos.cookies import StateCookie
from tests.test_utils import TestUtils

_login_data = [
    {
        'session_id': '123',
        'expected_cookies': [{
            'name': StateCookie.cookie_name,
            'path': '/',
            'value': StateCookie(session_identifier='123').as_jwt(TestUtils.PRIVATE_KEY)
        }]
    },
    {
        'session_id': 'thaloo2iizaeD5aV8oRoh9oh',
        'expected_cookies': [{
            'name': StateCookie.cookie_name,
            'path': '/',
            'value': StateCookie(session_identifier='thaloo2iizaeD5aV8oRoh9oh').as_jwt(TestUtils.PRIVATE_KEY)
        }]
    },
    {
        'session_id': '12-45-85',
        'expected_cookies': [{
            'name': StateCookie.cookie_name,
            'path': '/',
            'value': StateCookie(session_identifier='12-45-85').as_jwt(TestUtils.PRIVATE_KEY)
        }]
    },
]


def get_login_data():
    for datum in _login_data:
        yield datum
