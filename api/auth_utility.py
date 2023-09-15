import calendar
import copy
import datetime
import json
import os
from hashlib import blake2b

import datastore as ds
import jwt
from bson import ObjectId

PW_DIGEST_SIZE = 20
SESSION_TIME_MIN = 30

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return calendar.timegm(o.utctimetuple())
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)


def credentials_match(username, password):
    user = ds.get_user(username=username)
    if user and user["password_hash"] == hash_password(password):
        return user
    return None


def hash_password(password):
    return blake2b(password.encode(), digest_size=PW_DIGEST_SIZE).hexdigest()

def new_expires_time():
    current_datetime = datetime.datetime.now()
    session_length = datetime.timedelta(minutes=SESSION_TIME_MIN)
    return current_datetime + session_length

def generate_token(user: dict):
    user.update({"exp": new_expires_time()})
    user.update({"iat": datetime.datetime.utcnow()})

    secret_key = os.environ.get("SESSION_SECRET_KEY")
    return jwt.encode(user, secret_key, algorithm='HS256', json_encoder=EnhancedJSONEncoder)
