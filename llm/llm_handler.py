# llm/llm_handler.py
from langchain.chains import LLMChain
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.callbacks.manager import get_openai_callback

from .token_tracker import token_tracker
from .memory import add_turn, get_formatted_memory

# Global flag to control token debug output.
DEBUG_TOKENS = False

# Global variable to track tokens used for LLM calls.
total_tokens_used = 0

# Create a simple prompt template without reasoning
template = PromptTemplate(
    input_variables=["conversation_history", "game_output"],
    template="""
You are playing the text adventure game Zork.

Here is the conversation history:
{conversation_history}

Here is the latest game output:
{game_output}

Provide a single command to progress in the game. Just return the exact command text, no labels, no prefixes, no explanations.
IMPORTANT: Your response must be ONLY the command itself, nothing more.
"""
)

# Initialize the OpenAI LLM and chain.
llm = OpenAI(temperature=0.5)
chain = LLMChain(llm=llm, prompt=template)

def get_llm_command(game_output: str) -> str:
    """
    Sends the current game output (plus conversation history) to the LLM,
    obtains a simple command response, tracks token usage if debugging is enabled,
    and returns the command.
    """
    global total_tokens_used

    # 1. Record the game output in memory.
    add_turn("Game", game_output)

    # 2. Count tokens in the input using the dynamic tracker.
    input_tokens = token_tracker.update(game_output)
    if DEBUG_TOKENS:
        print(f"[DEBUG] Dynamic tokens from input: {input_tokens}")

    # 3. Get the formatted conversation history.
    conversation_history = get_formatted_memory()

    # 4. Invoke the LLM using a callback to capture token usage.
    with get_openai_callback() as cb:
        result = chain.invoke({
            "conversation_history": conversation_history,
            "game_output": game_output
        })
        tokens_used = cb.total_tokens
        total_tokens_used += tokens_used
        if DEBUG_TOKENS:
            print(f"[DEBUG] LLM tokens used this call: {tokens_used}")
            print(f"[DEBUG] Total LLM tokens used so far: {total_tokens_used}")

    # 5. Get the command (taking only the first line in case of multiple lines)
    command = result.get("text", "").strip().split('\n')[0].strip()

    # 6. Add the command to memory.
    add_turn("LLM Command", command)

    # 7. Count tokens for the response.
    output_tokens = token_tracker.update(command)
    if DEBUG_TOKENS:
        print(f"[DEBUG] Dynamic tokens from output: {output_tokens}")
        print(f"[DEBUG] Total dynamic tokens so far: {token_tracker.get_total_tokens()}")

    # 8. Return the command.
    return command

def count_tokens_dynamic(text: str) -> int:
    """
    Utility function to count tokens for any given text.
    """
    return token_tracker.count_tokens(text)
