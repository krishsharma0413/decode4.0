from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
import aiohttp
from secrets import token_urlsafe
from variables import env, db, limiter, templates, question_matrix_template
from routes.models import AnswerCheck, AddQuestion, Easter, Bug
from typing import Union
import datetime
import pytz
from helper import Helper

ist_timezone = pytz.timezone('Asia/Kolkata')

api_route = APIRouter(
    prefix="/api",
)

usercollection = db["users"]
questioncollection = db["questions"]
bannedcollection = db["banned"]
smcollection = db["solve_matrix"]

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    "User-Agent": "decode chan bot - api.py"
}
base_url = "https://discord.com/api/v10"


@api_route.get("/oauth2/discord", response_class=JSONResponse)
@limiter.limit("5/minute")
async def discord_oauth(request: Request, code: str):
    """
    - HTML response 
    - a continue button which sends the user to the play page
    - token saved using javascript which is unique to the user
    """
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': env["redirecturl"]
    }
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(base_url + "/oauth2/token", data=data, auth=aiohttp.BasicAuth(env["clientid"], env["clientsecret"])) as response:
                content = await response.json()

            async with session.get(base_url + "/users/@me", headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                "User-Agent": "decode chan bot - api.py",
                "Authorization": "Bearer %s" % content["access_token"]
            }) as response:
                user: dict = await response.json()
    except:
        return RedirectResponse("/")

    bannedlist = await bannedcollection.find_one({"_id": user["id"]})

    if bannedlist:
        return templates.TemplateResponse("banned.html", {"request": request})

    # try to save the avatar

    userdata = await usercollection.find_one({"_id": int(user["id"])})
    if userdata:
        temp = RedirectResponse(url="/")
        temp.set_cookie(key="token", value=userdata["token"], expires=5000)
        return temp
    else:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}?size=512") as response:
                    with open("./static/assets/avatars/%s.png" % user["id"], "wb") as f:
                        f.write(await response.read())
        except:
            with open("./static/assets/avatars/%s.png" % user["id"], "wb") as f:
                f.write(open("./static/assets/avatars/default.png", "rb").read())
        user.update(
            {
                "_id": int(user['id']),
                "token": token_urlsafe(16),
                "points": 0,
                "time": 0,
                "attempts": 0,
            }
        )
        user.update(question_matrix_template)
        
        userdata = await usercollection.insert_one(
            user
        )

        temp = RedirectResponse(url="/")
        temp.set_cookie(key="token", value=user["token"])
        return temp

def validator(experiment, etype):
    return 0 <= (experiment) <= 10 and 0 <= (etype) <= 3

points = {0:1,1:2,2:3}

@api_route.post("/check-answer", response_class=Union[JSONResponse, RedirectResponse])
@limiter.limit("1/second")
async def check_answer(request: Request, answer: AnswerCheck):
    userdata = await usercollection.find_one({"token": answer.token})
    if userdata:
        answer.attempt["experiment"] = int(answer.attempt["experiment"])
        answer.attempt["etype"] = int(answer.attempt["etype"])
        if not Helper.answer_validator(answer.attempt):
            return JSONResponse(content={"code": 69, "status": "invalid attempt."})
        question = await questioncollection.find_one({"_id": (answer.attempt["experiment"])})
        if not question:
            return JSONResponse(content={"code": 69, "status": "invalid question."})
        
        if not validator(answer.attempt["experiment"], answer.attempt["etype"]):
            return JSONResponse(content={"code": 69, "status": "invalid experiment or etype."})
        
        # check if the user has already solved the question
        if userdata[f'{answer.attempt["experiment"]}-{answer.attempt["etype"]}']["status"]:
            return JSONResponse(content={"code": 69, "status": "already solved."})
        
        # check if the user have access to that question via checking if the etype-1 is solved
        if answer.attempt["etype"] != 0:
            if not userdata[f'{answer.attempt["experiment"]}-{(answer.attempt["etype"])-1}']["status"]:
                return JSONResponse(content={"code": 69, "status": "solve the previous question first."})
        elif answer.attempt["etype"] == 0 and answer.attempt["experiment"] == 0:
            pass
        elif answer.attempt["etype"] == 0:
            if not userdata[f'{answer.attempt["experiment"]-1}-0']["status"]:
                return JSONResponse(content={"code": 69, "status": "solve the previous question first."})                
        
        etype = Helper.reverse_attempt[answer.attempt["etype"]]
        if (question[etype]["answer"]).replace(" ", "").lower() == (answer.answer).replace(" ", "").lower():
            await usercollection.update_one(
                {
                    "token": userdata["token"],
                },
                {
                    "$set": {
                        "time": (datetime.datetime.now(ist_timezone).timestamp()),
                        f'{answer.attempt["experiment"]}-{answer.attempt["etype"]}.status': True
                    },

                    "$inc": {
                        "points": points[answer.attempt["etype"]],
                        "attempts": 1
                    }
                }
            )
            await smcollection.insert_one(
                {
                    "user": userdata["_id"],
                    "experiment": answer.attempt["experiment"],
                    "etype": answer.attempt["etype"],
                    "time": datetime.datetime.now(ist_timezone).timestamp()
                }
            )
            return JSONResponse(content={"code": 420, "status": "correct"})
        else:
            await usercollection.update_one(
                {
                    "token": userdata["token"],
                },
                {
                    "$inc": {
                        "attempts": 1
                    }
                }
            )
            return JSONResponse(content={"code": 69, "status": "wrong answer, try again."})
    else:
        return RedirectResponse("/")