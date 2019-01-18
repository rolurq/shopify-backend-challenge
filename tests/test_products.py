import pytest
from .conftest import StarletteGraphQlClient


@pytest.fixture(autouse=True)
def initial_products(test_database):
    products = test_database("products")
    products.insert_multiple(
        [
            {"title": "Test Product 1", "price": 10.5, "inventory_count": 5},
            {"title": "Test Product 2", "price": 11.8, "inventory_count": 10},
            {"title": "Test Product 3", "price": 100, "inventory_count": 0},
        ]
    )
    yield
    products.purge()


def test_exclude_emptied_products(client: StarletteGraphQlClient):
    response = client.execute("{ products { inventoryCount } }")
    assert response == {
        "data": {"products": [{"inventoryCount": 5}, {"inventoryCount": 10}]},
        "errors": None,
    }


def test_obtain_by_id(client: StarletteGraphQlClient):
    response = client.execute(
        """
        query ($id: ID!){
            product(id: $id) { id }
        }
        """,
        variables={"id": "1"},
    )
    assert response == {"data": {"product": {"id": "1"}}, "errors": None}


def test_obtain_by_id_not_existent(client: StarletteGraphQlClient):
    response = client.execute(
        """
        query ($id: ID!) {
            product(id: $id) { id }
        }
        """,
        variables={"id": "not existent"},
    )
    assert response == {"data": {"product": None}, "errors": None}
