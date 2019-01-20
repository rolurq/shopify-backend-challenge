from datetime import datetime, timedelta

import graphene
import jwt
from graphql import GraphQLError

from config.settings import SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_DAYS

from .inputs import *
from .types import *
from ..utils.database import Q

__all__ = ("Signup", "Login", "AddToCart", "RemoveFromCart")


class Signup(graphene.Mutation):
    """
    Graphql mutation for user registration

    Takes an UserInput with data to create the new user a
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
            user.id = users.insert(user.to_doc())

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

            user = User.from_doc(user)
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
    class Arguments:
        productId = graphene.ID(required=True)
        amount = graphene.Int(default_value=1)

    Output = graphene.NonNull(Cart)

    @staticmethod
    def mutate(root, info, productId: str, amount: int):
        pass


class RemoveFromCart(graphene.Mutation):
    class Arguments:
        productId = graphene.ID(required=True)
        amount = graphene.Int()

    Output = Cart

    @staticmethod
    def mutate(root, info, productId: str, amount: int):
        pass
