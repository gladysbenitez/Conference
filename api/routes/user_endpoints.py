from auth_utility import credentials_match, hash_password
from datastore import create_user
from starlette.responses import JSONResponse, RedirectResponse

from .models import User


async def sign_up(request):
    content =  await request.json()
    username = content.get("username")
    password = content.pop("password")
    password2 = content.pop("password2")

    if username and password and password == password2:
        content["password_hash"] = hash_password(password)

        if await create_user(content):
            return JSONResponse(status_code=200, content={"message": "signup successful"})
        else:
            return JSONResponse(status_code=400, content={"message": "signup failed"})
    else:
        return JSONResponse(status_code=400, content={"message": "passwords do not match"})


async def login(request):
    content =  await request.json()
    username = content.get("username")
    password = content.get("password")
    db_user = credentials_match(username, password)

    if db_user:
        user = User(authenticated=True, **db_user)
        response = JSONResponse(status_code=200, content={"message": "login successful"})
        response.set_cookie(key="token", value=user.auth_profile.token, httponly=True)
        return response
    else:
        return JSONResponse(status_code=401, detail="Invalid credentials")



def logout(request):
    request.session.clear()
    return RedirectResponse(
        url=request.url_for("home"),
        status_code=302
    )
