from abc import ABC, abstractmethod
from app.business_logic.models.authentication import UserInfo


class TokenService(ABC):
    @abstractmethod
    def validate_id_token(self, _id_token: str, client_id: str) -> UserInfo:
        """
        :raises InvalidIdToken
        """
        raise NotImplementedError

    def get_token_endpoint_from_well_known_url(self) -> str:
        raise NotImplementedError
