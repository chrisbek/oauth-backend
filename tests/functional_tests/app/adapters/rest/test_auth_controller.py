from pytest import mark
from unittest.mock import patch, Mock
from app.business_logic.models.authentication import AuthenticationState
from tests.data_providers import frontend_provider, authorization_server_provider
from tests.test_utils import _validate_response_cookies


@mark.parametrize("data", frontend_provider.get_login_data())
def test_get_home(data: dict, backend_repository, client):
    expected_cookies = data['expected_cookies']
    backend_repository.create_authentication_state.return_value = AuthenticationState(state=data['session_id'])

    response = client.get(f'/auth/stateful', allow_redirects=False)

    assert response.status_code == 302
    _validate_response_cookies(response, expected_cookies)


@mark.parametrize("data", authorization_server_provider.get_authorization_server_redirect_data())
@patch('requests.post')
def test_login_redirect(
        post_mock: Mock,
        data: dict,
        backend_repository,
        client
):
    backend_repository.create_authentication_state.return_value = AuthenticationState(state=data['session_id'])
    post_mock.return_value = data['exchange_code_for_token_mocked_response']
    expected_cookies = data['expected_cookies']

    response = client.get(f'/auth/login_redirect', params={'state': data['session_id'], 'code': data['code']},
                          allow_redirects=False)

    backend_repository.get_authentication_state.assert_called_with(data['session_id'])
    backend_repository.update_authentication_state.assert_called_with(
        AuthenticationState(
            state=data['session_id'],
            access_token=data['access_token'],
            refresh_token=data['refresh_token'],
            id_token=data['id_token']
        )
    )
    assert response.status_code == 302
    _validate_response_cookies(response, expected_cookies)


@mark.parametrize("data", authorization_server_provider.get_authorization_server_redirect_data())
@patch('requests.post')
def test_code_redirect_for_signup(
        post_mock: Mock,
        data: dict,
        backend_repository,
        identity_provider,
        token_service,
        client
):
    backend_repository.create_authentication_state.return_value = AuthenticationState(state=data['session_id'])
    token_service.validate_id_token.return_value = data['user_info']
    post_mock.return_value = data['exchange_code_for_token_mocked_response']
    expected_cookies = data['expected_cookies']

    response = client.get(
        f'/auth/signup_redirect', params={'state': data['session_id'], 'code': data['code']}, allow_redirects=False)

    identity_provider.sign_up_user.assert_called_with(data['user_info'])
    backend_repository.update_authentication_state.assert_called_with(
        AuthenticationState(
            state=data['session_id'],
            access_token=data['access_token'],
            refresh_token=data['refresh_token'],
            id_token=data['id_token']
        )
    )
    assert response.status_code == 302
    _validate_response_cookies(response, expected_cookies)


@mark.parametrize("data", authorization_server_provider.get_exchange_refresh_for_access_request_data())
def test_exchange_refresh_for_access(
        data: dict,
        backend_repository,
        token_service,
        container,
        client
):
    cookies = data['cookies_in_frontend']
    backend_repository.pop_authentication_state.return_value = AuthenticationState(
        state=data['session_id'],
        refresh_token=data['refresh_token'],
        access_token=data['access_token'],
        id_token=data['id_token']
    )
    token_service.validate_id_token.return_value = data['user_info']
    expected_cookies = data['expected_cookies']

    response = client.put(
        f'/auth/exchange_refresh_for_access',
        json={'state': data['session_id']},
        cookies=cookies,
        allow_redirects=False,
    )
    assert response.status_code == 200
    backend_repository.pop_authentication_state.assert_called_with(data['session_id'], data['refresh_token'])
    token_service.validate_id_token.assert_called_with(data['id_token'], container.client_id)
    _validate_response_cookies(response, expected_cookies)


@mark.parametrize("data", authorization_server_provider.get_refresh_token_request_data())
@patch('requests.post')
def test_refresh_token(
        post_mock: Mock,
        data: dict,
        token_service,
        container,
        client
):
    cookies = data['cookies_in_frontend']
    post_mock.return_value = data['refresh_token_mocked_response']
    token_service.validate_id_token.return_value = data['user_info']

    response = client.put(
        f'/auth/refresh_token',
        cookies=cookies,
        allow_redirects=False,
    )
    assert response.status_code == 200
    assert response.json() == {'access_token': data['access_token_refreshed']}
    token_service.validate_id_token.assert_called_with(data['id_token_refreshed'], container.client_id)
    _validate_response_cookies(response, data['expected_cookies'])


@mark.parametrize("data", authorization_server_provider.get_logout_request_data())
@patch('requests.post')
def test_logout(
        post_mock: Mock,
        data: dict,
        client
):
    cookies = data['cookies_in_frontend']
    post_mock.return_value = data['refresh_token_mocked_response']

    response = client.put(
        f'/auth/logout',
        cookies=cookies,
        allow_redirects=False,
    )
    assert response.status_code == 303
    post_mock.assert_called_with(
        'https://oauth2.googleapis.com/revoke',
        params={'token': data['refresh_token']},
        headers={'content-type': 'application/x-www-form-urlencoded'}
    )
    _validate_response_cookies(response, data['expected_cookies'])
