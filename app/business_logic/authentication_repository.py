from abc import ABC, abstractmethod
from app.business_logic.models.authentication import AuthenticationState


class AuthenticationRepository(ABC):
    @abstractmethod
    def create_authentication_state(self, state: str) -> AuthenticationState:
        """
        :raises BackendRepositoryException
        """
        raise NotImplementedError

    @abstractmethod
    def get_authentication_state(self, state: str) -> AuthenticationState:
        """
        :raises BackendRepositoryException
        :raises UnauthorizedException: when state is not found
        """
        raise NotImplementedError

    @abstractmethod
    def update_authentication_state(self, auth_state: AuthenticationState):
        """
        :raises BackendRepositoryException
        """
        raise NotImplementedError

    @abstractmethod
    def pop_authentication_state(self, state: str, refresh_token: str) -> AuthenticationState:
        """
        :raises BackendRepositoryException
        :raises UnauthorizedException: when no {state, refresh_token} pair is found
        """
        raise NotImplementedError
