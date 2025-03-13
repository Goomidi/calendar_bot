import subprocess

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from app.core.config import bot_procs
from app.utils.daily import create_room_and_token

router = APIRouter()


@router.get("/")
async def bot_calendar_connect() -> RedirectResponse:
    room_url, token = await create_room_and_token()

    try:
        proc = subprocess.Popen(
            [f"python3 -m app.bot.main -u {room_url} -t {token}"],
            shell=True,
            bufsize=1,
        )
        bot_procs.add_proc(proc, room_url)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start subprocess: {e}",
        )

    return RedirectResponse(room_url)
