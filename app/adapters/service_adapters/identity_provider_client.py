import json
from logging import Logger
from typing import Optional
from identity_provider_rest_client import Configuration, ApiClient, ApiException
from identity_provider_rest_client.Api import default_api
from identity_provider_rest_client.model.user_out_dto import UserOutDTO
from identity_provider_rest_client.model.user_in_dto import UserInDTO
from urllib3.exceptions import MaxRetryError
from app.business_logic.exceptions import TimeoutException, IdentityProviderGenericException, \
    ResourceNotFoundException, ResourceAlreadyExists
from app.business_logic.models.authentication import UserInfo


class IdentityProviderClient:
    def __init__(self, logger: Logger, identity_provider_url: str, identity_provider_timeout: int):
        self.logger = logger
        configuration = Configuration(
            host=identity_provider_url,
        )
        configuration.retries = 1  # IMPORTANT: if we don't set this HERE, the urllib3 will retry upon a timeout
        client = ApiClient(configuration)
        self.identity_api = default_api.DefaultApi(client)
        self.timeout_in_seconds = identity_provider_timeout

    @staticmethod
    def _handle_identity_provider_error(e: ApiException):
        if e.status == 502:
            raise IdentityProviderGenericException("Account service is unavailable")

        raise IdentityProviderGenericException(f"{e.status}: {e.reason}")

    def _handle_exception(self, e: Exception):
        """
        :raises ResourceNotFoundException
        :raises ResourceAlreadyExists
        :raises IdentityProviderGenericException
        """
        if isinstance(e, MaxRetryError):
            raise TimeoutException('Account service timeout')

        if isinstance(e, ApiException):
            if e.status >= 500:
                self._handle_identity_provider_error(e)

            response = json.loads(e.body)
            if e.status == 404:
                raise ResourceNotFoundException(response.get('message'))
            elif e.status == 409:
                raise ResourceAlreadyExists('Validation of billing info failed')
            else:
                raise IdentityProviderGenericException(response.get('message'))

        raise IdentityProviderGenericException(str(e))

    def get_user(self, external_identifier: str) -> Optional[UserOutDTO]:
        try:
            user: UserOutDTO = self.identity_api.get_user_user_external_identifier_get(external_identifier)
            return user
        except ApiException as e:
            return None

    def _create_tcp_user(self, external_identifier: str, user_dto: UserInDTO) -> UserOutDTO:
        """
        :raises ResourceAlreadyExists
        :raises IdentityProviderGenericException
        """
        try:
            return self.identity_api.post_user_user_external_identifier_post(external_identifier, user_dto)
        except ApiException as e:
            self._handle_exception(e)

    def sign_up_user(self, user_info: UserInfo):
        """
        :raises ResourceAlreadyExists
        :raises IdentityProviderGenericException
        """
        user_dto = UserInDTO(
            email_address=user_info.email,
            first_name=user_info.first_name
        )
        self._create_tcp_user(user_info.external_identifier, user_dto)
