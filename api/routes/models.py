import json
import os
from datetime import datetime
from enum import Enum
from typing import List, Optional

from auth_utility import EnhancedJSONEncoder, generate_token
from bson import ObjectId
from common.constants import US_STATES, Status
from common.model import BaseMongoModel
from pydantic import BaseModel, Field
from pymongo import MongoClient
from starlette.authentication import SimpleUser

MONGO_DB_CONNECTION_STRING = os.environ["MONGO_DB_CONNECTION_STRING"]
MONGO_DB_NAME = os.environ["MONGO_DB_NAME"]

url = MONGO_DB_CONNECTION_STRING
db_name = MONGO_DB_NAME

client = MongoClient(url)
db = client[db_name]



class AuthenticatedUser(SimpleUser):
    def __init__(self, payload: dict):
        super().__init__(payload["username"])
        self.token = payload.get("token") or generate_token(payload)
        self.payload = payload

class User(BaseMongoModel):
    # __fields_set__ = set()
    username: str = Field(..., example="username")
    name: str = Field(..., example="John Doe")
    email: str = Field(..., example="email@gmail.com")
    company_name: str
    password_hash: str
    auth_profile: Optional[AuthenticatedUser] = Field(default_factory=None)
    presentations: List[ObjectId] = Field(default_factory=list)
    conferences: List[ObjectId] = Field(default_factory=list)

    def __init__(self, authenticated=False, **user: dict):
        super().__init__(**user)
        if authenticated:
            self.auth_profile = AuthenticatedUser(user)

    async def add_presentation(self, presentation_id: ObjectId):
        filter_criteria = {"_id": ObjectId(self.id)}
        update_query = {"$push": {"presentations": ObjectId(presentation_id)}}

        result = db.users.update_one(filter_criteria, update_query)
        return result.modified_count > 0

    async def add_conference(self, conference_id: ObjectId):
        filter_criteria = {"_id": ObjectId(self.id)}
        update_query = {"$push": {"conferences": ObjectId(conference_id)}}

        result = db.users.update_one(filter_criteria, update_query)

        return result.modified_count > 0


# Model class representing a state
class State(BaseModel):
    name: str = Field(..., example="New York")
    abbreviation: str = Field(..., example=US_STATES["New York"])


# Model class representing a presentation
class Presentation(BaseMongoModel):
    presenter: ObjectId
    title: str = Field(..., example="Presentation title")
    synopsis: str = Field(..., example="Presentation synopsis")
    status: str = Status.PENDING.value
    location_id: Optional[ObjectId] = Field(default_factory=None)
    conference_id: Optional[ObjectId] = Field(default_factory=None)


# Model class representing a conference
class Conference(BaseMongoModel):
    name: str = Field(..., example="Conference name")
    starts: datetime = Field(..., example=datetime.now())
    ends: datetime = Field(..., example=datetime.now())
    description: str = Field(..., example="Conference description")
    max_presentations: int = Field(..., example=10)
    max_attendees: int = Field(..., example=100)
    attendees: List[ObjectId] = Field(default_factory=list)
    presentations: List[Presentation] = Field(default_factory=list)
    location_id: Optional[ObjectId] = Field(default_factory=None)

    async def add_attendee(self, attendee_id: str):
        filter_criteria = {"_id": ObjectId(self.location_id), "conferences._id": ObjectId(self.id)}
        update_query = {"$push": {"conferences.$.attendees": ObjectId(attendee_id)}}

        result = db.locations.update_one(filter_criteria, update_query)

        return result.modified_count == 1

    async def add_presentation(self, presentation: Presentation):
        presentation.conference_id = ObjectId(self.id)
        presentation.location_id = ObjectId(self.location_id)

        filter_criteria = {"_id": ObjectId(self.location_id), "conferences._id": ObjectId(self.id)}
        update_query = {"$push": {"conferences.$.presentations": presentation.dict(by_alias=True)}}
        result = db.locations.update_one(filter_criteria, update_query)
        return result.modified_count == 1

    # Model class representing a location
class Location(BaseMongoModel):
    name: str = Field(..., example="Location name")
    city: str = Field(..., example="City name")
    room_count: int = Field(..., example=5)
    picture_url: str = Field(..., example="https://example.com/location-picture.jpg")
    state: State = Field(..., example={"name": "State name", "abbreviation": "State abbreviation"})
    conferences: List[Conference] = Field(default_factory=list)

    async def add_conference(self, conference: Conference):
        conference.location_id = ObjectId(self.id)
        filter_criteria = {"_id": ObjectId(self.id)}
        update_query = {"$push": {"conferences": conference.dict(by_alias=True)}}

        result = db.locations.update_one(filter_criteria, update_query)
        return result.modified_count == 1
