import os

from telegram import (
    get_updates_since_offset,
    filter_nonhuman_updates,
    Update,
    send_message,
)
from utils import ChatHistory, record_in_history, block_log_value, get_ans, set_ans
from gpt import user_input_as_prompt, get_gpt_response

CODE_RESULT_TEMPLATE = """
MASTER:
CODE RESULT
{}
"""

ERROR_RESULT_TEMPLATE = """
MASTER:
ERROR
{}
Show me your code without the EXEC: and DONE lines. Also tell me what the error was."""

MASTER_CONTINUE_TEMPLATE = """
MASTER:
continue.

"""


def handle_user_commands(updates: list[Update], history: ChatHistory) -> list[Update]:
    """
    Handle commands from the user.

    Supported commands:
    /clear - clear the history
    """
    unprocessed_updates = []
    for update in updates:
        if update.message.text == "/clear":
            history.clear()
            send_message(update.message.chat.id, "History cleared")
            continue
        unprocessed_updates.append(update)
    return unprocessed_updates


def parse_block(header: str, response: str) -> str:
    """
    Parse the code from the response.

    The response should be of the form:
    "EXEC: <code> DONE
    """
    exec_end = response.find(header) + len(header)
    done_start = response.find("DONE")
    return response[exec_end:done_start]


def handle_exec(response: str) -> str:
    block = parse_block("EXEC:", response)
    block_log_value("HANDLING EXEC COMMAND", response)
    try:
        exec(block)
    except Exception as e:
        set_ans(ERROR_RESULT_TEMPLATE.format(e))
    result = CODE_RESULT_TEMPLATE.format(get_ans())
    return result


def handle_process(response: str) -> str:
    block = parse_block("PROCESS:", response)
    block_log_value("HANDLING PROCESS COMMAND", response)
    return MASTER_CONTINUE_TEMPLATE


def handle_commands(response: str, chat_id: int, history: ChatHistory) -> bool:
    if "EXEC" in response:
        result = handle_exec(response)
        record_in_history(chat_id, result, history)
        return True
    if "PROCESS" in response:
        result = handle_process(response)
        record_in_history(chat_id, result, history)
        return True
    return False


def get_response_for_chat_id(chat_id: int, history: ChatHistory) -> str:
    while True:
        response = get_gpt_response(history.get(chat_id))
        record_in_history(chat_id, response, history)
        block_log_value("GOT RESPONSE FROM GPT", response)
        if handle_commands(response, chat_id, history):
            continue
        break
    return response


def read_and_respond_to_chats_forever():
    offset = 2083323969
    history = ChatHistory()
    while True:
        updates = get_updates_since_offset(offset=offset)
        if len(updates) == 0:
            continue
        block_log_value("GOT UPDATES", updates)
        offset = max([e.update_id for e in updates]) + 1

        updates = filter_nonhuman_updates(updates)
        updates = handle_user_commands(updates, history)
        for update in updates:
            chat_id = update.message.chat.id
            prompt = user_input_as_prompt(update.message.text)
            record_in_history(chat_id, prompt, history)
            response = get_response_for_chat_id(chat_id, history)
            send_message(chat_id, response)
