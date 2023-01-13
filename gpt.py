"""
This module contains the wrapper logic for interacting with GPT-3 as an LLM.
"""
import openai
from utils import retry, block_log_value
from prompts import (
    HUMAN_TITLE,
    INTRODUCTION,
    DIRECT_ANSWER_DIRECTIVE,
    MEMORY_DIRECTIVE,
    FALLABLE_DIRECTIVE,
    HUMILITY_DIRECTIVE,
    PROCESS_FAILURE_DIRECTIVE,
    PREPARATION,
)

PROMPT_PREFIX = f"""
{INTRODUCTION}

{DIRECT_ANSWER_DIRECTIVE}

{MEMORY_DIRECTIVE}

{FALLABLE_DIRECTIVE}

{HUMILITY_DIRECTIVE}

{PROCESS_FAILURE_DIRECTIVE}

{PREPARATION}
"""


def remove_hallucinated_master_response(text: str) -> str:
    if "MASTER:" in text:
        text = text.split("MASTER:")[0]
    return text


def get_gpt_response(text: str) -> str:
    MAX_LENGTH = int(4000 * 0.75)
    PREFIX_LENGTH = int(len(PROMPT_PREFIX) * 0.75)
    remaining_chars = int((MAX_LENGTH - PREFIX_LENGTH) * 0.75)
    text = text[-remaining_chars:]
    prompt = f"{PROMPT_PREFIX}\n{text}"
    block_log_value("USING PROMPT | LAST 100 CHARS", prompt[-100:])
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.0,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        # stop=[],
    )
    return remove_hallucinated_master_response(response.choices[0].text)  # type: ignore


def convert_to_prompt(text: str) -> str:
    return f"{HUMAN_TITLE}:\n\n{text}\n\nAssistant:"
