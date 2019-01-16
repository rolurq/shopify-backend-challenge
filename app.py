from starlette.applications import Starlette
from starlette.config import Config
from starlette.graphql import GraphQLApp
from starlette.datastructures import DatabaseURL

from graphql.execution.executors.asyncio import AsyncioExecutor

from models import schema
from utils.database import TinyDbMiddleware as DatabaseMiddleware

config = Config(".env")
DEBUG = config("DEBUG", cast=bool, default=False)
TESTING = config("TESTING", cast=bool, default=False)

DATABASE_URL = config("DATABASE_URL", cast=DatabaseURL)
if TESTING:
    DATABASE_URL = DATABASE_URL.replace(database="test_" + DATABASE_URL.database)

if DATABASE_URL.dialect != "tinydb":
    # use starlette default database middleware when not using tinydb
    # intended to make project work in a environment with a real database
    from starlette.middleware.database import DatabaseMiddleware

app = Starlette()
app.debug = DEBUG
app.add_middleware(DatabaseMiddleware, database_url=DATABASE_URL)
app.add_route("/query", GraphQLApp(schema=schema, executor=AsyncioExecutor()))
