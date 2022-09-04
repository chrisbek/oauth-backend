import logging
from logging import Logger, getLogger
import boto3
from dependency_injector import containers, providers
from app.adapters.service_adapters.identity_provider_client import IdentityProviderClient
from app.adapters.oauth.google_authentication_service import GoogleAuthenticationService
from app.adapters.oauth.google_token_service import GoogleTokenService
from app.adapters.oauth.local_authentication_service import LocalAuthenticationService
from app.adapters.oauth.local_token_service import LocalTokenService
from app.adapters.repositories.DynamoDBAdapter import DynamoDBRepository
from app.adapters.rest.auth_serializer import Serializer
from app.business_logic.authentication_repository import AuthenticationRepository
from app.business_logic.authentication_service import AuthenticationService
from app.business_logic.token_service import TokenService


def get_logger(log_level: str) -> Logger:
    logger = getLogger()
    logger.setLevel(log_level)
    return logger


def get_backend_repository(
        logger: Logger, platform_name: str, auth_table_name: str, dynamodb_local_url: str
) -> providers.Singleton[AuthenticationRepository]:
    def get_backend_repository_callback():
        if platform_name == 'local':
            dynamodb_client = boto3.resource('dynamodb',  endpoint_url=dynamodb_local_url)
        else:
            dynamodb_client = boto3.resource('dynamodb')

        auth_table = dynamodb_client.Table(auth_table_name)
        return auth_table

    return providers.Singleton(
        DynamoDBRepository,
        logger,
        get_backend_repository_callback
    )


def get_identity_provider_client(logger: Logger, identity_provider_url: str, identity_provider_timeout: int):
    return providers.Singleton(
        IdentityProviderClient,
        logger,
        identity_provider_url,
        identity_provider_timeout
    )


def get_token_service(platform_name: str) -> providers.Singleton[TokenService]:
    if platform_name == 'local':
        return providers.Singleton(LocalTokenService)

    return providers.Singleton(GoogleTokenService)


def get_serializer_service(backend_url: str, private_key: str, stage: str, authentication_route_prefix: str):
    return providers.Singleton(
        Serializer,
        backend_url,
        private_key,
        stage,
        authentication_route_prefix
    )


def get_redirect_uri_prefix(backend_url: str, authentication_route_prefix: str) -> str:
    """
    Returns a string like: https://{host}:{port}/{stage}/auth
    """
    return f"{backend_url}{authentication_route_prefix}"


def get_auth_service(
        logger,
        backend_repository,
        identity_provider_service,
        token_service,
        platform_name: str,
        client_id: str,
        client_secret: str,
        backend_url: str,
        authentication_route_prefix: str
) -> providers.Singleton[AuthenticationService]:
    if platform_name == 'local':
        return providers.Singleton(
            LocalAuthenticationService,
            platform_name,
            logger,
            client_id,
            client_secret,
            backend_repository,
            identity_provider_service,
            token_service,
            redirect_uri_prefix=get_redirect_uri_prefix(backend_url, authentication_route_prefix)
        )

    return providers.Singleton(
        GoogleAuthenticationService,
        platform_name,
        logger,
        client_id,
        client_secret,
        backend_repository,
        identity_provider_service,
        token_service,
        redirect_uri_prefix=get_redirect_uri_prefix(backend_url, authentication_route_prefix)
    )


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    config.platform_name.from_env("PLATFORM", as_=str, required=True)
    config.stage.from_env("STAGE", as_=str, required=True)
    config.auth_table.from_env("AUTH_TABLE", as_=str, required=True)
    config.backend_url.from_env("BACKEND_URL", as_=str, required=True)
    config.private_key.from_env("PRIVATE_KEY", as_=str, required=True)
    config.authentication_route_prefix.from_env("AUTHENTICATION_ROUTE_PREFIX", as_=str, required=True)
    config.authorization_route_prefix.from_env("AUTHORIZATION_ROUTE_PREFIX", as_=str, required=True)
    config.client_id.from_env("CLIENT_ID", as_=str, required=True)
    config.client_secret.from_env("CLIENT_SECRET", as_=str, required=True)
    config.log_level.from_env("LOG_LEVEL", default=logging.ERROR)
    config.rollbar_token.from_env("ROLLBAR_TOKEN", as_=str, required=True)
    config.rollbar_env.from_env("ROLLBAR_ENVIRONMENT", as_=str, required=True)
    config.rollbar_enabled.from_env("ROLLBAR_ENABLED", as_=bool, required=True)
    config.identity_provider_url.from_env("IDENTITY_PROVIDER_URL", as_=str, required=True)
    config.identity_provider_timeout.from_env("IDENTITY_PROVIDER_TIMEOUT", as_=int, required=True)
    config.dynamodb_local_url.from_env("DYNAMODB_LOCAL_URL", as_=str, required=False, default=None)

    platform_name = config.platform_name()
    stage = config.stage()
    auth_table = config.auth_table()
    backend_url = config.backend_url()
    private_key = config.private_key()
    authentication_route_prefix = config.authentication_route_prefix()
    authorization_route_prefix = config.authorization_route_prefix()
    client_id = config.client_id()
    client_secret = config.client_secret()
    log_level = config.log_level()
    rollbar_token = config.rollbar_token()
    rollbar_env = config.rollbar_env()
    rollbar_enabled = config.rollbar_enabled()
    identity_provider_url = config.identity_provider_url()
    identity_provider_timeout = config.identity_provider_timeout()
    dynamodb_local_url = config.dynamodb_local_url()

    logger = get_logger(log_level)
    backend_repository = get_backend_repository(logger, platform_name, auth_table, dynamodb_local_url)
    identity_provider_service = get_identity_provider_client(logger, identity_provider_url, identity_provider_timeout)
    token_service = get_token_service(platform_name)
    serializer = get_serializer_service(backend_url, private_key, stage, authentication_route_prefix)
    auth_service = get_auth_service(
        logger,
        backend_repository,
        identity_provider_service,
        token_service,
        platform_name,
        client_id,
        client_secret,
        backend_url,
        authentication_route_prefix
    )
