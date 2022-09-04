import jwt
import requests
from app.business_logic.models.authentication import UserInfo
from app.business_logic.token_service import TokenService


class LocalTokenService(TokenService):
    def validate_id_token(self, _id_token: str, client_id: str) -> UserInfo:
        payload = jwt.decode(_id_token, options={"verify_signature": False})
        return UserInfo(
            email=payload['email'],
            first_name=payload['name'],
            external_identifier=payload['sub']
        )

    def get_token_endpoint_from_well_known_url(self) -> str:
        response = requests.get(
            'https://authorization-server.local/auth/.well-known/openid-configuration', verify=False)
        if response.ok and 'token_endpoint' in response.json():
            return str(response.json()['token_endpoint'])

        return "https://authorization-server.local/auth/token"
