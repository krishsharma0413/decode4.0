from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from variables import limiter

socials_route = APIRouter(
    prefix="/socials",
)

@socials_route.get("/discord")
@limiter.limit("5/minute")
async def discord(request: Request):
    return RedirectResponse("https://discord.gg/AxfQAtHrjr")