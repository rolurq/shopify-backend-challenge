import uuid

from aiotinydb import AIOTinyDB
from starlette.datastructures import DatabaseURL
from starlette.types import ASGIApp, ASGIInstance, Scope
from tinydb import Query, TinyDB
from tinydb.database import Document, StorageProxy, Table

Q = Query()


class UuidTable(Table):
    """
    TinyDB table class to generate random uuid's as id's for documents
    """

    def _get_next_id(self) -> str:
        return uuid.uuid4().hex


class UuidStorageProxy(StorageProxy):
    """
    TinyDB storage proxy that allows string keys (uuid's) to be used
    as document id's
    """

    def _new_document(self, key: str, value: dict) -> Document:
        return Document(value, key)


# set table and proxy on AIOTinyDB since that's what's being used
AIOTinyDB.table_class = UuidTable
AIOTinyDB.storage_proxy_class = UuidStorageProxy


class TinyDbMiddleware:
    def __init__(self, app: ASGIApp, database_url: DatabaseURL) -> None:
        self.app = app
        self.database = AIOTinyDB(database_url.hostname + database_url.path)

    def __call__(self, scope: Scope) -> ASGIInstance:
        scope["database"] = self.database
        return self.app(scope)
