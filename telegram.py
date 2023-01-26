"""
Module for interfacing with telegram as a frontend.
"""

import os
import requests
from dotenv import load_dotenv
from functools import wraps
from typing import Callable
from pydantic import BaseModel, Field
import openai
from text_interface import TextInterface
from text_interface import Message as TextInterfaceMessage

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


def create_update(data):
    try:
        return Update(**data)
    except Exception as e:
        return None


@_provide_telegram_token
def get_new_message_updates(
    token: str = "", offset: int = 0
) -> tuple[list[Update], int]:
    method = "getUpdates"
    payload = {
        "offset": offset,
        "limit": 10,
        "timeout": 10,
    }
    response = _send_telegram_api_request(method, payload=payload, token=token)
    result = response.json()["result"]

    if len(result) == 0:
        return [], offset
    new_offset = max([e["update_id"] for e in result]) + 1
    print(f"New offset: {new_offset}")
    updates = [create_update(e) for e in result]
    return [u for u in updates if u is not None], new_offset


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
        print(e)


def filter_to_human_updates(updates: list[Update]) -> list[Update]:
    return [e for e in updates if not e.message.user_from.is_bot]


class TelegramInterface(TextInterface):
    def __init__(self):
        self.message_read_offset = 0

    def get_new_messages(self) -> list[TextInterfaceMessage]:
        updates, new_offset = get_new_message_updates(offset=self.message_read_offset)
        if len(updates) == 0:
            return []
        self.message_read_offset = new_offset
        updates = filter_to_human_updates(updates)
        return [
            TextInterfaceMessage(
                text=update.message.text,
                message_id=str(update.message.message_id),
                user_id=str(update.message.user_from.id),
                chat_id=str(update.message.chat.id),
            )
            for update in updates
        ]

    def send_message(self, original_message: TextInterfaceMessage, body: str):
        send_message(int(original_message.chat_id), body)
