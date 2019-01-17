import pytest
from tinydb import TinyDB
from starlette.config import environ

environ["TESTING"] = "True"

from akara.models import Product, User
from akara.app import app, DATABASE_URL


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    """
    Create a database for testing with initial data
    """
    database_url = DATABASE_URL.hostname + DATABASE_URL.path
    with TinyDB(database_url) as db:
        # users
        users = db.table("users")
        admin = User(username="admin")
        admin.set_password("@dm1N")
        users.insert(admin.to_doc())
        # products
        products = db.table("products")
        product = Product(title="Test Product 1", price=15.5, inventory_count=4)
        products.insert(product.to_doc())
    yield
    # remove database
    with TinyDB(database_url) as db:
        db.purge_tables()
