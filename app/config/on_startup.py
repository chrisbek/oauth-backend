from app.adapters.rest.dtos.exceptions import get_api_responses
from app.adapters.rest.auth_controller import router as auth_router
from app.adapters.rest.auth_server_mock import router as auth_server
from app.adapters.rest.exception_serializer import add_exception_handlers_to_app
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
import rollbar
from app.config.config import Container
from fastapi import APIRouter

# test_router = APIRouter()


def init() -> FastAPI:
    rollbar.init(
        access_token=Container.rollbar_token,
        environment=Container.rollbar_env,
        enabled=Container.rollbar_enabled
    )

    app = FastAPI(
        title="TCP Auth Backend",
        description='Serves the TCP Frontend',
        root_path=f'/{Container.stage}',
    )
    # Mount order matters
    app.include_router(
        auth_router,
        prefix=f"/{Container.authentication_route_prefix}",
        responses=get_api_responses([200, 400, 403, 404, 409, 500])
    )
    app.include_router(
        auth_server,
        prefix=f"/{Container.authorization_route_prefix}",
        responses=get_api_responses([200, 400, 403, 404, 409, 500])
    )
    # app.include_router(
    #     test_router,
    #     prefix=f"/test"
    # )
    # app.mount(
    #     "",
    #     StaticFiles(directory="./dist", html=True),
    #     name="static"
    # )
    add_exception_handlers_to_app(app)
    return app
