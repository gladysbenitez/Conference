from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, Field, root_validator, validator


class BaseMongoModel(BaseModel):
    id: ObjectId = Field(default_factory=lambda: ObjectId(), alias="_id")
    created: datetime = datetime.now()
    updated: datetime = datetime.now()

    @root_validator
    def number_validator(cls, values):
        values["updated"] = datetime.now()
        return values

    @validator("conferences", "presentations", pre=True, check_fields=False)
    def convert_conferences_and_preferences_to_object_ids(cls, value):
        if isinstance(value, str):
            return [ObjectId(value)]
        elif isinstance(value, list):
            return [ObjectId(val) if isinstance(val, str) else val for val in value]
        return value

    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: lambda x: str(x),
        }
