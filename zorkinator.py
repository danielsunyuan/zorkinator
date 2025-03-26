import os
import sys
import time
import subprocess
import select
import argparse
import atexit
from llm.llm_handler import get_llm_command, DEBUG_TOKENS
from llm.memory import get_formatted_memory
from monitoring import update_map, get_map_visualization
from monitoring import get_locations, get_connections, get_current_location
from monitoring import start_visual_map, update_visual_map, stop_visual_map

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--token", action="store_true", help="Enable token debug output")
parser.add_argument("--dump-history", nargs="?", const="conversation_history.txt",
                    help="Dump the full conversation history (chain-of-thought and all) to a file (default: conversation_history.txt)")
parser.add_argument("--show-map", action="store_true", help="Show the Zork map visualization as text")
parser.add_argument("--visual-map", action="store_true", help="Show a graphical map visualization in a separate window")
args = parser.parse_args()

# Set the debug flag for tokens if requested.
if args.token:
    DEBUG_TOKENS = True

# Determine whether to dump history and to which file.
dump_history = False
dump_file = None
if args.dump_history is not None:
    dump_history = True
    dump_file = args.dump_history

# ANSI color codes for output
ZORK_COLOR = "\033[32m"   # Green for Zork output
LLM_COLOR = "\033[35m"    # Magenta for LLM suggestions
MAP_COLOR = "\033[36m"    # Cyan for map visualization
RESET_COLOR = "\033[0m"   # Reset to default

# Resolve the absolute path to the Zork game directory.
zork_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "zork"))

def launch_zork():
    """Starts the Zork process in the correct directory."""
    return subprocess.Popen(
        ["./zork"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=zork_dir
    )

def read_until_prompt(process, prompt_char=">"):
    """
    Reads Zork output until a line ending with the prompt character is encountered.
    It collects the output without printing immediately.
    """
    output_lines = []
    while True:
        rlist, _, _ = select.select([process.stdout], [], [], 1)
        if process.stdout in rlist:
            line = process.stdout.readline()
            if not line:
                break
            output_lines.append(line)
            if line.strip().endswith(prompt_char):
                break
        else:
            break  # No data available right now
    return "".join(output_lines)

def cleanup():
    """Clean up resources before exiting."""
    stop_visual_map()

def main():
    # Register the cleanup function to run at exit
    atexit.register(cleanup)
    
    # Start the visual map if requested
    if args.visual_map:
        start_visual_map()
    
    proc = launch_zork()

    while True:
        game_output = read_until_prompt(proc)
        if not game_output:
            print("Zork process terminated. Restarting...")
            time.sleep(2)
            proc = launch_zork()
            continue

        # Print Zork's output in green.
        print(f"{ZORK_COLOR}=== Zork Output ==={RESET_COLOR}")
        print(f"{ZORK_COLOR}{game_output}{RESET_COLOR}")

        # Get the AI-generated command (simple response without reasoning)
        command = get_llm_command(game_output)
        # Remove any prefix that might have been added by the LLM (like "LLM Command:")
        clean_command = command
        if ":" in command:
            possible_prefix, cmd = command.split(":", 1)
            if possible_prefix.strip().lower() in ["llm command", "command"]:
                clean_command = cmd.strip()
        print(f"{LLM_COLOR}>>> LLM Command: {clean_command}{RESET_COLOR}")

        # Update the map with the current game state and command
        update_map(game_output, clean_command)
        
        # Update the visual map if it's active
        if args.visual_map:
            update_visual_map(
                get_locations(),
                get_connections(),
                get_current_location()
            )
        
        # Display text map if requested
        if args.show_map:
            map_visual = get_map_visualization()
            print(f"{MAP_COLOR}{map_visual}{RESET_COLOR}")

        if proc.poll() is None:  # Ensure the process is still running.
            try:
                proc.stdin.write(clean_command + "\n")
                proc.stdin.flush()
            except BrokenPipeError:
                print("Pipe broken. Restarting Zork...")
                proc = launch_zork()
        else:
            print("Zork process ended. Restarting...")
            proc = launch_zork()

        # If the dump-history flag is enabled, write the full conversation history to file.
        if dump_history and dump_file:
            try:
                with open(dump_file, "w", encoding="utf-8") as f:
                    f.write(get_formatted_memory())
                print(f"[DEBUG] Conversation history written to {dump_file}")
            except Exception as e:
                print(f"[DEBUG] Error writing conversation history: {e}")

        time.sleep(1)

if __name__ == "__main__":
    main()
