import os
from typing import List

from bson import ObjectId
from bson.errors import InvalidId
from common.constants import Role
from pydantic import ValidationError
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import PyMongoError
from routes.models import Conference, Location, Presentation, User
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


async def location_create(location: Location):
    if (count := db.locations.count_documents({"name": location.name})) > 0:
        raise HTTPException(status_code=400, detail="Location already exists")
    try:
        response = db.locations.insert_one(location.dict(by_alias=True))
        location = db["locations"].find_one({"_id": response.inserted_id})
        return Location(**location)
    except (ValidationError, PyMongoError) as e:
        handle_exceptions(location.name, e)

async def location_all():
    try:
        db_locations = db.locations.find()
        return [Location(**location) for location in db_locations]
    except (ValidationError, PyMongoError) as e:
        handle_exceptions(e)

async def location_details(location_id: str):
    try:
        if (location := db.locations.find_one({"_id": ObjectId(location_id)})) is None:
            raise HTTPException(status_code=400, detail="Location does not exist")
        return Location(**location)
    except (ValidationError, PyMongoError, InvalidId) as e:
        handle_exceptions(e, location_id)

async def location_update(update_fields: dict, id: str):
    try:
        # The $set operator within the update document specifies the properties you want to update for
        # the matched location.
        result = db.locations.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_fields}
        )
        if result.modified_count > 0:
            return await location_details(id)
        elif result.matched_count < 0:
            raise HTTPException(status_code=400, detail="Location does not exist")
        else:
            raise HTTPException(status_code=304, detail="No changes were made")
    except (PyMongoError, InvalidId) as e:
        handle_exceptions(e, id)

async def location_delete(location_id: str):
    try:
        return db.locations.delete_one({"_id": ObjectId(location_id)}).deleted_count
    except (PyMongoError, InvalidId) as e:
        handle_exceptions(e, location_id)

async def conference_all():
    conferences: List[Conference] = []
    locations = await location_all()

    for location in locations:
        conferences.extend(location.conferences)
    return conferences

async def conference_details(location_id: str, conference_id: str):
    try:
        result = db.locations.find_one(
            {"_id": ObjectId(location_id), "conferences._id": ObjectId(conference_id)},
        )

        if result:
            conference = result["conferences"][0]
            return Conference(**conference)
        raise HTTPException(status_code=400, detail="Conference does not exist")
    except (PyMongoError, InvalidId, ValidationError) as e:
        handle_exceptions(e, conference_id, "conference")

async def conference_update(location_id: str, conference_id: str, update_fields: dict):
    if update_fields.get("location_id"):
        update_fields.update({"location_id": ObjectId(update_fields["location_id"])})

    # The $set operator within the update document specifies the properties you want to update for
    # the matched conference.

    # Because the conferences array is a subdocument, you need to use the
    # positional operator $ to identify the specific conference within the conferences array.
    # The positional operator $ in the query ("conferences._id": ObjectId(conference_id))
    # identifies the specific conference within the conferences array based on its ID.
    set_dict = {f"conferences.$.{key}": value for key, value in update_fields.items()}

    try:
        result = db.locations.update_one(
            {"_id": ObjectId(location_id), "conferences._id": ObjectId(conference_id)},
            {"$set": set_dict},
        )
        if result.modified_count > 0:
            return await conference_details(location_id, conference_id)
        elif result.matched_count < 1:
            raise HTTPException(status_code=400, detail="Conference does not exist")
        else:
            raise HTTPException(status_code=400, detail="No changes to conference")
    except (PyMongoError, InvalidId) as e:
        handle_exceptions(e)

async def conference_delete(location_id: str, conference_id: str):
    filter = {"_id": ObjectId(location_id)}
    update = {"$pull": {"conferences": {"_id": ObjectId(conference_id)}}}

    try:
        if (result := db.locations.update_one(filter, update)).matched_count > 0:
            return result.modified_count
        raise HTTPException(status_code=400, detail="Location does not exist")
    except (PyMongoError, InvalidId) as e:
        handle_exceptions(e)

async def presentation_create(location_id: str, conference_id: str, presentation:Presentation):
    result = db.locations.find_one_and_update(
        {"_id": ObjectId(location_id), "conferences._id": ObjectId(conference_id)},
        {"$addToSet": {
            "presentation": {
                "$each": [presentation.dict(by_alias=True)]
            }
        }},
        return_document=ReturnDocument.AFTER
    )
    return result

async def presentation_details(location_id: str, conference_id: str, presentation_id: str):
    filter = {
        "_id": ObjectId(location_id),
        "conferences._id": ObjectId(conference_id),
        "presentations._id": ObjectId(presentation_id)
        }

    try:
        result = db.locations.find_one(filter)

        if result:
            return result["presentations"][0]
        raise HTTPException(status_code=400, detail="Presentation does not exist")
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

async def presentation_update(location_id: str, conference_id: str, presentation_id:str, presentation: dict):
    pass


async def presentation_all():
    conferences = await conference_all()
    presentations: List[Presentation] = []
    for conference in conferences:
        presentations.extend(conference.presentations)
    return presentations


async def attendees_all():
    cursor = db.locations.aggregate(
        [
            { "$unwind": "$conferences.attendees" },
            {"$replaceRoot": {"newRoot": "$attendees"}},
            { "$project": {"_id": 0} }
        ]
    )
    return cursor.to_list(length=100)

async def attendee_details(location_id: str, conference_id: str, attendee_id: str):
    try:
        result= await db.locations.find_one(
            {"_id": ObjectId(location_id), "conferences._id": ObjectId(conference_id), "attendees._id": ObjectId(attendee_id)},
            {"attendees.$": 1}
        )
        if result:
            return result["attendees"][0]
        raise HTTPException(status_code=400, detail="Attendee does not exist")
    except (PyMongoError, InvalidId) as e:
        handle_exceptions(e)


############# Auth related functions ################################
# user related functions
async def create_user(user: dict):
    try:
        User(**user)
        user["roles"] = [Role.USER]
        if user.get("is_superuser"):
            user["roles"].append(Role.ADMIN)
        if (result := db.users.insert_one(user)).inserted_id is not None:
            return True
        return False
    except (PyMongoError, ValidationError) as e:
        handle_exceptions(e)

def get_user(id=None, username=None):
    if id:
        return db.users.find_one({"_id": id})
    return db.users.find_one({"username": username})
