"""
This module contains the wrapper logic for interacting with GPT-3 as an LLM.
"""
import openai
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


def remove_hallucinated_master_response(text: str) -> str:
    if "MASTER:" in text:
        text = text.split("MASTER:")[0]
    return text


def write_most_recent_prompt_to_file(prompt: str):
    with open("most_recent_prompt.txt", "w") as f:
        f.write(prompt)


def get_gpt_response(text: str) -> str:
    prompt = f"{PROMPT_PREFIX}\n{text}"
    write_most_recent_prompt_to_file(prompt)
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.0,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
    )
    return remove_hallucinated_master_response(response.choices[0].text)  # type: ignore


def convert_to_human_message(text: str) -> str:
    """
    Format the text as a message from human's side of the conversation.
    """
    return f"{HUMAN_TITLE}:\n\n{text}\n\nAssistant:"
