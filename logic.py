"""
This file contains the business logic for interacting with the LLM.

It handles user commands/messages, as well as the LLM's responses/directives.

"""


from prompts import (
    MASTER_CONTINUE_TEMPLATE,
    MASTER_USE_DATA_TEMPLATE,
    CODE_RESULT_TEMPLATE,
    ERROR_RESULT_TEMPLATE,
)
from utils import ChatHistory, record_in_history, block_log_value, get_ans, set_ans
from gpt import convert_to_prompt, get_gpt_response
from text_interface import Message, TextInterface


def handle_user_message(
    message: Message, history: ChatHistory, chat_interface: TextInterface
):
    """
    Handle a message from the user.

    Passes the message to the LLM and sends the response to the user.
    """
    prompt = convert_to_prompt(message.text)
    record_in_history(message.chat_id, prompt, history)
    response = get_llm_completion_for_chat(message.chat_id, history)
    chat_interface.send_message(message, response)


def handle_user_commands(
    messages: list[Message], history: ChatHistory, text_interface: TextInterface
) -> list[Message]:
    """
    Handle commands from the user.

    Supported commands:
    /clear - clear the history
    """
    unprocessed_messages = []
    for message in messages:
        if message.text == "/clear":
            history.clear()
            text_interface.send_message(message, "History cleared")
            continue
        unprocessed_messages.append(message)
    return unprocessed_messages


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


def handle_empty_response(response: str) -> str:
    block_log_value("HANDLING EMPTY RESPONSE", response)
    return MASTER_USE_DATA_TEMPLATE


def maybe_intercept_ai_response(
    response: str, chat_id: str, history: ChatHistory
) -> str | None:
    """
    Intercept commands from the AI.

    Supported commands:
    EXEC: <code> DONE
    PROCESS: <code> DONE

    Returns True if a command was intercepted, False otherwise.
    """
    result = None
    # AI is running cod
    if "EXEC" in response:
        result = handle_exec(response)
    # AI is planning
    if "PROCESS" in response:
        result = handle_process(response)
    if len(response) < 5:
        result = handle_empty_response(response)
        result = None
    return result


def get_llm_completion_for_chat(chat_id: str, history: ChatHistory) -> str:
    """
    Gets a completion from the LLM for a given chat.

    Returns the completion as a string.
    """
    while True:
        response = get_gpt_response(history.get(chat_id))
        record_in_history(chat_id, response, history)
        block_log_value(
            "GOT RESPONSE FROM GPT",
            f"{response}",
        )
        intercept_result = maybe_intercept_ai_response(response, chat_id, history)
        if intercept_result is not None:
            record_in_history(chat_id, intercept_result, history)
            continue
        break
    return response


def write_history_into_file(history: ChatHistory):
    with open("history.txt", "w") as f:
        for chat_id, chat_history in history.history.items():
            f.write(f"Chat {chat_id}\n")
            f.write("\n".join(chat_history))


def read_and_respond_to_chats_forever(
    history: ChatHistory, chat_interface: TextInterface
):
    while True:
        messages = chat_interface.get_new_messages()
        if len(messages) == 0:
            continue
        block_log_value("RECEIVED USER MESSAGE", messages)

        remaining_messages = handle_user_commands(messages, history, chat_interface)
        for message in remaining_messages:
            handle_user_message(message, history, chat_interface)
        write_history_into_file(history)
