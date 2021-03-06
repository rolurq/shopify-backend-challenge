from starlette.applications import Starlette
from starlette.graphql import GraphQLApp
from starlette.middleware.authentication import AuthenticationMiddleware

from graphql.execution.executors.asyncio import AsyncioExecutor

from .models import schema
from .utils.authentication import JWTAuthenticationBackend
from config.settings import (
    DEBUG,
    DATABASE_URL,
    SECRET_KEY,
    JWT_ALGORITHM,
    DatabaseMiddleware,
)


app = Starlette()
app.debug = DEBUG
app.add_middleware(
    AuthenticationMiddleware,
    backend=JWTAuthenticationBackend(SECRET_KEY, JWT_ALGORITHM),
)
app.add_middleware(DatabaseMiddleware, database_url=DATABASE_URL)
app.add_route("/query", GraphQLApp(schema=schema, executor=AsyncioExecutor()))
