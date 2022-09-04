from http.cookiejar import Cookie


class TestUtils:
    PLATFORM = 'test'
    STAGE = 'dev'
    AUTH_TABLE = 'Auth-table'
    BACKEND_URL = 'https://frontend.local/dev'
    PRIVATE_KEY = 'IJif5Gaizeech7ahree5geoL'
    AUTHENTICATION_ROUTE_PREFIX = 'auth'
    AUTHORIZATION_ROUTE_PREFIX = 'oauth2'
    CLIENT_ID = 'pae8fiexiebika2OhYihae7H'
    CLIENT_SECRET = 'shae2Hahre0Av8ooshaiw4va'
    ROLLBAR_TOKEN = '00000000000000000000000000a'
    ROLLBAR_ENVIRONMENT = 'local'
    ROLLBAR_ENABLED = 'true'
    IDENTITY_PROVIDER_URL = 'http://identity-provider.local'
    IDENTITY_PROVIDER_TIMEOUT = '3'
    DYNAMODB_LOCAL_URL = 'http://dynamodb.local:8088'


def _validate_response_cookies(response, expected_cookies: list):
    assert len(response.cookies) == len(expected_cookies)
    for cookie, expected_cookie in zip(response.cookies, expected_cookies):
        cookie: Cookie
        assert expected_cookie['name'] == cookie.name
        assert expected_cookie['path'] == cookie.path
        assert expected_cookie['value'] == cookie.value
