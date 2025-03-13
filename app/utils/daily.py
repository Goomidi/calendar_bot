from fastapi import HTTPException
from pipecat.transports.services.helpers.daily_rest import (
    DailyRoomParams,
)

from app.core.config import daily_helpers


async def create_room_and_token() -> tuple[str, str]:
    """Helper function to create a Daily room and generate an access token.

    Returns:
        tuple[str, str]: A tuple containing (room_url, token)

    Raises:
        HTTPException: If room creation or token generation fails
    """
    room = await daily_helpers["rest"].create_room(DailyRoomParams())

    if not room.url:
        raise HTTPException(status_code=500, detail="Failed to create room")

    token = await daily_helpers["rest"].get_token(room.url)
    if not token:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get token for room: {room.url}",
        )

    return room.url, token
