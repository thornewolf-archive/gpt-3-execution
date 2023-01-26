from prompt_building.prompts import Prompt

BASE_PROMPT = Prompt(
    """
$history

"""
)

WRITE_CODE_TEMPLATE = BASE_PROMPT.add(
    """
Write python code to solve the problem below.

What is 1+1?

# Start like this:
# def solve():
#   import os
# Replace the return statement with storing the result into os.environ["ANSWER"]
# After you are done writing the code, call the function solve() then stop writing anything.
def solve():
    import os
    os.environ["ANSWER"] = str(1+1)
solve()


Write python code to solve the problem below.

$prompt

# Start like this:
# def solve():
#   import os
# Replace the return statement with storing the result into os.environ["ANSWER"]
# After you are done writing the code, call the function solve() then stop writing anything.
"""
)


ONLINE_SEARCH_TEMPLATE = BASE_PROMPT.add(
    """
:SEARCH:
$prompt
:END:
    """
)

SCIENTIFIC_PAPER_TEMPLATE = BASE_PROMPT.add(
    """
You are a scientist attempting to solve a student's problem. The student's problem is:
$prompt

Write a scientific summary of the problem and your solution.
    """
)

CONVERSATIONAL_TEMPLATE = BASE_PROMPT.add(
    """
You are a conversational AI. Response to the user as a human would.
USER: $prompt
AI:
    """
)

RESULT_TEMPLATE = BASE_PROMPT.add(
    """
You are a conversational AI. You have a result to give to the user based on the context you have.

The user's asked:
$prompt

The results from previous conversations are:
$context

To answer "$prompt", the result is:"""
)

ROUTING_TEMPLATE = BASE_PROMPT.add(
    """
You are a switchboard AI. You have a list of possible templates to use to solve a user's. Select the template that best matches the user's problem.
The user's problem is:
$prompt

The templates are:
WRITE_CODE_TEMPLATE - This is used for all numeric problems. If you already have the result from previous conversations, you can use the RESULT_TEMPLATE.
SCIENTIFIC_PAPER_TEMPLATE - This is used if the user asks anything related to what one would learn in a science class.
CONVERSATIONAL_TEMPLATE - This is used if the user says something conversational.
RESULT_TEMPLATE - This is used if you can answer the user's question directly with the context you have.
UNSURE_TEMPLATE - This is used if you are unsure how to respond to the user's message.

These are the results from previous conversations:
$context


Which of the remaining templates do you choose?
I select: """
)

UNSURE_TEMPLATE = BASE_PROMPT.add(
    """
Repeat the following:
I am unsure how to respond to your message. Please try again.
"""
)

prompt_template_mapping = {
    "WRITE_CODE_TEMPLATE": WRITE_CODE_TEMPLATE,
    "SCIENTIFIC_PAPER_TEMPLATE": SCIENTIFIC_PAPER_TEMPLATE,
    "CONVERSATIONAL_TEMPLATE": CONVERSATIONAL_TEMPLATE,
    "RESULT_TEMPLATE": RESULT_TEMPLATE,
}

response_template_mapping = {
    "ONLINE_SEARCH_TEMPLATE": ONLINE_SEARCH_TEMPLATE,
}
