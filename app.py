from starlette.applications import Starlette
from starlette.graphql import GraphQLApp

from graphql.execution.executors.asyncio import AsyncioExecutor

from models import schema
from config.settings import DEBUG, DATABASE_URL, DatabaseMiddleware


app = Starlette()
app.debug = DEBUG
app.add_middleware(DatabaseMiddleware, database_url=DATABASE_URL)
app.add_route("/query", GraphQLApp(schema=schema, executor=AsyncioExecutor()))
