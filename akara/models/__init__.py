import graphene
from graphql import GraphQLError

from .types import *
from .mutations import *
from ..utils.database import Q
from ..utils.authentication import requires


class Query(graphene.ObjectType):
    products = graphene.List(
        graphene.NonNull(Product),
        required=True,
        available=graphene.Boolean(default_value=False),
    )
    product = graphene.Field(Product, id=graphene.ID(required=True))
    cart = graphene.Field(Cart)
    user = graphene.Field(User)

    async def resolve_products(_, info, available: bool):
        """
        Obtain the list of all products

        :param available bool: flag indicating if unavailable products should be
        excluded from results
        """
        request = info.context.get("request")
        async with request.database as db:
            products = db.table("products").search(
                Q.inventory_count > 0 if available else Q
            )

        return [await Product.from_doc(doc) for doc in products]

    async def resolve_product(self, info, id: str):
        """
        Obtain a single product info using its id

        :param id str: id of the product to query
        """
        request = info.context.get("request")
        async with request.database as db:
            products = db.table("products")

            product = products.get(doc_id=id)
            if not product:
                return None

        return await Product.from_doc(product)

    @requires("authenticated", message="you must be logged in to access the cart")
    async def resolve_cart(self, info):
        """
        Obtain the current status of the shopping cart
        """
        request = info.context.get("request")
        user = request.user
        async with request.database as db:
            cart_items = db.table("cart_items")

            cart = cart_items.search(Q.user == user.id)
            if not cart:
                return None

        return await Cart.from_doc(cart, request.database)

    @requires("authenticated", message="you must be loged in to access your user data")
    async def resolve_user(self, info):
        """
        Obtain the current logged in user data
        """
        request = info.context.get("request")
        return request.user


class Mutation(graphene.ObjectType):
    signup = Signup.Field()
    login = Login.Field()
    addToCart = AddToCart.Field()
    removeFromCart = RemoveFromCart.Field()
    completeCart = CompleteCart.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
