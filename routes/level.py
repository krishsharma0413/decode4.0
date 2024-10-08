from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from variables import templates
from variables import db, limiter
from helper import Helper, authenticator

level_route = APIRouter(
    prefix="/level",
)
usercollection = db["users"]
questioncollection = db["questions"]
smcollection = db["solve_matrix"]

def validator(experiment, etype):
    return 0 <= experiment <= 10 and 0 <= etype <= 3

@level_route.get("/escape-day")
@limiter.limit("5/minute")
async def escape_day(request: Request):
    token = request.cookies.get("token")
    if token:
        userdata = await usercollection.find_one({"token": token})
        if userdata:
            totalsolved = await smcollection.count_documents({"user": int(userdata["_id"])})
            if totalsolved >= 33:
                return templates.TemplateResponse(
                    "error.html",
                    authenticator(userdata, {
                        "heading": "ESCAPE DAY",
                        "desc": "I'm travelling through the hallway after exiting the room i am very exhausted and i don't have the energy yet I'm running by burning my  life force to push on when i heard footsteps i quickly started to try the door handles in the hallway and on of the rooms opened. i entered inside and closed the door shut breathing a sigh of relief i looked around and i saw there were a few monitors playing CCTV footage of a room the white room! it had a few blood stains and scratches but it wasn't as messy as i remembered it was and the corpses were missing? a terror ran down my spine i went near them to inspect the room, it was empty i saw a file at the table labeled confidential i opened it and on the first page it was written experiment__. wait isn't that the same name which the speaker narrated in the start. my mind went into a spiral i had so many questions where am i? what was the purpose of all this ? when something hit me and the file fell from my hand how did i run i looked down slowly and realised that my leg was right there in one piece i was whole again i dropped to the ground holding my head in my hands because nothing was making any sense was it all a bad dream was i hallucinating then? or am i hallucinating now but everything felt so real i don't have blisters and frostbites on my body nothing makes sense there are people at the door banging on it I'm caught i don't know what to do or more like i have given up my mind cant take it anymore that's when the door opened a few men rushed to me and hit me with a bat and everything went dark…<br><br>I wake up, where am i ? i seem to be in a room where was i last i don't seem to remember my head hurts and there is this white noise in the background i look around myself and i appear to be in a white room with a CCTV camera and a speaker i was inspecting my surrounding when the speaker burst to life, 'Test subject looks conscious. fyodor romanov, age ____. This is day 1 of experiment ______.'",
                        "request": request
                    })
                )
    return RedirectResponse("/menu")

@level_route.get("/{experiment}/{etype}")
@limiter.limit("10/minute")
async def display_level(request: Request, experiment: int, etype: int):
    token = request.cookies.get("token")
    if token:
        if not validator(experiment, etype):
            return RedirectResponse("/menu")
        userdata = await usercollection.find_one({"token": token})
        if userdata:
            if userdata[f"{experiment}-{etype}"]["status"] == True:
                return templates.TemplateResponse(
                    "error.html",
                    authenticator(userdata, {
                        "heading": "ERROR",
                        "desc": "You have already completed this experiment level. <br> Please go back to the <a class='text-links' href='/menu'>menu</a> and select another experiment level.",
                        "request": request
                    })
                )
            if experiment == 0 and etype == 0:
                questiondata = await questioncollection.find_one({"_id": 0})
                questiondata = questiondata[Helper.reverse_attempt[etype]]
                return templates.TemplateResponse(
                    "level.html",
                    authenticator(userdata, {
                        "enumber": 0,
                        "edesc": questiondata["question"],
                        "evideo": questiondata["video"],
                        "eimg": questiondata["img"],
                        "eaudio": questiondata["audio"],
                        "request": request,
                        "experiment": experiment,
                        "user": userdata
                    })
                )
            if etype == 0:
                if userdata[f"{experiment-1}-0"]["status"] == True:
                    questiondata = await questioncollection.find_one({"_id": experiment})
                    questiondata = questiondata[Helper.reverse_attempt[etype]]
                    return templates.TemplateResponse(
                        "level.html",
                        authenticator(userdata, {
                            "enumber": experiment,
                            "edesc": questiondata["question"],
                            "evideo": questiondata["video"],
                            "eimg": questiondata["img"],
                            "eaudio": questiondata["audio"],
                            "request": request,
                            "experiment": experiment,
                            "user": userdata
                        })
                    )
                else:
                    return RedirectResponse("/menu")
            if userdata[f"{experiment}-{etype-1}"]["status"] == True:
                questiondata = await questioncollection.find_one({"_id": experiment})
                questiondata = questiondata[Helper.reverse_attempt[etype]]
                return templates.TemplateResponse(
                    "level.html",
                    authenticator(userdata, {
                        "enumber": experiment,
                        "edesc": questiondata["question"],
                        "evideo": questiondata["video"],
                        "eimg": questiondata["img"],
                        "eaudio": questiondata["audio"],
                        "request": request,
                        "experiment": experiment,
                        "user": userdata
                    })
                )
            else:
                return RedirectResponse("/menu")
