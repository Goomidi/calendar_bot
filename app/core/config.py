import os
import subprocess

from fastapi.templating import Jinja2Templates
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_PATH = os.getcwd()
TEMPLATES_PATH = os.path.join(BASE_PATH, "app", "templates")
UTILS_PATH = os.path.join(BASE_PATH, "app", "utils")


class Settings(BaseSettings):
    DAILY_API_KEY: str
    DAILY_API_URL: str = "https://api.daily.co/v1"
    DAILY_SAMPLE_ROOM_URL: str

    OPENAI_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=[
            ".env",
            ".env.example",
        ],
        env_ignore_empty=True,
        extra="ignore",
    )


class BotProcs:
    def __init__(self):
        self.procs = {}

    def add_proc(self, proc: subprocess.Popen, room_url: str) -> None:
        self.procs[proc.pid] = (proc, room_url)

    def get_proc(self, pid: int) -> tuple[subprocess.Popen, str] | None:
        return self.procs.get(pid)

    def remove_proc(self, pid: int) -> None:
        del self.procs[pid]

    def cleanup(self) -> None:
        for proc in self.procs.values():
            proc[0].terminate()
            proc[0].wait()


settings = Settings()
templates = Jinja2Templates(directory=TEMPLATES_PATH)

daily_helpers = {}
bot_procs = BotProcs()
