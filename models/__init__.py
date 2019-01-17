import graphene

from .types import *
from .mutations import *
from utils.database import Q


class Query(graphene.ObjectType):
    products = graphene.List(graphene.NonNull(Product), required=True)
    product = graphene.Field(Product, id=graphene.ID(required=True))
    cart = graphene.Field(Cart)
    user = graphene.Field(User)

    async def resolve_products(self, info):
        request = info.context.get("request")
        async with request.database as db:
            products = db.table("products")

            return [
                Product.from_doc(doc) for doc in products.search(Q.inventory_count > 0)
            ]

    async def resolve_product(self, info, id: str):
        request = info.context.get("request")
        async with request.database as db:
            products = db.table("products")

            product = products.get(doc_id=id)
            if not product:
                return None

        return Product.from_doc(product)

    def resolve_user(self, info):
        return None


class Mutation(graphene.ObjectType):
    signup = Signup.Field()
    login = Login.Field()
    addToCart = AddToCart.Field()
    removeFromCart = RemoveFromCart.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
