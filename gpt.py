"""
This module contains the wrapper logic for interacting with GPT-3 as an LLM.
"""
import openai
import logging
import os
from prompts import (
    HUMAN_TITLE,
    INTRODUCTION,
    DIRECT_ANSWER_DIRECTIVE,
    MEMORY_DIRECTIVE,
    FALLABLE_DIRECTIVE,
    HUMILITY_DIRECTIVE,
    PROCESS_DIRECTIVE,
    PROCESS_FAILURE_DIRECTIVE,
    PREPARATION,
)

PROMPT_PREFIX = f"""
{INTRODUCTION}

{DIRECT_ANSWER_DIRECTIVE}

{MEMORY_DIRECTIVE}

{FALLABLE_DIRECTIVE}

{HUMILITY_DIRECTIVE}

{PROCESS_DIRECTIVE}

{PROCESS_FAILURE_DIRECTIVE}

{PREPARATION}
"""

logger = logging.getLogger(__name__)


def remove_hallucinated_master_response(text: str) -> str:
    if "MASTER:" in text:
        text = text.split("MASTER:")[0]
    return text


def write_most_recent_prompt_to_file_if_enabled(prompt: str):
    if os.environ.get("ENABLE_WRITE_PROMPT_TO_FILE", "0") != "1":
        print("skipping")
        return
    with open("most_recent_prompt.txt", "w") as f:
        f.write(prompt)


def get_gpt_prefixed_response(text: str) -> str:
    prompt = f"{PROMPT_PREFIX}\n{text}"
    write_most_recent_prompt_to_file_if_enabled(prompt)
    response = get_gpt_response(prompt)
    return remove_hallucinated_master_response(response)


def get_gpt_response(text: str) -> str:
    logger.info(f"Sending prompt to GPT-3: {text}")
    return (
        openai.Completion.create(
            engine="text-davinci-003",
            prompt=text,
            temperature=0.0,
            max_tokens=500,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6,
        )
        .choices[0]  # type: ignore
        .text  # type: ignore
    )


def convert_to_human_message(text: str) -> str:
    """
    Format the text as a message from human's side of the conversation.
    """
    return f"{HUMAN_TITLE}:\n\n{text}\n\nAssistant:"
