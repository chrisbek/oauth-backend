from pydantic import BaseModel, Field


class AccessTokenDTO(BaseModel):
    access_token: str = Field(...)

    @staticmethod
    def get_dto(access_token: str) -> 'AccessTokenDTO':
        return AccessTokenDTO(access_token=access_token)
