from google.oauth2 import id_token
from google.auth.transport import requests
from app.business_logic.exceptions import InvalidIdToken
from app.business_logic.models.authentication import UserInfo
from app.business_logic.token_service import TokenService
import requests


class GoogleTokenService(TokenService):
    def validate_id_token(self, _id_token: str, client_id: str) -> UserInfo:
        """
        https://developers.google.com/identity/protocols/oauth2/openid-connect#obtainuserinfo :
        An identifier for the user, unique among all Google accounts and never reused.
        A Google account can have multiple email addresses at different points in time,
        but the sub value is never changed.
        Use sub within your application as the unique-identifier key for the user.
        Maximum length of 255 case-sensitive ASCII characters.
        """
        payload = id_token.verify_token(_id_token, requests.Request(), client_id)
        if 'email' not in payload or 'name' not in payload:
            raise InvalidIdToken(f'Id token without credentials: {payload}')

        return UserInfo(
            email=payload['email'],
            first_name=payload['name'],
            external_identifier=payload['sub']
        )

    def get_token_endpoint_from_well_known_url(self) -> str:
        # TODO: Cache the response. In order to do so you should respect the cache control headers
        #   returned as response
        response = requests.get('https://accounts.google.com/.well-known/openid-configuration')
        if response.ok and 'token_endpoint' in response.json():
            return str(response.json()['token_endpoint'])

        return "https://oauth2.googleapis.com/token"
