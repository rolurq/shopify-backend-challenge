import typing

import graphene
from tinydb.database import Document
from aiotinydb import AIOTinyDB
from starlette.authentication import BaseUser

from ..utils.password import hash_password, verify_password

__all__ = ("Product", "CartItem", "Cart", "User")


class TinyDbSerializale:
    async def from_doc(self, doc: Document, database: AIOTinyDB = None) -> typing.Any:
        raise NotImplementedError()

    async def to_doc(self) -> Document:
        raise NotImplementedError()


class Product(graphene.ObjectType, TinyDbSerializale):
    id = graphene.ID(required=True)
    title = graphene.String(required=True)
    price = graphene.Float(required=True)
    inventory_count = graphene.Int(required=True)

    async def to_doc(self) -> dict:
        return {
            "title": self.title,
            "price": self.price,
            "inventory_count": self.inventory_count,
        }

    @staticmethod
    async def from_doc(doc: Document) -> "Product":
        return Product(
            id=doc.doc_id,
            title=doc.get("title"),
            price=doc.get("price"),
            inventory_count=doc.get("inventory_count"),
        )


class CartItem(graphene.ObjectType, TinyDbSerializale):
    product = graphene.Field(Product, required=True)
    amount = graphene.Int(required=True, default_value=1)

    @staticmethod
    async def from_doc(doc: Document) -> "CartItem":
        return CartItem(
            product=Product.from_doc(doc.get("product")), amount=doc.get("amount")
        )

    async def to_doc(self) -> dict:
        return {"product": self.product.id, "amount": self.amount, "user": self.user_id}


class Cart(graphene.ObjectType, TinyDbSerializale):
class User(graphene.ObjectType, BaseUser, TinyDbSerializale):
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
    async def from_doc(doc: Document) -> "User":
        user = User(id=doc.doc_id, username=doc.get("username"))
        user.password_hash = doc.get("password_hash")
        return user

    async def to_doc(self) -> dict:
        return {"username": self.username, "password_hash": self.password_hash}

    @staticmethod
    def from_json(data: dict) -> "User":
        return User(**data)

    def to_json(self) -> dict:
        return {"username": self.username, "id": self.id}

