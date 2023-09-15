from os import environ

from auth_middleware import JWTAuthenticationBackend
from routes.endpoints import (create_attendee, create_conference,
                              create_location, create_presentation,
                              delete_attendee, delete_conference,
                              delete_location, delete_presentation,
                              list_attendees, list_conferences, list_locations,
                              list_presentations, list_states, show_attendee,
                              show_conference, show_location,
                              show_presentation, update_conference,
                              update_location, update_presentation)
from routes.user_endpoints import login, sign_up
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.routing import Route

middleware = [
    Middleware(CORSMiddleware, allow_origins=["http://localhost:3001"], allow_methods=['*']),
    Middleware(TrustedHostMiddleware, allowed_hosts=["localhost"]),
    Middleware(AuthenticationMiddleware, backend=JWTAuthenticationBackend(secret_key=environ.get("SESSION_SECRET_KEY")))
]

routes = [
    # States
    Route("/api/states/", list_states, methods=["GET"]),

    # Locations
    Route("/api/locations/", list_locations, methods=["GET"]),
    Route("/api/locations/", create_location, methods=["POST"]),
    Route("/api/locations/{location_id}/", show_location, methods=["GET"]),
    Route("/api/locations/{location_id}/", update_location, methods=["PUT"]),
    Route("/api/locations/{location_id}/", delete_location, methods=["DELETE"]),

    # Conferences
    Route("/api/conferences/", list_conferences, methods=["GET"]),
    Route("/api/locations/{location_id}/conferences/", list_conferences, methods=["GET"]),
    Route("/api/locations/{location_id}/conferences/", create_conference, methods=["POST"]),
    Route("/api/locations/{location_id}/conferences/{conference_id}", show_conference, methods=["GET"]),
    Route("/api/locations/{location_id}/conferences/{conference_id}", update_conference, methods=["PUT"]),
    Route("/api/locations/{location_id}/conferences/{conference_id}", delete_conference, methods=["DELETE"]),

    # Presentations
    Route("/api/presentations/", list_presentations, methods=["GET"]),
    Route("/api/locations/{location_id}/conferences/{conference_id}/presentations/", list_presentations, methods=["GET"]),
    Route("/api/locations/{location_id}/conferences/{conference_id}/presentations/", create_presentation, methods=["POST"]),
    Route("/api/locations/{location_id}/conferences/{conference_id}/presentations/{presentation_id}", show_presentation, methods=["GET"]),
    Route("/api/locations/{location_id}/conferences/{conference_id}/presentations/{presentation_id}", update_presentation, methods=["PUT"]),
    Route("/api/locations/{location_id}/conferences/{conference_id}/presentations/{presentation_id}", delete_presentation, methods=["DELETE"]),

    # Attendees
    Route("/api/attendees/", list_attendees, methods=["GET"]),
    Route("/api/locations/{location_id}/conferences/{conference_id}/attendees/", list_attendees, methods=["GET"]),
    Route("/api/locations/{location_id}/conferences/{conference_id}/attendees/", create_attendee, methods=["POST"]),
    Route("/api/locations/{location_id}/conferences/{conference_id}/attendees/{attendee_id}", show_attendee, methods=["GET"]),
    Route("/api/locations/{location_id}/conferences/{conference_id}/attendees/{attendee_id}", delete_attendee, methods=["DELETE"]),

    # User endpoints
    Route("/signup/", sign_up, methods=["POST"]),
    Route("/login/", login, methods=["POST"]),
]

app = Starlette(debug=True, routes=routes, middleware=middleware)
