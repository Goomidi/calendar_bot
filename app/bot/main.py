import asyncio
import datetime
from collections.abc import Callable

import aiohttp
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.processors.frameworks.rtvi import RTVIConfig, RTVIProcessor
from pipecat.services.openai import OpenAILLMService, OpenAITTSService
from pipecat.transports.services.daily import (
    DailyParams,
    DailyTranscriptionSettings,
    DailyTransport,
)

from app.bot.runner import configure
from app.core.config import settings
from app.utils.google import create_event, update_event


async def fetch_current_date(
    function_name: str,
    tool_call_id: str,
    args: dict,
    llm: OpenAILLMService,
    context: OpenAILLMContext,
    result_callback: Callable,
):
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    await result_callback(current_date)


async def create_calendar_reservation(
    function_name: str,
    tool_call_id: str,
    args: dict,
    llm: OpenAILLMService,
    context: OpenAILLMContext,
    result_callback: Callable,
):
    summary = args.get("summary", "Untitled Event")
    start_time_str = args.get("start_time")
    duration_minutes = args.get("duration_minutes", 30)
    description = args.get("description", "")
    location = args.get("location", "")
    attendees = args.get("attendees", [])

    start_time = datetime.datetime.fromisoformat(start_time_str)

    try:
        event = create_event(
            summary=summary,
            start_time=start_time,
            duration_minutes=duration_minutes,
            description=description,
            location=location,
            attendees=attendees,
        )

        result = {
            "status": "success",
            "event_id": event.get("id"),
            "summary": summary,
            "start_time": start_time_str,
            "link": event.get("htmlLink", ""),
        }

    except Exception as e:
        result = {
            "status": "error",
            "message": f"Failed to create calendar event: {e!s}",
        }

    await result_callback(result)


async def update_calendar_reservation(
    function_name: str,
    tool_call_id: str,
    args: dict,
    llm: OpenAILLMService,
    context: OpenAILLMContext,
    result_callback: Callable,
):
    event_id = args.get("event_id")
    summary = args.get("summary")
    start_time_str = args.get("start_time")
    duration_minutes = args.get("duration_minutes")
    description = args.get("description")
    location = args.get("location")
    attendees = args.get("attendees")

    if start_time_str:
        start_time = datetime.datetime.fromisoformat(start_time_str)

    else:
        start_time = None

    try:
        if not event_id:
            raise ValueError("Event ID is required")

        event = update_event(
            event_id=event_id,
            summary=summary,
            start_time=start_time,
            duration_minutes=duration_minutes,
            description=description,
            location=location,
            attendees=attendees,
        )

        result = {
            "status": "success",
            "event_id": event.get("id"),
            "summary": summary,
            "start_time": start_time_str,
            "link": event.get("htmlLink", ""),
        }

    except Exception as e:
        result = {
            "status": "error",
            "message": f"Failed to update calendar event: {e!s}",
        }

    await result_callback(result)


async def main():
    async with aiohttp.ClientSession() as session:
        (room_url, token) = await configure(session)

        transport = DailyTransport(
            room_url,
            token,
            "Google Calendar Bot",
            DailyParams(
                audio_out_enabled=True,
                vad_enabled=True,
                vad_analyzer=SileroVADAnalyzer(),
                transcription_enabled=True,
                transcription_settings=DailyTranscriptionSettings(
                    language="fr",
                    model="nova-2-general",
                ),
            ),
        )

        llm = OpenAILLMService(api_key=settings.OPENAI_API_KEY, model="gpt-4o")

        llm.register_function(
            "get_current_date",
            fetch_current_date,
        )

        llm.register_function(
            "make_calendar_reservation",
            create_calendar_reservation,
        )

        llm.register_function(
            "update_calendar_reservation",
            update_calendar_reservation,
        )

        messages = [
            {
                "role": "system",
                "content": """
                Tu es un assistant de réservation de rendez-vous sur Google Calendar dans un appel WebRTC.

                Quand on te donne les détails de la réservation, tu dois faire appel à la fonction "make_calendar_reservation" pour créer la réservation ou "update_calendar_reservation" pour mettre à jour la réservation.
                Tu as également la possibilité de faire appel à la fonction "get_current_date" pour obtenir la date et l'heure actuelles.

                Ta réponse sera convertie en audio et diffusée à l'utilisateur donc n'inclut pas de caractères spéciaux dans ta réponse.
                """,
            },
        ]

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_current_date",
                    "description": "Retrieve the current date and time.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "make_calendar_reservation",
                    "description": "Create a reservation on Google Calendar with specified details.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "summary": {
                                "type": "string",
                                "description": "Title of the calendar event",
                            },
                            "start_time": {
                                "type": "string",
                                "description": "Start time of the event in ISO format (YYYY-MM-DDTHH:MM:SS)",
                            },
                            "duration_minutes": {
                                "type": "integer",
                                "description": "Duration of the event in minutes",
                                "default": 30,
                            },
                            "description": {
                                "type": "string",
                                "description": "Detailed description of the event",
                            },
                            "location": {
                                "type": "string",
                                "description": "Physical or virtual location of the event",
                            },
                            "attendees": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of email addresses for attendees",
                            },
                        },
                        "required": ["summary", "start_time"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "update_calendar_reservation",
                    "description": "Update a reservation on Google Calendar with specified details.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "event_id": {
                                "type": "string",
                                "description": "ID of the calendar event to update",
                            },
                            "summary": {
                                "type": "string",
                                "description": "Title of the calendar event",
                            },
                            "start_time": {
                                "type": "string",
                                "description": "Start time of the event in ISO format (YYYY-MM-DDTHH:MM:SS)",
                            },
                            "duration_minutes": {
                                "type": "integer",
                                "description": "Duration of the event in minutes",
                                "default": 30,
                            },
                            "description": {
                                "type": "string",
                                "description": "Detailed description of the event",
                            },
                            "location": {
                                "type": "string",
                                "description": "Physical or virtual location of the event",
                            },
                            "attendees": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of email addresses for attendees",
                            },
                        },
                        "required": ["event_id"],
                    },
                },
            },
        ]

        context = OpenAILLMContext(messages=messages, tools=tools)
        context_aggregator = llm.create_context_aggregator(context)

        tts = OpenAITTSService(
            api_key=settings.OPENAI_API_KEY,
            voice="nova",
            model="tts-1-hd",
        )

        rtvi = RTVIProcessor(config=RTVIConfig(config=[]))

        pipeline = Pipeline(
            [
                transport.input(),
                rtvi,
                context_aggregator.user(),
                llm,
                tts,
                transport.output(),
                context_aggregator.assistant(),
            ]
        )

        task = PipelineTask(
            pipeline,
            params=PipelineParams(
                allow_interruptions=True,
                enable_metrics=True,
                enable_usage_metrics=True,
            ),
        )

        @rtvi.event_handler("on_client_ready")
        async def on_client_ready(rtvi: RTVIProcessor):
            await rtvi.set_bot_ready()

        @transport.event_handler("on_first_participant_joined")
        async def on_first_participant_joined(
            transport: DailyTransport,
            participant: dict,
        ):
            await transport.capture_participant_transcription(participant["id"])
            await task.queue_frames([context_aggregator.user().get_context_frame()])

        @transport.event_handler("on_participant_left")
        async def on_participant_left(
            transport: DailyTransport,
            participant: dict,
            reason: str,
        ):
            await task.cancel()

        runner = PipelineRunner()

        await runner.run(task)


if __name__ == "__main__":
    asyncio.run(main())
