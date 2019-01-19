import graphene
from tinydb.database import Document
from starlette.authentication import BaseUser

from ..utils.password import hash_password, verify_password

__all__ = ("Product", "CartProduct", "Cart", "User")


class Product(graphene.ObjectType):
    id = graphene.ID(required=True)
    title = graphene.String(required=True)
    price = graphene.Float(required=True)
    inventory_count = graphene.Int(required=True)

    def to_doc(self) -> dict:
        return {
            "title": self.title,
            "price": self.price,
            "inventory_count": self.inventory_count,
        }

    @staticmethod
    def from_doc(doc: Document) -> "Product":
        return Product(
            id=doc.doc_id,
            title=doc.get("title"),
            price=doc.get("price"),
            inventory_count=doc.get("inventory_count"),
        )


class CartProduct(graphene.ObjectType):
    product = graphene.Field(Product, required=True)
    amount = graphene.Int(required=True, default_value=1)


class Cart(graphene.ObjectType):
    products = graphene.List(graphene.NonNull(CartProduct), required=True)
    price = graphene.Float(required=True)


class User(graphene.ObjectType, BaseUser):
    id = graphene.ID(required=True)
    username = graphene.String(required=True)

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.username

    def set_password(self, password: str) -> None:
        self.password_hash = hash_password(password)

    def check_password(self, password: str) -> bool:
        return verify_password(password, self.password_hash)

    @staticmethod
    def from_doc(doc: Document) -> "User":
        user = User(id=doc.doc_id, username=doc.get("username"))
        user.password_hash = doc.get("password_hash")
        return user

    def to_doc(self) -> dict:
        return {"username": self.username, "password_hash": self.password_hash}

    @staticmethod
    def from_json(data: dict) -> "User":
        return User(**data)

    def to_json(self) -> dict:
        return {"username": self.username, "id": self.id}

