import datetime
from hashlib import blake2b
from multiprocessing import AuthenticationError
from os import environ

import datastore as ds
import jwt
from bson import ObjectId
from pydantic import Field
from routes.models import AuthenticatedUser, User
from starlette.authentication import (AuthCredentials, AuthenticationBackend,
                                      UnauthenticatedUser)


class JWTAuthenticationBackend(AuthenticationBackend):
    algorithm = 'HS256'
    prefix = 'Bearer'
    username_field = 'username'
    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    def get_token_from_header(self, authorization):
        try:
            scheme, token = authorization.split()
        except ValueError:
            raise AuthenticationError('Invalid token header. No credentials provided.')

        if scheme.lower() != self.prefix.lower():
            raise AuthenticationError('Authorization scheme {scheme} not supported.')
        return token

    async def authenticate(self, conn):
        if "Authorization" not in conn.headers:
            return AuthCredentials([]), UnauthenticatedUser()
        token = self.get_token_from_header(conn.headers["Authorization"])
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            payload["_id"] = ObjectId(payload["_id"])

        except jwt.InvalidTokenError as e:
            raise AuthenticationError(str(e))
        return AuthCredentials(["authenticated", *payload["roles"]]), User(authenticated=True, **payload)
