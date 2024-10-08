from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from variables import templates, db, limiter
from helper import authenticator, Helper
from pytz import timezone
import datetime

ist_timezone = timezone('Asia/Kolkata')

usercollection = db["users"]
smcollection = db["solve_matrix"]
users_route = APIRouter(
    prefix="/users",
)

@users_route.get("/@me")
@limiter.limit("5/minute")
async def discord(request: Request):
    token = request.cookies.get("token")
    if token:
        userdata = await usercollection.find_one({"token": token})
        if userdata:
            smdata = await smcollection.find({"user": int(userdata["_id"])}).to_list(length=1000)
            smdata.sort(key=lambda x: x["time"], reverse=True)
            for x in smdata:
                x["time"] = datetime.datetime.fromtimestamp(x["time"],ist_timezone).strftime("%d %b %Y, %I:%M %p")
                x["name"] = Helper.experiments[x["experiment"]] + " - " + Helper.reverse_attempt[x["etype"]].upper()
            return templates.TemplateResponse(
                "user.html",
                authenticator(userdata, {
                    "request": request,
                    "user": userdata,
                    "smdata": smdata,
                    "totalsolved": len(smdata)
                })
            )
    return RedirectResponse("/")


@users_route.get("/{user_id}")
@limiter.limit("5/minute")
async def instagram(request: Request, user_id: str):
    token = request.cookies.get("token")
    if token:
        userdata = await usercollection.find_one({"token": token})
        if userdata:
            userdata = await usercollection.find_one({"_id": int(user_id)})
            if not userdata:
                return RedirectResponse("/")
            smdata = await smcollection.find({"user": int(userdata["_id"])}).to_list(length=1000)
            smdata.sort(key=lambda x: x["time"], reverse=True)
            for x in smdata:
                x["time"] = datetime.datetime.fromtimestamp(x["time"],ist_timezone).strftime("%d %b %Y, %I:%M %p")
                x["name"] = Helper.experiments[x["experiment"]] + " - " + Helper.reverse_attempt[x["etype"]].upper()
            return templates.TemplateResponse(
                "user.html",
                authenticator(userdata, {
                    "request": request,
                    "user": userdata,
                    "smdata": smdata,
                    "totalsolved": len(smdata)
                })
            )
    return RedirectResponse("/")