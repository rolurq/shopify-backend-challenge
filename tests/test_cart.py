import pytest
import typing
from tinydb.database import Document

from .conftest import StarletteGraphQlClient
from .test_users import initial_user


@pytest.fixture
def user_jwt(initial_user, client: StarletteGraphQlClient):
    response = client.execute(
        """
        mutation($username: String!, $password: String!) {
            login(username: $username, password: $password) {
                token
            }
        }
        """,
        variables={"username": initial_user.username, "password": "T3st_"},
    )
    yield response.get("data").get("login").get("token")


@pytest.fixture
def insert_product(test_database):
    products = test_database("products")

    def _make_product(**kwargs):
        return products.insert(kwargs)

    yield _make_product
    products.purge()


def test_cart_access_no_auth(client: StarletteGraphQlClient):
    response = client.execute("{ cart { price } }")
    assert response.get("data") == {"cart": None}
    assert (
        response.get("errors")[0].get("message")
        == "you must be logged in to access the cart"
    )


def test_empty_initial_cart(user_jwt: str, client: StarletteGraphQlClient):
    response = client.execute(
        "{ cart { price } }", headers={"Authorization": f"Bearer {user_jwt}"}
    )
    assert response == {"data": {"cart": None}, "errors": None}


def test_add_to_cart(
    user_jwt: str, client: StarletteGraphQlClient, insert_product: typing.Callable
):
    productData = {"title": "Test Product", "price": 10, "inventory_count": 1}
    productId = insert_product(**productData)

    response = client.execute(
        """
        mutation($id: ID!) {
            addToCart(productId: $id) {
                products {
                    product {
                        id
                    }
                    amount
                }
                price
            }
        }
        """,
        variables={"id": productId},
        headers={"Authorization": f"Bearer {user_jwt}"},
    )
    assert response == {
        "data": {
            "addToCart": {
                "price": productData["price"],
                "products": [{"amount": 1, "product": {"id": productId}}],
            }
        },
        "errors": None,
    }


def test_get_cart(
    user_jwt: str, client: StarletteGraphQlClient, insert_product: typing.Callable
):
    productData = {"title": "Test Product", "price": 10, "inventory_count": 1}
    productId = insert_product(**productData)

    response = client.execute(
        """
        mutation($id: ID!) {
            addToCart(productId: $id) {
                price
            }
        }
        """,
        variables={"id": productId},
        headers={"Authorization": f"Bearer {user_jwt}"},
    )
    assert response.get("errors") == None

    response = client.execute(
        """
        {
            cart {
                products {
                    product {
                        id
                    }
                    amount
                }
                price
            }
        }
        """,
        headers={"Authorization": f"Bearer {user_jwt}"},
    )
    assert response == {
        "data": {
            "cart": {
                "price": productData["price"],
                "products": [{"amount": 1, "product": {"id": productId}}],
            }
        },
        "errors": None,
    }


def test_remove_from_cart(
    user_jwt: str, client: StarletteGraphQlClient, insert_product: typing.Callable
):
    productData = {"title": "Test Product", "price": 10, "inventory_count": 1}
    productId = insert_product(**productData)

    response = client.execute(
        """
        mutation($id: ID!) {
            addToCart(productId: $id) {
                price
            }
        }
        """,
        variables={"id": productId},
        headers={"Authorization": f"Bearer {user_jwt}"},
    )
    assert response.get("errors") == None

    response = client.execute(
        """
        mutation($id: ID!) {
            removeFromCart(productId: $id) {
                products {
                    amount
                }
                price
            }
        }
        """,
        variables={"id": productId},
        headers={"Authorization": f"Bearer {user_jwt}"},
    )
    assert response == {"data": {"removeFromCart": None}, "errors": None}


def test_complete_cart(
    user_jwt: str, client: StarletteGraphQlClient, insert_product: typing.Callable
):
    productData = {"title": "Test Product", "price": 10, "inventory_count": 1}
    productId = insert_product(**productData)

    response = client.execute(
        """
        mutation($id: ID!) {
            addToCart(productId: $id) {
                price
            }
        }
        """,
        variables={"id": productId},
        headers={"Authorization": f"Bearer {user_jwt}"},
    )
    assert response.get("errors") == None

    response = client.execute(
        """
        mutation {
            completeCart {
                success
                charged
            }
        }
        """,
        headers={"Authorization": f"Bearer {user_jwt}"},
    )
    assert response == {
        "data": {"completeCart": {"success": True, "charged": productData["price"]}},
        "errors": None,
    }

    response = client.execute(
        "{ cart { price } }", headers={"Authorization": f"Bearer {user_jwt}"}
    )
    # cart must be clear afterwards
    assert response == {"data": {"cart": None}, "errors": None}
