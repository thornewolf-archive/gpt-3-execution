import openai
from utils import retry
from prompts import (
    HUMAN_TITLE,
    INTRODUCTION,
    DIRECT_ANSWER_DIRECTIVE,
    MEMORY_DIRECTIVE,
    FALLABLE_DIRECTIVE,
    HUMILITY_DIRECTIVE,
    PROCESS_FAILURE_DIRECTIVE,
    CIVILITY_DIRECTIVE,
    REFERENCE_DIRECTIVE,
    PREPARATION,
)

PROMPT_PREFIX = f"""
{INTRODUCTION}

{DIRECT_ANSWER_DIRECTIVE}

{MEMORY_DIRECTIVE}

{FALLABLE_DIRECTIVE}

{HUMILITY_DIRECTIVE}

{PROCESS_FAILURE_DIRECTIVE}

{CIVILITY_DIRECTIVE}

{REFERENCE_DIRECTIVE}

{PREPARATION}
"""


def remove_hallucinated_master_response(text: str) -> str:
    if "MASTER:" in text:
        text = text.split("MASTER:")[0]
    return text


def get_gpt_response(text: str) -> str:
    MAX_LENGTH = 4097 // 2
    HEADER_LENGTH = len(PROMPT_PREFIX) // 4
    remaining_chars = (MAX_LENGTH - HEADER_LENGTH) * 2
    text = text[-remaining_chars:]
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"{PROMPT_PREFIX}\n{text}",
        temperature=0.0,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=["\n\nMaster", "\n\nRESPONSE", "Master"],
    )
    return remove_hallucinated_master_response(response.choices[0].text)  # type: ignore


def convert_to_prompt(text: str) -> str:
    return f"{HUMAN_TITLE}:\n\n{text}\n\nAssistant:"


print(convert_to_prompt("Hello"))
