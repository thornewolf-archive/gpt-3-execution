"""
Generic interface for text-based messengers. This allows for alternative frontends to be used to the initial Telegram frontend.
"""

from dataclasses import dataclass
from abc import ABC


@dataclass
class Message:
    text: str
    message_id: str
    user_id: str
    chat_id: str


class TextInterface(ABC):
    def get_new_messages(self) -> list[Message]:
        ...

    def send_message(self, original_message: Message, body: str):
        ...
