import json
from datetime import datetime

import datastore as ds
from common.constants import US_STATES
from common.json import PydanticJSONResponse
from pydantic import ValidationError
from routes.models import Conference, Location, Presentation, User
from starlette.authentication import requires
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from .third_party import get_photo


# States
async def list_states(request: Request):
    return JSONResponse(status_code=200, content={"states": US_STATES})


# Locations
async def list_locations(request: Request):
    locations = await ds.location_all()
    return PydanticJSONResponse(status_code=200, content={"locations": locations})


async def create_location(request: Request):
    content = await request.json()
    if content.get("state", "_").title() in US_STATES:
        content["state"] = {"name": content["state"], "abbreviation": US_STATES[content["state"]]}
        photo = await get_photo(content["city"], content["state"]["abbreviation"])
        content.update(photo)
        location = Location(**content)
        new_location = await ds.location_create(location)
        return PydanticJSONResponse(status_code=201, content=new_location)
    else:
        raise HTTPException(status_code=400, detail=f"Invalid state: {content.get('state')}")


async def show_location(request: Request):
    location_id = request.path_params["location_id"]
    location = await ds.location_details(location_id)
    return PydanticJSONResponse(status_code=200, content=location)


async def update_location(request: Request):
    location_id = request.path_params["location_id"]
    content = await request.json()
    updated_location = await ds.location_update(content, location_id)
    return PydanticJSONResponse(status_code=200, content=updated_location)


async def delete_location(request: Request):
    location_id = request.path_params["location_id"]
    deleted_count = await ds.location_delete(location_id)
    return JSONResponse(status_code=204, content={"deleted": deleted_count > 0})


# Conferences
async def list_conferences(request: Request):
    location_id = request.path_params.get("location_id")
    if location_id:
        location = await ds.location_details(location_id)
        return PydanticJSONResponse(status_code=200, content={"conferences": location.conferences})
    else:
        conferences = await ds.conference_all()
        return PydanticJSONResponse(status_code=200, content={"conferences": conferences})


async def create_conference(request: Request):
    content = await request.json()
    content.update({
        "starts": datetime.strptime(content["starts"], '%Y-%m-%d'),
        "ends": datetime.strptime(content["ends"], '%Y-%m-%d')
    })
    conference = Conference(**content)
    location_id = request.path_params["location_id"]
    location = await ds.location_details(location_id)
    if (added := await location.add_conference(conference)):
        updated_location = await ds.location_details(location_id)
        return PydanticJSONResponse(status_code=201, content=updated_location.conferences)


async def show_conference(request: Request):
    location_id = request.path_params["location_id"]
    conference_id = request.path_params["conference_id"]
    conference = await ds.conference_details(location_id, conference_id)
    return PydanticJSONResponse(status_code=200, content=conference)


async def update_conference(request: Request):
    location_id = request.path_params["location_id"]
    conference_id = request.path_params["conference_id"]
    content = await request.json()
    conference = await ds.conference_update(location_id, conference_id, content)
    return PydanticJSONResponse(status_code=200, content=conference)


async def delete_conference(request: Request):
    location_id = request.path_params["location_id"]
    conference_id = request.path_params["conference_id"]
    deleted_count = await ds.conference_delete(location_id, conference_id)
    return JSONResponse(status_code=200, content={"deleted": deleted_count > 0})

# Presentations
async def list_presentations(request: Request):
    location_id = request.path_params.get("location_id")
    conference_id = request.path_params.get("conference_id")
    if location_id and conference_id:
        conference = await ds.conference_details(location_id, conference_id)
        return PydanticJSONResponse(status_code=200, content=conference.presentations)
    else:
        presentations = await ds.presentation_all()
        return PydanticJSONResponse(status_code=200, content=[Presentation(**presentation) for presentation in presentations])

@requires(["authenticated", "admin"])
async def create_presentation(request: Request):
    try:
        content = await request.json()
        content.update({ "presenter": request.user.id })
        presentation = Presentation(**content)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=json.dumps(e.errors()))

    location_id = request.path_params.get("location_id")
    conference_id = request.path_params.get("conference_id")
    conference = await ds.conference_details(location_id, conference_id)

    if (await conference.add_presentation(presentation)):
        conference = await ds.conference_details(location_id, conference_id)
        presentation_id = conference.presentations[-1].id

        if (await request.user.add_presentation(presentation_id)):
            conference = await ds.conference_details(location_id, conference_id)
            return PydanticJSONResponse(status_code=201, content=conference)


async def show_presentation(request: Request):
    location_id = request.path_params.get("location_id")
    conference_id = request.path_params.get("conference_id")
    presentation_id = request.path_params.get("presentation_id")

    presentation = await ds.presentation_details(location_id, conference_id, presentation_id)
    return PydanticJSONResponse(status_code=200, content=presentation)


async def update_presentation(request: Request):
    location_id = request.path_params.get("location_id")
    conference_id = request.path_params.get("conference_id")
    presentation_id = request.path_params.get("presentation_id")

    content = await request.json()
    presentation = await ds.presentation_update(location_id, conference_id, presentation_id, content)
    return PydanticJSONResponse(status_code=200, content=presentation)


async def delete_presentation(request: Request):
    location_id = request.path_params.get("location_id")
    conference_id = request.path_params.get("conference_id")
    presentation_id = request.path_params.get("presentation_id")
    pass


# Attendees
async def list_attendees(request: Request):
    location_id = request.path_params.get("location_id")
    conference_id = request.path_params.get("conference_id")
    conference = await ds.conference_details(location_id, conference_id)
    return PydanticJSONResponse(status_code=200, content=conference.attendees)


@requires(["authenticated"])
async def create_attendee(request: Request):
    location_id = request.path_params.get("location_id")
    conference_id = request.path_params.get("conference_id")
    conference = await ds.conference_details(location_id, conference_id)

    if (await conference.add_attendee(request.user.id)):
        if (await request.user.add_conference(conference_id)):
            conference = await ds.conference_details(location_id, conference_id)
            return PydanticJSONResponse(status_code=201, content=conference)


async def show_attendee(request: Request, id: str = None):
    location_id = request.path_params.get("location_id")
    conference_id = request.path_params.get("conference_id")
    attendee_id = request.path_params.get("attendee_id")

    attendee = await ds.attendee_details(location_id, conference_id, attendee_id)
    return PydanticJSONResponse(status_code=200, content=attendee)


async def delete_attendee(request: Request, id: str = None):
    location_id = request.path_params.get("location_id")
    conference_id = request.path_params.get("conference_id")
    attendee_id = request.path_params.get("attendee_id")
    pass
