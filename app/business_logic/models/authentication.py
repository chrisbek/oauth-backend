from typing import Optional
from pydantic import BaseModel


class AuthenticationState(BaseModel):
    state: Optional[str] = None
    refresh_token: Optional[str] = None
    access_token: Optional[str] = None
    id_token: Optional[str] = None


class UserInfo(BaseModel):
    email: str
    first_name: str
    external_identifier: str
