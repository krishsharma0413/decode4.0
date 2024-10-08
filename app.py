import fastapi
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from routes.api import api_route
from routes.socials import socials_route
from variables import templates, db, limiter
from typing import Union
from slowapi.errors import RateLimitExceeded
from helper import Helper
from routes.backlink import backlink_route
from routes.level import level_route
from routes.users import users_route
from helper import authenticator

usercollection = db["users"]
questioncollection = db["questions"]
announcementcollection = db["announcements"]
smcollection = db["solve_matrix"]


def _ratelimit_handler(request: fastapi.Request, exc: RateLimitExceeded):
    response = templates.TemplateResponse(
        "error.html", {
            "request": request,
            "heading": "RATE LIMIT",
            "desc": "Cam down, you are being rate limited. Try again in a minute."
        }
    )
    return response


app = fastapi.FastAPI(redoc_url=None, docs_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _ratelimit_handler)
app.include_router(api_route)
app.include_router(socials_route)
app.include_router(level_route)
app.include_router(users_route)
app.include_router(backlink_route)

@app.get("/", response_class=HTMLResponse)
@limiter.limit("1/second")
async def root(request: fastapi.Request):
    token = request.cookies.get("token")
    if token:
        userdata = await usercollection.find_one({"token": token})
        if userdata:

            temp = """
<div style="background-color:white;"
    class="bg-white rounded-lg text-center my-4 text-background font-nulshock text-xl md:text-2xl py-8">
    %s
</div>"""

            ann = ""
            announcements = await announcementcollection.find().to_list(length=1000)
            for announcement in sorted(announcements, key=lambda x: x["_id"], reverse=True):
                ann += temp % (announcement["description"])

            return templates.TemplateResponse(
                "index.html",
                authenticator(
                    userdata,
                    {
                        "request": request,
                        "session": "PLAY",
                        "announcements": ann,
                        "user": userdata
                    })
            )
    return templates.TemplateResponse(
        "index.html",
        {
            "authenticated": False,
            "request": request,
            "session": "LOGIN",
            "session_link": "/login",
            "announcements": """
<div class="text-center text-background" style="margin-top: 30px">
    Login to check announcements.
</div>

"""
        }
    )


@app.get("/menu", response_class=HTMLResponse)
@limiter.limit("1/second")
async def level_selector(request: fastapi.Request):
    token = request.cookies.get("token")
    if token:
        userdata = await usercollection.find_one({"token": token})
        if userdata:
            totaldata = await smcollection.find({"user":int(userdata["_id"])}).to_list(length=1000)
            length = len(totaldata)
            return templates.TemplateResponse(
                "menu.html",
                authenticator(userdata, {
                    "request": request,
                    "experiments": Helper.experiments,
                    "userData": userdata,
                    "length": length
                })
            )

    return RedirectResponse("/")


@app.get("/about", response_class=RedirectResponse)
@limiter.limit("10/minute")
async def about_root(request: fastapi.Request):
    return RedirectResponse("https://muj.acm.org/")


@app.get("/login", response_class=RedirectResponse)
@limiter.limit("5/minute")
async def login_root(request: fastapi.Request):
    return RedirectResponse("https://discord.com/oauth2/authorize?client_id=788099648291340318&response_type=code&redirect_uri=http%3A%2F%2Flocalhost:5555%2Fapi%2Foauth2%2Fdiscord&scope=email+identify")


