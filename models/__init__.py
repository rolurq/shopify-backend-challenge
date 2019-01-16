import graphene

from .types import *
from .mutations import *


class Query(graphene.ObjectType):
    products = graphene.List(graphene.NonNull(Product), required=True)
    product = graphene.Field(Product, id=graphene.ID(required=True))
    cart = graphene.Field(Cart)
    user = graphene.Field(User)

    def resolve_products(self, info):
        return []

    def resolve_product(self, info, id: str):
        return None

    def resolve_user(self, info):
        return None


class Mutation(graphene.ObjectType):
    signup = Signup.Field()
    login = Login.Field()
    addToCart = AddToCart.Field()
    removeFromCart = RemoveFromCart.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
