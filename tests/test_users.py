from datetime import datetime, timedelta

import jwt
import pytest

from akara.models import User

from config.settings import SECRET_KEY, JWT_ALGORITHM
from .conftest import StarletteGraphQlClient


@pytest.fixture
def initial_user(test_database):
    username = "test"
    password = "T3st_"
    user = User(username=username)
    user.set_password(password)

    users = test_database("users")
    user.id = users.insert(
        {"username": user.username, "password_hash": user.password_hash}
    )
    yield user
    users.purge()


def test_signup(client: StarletteGraphQlClient):
    username = "test"
    password = "T3st_"

    response = client.execute(
        """
        mutation($username: String!, $password: String!) {
            signup(input: { username: $username, password: $password }) {
                token
            }
        }
        """,
        variables={"username": username, "password": password},
    )
    assert response.get("data").get("signup").get("token")

    token = response.get("data").get("signup").get("token")
    payload = jwt.decode(token, key=SECRET_KEY, algorithms=(JWT_ALGORITHM,))
    assert username == payload.get("username")


def test_signup_username_taken(initial_user: User, client: StarletteGraphQlClient):
    response = client.execute(
        """
        mutation($username: String!, $password: String!) {
            signup(input: { username: $username, password: $password }) {
                token
            }
        }
        """,
        variables={"username": initial_user.username, "password": "anything"},
    )
    assert response.get("data") == {"signup": None}
    assert response.get("errors")[0].get("message") == "username is alredy taken"


def test_login(initial_user: User, client: StarletteGraphQlClient):
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
    assert response.get("data").get("login").get("token")
    token = response.get("data").get("login").get("token")
    payload = jwt.decode(token, key=SECRET_KEY, algorithms=(JWT_ALGORITHM,))
    assert initial_user.username == payload.get("username")


def test_login_invalid_user(client: StarletteGraphQlClient):
    response = client.execute(
        """
        mutation($username: String!, $password: String!) {
            login(username: $username, password: $password) {
                token
            }
        }
        """,
        variables={"username": "test", "password": "anything"},
    )
    assert response.get("data") == {"login": None}
    assert response.get("errors")[0].get("message") == "user does not exist"


def test_login_incorrect_password(initial_user: User, client: StarletteGraphQlClient):
    response = client.execute(
        """
        mutation($username: String!, $password: String!) {
            login(username: $username, password: $password) {
                token
            }
        }
        """,
        variables={"username": initial_user.username, "password": "wrong_one"},
    )
    assert response.get("data") == {"login": None}
    assert response.get("errors")[0].get("message") == "incorrect password"


def test_login_expired_token(initial_user: User, client: StarletteGraphQlClient):
    token = jwt.encode(
        {**initial_user.to_json(), "exp": datetime.utcnow() - timedelta(seconds=1)},
        key=SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    ).decode()
    response = client.execute(
        "{ user { username } }", headers={"Authorization": f"Bearer {token}"}
    )
    assert response == "Signature has expired"


def test_login_bad_header(initial_user: User, client: StarletteGraphQlClient):
    token = jwt.encode(
        {**initial_user.to_json(), "exp": datetime.utcnow() + timedelta(days=1)},
        key=SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    ).decode()
    response = client.execute(
        "{ user { username } }", headers={"Authorization": f"Bearer{token}"}
    )
    assert response == "incorrect authorization header format"


def test_login_wrong_scheme(initial_user: User, client: StarletteGraphQlClient):
    token = jwt.encode(
        {**initial_user.to_json(), "exp": datetime.utcnow() + timedelta(days=1)},
        key=SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    ).decode()
    response = client.execute(
        "{ user { username } }", headers={"Authorization": f"Auth {token}"}
    )
    assert response == "authorization scheme Auth is not supported"


def test_user(initial_user: User, client: StarletteGraphQlClient):
    token = jwt.encode(
        {**initial_user.to_json(), "exp": datetime.utcnow() + timedelta(days=1)},
        key=SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    ).decode()
    response = client.execute(
        "{ user { username } }", headers={"Authorization": f"Bearer {token}"}
    )
    assert response == {
        "data": {"user": {"username": initial_user.username}},
        "errors": None,
    }


def test_user_not_logged(client: StarletteGraphQlClient):
    response = client.execute("{ user { id } }")
    assert response.get("data") == {"user": None}
    assert (
        response.get("errors")[0].get("message")
        == "you must be loged in to access your user data"
    )
