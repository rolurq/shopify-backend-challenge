import hashlib
import uuid


def hash_password(password: str) -> str:
    """
    Creates a hash from a password adding a random salt

    :param password str: Password to hash
    :returns: The bytes from the hashed password
    :rtype: bytes
    """
    salt = uuid.uuid4().hex
    _hash = hashlib.sha512(password.encode() + salt.encode()).hexdigest()
    return salt + _hash


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a raw password against a hashed one

    :param password str: Raw password to check
    :param password_hash bytes: Password hash to check against
    :returns: If the password matched with the hashed one or not
    :rtype: bool
    """
    salt = password_hash[:32]
    _hash = password_hash[32:]
    _new_hash = hashlib.sha512(password.encode() + salt.encode()).hexdigest()
    return _new_hash == _hash
