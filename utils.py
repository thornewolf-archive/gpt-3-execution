import sys
from functools import wraps
from typing import Callable, Any
from collections import defaultdict
import os
import logging

logger = logging.getLogger(__name__)

"""
This module contains various utilities for the project.
"""


class ChatHistory:
    def __init__(self):
        self.history: defaultdict[str, list[str]] = defaultdict(list)

    def add(self, chat_id: str, message: str):
        if sys.getsizeof(self.history) > 1 * 1024:  # 1kb
            self.clear()
        self.history[chat_id].append(message)

    def get(self, chat_id: str) -> str:
        return "\n".join(self.history[chat_id])

    def clear(self):
        for k in self.history.keys():
            self.history[k] = []


def write_history_into_file(history: ChatHistory):
    print("Writing history into file...")
    with open("history.txt", "w") as f:
        for chat_id, chat_history in history.history.items():
            f.write(f"Chat {chat_id}\n")
            f.write("\n".join(chat_history))


def record_in_history(chat_id: str, text: str, history: ChatHistory):
    history.add(chat_id, text)
    # log_value_annotated("CHAT HISTORY", history.get(chat_id))


def retry(times: int = 3):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Error: {e}")

        return wrapper

    return decorator


def log_event(statement: str, value: Any):
    logger.log(
        21,
        f"""
#####################################################
{statement.upper()}
______________________________________________________
{value}
______________________________________________________

    """,
    )


def set_ans(value: str):
    os.environ["ans"] = value


def get_ans() -> str:
    return os.environ.get("ans", "")
