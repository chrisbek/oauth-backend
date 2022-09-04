from fastapi import APIRouter
from fastapi.exceptions import RequestValidationError
from starlette.responses import RedirectResponse
from app.config.config import Container

router = APIRouter()


@router.get("/auth")
def fake_authorization_grant_endpoint(response_type: str, client_id: str, scope: str, redirect_uri: str, state: str):
    Container.logger.error("fake_authorization_grant_endpoint invoked")
    desired_redirect_uris = [
        f"{Container.backend_url}auth/login_redirect",
        f"{Container.backend_url}auth/signup_redirect",
    ]
    if redirect_uri not in desired_redirect_uris:
        raise RequestValidationError(f"invalid redirect uri {redirect_uri}")

    code = "Yei4EiJ2aequaijahpookoo4"
    scope = "openid%20email%20https://www.googleapis.com/auth/userinfo.email"
    return RedirectResponse(f"{redirect_uri}?state={state}&code={code}&scope={scope}", 302)
