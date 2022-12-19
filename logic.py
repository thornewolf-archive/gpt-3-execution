import os

from telegram import (
    get_updates_since_offset,
    filter_nonhuman_updates,
    Update,
    send_message,
)
from utils import (
    ChatHistory,
    get_gpt_response,
    record_in_history,
)
from gpt import user_input_as_prompt


def handle_commands(updates: list[Update], history: ChatHistory) -> list[Update]:
    unprocessed_updates = []
    for update in updates:
        if update.message.text == "/clear":
            history.clear()
            send_message(update.message.chat.id, "History cleared")
            continue
        unprocessed_updates.append(update)
    return unprocessed_updates


def parse_code(response: str) -> str:
    return response.replace("EXEC:\n", "").replace("DONE", "")


def get_response_for_chat_id(chat_id: int, history: ChatHistory) -> str:
    while True:
        response = get_gpt_response(history.get(chat_id))
        record_in_history(chat_id, response, history)
        if "EXEC" in response:
            code = parse_code(response)
            print("EXECUTING CODE")
            print(code)
            print()
            try:
                exec(code)
            except Exception as e:
                print(e)
                os.environ["ans"] = str(e)
            record_in_history(chat_id, user_input_as_prompt(os.environ["ans"]), history)
            continue
        break
    return response


def read_and_respond_to_chats_forever():
    offset = 2083323969
    history = ChatHistory()
    while True:
        updates = get_updates_since_offset(offset=offset)
        if len(updates) > 0:
            offset = max([e.update_id for e in updates]) + 1

        updates = filter_nonhuman_updates(updates)
        updates = handle_commands(updates, history)
        for update in updates:
            chat_id = update.message.chat.id

            prompt = user_input_as_prompt(update.message.text)
            record_in_history(chat_id, prompt, history)
            response = get_response_for_chat_id(chat_id, history)
            record_in_history(chat_id, response, history)
            send_message(chat_id, response)
