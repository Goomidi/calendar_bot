import argparse

import aiohttp
from pipecat.transports.services.helpers.daily_rest import DailyRESTHelper

from app.core.config import settings


async def configure(aiohttp_session: aiohttp.ClientSession) -> tuple[str, str]:
    (url, token, _) = await configure_with_args(aiohttp_session)

    return (url, token)


async def configure_with_args(
    aiohttp_session: aiohttp.ClientSession,
    parser: argparse.ArgumentParser | None = None,
) -> tuple[str, str, argparse.Namespace]:
    if not parser:
        parser = argparse.ArgumentParser(description="Daily AI SDK Bot Sample")
    parser.add_argument(
        "-u", "--url", type=str, required=False, help="URL of the Daily room to join"
    )
    parser.add_argument(
        "-k",
        "--apikey",
        type=str,
        required=False,
        help="Daily API Key (needed to create an owner token for the room)",
    )

    args, unknown = parser.parse_known_args()

    url = args.url or settings.DAILY_SAMPLE_ROOM_URL
    key = args.apikey or settings.DAILY_API_KEY

    if not url:
        raise Exception(
            "No Daily room specified. use the -u/--url option from the command line, or set DAILY_SAMPLE_ROOM_URL in your environment to specify a Daily room URL."
        )

    if not key:
        raise Exception(
            "No Daily API key specified. use the -k/--apikey option from the command line, or set DAILY_API_KEY in your environment to specify a Daily API key, available from https://dashboard.daily.co/developers."
        )

    daily_rest_helper = DailyRESTHelper(
        daily_api_key=key,
        daily_api_url=settings.DAILY_API_URL,
        aiohttp_session=aiohttp_session,
    )

    expiry_time: float = 60 * 60

    token = await daily_rest_helper.get_token(url, expiry_time)

    return (url, token, args)
