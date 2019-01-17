import graphene


class UserInput(graphene.InputObjectType):
    """
    Input data to register an user
    """

    username = graphene.String(required=True)
    password = graphene.String(required=True)
