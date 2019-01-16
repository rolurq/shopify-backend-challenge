import graphene

class Product(graphene.ObjectType):
    id = graphene.ID(required=True)
    title = graphene.String(required=True)
    price = graphene.Float(required=True)
    inventory_count = graphene.Int(required=True)

class CartProduct(graphene.ObjectType):
    product = graphene.Field(Product, required=True)
    amount = graphene.Int(required=True, default_value=1)

class Cart(graphene.ObjectType):
    products = graphene.List(graphene.NonNull(CartProduct), required=True)
    price = graphene.Float(required=True)

class User(graphene.ObjectType):
    id = graphene.ID(required=True)
    username = graphene.String(required=True)
    jwt = graphene.String()
