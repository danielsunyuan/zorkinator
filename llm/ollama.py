# llm/llm_handler.py
from langchain.chains import LLMChain
from langchain_ollama import Ollama  # Use Ollama instead of OpenAI
from langchain.prompts import PromptTemplate
from langchain.callbacks import get_openai_callback  # (If an Ollama callback exists, swap this accordingly)
from .token_tracker import token_tracker  # Import our token tracker

# Global variable to track tokens used for LLM calls
total_tokens_used = 0

# LLM prompt template
prompt_template = """
Based on the game output below, decide on the next command to progress through the game.
Respond with only the command itself - no extra commentary, no labels, no prefixes.

Game Output:
{game_output}

IMPORTANT: Your response must be ONLY the command itself, nothing more."""

template = PromptTemplate(input_variables=["game_output"], template=prompt_template)

# Initialize the Ollama LLM and chain.
# (Here we assume the Ollama class accepts a parameter "model" similar to "model_name". Adjust as needed.)
llm = Ollama(model="llama2", temperature=0.5)
chain = LLMChain(llm=llm, prompt=template)

def get_llm_command(game_output):
    """
    Sends the current game output to the Ollama LLM, captures the generated command,
    and tracks token usage using both a callback and the dynamic token tracker.
    """
    global total_tokens_used

    # Use the token tracker to count tokens in the input text.
    dynamic_input_tokens = token_tracker.update(game_output)
    print(f"Dynamic tokens from input: {dynamic_input_tokens}")

    # Use LangChain's callback to track tokens used during the API call.
    # (If Ollama supports callbacks in the same way, this should work; otherwise, adjust accordingly.)
    with get_openai_callback() as cb:
        result = chain.invoke({"game_output": game_output})
        tokens_used = cb.total_tokens
        total_tokens_used += tokens_used
        print(f"Tokens used for this LLM call: {tokens_used}")
        print(f"Total LLM tokens used so far: {total_tokens_used}")

    # Use the token tracker to count tokens in the output text.
    dynamic_output_tokens = token_tracker.update(result.get("text", ""))
    print(f"Dynamic tokens from output: {dynamic_output_tokens}")
    print(f"Total dynamic tokens (reasoning) so far: {token_tracker.get_total_tokens()}")

    return result.get("text", "").strip()

def count_tokens_dynamic(text):
    """
    A utility function to dynamically count tokens for any given text.
    """
    return token_tracker.count_tokens(text)