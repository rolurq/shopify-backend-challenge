from datetime import datetime, timedelta

import graphene
import jwt
from graphql import GraphQLError

from config.settings import SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_DAYS

from .inputs import *
from .types import *
from ..utils.database import Q
from ..utils.authentication import requires

__all__ = ("Signup", "Login", "AddToCart", "RemoveFromCart", "CompleteCart")


class Signup(graphene.Mutation):
    """
    Graphql mutation for user registration

    :param input UserInput: an object with the neccessary data to create a new user
    :returns: the JWT that the user must use in upcoming requests
    """

    class Arguments:
        input = UserInput(required=True)

    token = graphene.String()

    @staticmethod
    async def mutate(root, info, input: UserInput) -> "Signup":
        user = User(username=input.username)

        request = info.context["request"]
        async with request.database as db:
            users = db.table("users")

            if users.get(Q.username == user.username):
                raise GraphQLError("username is alredy taken")

            user.set_password(input.password)
            user.id = users.insert(await user.to_doc())

        return Signup(
            token=jwt.encode(
                {
                    **user.to_json(),
                    "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS),
                },
                key=SECRET_KEY,
                algorithm=JWT_ALGORITHM,
            ).decode()
        )


class Login(graphene.Mutation):
    """
    Mutation for user login

    :param username str:
    :param password str:
    :returns: the JWT that the user must use in upcoming requests
    """

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    token = graphene.String()

    @staticmethod
    async def mutate(root, info, username: str, password: str) -> "Login":
        request = info.context["request"]

        async with request.database as db:
            users = db.table("users")

            user = users.get(Q.username == username)
            if not user:
                raise GraphQLError("user does not exist")

            user = await User.from_doc(user)
            if not user.check_password(password):
                raise GraphQLError("incorrect password")

        return Login(
            token=jwt.encode(
                {
                    **user.to_json(),
                    "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS),
                },
                key=SECRET_KEY,
                algorithm=JWT_ALGORITHM,
            ).decode()
        )


class AddToCart(graphene.Mutation):
    """
    Mutation to add item to shopping cart

    :param productId str: id of the product to add
    :param amount int: amount of the product to add, defaults to 1
    :return: the current state of the cart
    """

    class Arguments:
        productId = graphene.ID(required=True)
        amount = graphene.Int(default_value=1)

    Output = graphene.NonNull(Cart)

    @staticmethod
    @requires("authenticated", message="you must be logged in to access the cart")
    async def mutate(root, info, productId: str, amount: int):
        request = info.context["request"]
        user = request.user

        async with request.database as db:
            products = db.table("products")
            cart_items = db.table("cart_items")

            product = products.get(doc_id=productId)
            if not product:
                raise GraphQLError("product does not exists")

            product = await Product.from_doc(product)

            # get the cart item, there must be only one, given that the convination of user
            # and product is used both for queryng and storing
            item = cart_items.get((Q.user == user.id) & (Q.product == productId))
            current_order = 0
            if item:
                current_order = item.get("amount")

            if product.inventory_count < amount + current_order:
                raise GraphQLError(
                    "there's not enougth availability to fullfil your order"
                )

            if not item:
                item = CartItem(product=product, amount=amount)
                item.user_id = user.id
                cart_items.insert(await item.to_doc())
            else:
                item["amount"] += amount
                cart_items.write_back([item])

            # the cart is the list of cart items associated to a user
            # there's not explicit model for the cart in the storage
            cart = cart_items.search(Q.user == user.id)

        return await Cart.from_doc(cart, request.database)


class RemoveFromCart(graphene.Mutation):
    """
    Mutation to remove an item, or an amount of that item, from the shopping cart

    :param productId str: id of the product to remove or reduce
    :param amount int: amount of the product to reduce, if not present, removes product
    completely
    :return: the current state of the cart
    """

    class Arguments:
        productId = graphene.ID(required=True)
        amount = graphene.Int()

    Output = Cart

    @staticmethod
    @requires("authenticated", message="you must be logged in to access the cart")
    async def mutate(root, info, productId: str, amount: int = None):
        request = info.context["request"]
        user = request.user

        async with request.database as db:
            products = db.table("products")
            cart_items = db.table("cart_items")

            product = products.get(doc_id=productId)
            if not product:
                raise GraphQLError("product does not exists")

            product = await Product.from_doc(product)

            item = cart_items.get((Q.user == user.id) & (Q.product == productId))

            if not item:
                raise GraphQLError("cannot remove item from empty cart")

            current_order = item.get("amount")
            if not amount or current_order == amount:
                cart_items.remove(doc_ids=[item.doc_id])
            else:
                if current_order < amount:
                    raise GraphQLError("cannot remove more items than where added")

                item["amount"] -= amount
                cart_items.write_back([item])

            # the cart is the list of cart items associated to a user
            # there's not explicit model for the cart in the storage
            cart = cart_items.search(Q.user == user.id)

        if not cart:
            return None
        return await Cart.from_doc(cart, request.database)


class CompleteCart(graphene.Mutation):
    """
    Mutation to submit the current cart

    :return: the charged amount and a flag indicating success or not
    """

    charged = graphene.Float(required=True)
    # to control if charge was applied correctly, right now will always be True
    success = graphene.Boolean(required=True)

    @staticmethod
    @requires("authenticated", message="you must be logged in to buy")
    async def mutate(root, info):
        request = info.context["request"]
        user = request.user

        async with request.database as db:
            products = db.table("products")
            cart_items = db.table("cart_items")

            cart = cart_items.search(Q.user == user.id)
            if not cart:
                raise GraphQLError("cart is empty")

            # store total charged value
            charged = 0
            # store modified products and their ids in order to execute a batch update later
            bought_products_ids = []
            bought_products = []
            for item in cart:
                product = products.get(doc_id=item.get("product"))

                amount = item.get("amount")
                product["inventory_count"] -= amount
                charged += product.get("price") * amount

                bought_products_ids.append(product.doc_id)
                bought_products.append(product)

            # make batch update of bought products
            products.write_back(bought_products, doc_ids=bought_products_ids)
            # clear the cart
            cart_items.remove(doc_ids=[item.doc_id for item in cart])

        return CompleteCart(success=True, charged=charged)
