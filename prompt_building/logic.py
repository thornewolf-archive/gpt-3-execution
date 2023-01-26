from utils import ChatHistory, log_event, write_history_into_file
from text_interface import Message, TextInterface
from prompt_building import templates
from prompt_building.prompts import Prompt
from gpt import get_gpt_response
import re


def handle_code_execution(text: str):
    import os

    try:
        exec(text)
        return os.environ["ANSWER"].strip()
    except Exception as e:
        return f"Error: {e}"


def is_code_execution(text: str) -> bool:
    if "def solve" in text:
        return True
    return False


def resolve_ai_response(message: str, history: str) -> str:
    response = ""
    context = Prompt("")
    still_need_response = True
    while still_need_response:
        routing_prompt = templates.ROUTING_TEMPLATE.supply(
            prompt=message, context=context.text, history=history
        ).text
        routing_response = get_gpt_response(routing_prompt).strip()
        templated_prompt = (
            templates.prompt_template_mapping.get(
                routing_response, templates.UNSURE_TEMPLATE
            )
            .supply(prompt=message, context=context.text, history=history)
            .text
        )
        response = get_gpt_response(templated_prompt)

        log_event("ROUTING PROMPT", routing_prompt)
        log_event("ROUTING DECISION", routing_response)
        log_event("FILLED TEMPLATE", templated_prompt)
        log_event("RESPONSE", response)
        if is_code_execution(response):
            command_result = handle_code_execution(response)
            context = context.add(
                f"""
{routing_response}:
{response}
# ANSWER = {command_result}\n"""
            )

        still_need_response = False
        if routing_response in ("WRITE_CODE_TEMPLATE"):
            still_need_response = True
    return response


def handle_user_commands(
    messages: list[Message], history: ChatHistory, text_interface: TextInterface
) -> list[Message]:
    return messages


def to_user_message(text: str):
    return "USER: " + text


def to_ai_message(text: str):
    return "AI: " + text


def handle_user_message(
    message: Message, history: ChatHistory, chat_interface: TextInterface
):
    response = resolve_ai_response(message.text, history.get(message.chat_id))
    chat_interface.send_message(message, response)

    history.add(message.chat_id, to_user_message(message.text))
    history.add(message.chat_id, to_ai_message(response))


def main_conversation_loop(history: ChatHistory, chat_interface: TextInterface):
    while True:
        messages = chat_interface.get_new_messages()
        if len(messages) == 0:
            continue
        log_event("RECEIVED USER MESSAGE", messages)

        remaining_messages = handle_user_commands(messages, history, chat_interface)
        for message in remaining_messages:
            handle_user_message(message, history, chat_interface)
        write_history_into_file(history)
