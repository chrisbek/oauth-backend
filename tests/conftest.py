from unittest.mock import patch
import pytest
from _pytest.monkeypatch import MonkeyPatch
from starlette.testclient import TestClient
from app.adapters.service_adapters.identity_provider_client import IdentityProviderClient
from app.business_logic.authentication_repository import AuthenticationRepository
from app.business_logic.authentication_service import AuthenticationService
from app.business_logic.token_service import TokenService
from tests.test_utils import TestUtils


@pytest.fixture(scope="session", autouse=True)
def monkeysession(request):
    monkeypatch = MonkeyPatch()
    monkeypatch.setenv('PLATFORM', TestUtils.PLATFORM)
    monkeypatch.setenv('STAGE', TestUtils.STAGE)
    monkeypatch.setenv('AUTH_TABLE', TestUtils.AUTH_TABLE)
    monkeypatch.setenv('BACKEND_URL', TestUtils.BACKEND_URL)
    monkeypatch.setenv('PRIVATE_KEY', TestUtils.PRIVATE_KEY)
    monkeypatch.setenv('AUTHENTICATION_ROUTE_PREFIX', TestUtils.AUTHENTICATION_ROUTE_PREFIX)
    monkeypatch.setenv('AUTHORIZATION_ROUTE_PREFIX', TestUtils.AUTHORIZATION_ROUTE_PREFIX)
    monkeypatch.setenv('CLIENT_ID', TestUtils.CLIENT_ID)
    monkeypatch.setenv('CLIENT_SECRET', TestUtils.CLIENT_SECRET)
    monkeypatch.setenv('ROLLBAR_TOKEN', TestUtils.ROLLBAR_TOKEN)
    monkeypatch.setenv('ROLLBAR_ENVIRONMENT', TestUtils.ROLLBAR_ENVIRONMENT)
    monkeypatch.setenv('ROLLBAR_ENABLED', TestUtils.ROLLBAR_ENABLED)
    monkeypatch.setenv('IDENTITY_PROVIDER_URL', TestUtils.IDENTITY_PROVIDER_URL)
    monkeypatch.setenv('IDENTITY_PROVIDER_TIMEOUT', TestUtils.IDENTITY_PROVIDER_TIMEOUT)
    monkeypatch.setenv('DYNAMODB_LOCAL_URL', TestUtils.DYNAMODB_LOCAL_URL)
    yield monkeypatch
    monkeypatch.undo()


@pytest.fixture(scope='function')
def container():
    from app.config.config import Container
    yield Container
    Container.backend_repository.reset_last_overriding()


@pytest.fixture(scope='function')
def client(container, backend_repository, identity_provider, token_service) -> TestClient:
    from app.config import on_startup
    app = on_startup.init()

    if container.backend_repository.overridden:
        container.backend_repository.reset_override()
    if container.identity_provider_service.overridden:
        container.identity_provider_service.reset_override()
    if container.token_service.overridden:
        container.token_service.reset_override()
    if container.auth_service.overridden:
        container.auth_service.reset_override()
    container.backend_repository.override(backend_repository)
    container.identity_provider_service.override(identity_provider)
    container.token_service.override(token_service)

    return TestClient(app, base_url=f'{container.backend_url}', root_path=f'/{container.stage}')


@pytest.fixture(scope="session")
@patch("app.business_logic.authentication_repository.AuthenticationRepository", spec_set=AuthenticationRepository)
def backend_repository(authentication_repository_mock) -> AuthenticationRepository:
    return authentication_repository_mock


@pytest.fixture(scope="session")
@patch("app.adapters.service_adapters.identity_provider_client.IdentityProviderClient", spec_set=IdentityProviderClient)
def identity_provider(identity_provider_mock) -> IdentityProviderClient:
    return identity_provider_mock


@pytest.fixture(scope="session")
@patch("app.business_logic.token_service.TokenService", spec_set=TokenService)
def token_service(token_service_mock) -> TokenService:
    return token_service_mock


@pytest.fixture(scope="session")
@patch("app.business_logic.authentication_service.AuthenticationService", spec_set=AuthenticationService)
def authentication_service(auth_service_mock) -> AuthenticationService:
    return auth_service_mock
