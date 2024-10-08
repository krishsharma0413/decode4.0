from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from variables import limiter, templates

backlink_route = APIRouter(
    prefix="/backlink",
)

data = {
    "gray": "well you did find a backlink, but not the right one...",
    "totally-hidden": "well you found it! the answer to the question the name of the event itself.",
    "dn9327hao3jk": "<img src='/static/assets/images/asikudg23780eyai.png'><br>“Fair is Foul, and Foul is Fair” #🎨 ®️🚗",
    "gasgasgas": "<a href='https://www.unep.org/news-and-stories/story/three-ways-we-can-better-use-nitrogen-farming'>1</a> <a href='https://www.rsc.org/periodic-table/element/12/magnesium'>2</a> <a href='https://www.britannica.com/technology/niobium-processing'>3</a>"
}

@backlink_route.get("/{backlink}", response_class=HTMLResponse)
@limiter.limit("3/minute")
async def discord(request: Request, backlink: str):
    if data.get(backlink):
        return HTMLResponse(content=data[backlink])
    else:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "heading": "ERROR",
                "desc": "The backlink you are trying to access does not exist. Maybe you are looking at the clue wrong?"
            }
        )
        