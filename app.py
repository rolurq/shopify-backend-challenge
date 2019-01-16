from starlette.applications import Starlette
from starlette.graphql import GraphQLApp

from graphql.execution.executors.asyncio import AsyncioExecutor

from models import schema


app = Starlette()
app.add_route('/query', GraphQLApp(schema=schema, executor=AsyncioExecutor()))
