from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import aiohttp
from fastapi import FastAPI
from pipecat.transports.services.helpers.daily_rest import DailyRESTHelper

from app.core.config import bot_procs, daily_helpers, settings


def init_app(init_db=True):
    lifespan = None

    if init_db:

        @asynccontextmanager
        async def lifespan(_: FastAPI) -> AsyncIterator[None]:
            aiohttp_session = aiohttp.ClientSession()

            daily_helpers["rest"] = DailyRESTHelper(
                daily_api_key=settings.DAILY_API_KEY,
                daily_api_url=settings.DAILY_API_URL,
                aiohttp_session=aiohttp_session,
            )

            yield

            await aiohttp_session.close()
            bot_procs.cleanup()

    app = FastAPI(
        title="Calendar Reservation API",
        description="API for calendar reservations with voice input",
        version="0.1.0",
        debug=True,
        lifespan=lifespan,
    )

    from app.api.endpoints import router

    app.include_router(router, prefix="/api")

    return app