@app.get("/leaderboard", response_class=Union[HTMLResponse, RedirectResponse])
@limiter.limit("5/minute")
async def leaderboard_root(request: fastapi.Request):
    token = request.cookies.get("token")
    if token:
        userdata = await usercollection.find_one({"token": token})
        if userdata:
            cursor = usercollection.find()

            ls = await cursor.to_list(length=1000)
            ls = sorted(ls, key=lambda x: x["points"], reverse=True)

            maxscore = ls[0]["points"]
            ldata = []
            new = []

            standard_template = {
                1: """
    <tr>
        <td class="border-2 text-text text-left px-2 bg-background font-nulshock border-hard-bg">{0}</td>
        <td class="border-2 flex place-items-center text-text text-left px-2 bg-background font-nulshock border-hard-bg"><svg width="15" height="15" viewBox="77.4 77.4 360 360" xmlns="http://www.w3.org/2000/svg">
    <path fill="#FFD43B" d="M 81.4 257.4 C 81.4 121.915 228.067 37.237 345.4 104.98 C 399.855 136.419 433.4 194.521 433.4 257.4 C 433.4 392.885 286.733 477.563 169.4 409.82 C 114.945 378.381 81.4 320.279 81.4 257.4 Z M 265.8 162.5 C 262.4 155.5 252.5 155.5 249 162.5 L 226.6 207.9 C 225.2 210.7 222.6 212.6 219.6 213 L 169.4 220.3 C 161.7 221.4 158.7 230.8 164.2 236.3 L 200.5 271.7 C 202.7 273.9 203.7 276.9 203.2 280 L 194.6 329.9 C 193.3 337.5 201.3 343.4 208.2 339.8 L 253 316.2 C 255.7 314.8 259 314.8 261.7 316.2 L 306.5 339.8 C 313.4 343.4 321.4 337.6 320.1 329.9 L 311.5 280 C 311 277 312 273.9 314.2 271.7 L 350.5 236.3 C 356.1 230.9 353 221.5 345.3 220.3 L 295.2 213 C 292.2 212.6 289.5 210.6 288.2 207.9 L 265.8 162.5 Z" style="opacity: 0.8;"/>
    </svg> &nbsp; <a href="/users/{3}">{1}</a></td>
        <td class="border-2 text-text text-left px-2 bg-background font-nulshock border-hard-bg">{2}</td>
    </tr>
    """,
                2: """
    <tr>
        <td class="border-2 text-text text-left px-2 bg-background font-nulshock border-hard-bg">{0}</td>
        <td class="border-2 flex place-items-center text-text text-left px-2 bg-background font-nulshock border-hard-bg"><svg width="15" height="15" viewBox="77.4 77.4 360 360" xmlns="http://www.w3.org/2000/svg">
    <path fill="#C0C0C0" d="M 81.4 257.4 C 81.4 121.915 228.067 37.237 345.4 104.98 C 399.855 136.419 433.4 194.521 433.4 257.4 C 433.4 392.885 286.733 477.563 169.4 409.82 C 114.945 378.381 81.4 320.279 81.4 257.4 Z M 265.8 162.5 C 262.4 155.5 252.5 155.5 249 162.5 L 226.6 207.9 C 225.2 210.7 222.6 212.6 219.6 213 L 169.4 220.3 C 161.7 221.4 158.7 230.8 164.2 236.3 L 200.5 271.7 C 202.7 273.9 203.7 276.9 203.2 280 L 194.6 329.9 C 193.3 337.5 201.3 343.4 208.2 339.8 L 253 316.2 C 255.7 314.8 259 314.8 261.7 316.2 L 306.5 339.8 C 313.4 343.4 321.4 337.6 320.1 329.9 L 311.5 280 C 311 277 312 273.9 314.2 271.7 L 350.5 236.3 C 356.1 230.9 353 221.5 345.3 220.3 L 295.2 213 C 292.2 212.6 289.5 210.6 288.2 207.9 L 265.8 162.5 Z" style="opacity: 0.8;"/>
    </svg> &nbsp; <a href="/users/{3}">{1}</a></td>
        <td class="border-2 text-text text-left px-2 bg-background font-nulshock border-hard-bg">{2}</td>
    </tr>
    """,
                3: """
    <tr>
        <td class="border-2 text-text text-left px-2 bg-background font-nulshock border-hard-bg">{0}</td>
        <td class="border-2 flex place-items-center text-text text-left px-2 bg-background font-nulshock border-hard-bg">
    <svg width="15" height="15" viewBox="77.4 77.4 360 360" xmlns="http://www.w3.org/2000/svg">
    <path fill="#CD7F32" d="M 81.4 257.4 C 81.4 121.915 228.067 37.237 345.4 104.98 C 399.855 136.419 433.4 194.521 433.4 257.4 C 433.4 392.885 286.733 477.563 169.4 409.82 C 114.945 378.381 81.4 320.279 81.4 257.4 Z M 265.8 162.5 C 262.4 155.5 252.5 155.5 249 162.5 L 226.6 207.9 C 225.2 210.7 222.6 212.6 219.6 213 L 169.4 220.3 C 161.7 221.4 158.7 230.8 164.2 236.3 L 200.5 271.7 C 202.7 273.9 203.7 276.9 203.2 280 L 194.6 329.9 C 193.3 337.5 201.3 343.4 208.2 339.8 L 253 316.2 C 255.7 314.8 259 314.8 261.7 316.2 L 306.5 339.8 C 313.4 343.4 321.4 337.6 320.1 329.9 L 311.5 280 C 311 277 312 273.9 314.2 271.7 L 350.5 236.3 C 356.1 230.9 353 221.5 345.3 220.3 L 295.2 213 C 292.2 212.6 289.5 210.6 288.2 207.9 L 265.8 162.5 Z" style="opacity: 0.8;"/>
    </svg> &nbsp; <a href="/users/{3}">{1}</a>
        </td>
        <td class="border-2 text-text text-left px-2 bg-background font-nulshock border-hard-bg">{2}</td>
    </tr>
    """
            }

            for x in ls:
                if x["points"] == maxscore:
                    ldata.append(x)
                else:
                    new.extend(
                        sorted(ldata, key=lambda y: y["time"])
                    )
                    ldata = [x]
                    maxscore = x["points"]

            new.extend(
                sorted(ldata, key=lambda y: y["time"])
            )

            position = 1
            lc = ""
            for xy in new:
                lc += (standard_template.get(position, """
    <tr>
        <td class="border-2 text-text text-left px-2 bg-background font-nulshock border-hard-bg">{0}</td>
        <td class="border-2 text-text text-left px-2 bg-background font-nulshock border-hard-bg"><a href="/users/{3}">{1}</a></td>
        <td class="border-2 text-text text-left px-2 bg-background font-nulshock border-hard-bg">{2}</td>
    </tr>
    """)).format(position, xy["username"], xy["points"], xy["_id"])
                position += 1

            return templates.TemplateResponse(
                "leaderboard.html",
                authenticator(userdata,{
                    "request": request,
                    "leaderboard_content": lc,
                    "user": userdata
                })
            )

    return RedirectResponse("/")
