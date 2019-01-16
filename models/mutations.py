import graphene

from .types import *
from .inputs import *

__all__ = ('Signup', 'Login', 'AddToCart', 'RemoveFromCart')


class Signup(graphene.Mutation):
    class Arguments:
        input = UserInput(required=True)

    Output = graphene.NonNull(User)

    @staticmethod
    def mutate(root, info, input):
        pass

class Login(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    Output = User

    @staticmethod
    def mutate(root, info, username, password):
        pass

class AddToCart(graphene.Mutation):
    class Arguments:
        productId = graphene.ID(required=True)
        amount = graphene.Int(default_value=1)

    Output = graphene.NonNull(Cart)

    @staticmethod
    def mutate(root, info, productId, amount):
        pass

class RemoveFromCart(graphene.Mutation):
    class Arguments:
        productId = graphene.ID(required=True)
        amount = graphene.Int()

    Output = Cart

    @staticmethod
    def mutate(root, info, productId, amount):
        pass
