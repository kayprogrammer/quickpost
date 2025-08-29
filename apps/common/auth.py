from ninja.security import HttpBearer
from apps.accounts.auth import Authentication
from apps.common.exceptions import RequestError, ErrorCode


async def get_user(token):
    user = await Authentication.decodeAuthorization(token)
    if not user:
        raise RequestError(
            err_code=ErrorCode.INVALID_TOKEN,
            err_msg="Auth Token is Invalid or Expired!",
            status_code=401,
        )
    return user


class AuthUser(HttpBearer):
    async def authenticate(self, request, token):
        if not token:
            raise RequestError(
                err_code=ErrorCode.INVALID_AUTH,
                err_msg="Auth Bearer not provided!",
                status_code=401,
            )
        return await get_user(token)
