import sys
from dotenv import load_dotenv
from functools import wraps
from typing import Callable
from pydantic import BaseModel, Field
import openai
from collections import defaultdict
from telegram import (
    Update,
)
from gpt import get_gpt_response, user_input_as_prompt


class ChatHistory:
    def __init__(self):
        self.history: defaultdict[int, list[str]] = defaultdict(list)

    def add(self, chat_id: int, message: str):
        if sys.getsizeof(self.history) > 1 * 1024:  # 1kb
            self.clear()
        self.history[chat_id].append(message)

    def get(self, chat_id: int) -> str:
        return "\n".join(self.history[chat_id])

    def clear(self):
        for k in self.history.keys():
            self.history[k] = []


def record_in_history(chat_id: int, text: str, history: ChatHistory):
    history.add(chat_id, text)
    print("HISTORY")
    print(history.get(chat_id))


