from abc import ABC, abstractmethod
from app.business_logic.models.authentication import AuthenticationState, UserInfo


class AuthenticationService(ABC):
    @abstractmethod
    def create_state(self) -> str:
        """
        :raises BackendRepositoryException
        """
        raise NotImplementedError

    @abstractmethod
    def validate_state(self, state: str):
        """
        :raises InvalidState
        """
        raise NotImplementedError

    @abstractmethod
    def exchange_code_for_token(self, state: str, code: str, endpoint_uri: str) -> AuthenticationState:
        """
        If the redirect URI was included in the initial authorization request,
        the service must require it in the token request as well.
        The redirect URI in the token request must be an exact match of the redirect URI that was used when generating
        the authorization code. The service must reject the request otherwise.

        :raises InvalidState
        :raises UnauthorizedException
        """
        raise NotImplementedError

    @abstractmethod
    def temporarily_store_auth_state(self, auth_state: AuthenticationState):
        """
        :raises BackendRepositoryException
        """
        raise NotImplementedError

    def get_temporarily_stored_access_token(self, state: str, refresh_token: str) -> AuthenticationState:
        """
        :raises BackendRepositoryException
        :raises UnauthorizedException: when no {state, refresh_token} pair is found
        """
        raise NotImplementedError

    def revoke_refresh_token(self, refresh_token: str):
        """
        :raises InvalidRefreshToken
        """
        raise NotImplementedError

    def create_user(self, id_token: str) -> UserInfo:
        """
        :raises InvalidIdToken
        :raises ResourceAlreadyExists
        :raises IdentityProviderGenericException
        """
        raise NotImplementedError

    def get_user_info(self, id_token: str) -> UserInfo:
        """
        :raises InvalidIdToken
        """
        raise NotImplementedError

    def refresh_access_token(self, refresh_token: str) -> AuthenticationState:
        """
        :raises InvalidRefreshToken
        """
        raise NotImplementedError

    def ensure_user_exists(self, user_identifier: str):
        """
        :raises ResourceNotFoundException
        """
        raise NotImplementedError
