from ninja import NinjaAPI, Schema
from ninja.responses import Response
from ninja.errors import ValidationError, AuthenticationError, Throttled
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from apps.common.exceptions import (
    ErrorCode,
    RequestError,
    request_errors,
    validation_errors,
)

from apps.accounts.views import auth_router, profiles_router
from apps.blog.views import blog_router
from apps.common.auth import AuthUser

api = NinjaAPI(
    title="QuickPost API",
    description="""
        QuickPost API powered by Django Ninja
    """,
    version="1.0.0",
    docs_url="/",
)

# Routes Registration
api.add_router("/api/v1/auth", auth_router)
api.add_router("/api/v1/profiles", profiles_router, auth=AuthUser())
api.add_router("/api/v1/blog", blog_router)


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


@api.exception_handler(Throttled)
def custom_throttled_handler(request, exc):
    retry_after = int(exc.wait) if exc.wait else 0

    response_data = {
        "status": "failure",
        "code": ErrorCode.RATE_LIMIT_EXCEEDED,
        "message": _(
            f"Rate limit exceeded. Please try again in {retry_after} seconds."
        ),
        "data": {
            "retry_after": retry_after,
        },
    }

    response = JsonResponse(response_data, status=429)
    response["Retry-After"] = str(retry_after)  # industry standard header
    return response
