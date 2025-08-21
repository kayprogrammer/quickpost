from ninja import NinjaAPI, Schema
from ninja.responses import Response
from ninja.errors import ValidationError, AuthenticationError
from apps.common.exceptions import (
    ErrorCode,
    RequestError,
    request_errors,
    validation_errors,
)

from apps.accounts.views import auth_router, profiles_router
from apps.blog.views import blog_router
from apps.common.utils import AuthUser

api = NinjaAPI(
    title="QuickPost API",
    description="""
        QuickPost API powered by Django Ninja
    """,
    version="1.0.0",
    docs_url="/",
)


class HealthCheckResponse(Schema):
    message: str


@api.get("/api/v1/healthcheck/", response=HealthCheckResponse, tags=["HealthCheck"])
async def healthcheck(request):
    return {"message": "pong"}


@api.exception_handler(RequestError)
def request_exc_handler(request, exc):
    return request_errors(exc)


@api.exception_handler(ValidationError)
def validation_exc_handler(request, exc):
    return validation_errors(exc)


@api.exception_handler(AuthenticationError)
def request_exc_handler(request, exc):
    return Response(
        {
            "status": "failure",
            "code": ErrorCode.INVALID_AUTH,
            "message": "Unauthorized User",
        },
        status=401,
    )


# Routes Registration
api.add_router("/api/v1/auth/", auth_router)
api.add_router("/api/v1/profiles", profiles_router, auth=AuthUser())
api.add_router("/api/v1/blog/", blog_router)
