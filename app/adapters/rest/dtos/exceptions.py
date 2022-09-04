from pydantic import BaseModel, ValidationError
from starlette import status
from app.adapters.rest.dtos.authentication_data import AuthenticationDataDTO
from app.business_logic.exceptions import BusinessLogicException, ServerException, UnauthorizedException, \
    InvalidState, InvalidIdToken, InvalidRefreshToken, ResourceNotFoundException, BackendRepositoryException, \
    ResourceAlreadyExists, TimeoutException, IdentityProviderGenericException
import inspect

Exception_Error_Code_Mapping = {
    # Uncategorized Exceptions
    Exception: 3000,
    ValueError: 3001,
    ValidationError: 3002,

    # Unauthorized Exceptions
    UnauthorizedException: 4001,
    InvalidState: 4002,
    InvalidIdToken: 4003,
    InvalidRefreshToken: 4004,

    # Business Logic Exceptions
    BusinessLogicException: 4100,
    ResourceNotFoundException: 4101,
    ResourceAlreadyExists: 4102,

    # Server Exceptions
    ServerException: 5000,
    TimeoutException: 5001,
    BackendRepositoryException: 5003,
    IdentityProviderGenericException: 5004,
}


def get_error_code_for_exception(exception: Exception) -> int:
    if type(exception) == object:
        return -1

    if type(exception) in Exception_Error_Code_Mapping:
        return Exception_Error_Code_Mapping[type(exception)]

    next_class_in_mro = inspect.getmro(type(exception))[1]
    return get_error_code_for_exception(next_class_in_mro())


class ExceptionDTO(BaseModel):
    message: str
    error_code: int


class BusinessLogicExceptionDTO(ExceptionDTO):
    error_code: int = Exception_Error_Code_Mapping[BusinessLogicException]


class ServerExceptionDTO(ExceptionDTO):
    error_code: int = Exception_Error_Code_Mapping[ServerException]


def get_api_responses(response_types: list) -> dict:
    responses = {}

    if 200 in response_types:
        responses[status.HTTP_200_OK] = {"model": AuthenticationDataDTO, "description": "success"}
    if 400 in response_types:
        responses[status.HTTP_400_BAD_REQUEST] = {
            "model": BusinessLogicExceptionDTO,
            "description": "Business Logic Exception"
        }
    if 403 in response_types:
        responses[status.HTTP_403_FORBIDDEN] = {"description": "Action not allowed"}
    if 404 in response_types:
        responses[status.HTTP_404_NOT_FOUND] = {"model": BusinessLogicExceptionDTO}
    if 409 in response_types:
        responses[status.HTTP_409_CONFLICT] = {"model": BusinessLogicExceptionDTO}
    if 500 in response_types:
        responses[status.HTTP_500_INTERNAL_SERVER_ERROR] = {"model": ServerExceptionDTO}

    return responses
