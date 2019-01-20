import jwt
from starlette.authentication import (
    AuthenticationBackend,
    AuthenticationError,
    AuthCredentials,
    UnauthenticatedUser,
)

from ..models import User


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
