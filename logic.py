import os

from prompts import (
    MASTER_CONTINUE_TEMPLATE,
    CODE_RESULT_TEMPLATE,
    ERROR_RESULT_TEMPLATE,
)
from telegram import (
    get_updates_since_offset,
    get_only_human_updates,
    Update,
    send_message,
)
from utils import ChatHistory, record_in_history, log_value_annotated, get_ans, set_ans
from gpt import convert_to_prompt, get_gpt_response


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
    log_value_annotated("HANDLING EXEC COMMAND", response)
    try:
        exec(block)
    except Exception as e:
        set_ans(ERROR_RESULT_TEMPLATE.format(e))
    result = CODE_RESULT_TEMPLATE.format(get_ans())
    return result


def handle_process(response: str) -> str:
    block = parse_block("PROCESS:", response)
    log_value_annotated("HANDLING PROCESS COMMAND", response)
    return MASTER_CONTINUE_TEMPLATE


def intercept_ai_commands(
    response: str, chat_id: int, history: ChatHistory
) -> str | None:
    """
    Intercept commands from the AI.

    Supported commands:
    EXEC: <code> DONE
    PROCESS: <code> DONE

    Returns True if a command was intercepted, False otherwise.
    """
    result = None
    if "EXEC" in response:
        result = handle_exec(response)
    if "PROCESS" in response:
        result = handle_process(response)
    return result


def get_llm_completion_for_chat(chat_id: int, history: ChatHistory) -> str:
    """
    Gets a completion from the LLM for a given chat.

    Returns the completion as a string.
    """
    while True:
        response = get_gpt_response(history.get(chat_id))
        record_in_history(chat_id, response, history)
        log_value_annotated("GOT RESPONSE FROM GPT", response)
        if (
            command_result := intercept_ai_commands(response, chat_id, history)
        ) is not None:
            record_in_history(chat_id, command_result, history)
            continue
        break
    return response


def read_and_respond_to_chats_forever():
    offset = 0
    history = ChatHistory()
    while True:
        updates = get_updates_since_offset(offset=offset)
        if len(updates) == 0:
            continue
        log_value_annotated("GOT UPDATES", updates)
        offset = max([e.update_id for e in updates]) + 1

        updates = get_only_human_updates(updates)
        updates = handle_user_commands(updates, history)
        for update in updates:
            chat_id = update.message.chat.id
            prompt = convert_to_prompt(update.message.text)
            record_in_history(chat_id, prompt, history)
            response = get_llm_completion_for_chat(chat_id, history)
            send_message(chat_id, response)
