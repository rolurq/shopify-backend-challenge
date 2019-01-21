import pytest

from tinydb import TinyDB
from starlette.config import environ
from starlette.testclient import TestClient

environ["TESTING"] = "True"

from akara.app import app, DATABASE_URL
from akara.utils.database import UuidStorageProxy, UuidTable

TinyDB.table_class = UuidTable
TinyDB.storage_proxy_class = UuidStorageProxy


@pytest.fixture
def test_database(request):
    """
    Create a database for testing
    """
    database_url = DATABASE_URL.hostname + DATABASE_URL.path
    with TinyDB(database_url) as db:

        def _make_table(name: str):
            return db.table(name)

        yield _make_table

        db.purge_tables()


class StarletteGraphQlClient:
    """
    Client that passess trough starlette request system in order
    to ensure that context is correctly set in graphql resolvers
    """

    def __init__(self, client: TestClient):
        self.client = client

    def execute(self, query, variables=None, **kwargs) -> dict:
        body = {"query": query}
        if variables:
            body["variables"] = variables
        response = self.client.request("POST", "/query", json=body, **kwargs)
        if response.headers.get("content-type") != "application/json":
            return response.text
        return response.json()


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield StarletteGraphQlClient(client)
