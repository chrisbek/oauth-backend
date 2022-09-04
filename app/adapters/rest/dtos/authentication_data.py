from pydantic import BaseModel, validator
from uuid import UUID
from app.business_logic.exceptions import InvalidState


class AuthenticationDataDTO(BaseModel):
    state: str

    @validator('state', pre=True)
    def state_validations(cls, v):
        """
        Ensures that state is a string containing a valid uuid
        :raises InvalidState
        """
        if not v:
            raise InvalidState

        if not isinstance(v, str):
            raise InvalidState

        try:
            UUID(v)
        except ValueError:
            raise InvalidState

        return v
