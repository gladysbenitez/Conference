import os
from typing import List

from bson import ObjectId
from bson.errors import InvalidId
from pydantic import ValidationError
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import PyMongoError
from routes.models import Conference, User, Presentation
from starlette.exceptions import HTTPException

MONGO_DB_CONNECTION_STRING = os.environ["MONGO_DB_CONNECTION_STRING"]
MONGO_DB_NAME = os.environ["MONGO_DB_NAME"]

url = MONGO_DB_CONNECTION_STRING
db_name = MONGO_DB_NAME

client = MongoClient(url)
db = client[db_name]

def handle_exceptions(e, id=None, model_name=""):
    if isinstance(e, InvalidId):
        raise HTTPException(status_code=400, detail=f"Invalid ID: {str(e)}")
    elif isinstance(e, ValidationError):
        raise HTTPException(status_code=400, detail=f"Invalid {model_name}: {str(e)}")
    elif isinstance(e, PyMongoError):
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    else:
        raise e


async def user_create(user: User):
    if (count := db.users.count_documents({"name": user.name})) > 0:
        raise HTTPException(status_code=400, detail="User already exists")
    try:
        response = db.users.insert_one(user.dict(by_alias=True))
        user = db["users"].find_one({"_id": response.inserted_id})
        return User(**user)
    except (ValidationError, PyMongoError) as e:
        handle_exceptions(user.name, e)

async def user_all():
    try:
        db_users = db.users.find()
        return [User(**user) for user in db_users]
    except (ValidationError, PyMongoError) as e:
        handle_exceptions(e)

async def user_details(user_id: str):
    try:
        if (user := db.users.find_one({"_id": ObjectId(user_id)})) is None:
            raise HTTPException(status_code=400, detail="User does not exist")
        return User(**user)
    except (ValidationError, PyMongoError, InvalidId) as e:
        handle_exceptions(e, user_id)

async def user_update(update_fields: dict, id: str):
    try:
        # The $set operator within the update document specifies the properties you want to update for
        # the matched user.
        result = db.users.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_fields}
        )
        if result.modified_count > 0:
            return await user_details(id)
        elif result.matched_count < 0:
            raise HTTPException(status_code=400, detail="User does not exist")
        else:
            raise HTTPException(status_code=304, detail="No changes were made")
    except (PyMongoError, InvalidId) as e:
        handle_exceptions(e, id)

async def user_delete(user_id: str):
    try:
        return db.users.delete_one({"_id": ObjectId(user_id)}).deleted_count
    except (PyMongoError, InvalidId) as e:
        handle_exceptions(e, user_id)
