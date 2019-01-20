import asyncio
import functools
import typing

import jwt
from graphql import GraphQLError
from starlette.authentication import (
    AuthenticationBackend,
    AuthenticationError,
    AuthCredentials,
    UnauthenticatedUser,
    has_required_scope,
)

from ..models import User


def requires(
    scopes: typing.Union[str, typing.Sequence[str]],
    message: str = "you must be logged in",
) -> typing.Callable:
    """
    Decorator to ensure scope existence for a resolver method. Works similar
    to the one provided in the authentication module of starlette but works
    with graphql (request is not a paremeter, it's inside a context value)

    :param scopes: scope name or list of scope names to check
    :param message: optional error message to show when the scopes are not present
    """
    scopes = [scopes] if isinstance(scopes, str) else list(scopes)

    def decorator(func: typing.Callable) -> typing.Callable:
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
                info = kwargs.get("info", args[1])
                request = info.context.get("request")

                if not has_required_scope(request, scopes):
                    raise GraphQLError(message)
                return await func(*args, **kwargs)

            return wrapper

        @functools.wraps(func)
        def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            info = kwargs.get("info", args[1])
            request = info.context.get("request")

            if not has_required_scope(request, scopes):
                raise GraphQLError(message)
            return func(*args, **kwargs)

        return wrapper

    return decorator


class JWTAuthenticationBackend(AuthenticationBackend):
    """
    Authentication backend that uses JWT as authentication tokens
    """

    def __init__(self, secret_key: str, algorithm: str, prefix: str = "Bearer"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.prefix = prefix

    @classmethod
    def get_token_from_header(cls, authorization: str, prefix: str) -> str:
        """
        Parses the Authorization header and returns only the token

        :param authorization str: Value of the authorization header
        :param prefix str: Token prefix in the header
        :return: The token value
        :rtype str:
        :raises AuthenticationError: If prefix in header doesn't match `prefix` or
        if header value doesn't follow the `<prefix> <token>` pattern
        """
        try:
            scheme, token = authorization.split()
        except ValueError:
            raise AuthenticationError("incorrect authorization header format")
        if scheme.lower() != prefix.lower():
            raise AuthenticationError(f"authorization scheme {scheme} is not supported")
        return token

    async def authenticate(self, request):
        if "Authorization" not in request.headers:
            return

        auth = request.headers["Authorization"]
        token = self.get_token_from_header(authorization=auth, prefix=self.prefix)
        try:
            payload = jwt.decode(
                token, key=self.secret_key, algorithms=(self.algorithm,)
            )
        except jwt.PyJWTError as e:
            raise AuthenticationError(str(e))

        # removes 'exp' key to create user object only with relevant data
        del payload["exp"]
        return (AuthCredentials(["authenticated"]), User.from_json(payload))
