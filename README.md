# Google Calendar AI Planner

A voice-controlled AI assistant that integrates with Google Calendar for scheduling and managing events through natural conversation.

## Features

- **Voice Interaction**: Communicate with the AI assistant using natural language
- **Google Calendar Integration**: Create, update, and manage calendar events
- **Real-Time Voice Interface (RTVI)**: Powered by PipeCat for seamless voice interaction

## Prerequisites

- Python 3.12+
- Google Cloud Platform account with Calendar API enabled
- API keys for:
  - Daily.co
  - OpenAI

## Setup

1. **Clone the repository**

```bash
git clone https://github.com/goomidi/calendar_bot.git
cd calendar_bot
```

2. **Set up a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install uv
uv sync
```

4. **Configure Google Calendar API**

- Create a project in Google Cloud Console
- Enable the Google Calendar API
- Create OAuth credentials and download as `google_oauth.json`
- Place the file in the project root directory

5. **Set up environment variables**

Copy `.env.example` into a `.env` file in the project root and modify the following variables:

```
DAILY_API_KEY=your_daily_api_key
DAILY_API_URL=your_daily_api_url
DAILY_SAMPLE_ROOM_URL=your_daily_sample_room_url
OPENAI_API_KEY=your_openai_api_key
```

## Running the Application

### Local Development

```bash
uv run fastapi dev app/run.py
```

### Docker

```bash
docker compose up -d
```

## Usage

1. Access the application at `http://localhost:8000`
2. Connect to a voice room by visiting `/api/calendar/connect`
3. Speak naturally to the assistant to:
   - Create calendar events
   - Update the created event

## API Endpoints

- `GET /api/calendar/connect`: Connect to a voice room with the AI assistant

## Architecture

- **FastAPI**: Web framework for the API
- **PipeCat**: Real-time voice interaction pipeline
- **Daily.co**: WebRTC platform for voice communication
- **Google Calendar API**: For calendar management
- **Open AI LLM**: For handling reservations

## License

[MIT License](LICENSE)
