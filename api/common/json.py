import json
import typing

from starlette.responses import JSONResponse


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        return json.loads(obj.json())



class PydanticJSONResponse(JSONResponse):
    def __init__(self, status_code, content, encoder=CustomEncoder):
        self.encoder = encoder
        super().__init__(status_code=status_code, content=content)

    def render(self, content: typing.Any) -> bytes:
        return json.dumps(content, cls=CustomEncoder).encode("utf-8")
