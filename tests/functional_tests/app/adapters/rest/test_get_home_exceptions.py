from unittest.mock import Mock, patch
from pytest import mark
from tests.data_providers import exceptions_provider
from tests.test_utils import _validate_response_cookies


@mark.parametrize("data", exceptions_provider.get_data_for_home())
def test_frontend_with_state_exceptions(data: dict, backend_repository, client):
    repository_exception = data['repository_exception']
    if repository_exception:
        backend_repository.create_authentication_state.side_effect = repository_exception

    response = client.get(f'/auth/stateful', allow_redirects=False)

    assert response.status_code == 302
    _validate_response_cookies(response, data['expected_cookies'])


@mark.parametrize("data", exceptions_provider.get_data_for_login_redirect_exceptions())
def test_login_redirect_exceptions(data: dict, authentication_service, container, client):
    container.auth_service.override(authentication_service)

    if 'exchange_code_for_token_exception' in data:
        authentication_service.exchange_code_for_token.side_effect = data['exchange_code_for_token_exception']
    if 'temporarily_store_auth_state_exception' in data:
        authentication_service.exchange_code_for_token.side_effect = None
        authentication_service.temporarily_store_auth_state.side_effect = data['temporarily_store_auth_state_exception']

    response = client.get(
        f'/auth/login_redirect', params={'state': data['session_id'], 'code': data['code']}, allow_redirects=False)

    assert response.status_code == 302
    _validate_response_cookies(response, data['expected_cookies'])


@mark.parametrize("data", exceptions_provider.get_data_for_signup_redirect_exceptions())
def test_signup_redirect_exceptions(data: dict, authentication_service, container, client):
    container.auth_service.override(authentication_service)

    if 'exchange_code_for_token_exception' in data:
        authentication_service.exchange_code_for_token.side_effect = data['exchange_code_for_token_exception']
    if 'create_user_exception' in data:
        authentication_service.exchange_code_for_token.side_effect = None
        authentication_service.create_user.side_effect = data['create_user_exception']
    if 'temporarily_store_auth_state_exception' in data:
        authentication_service.exchange_code_for_token.side_effect = None
        authentication_service.create_user.side_effect = None
        authentication_service.temporarily_store_auth_state.side_effect = data['temporarily_store_auth_state_exception']

    response = client.get(
        f'/auth/signup_redirect', params={'state': data['session_id'], 'code': data['code']}, allow_redirects=False)

    assert response.status_code == 302
    _validate_response_cookies(response, data['expected_cookies'])


@mark.parametrize("data", exceptions_provider.get_data_for_exchange_refresh_for_access_exceptions())
@patch('app.adapters.rest.dtos.cookies.RefreshTokenCookie.get_cookie_from_request')
def test_exchange_refresh_for_access_exceptions(
        get_cookie_from_request_mock: Mock,
        data: dict,
        authentication_service,
        container,
        client
):
    container.auth_service.override(authentication_service)

    if 'get_refresh_cookie_exception' in data:
        get_cookie_from_request_mock.side_effect = data['get_refresh_cookie_exception']
    else:
        get_cookie_from_request_mock.return_value = data['refresh_cookie_mock']

    if 'get_temporarily_stored_access_token_exception' in data:
        authentication_service.get_temporarily_stored_access_token.side_effect = \
            data['get_temporarily_stored_access_token_exception']
    if 'get_user_info_exception' in data:
        authentication_service.get_temporarily_stored_access_token.side_effect = None
        authentication_service.get_user_info.side_effect = data['get_user_info_exception']

    response = client.put(
        f'/auth/exchange_refresh_for_access',
        json={'state': data['session_id']},
        cookies=[],
        allow_redirects=False,
    )

    assert response.status_code == 302
    _validate_response_cookies(response, data['expected_cookies'])


@mark.parametrize("data", exceptions_provider.get_data_for_refresh_token_exceptions())
@patch('app.adapters.rest.dtos.cookies.RefreshTokenCookie.get_cookie_from_request')
def test_refresh_token_endpoint_exceptions(
        get_cookie_from_request_mock: Mock,
        data: dict,
        authentication_service,
        container,
        client
):
    container.auth_service.override(authentication_service)

    if 'get_refresh_cookie_exception' in data:
        get_cookie_from_request_mock.side_effect = data['get_refresh_cookie_exception']
    else:
        get_cookie_from_request_mock.return_value = data['refresh_cookie_mock']

    if 'refresh_access_token_exception' in data:
        authentication_service.refresh_access_token.side_effect = data['refresh_access_token_exception']
    if 'get_user_info' in data:
        authentication_service.refresh_access_token.side_effect = None
        authentication_service.get_user_info.side_effect = data['get_user_info']

    response = client.put(
        f'/auth/refresh_token',
        cookies=[],
        allow_redirects=False,
    )

    assert response.status_code == 302
    _validate_response_cookies(response, data['expected_cookies'])


@mark.parametrize("data", exceptions_provider.get_logout_exceptions())
@patch('app.adapters.rest.dtos.cookies.RefreshTokenCookie.get_cookie_from_request')
def test_logout_exceptions(
        get_cookie_from_request_mock: Mock,
        data: dict,
        authentication_service,
        container,
        client
):
    container.auth_service.override(authentication_service)

    if 'get_refresh_cookie_exception' in data:
        get_cookie_from_request_mock.side_effect = data['get_refresh_cookie_exception']
    else:
        get_cookie_from_request_mock.return_value = data['refresh_cookie_mock']

    if 'revoke_refresh_token_exception' in data:
        authentication_service.revoke_refresh_token.side_effect = data['revoke_refresh_token_exception']

    response = client.put(
        f'/auth/logout',
        cookies=[],
        allow_redirects=False,
    )

    assert response.status_code == 302
    _validate_response_cookies(response, data['expected_cookies'])
