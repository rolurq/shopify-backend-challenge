import jwt

from config.settings import SECRET_KEY, JWT_ALGORITHM
from .conftest import StarletteGraphQlClient


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
    assert response

    token = response.get("data").get("signup").get("token")
    payload = jwt.decode(token, key=SECRET_KEY, algorithms=(JWT_ALGORITHM,))
    assert username == payload.get("username")


def test_user_not_logged(client: StarletteGraphQlClient):
    response = client.execute("{ user { id } }")
    assert response.get("data") == {"user": None}
    assert (
        response.get("errors")[0].get("message")
        == "you must be loged in to access your user data"
    )
