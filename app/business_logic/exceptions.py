class BusinessLogicException(Exception):
    pass


class ServerException(Exception):
    pass


class UnauthorizedException(Exception):
    pass


class BackendRepositoryException(ServerException):
    pass


class TimeoutException(ServerException):
    pass


class IdentityProviderGenericException(ServerException):
    pass


class InvalidState(UnauthorizedException):
    pass


class InvalidIdToken(UnauthorizedException):
    pass


class InvalidRefreshToken(UnauthorizedException):
    pass


class ResourceNotFoundException(BusinessLogicException):
    pass


class ResourceAlreadyExists(BusinessLogicException):
    pass
