import sys
from functools import wraps
from typing import Callable, Any
from collections import defaultdict
import os


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
    block_log_value("CHAT HISTORY", history.get(chat_id))


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


def block_log_value(statement: str, value: Any):
    print()
    print(statement.upper())
    print("__________________" * 3)
    print(value)
    print("__________________" * 3)
    print()


def set_ans(value: str):
    os.environ["ans"] = value


def get_ans() -> str:
    return os.environ.get("ans", "")
