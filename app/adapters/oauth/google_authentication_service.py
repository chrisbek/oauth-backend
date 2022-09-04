from app.business_logic.authentication_service import AuthenticationService
from app.business_logic.exceptions import BackendRepositoryException, InvalidState, UnauthorizedException, \
    InvalidRefreshToken
from app.business_logic.authentication_repository import AuthenticationRepository
from app.business_logic.models.authentication import AuthenticationState, UserInfo
from app.business_logic.token_service import TokenService
from app.adapters.service_adapters.identity_provider_client import IdentityProviderClient
from logging import Logger
import requests
from uuid import uuid4


class GoogleAuthenticationService(AuthenticationService):
    def __init__(
            self,
            platform: str,
            logger: Logger,
            client_id: str,
            client_secret: str,
            backend_repository: AuthenticationRepository,
            identity_provider_service: IdentityProviderClient,
            token_service: TokenService,
            redirect_uri_prefix: str
    ):
        self.platform = platform
        self.logger = logger
        self.client_id = client_id
        self.client_secret = client_secret
        self.backend_repository = backend_repository
        self.identity_provider_service = identity_provider_service
        self.token_service = token_service
        self.redirect_uri_prefix = redirect_uri_prefix

    def create_state(self) -> str:
        state = str(uuid4())
        auth_state = self.backend_repository.create_authentication_state(state)
        return auth_state.state

    def validate_state(self, state: str):
        """
        :raises InvalidState
        """
        try:
            self.backend_repository.get_authentication_state(state)
        except BackendRepositoryException:
            raise InvalidState('invalid state')

    def exchange_code_for_token(self, state: str, code: str, endpoint_uri: str) -> AuthenticationState:
        self.validate_state(state)
        token_endpoint = self.token_service.get_token_endpoint_from_well_known_url()
        """
        If the redirect URI was included in the initial authorization request, 
        the service must require it in the token request as well. 
        The redirect URI in the token request must be an exact match of the redirect URI that was used when generating 
        the authorization code. The service must reject the request otherwise.
        """
        redirect_uri = f"{self.redirect_uri_prefix}{endpoint_uri}"

        response = requests.post(
            token_endpoint,
            data={
                "code": code,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code"
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

        self.logger.warning(f'response = {response}')
        # TODO handle response and throw exceptions
        if response.ok:
            return AuthenticationState(
                state=state,
                access_token=response.json()['access_token'],
                refresh_token=response.json()['refresh_token'],
                id_token=response.json()['id_token']
            )

        raise UnauthorizedException(response.reason)

    def temporarily_store_auth_state(self, auth_state: AuthenticationState):
        self.backend_repository.update_authentication_state(auth_state)

    def get_temporarily_stored_access_token(self, state: str, refresh_token: str) -> AuthenticationState:
        return self.backend_repository.pop_authentication_state(state, refresh_token)

    def revoke_refresh_token(self, refresh_token: str):
        """
        When hitting the https://oauth2.googleapis.com/revoke the corresponding {token}
        can be an access token or a refresh token.
        If the token is an access token, and it has a corresponding refresh token,
        the refresh token will also be revoked.
        In our case we only have the refresh_token available (through an http-only cookie).
        We do not want to send the raw access_token through the internet.
        Access token exists only in Frontend's memory, and it will be deleted from there.
        Refresh token exists only in Frontend's http-only cookie, and for extra safety it will be revoked.
        The actual access_token will expire soon anyway.
        """
        # use the https://accounts.google.com/o/oauth2/revoke?token={refresh_token}
        # https://developers.google.com/identity/protocols/oauth2/web-server#tokenrevoke
        response = requests.post(
            'https://oauth2.googleapis.com/revoke',
            params={'token': refresh_token},
            headers={'content-type': 'application/x-www-form-urlencoded'}
        )

        if response.ok:
            return
        elif response.status_code == 400:
            if 'error' in response.json() and response.json()['error'] == 'invalid_token':
                raise InvalidRefreshToken()
        # TODO handle other cases and raise exceptions

    def create_user(self, id_token: str) -> UserInfo:
        user_info = self.token_service.validate_id_token(id_token, self.client_id)
        self.identity_provider_service.sign_up_user(user_info)

        return user_info

    def get_user_info(self, id_token: str) -> UserInfo:
        return self.token_service.validate_id_token(id_token, self.client_id)

    def refresh_access_token(self, refresh_token: str) -> AuthenticationState:
        token_endpoint = self.token_service.get_token_endpoint_from_well_known_url()
        response = requests.post(
            token_endpoint,
            data={
                "refresh_token": refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token"
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

        self.logger.warning(f'response = {response}')
        if response.ok:
            return AuthenticationState(
                access_token=response.json()['access_token'],
                refresh_token=response.json()['refresh_token'],
                id_token=response.json()['id_token']
            )

        raise InvalidRefreshToken('invalid refresh token')

    def ensure_user_exists(self, user_identifier: str):
        """
        :raises ResourceNotFoundException
        """
        raise NotImplementedError
