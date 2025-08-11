from ninja import NinjaAPI, Schema
from apps.common.exceptions import RequestError, request_errors, ErrorCode

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
