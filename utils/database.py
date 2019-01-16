from aiotinydb import AIOTinyDB
from starlette.datastructures import DatabaseURL
from starlette.types import ASGIApp, ASGIInstance, Scope


class TinyDbMiddleware:
    def __init__(self, app: ASGIApp, database_url: DatabaseURL) -> None:
        self.app = app
        self.database = AIOTinyDB(database_url.hostname + database_url.path)

    def __call__(self, scope: Scope) -> ASGIInstance:
        scope["database"] = self.database
        return self.app(scope)
