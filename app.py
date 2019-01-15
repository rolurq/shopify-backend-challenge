import graphene
import uvicorn

from starlette.applications import Starlette
from starlette.graphql import GraphQLApp


class Query(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="stranger"))

    def resolve_hello(self, info, name):
        return "Hello " + name


app = Starlette()
app.add_route('/', GraphQLApp(schema=graphene.Schema(query=Query)))

