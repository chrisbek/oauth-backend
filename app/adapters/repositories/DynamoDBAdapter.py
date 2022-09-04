from app.business_logic.exceptions import BackendRepositoryException, UnauthorizedException, InvalidState
from app.business_logic.authentication_repository import AuthenticationRepository
from app.business_logic.models.authentication import AuthenticationState
from logging import Logger
from botocore.exceptions import ClientError


class DynamoDBRepository(AuthenticationRepository):

    def __init__(
            self,
            logger: Logger,
            get_repository_callback
    ):
        self.logger = logger
        self.auth_table = get_repository_callback()

    def create_authentication_state(self, state: str) -> AuthenticationState:
        try:
            self.auth_table.put_item(
                Item={
                    'State': state
                }
            )
        except ClientError as e:
            raise BackendRepositoryException(f'Cannot create state: {str(e)}')

        return AuthenticationState(state=state)

    def get_authentication_state(self, state: str) -> AuthenticationState:
        fetch_only_fields = ['#state_reserved_word']
        try:
            response = self.auth_table.get_item(
                Key={'State': state},
                ProjectionExpression=', '.join(fetch_only_fields),
                ExpressionAttributeNames={'#state_reserved_word': 'State'}
            )
        except ClientError as e:
            raise BackendRepositoryException(f'Cannot fetch state: {str(e)}')

        if 'Item' in response and response['Item']:
            return AuthenticationState(state=response['Item']['State'])
        else:
            raise InvalidState('invalid state')

    def update_authentication_state(self, auth_state: AuthenticationState):
        try:
            self.auth_table.update_item(
                Key={'State': auth_state.state},
                UpdateExpression="set AccessToken= :access_token, RefreshToken= :refresh_token, IdToken= :id_token",
                ExpressionAttributeValues={
                    ':access_token': auth_state.access_token,
                    ':refresh_token': auth_state.refresh_token,
                    ':id_token': auth_state.id_token,
                },
            )
        except ClientError as e:
            raise BackendRepositoryException(f'Could not update authentication data: {str(e)}')

    def pop_authentication_state(self, state: str, refresh_token: str) -> AuthenticationState:
        try:
            # fetch_only_fields = ['AccessToken', 'IdToken']
            response = self.auth_table.delete_item(
                Key={'State': state},
                ConditionExpression="RefreshToken= :refresh_token",
                # ProjectionExpression=', '.join(fetch_only_fields),
                ReturnValues="ALL_OLD",
                ExpressionAttributeValues={
                    ":refresh_token": refresh_token
                },
            )
        except ClientError as e:
            if e.response['Error']['Code'] == "ConditionalCheckFailedException":
                raise UnauthorizedException(f'No data found for state: {state}, refresh_token: {refresh_token}')
            else:
                raise BackendRepositoryException(
                    f'Delete failed access_token for: {state}, refresh_token: {refresh_token}')

        return AuthenticationState(
            state=state,
            refresh_token=refresh_token,
            access_token=response['Attributes']['AccessToken'],
            id_token=response['Attributes']['IdToken']
        )
