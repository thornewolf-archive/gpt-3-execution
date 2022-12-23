import os
import requests
from dotenv import load_dotenv
from functools import wraps
from typing import Callable
from pydantic import BaseModel, Field
import openai

load_dotenv()

TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")


class User(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    last_name: str | None
    username: str | None
    language_code: str | None


class Chat(BaseModel):
    id: int
    first_name: str
    last_name: str | None
    username: str | None
    type: str


class Message(BaseModel):
    message_id: int
    user_from: User = Field(alias="from")
    text: str
    chat: Chat


class Update(BaseModel):
    update_id: int
    message: Message


def _provide_telegram_token(fn: Callable):
    assert TELEGRAM_API_KEY is not None

    @wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, token=TELEGRAM_API_KEY, **kwargs)

    return wrapper


def _send_telegram_api_request(
    method: str, payload: dict | None = None, token: str = ""
):
    assert token is not None
    assert token != ""
    base_uri = f"https://api.telegram.org/bot{token}/{method}"
    response = requests.post(base_uri, data=payload)

    if not (200 <= response.status_code < 300):
        raise Exception(
            f"Error: {response.status_code} {response.text} - Original request: {response.request.method} {response.request.url} {response.request.body}"
        )

    return response


@_provide_telegram_token
def get_updates_since_offset(token: str = "", offset: int = 0) -> list[Update]:
    method = "getUpdates"
    payload = {
        "offset": offset,
        "limit": 1,
        "timeout": 10,
    }
    response = _send_telegram_api_request(method, payload=payload, token=token)
    result = response.json()["result"]
    return [Update(**e) for e in result]


@_provide_telegram_token
def send_message(chat_id: int, text: str, token: str = "") -> None:
    if text.strip() == "":
        send_message(chat_id, "DEBUG: tried to end empty message")
        return
    method = "sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
    }
    try:
        _send_telegram_api_request(method, payload=payload, token=token)
    except Exception as e:
        print(f'Error sending message "{text[:10]}" to {chat_id}')
        raise e


def get_only_human_updates(updates: list[Update]) -> list[Update]:
    return [e for e in updates if not e.message.user_from.is_bot]
