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
    exec_end = response.find("EXEC:") + 5
    done_start = response.find("DONE")
    return response[exec_end:done_start]


def handle_exec(response: str) -> str:
    code = parse_code(response)
    print("RUNNING CODE BLOCK")
    print("__________________")
    print(f"Code: {response}")
    print("__________________")
    print("END CODE BLOCK")
    try:
        exec(code)
    except Exception as e:
        os.environ[
            "ans"
        ] = f"""ERROR: {e}
                Show me your code without the EXEC: and DONE lines. Also tell me what the error was."""
    result = f"""
MASTER:
CODE RESULT
{os.environ.get("ans", "")}
            """
    return result


def get_response_for_chat_id(chat_id: int, history: ChatHistory) -> str:
    while True:
        response = get_gpt_response(history.get(chat_id))
        record_in_history(chat_id, response, history)
        print("GOT RESPONSE FROM CHAT ID")
        print("__________________")
        print(response)
        print("__________________")
        if "EXEC" in response:
            code_result = handle_exec(response)
            record_in_history(chat_id, code_result, history)
            continue
        break
    return response


def read_and_respond_to_chats_forever():
    offset = 2083323969
    history = ChatHistory()
    while True:
        print("GETTING UPDATES")
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
            # record_in_history(chat_id, response, history)
            send_message(chat_id, response)
