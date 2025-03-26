# llm/reasoning_template.py

reasoning_prompt = """
You are playing a text adventure game called Zork.

Here is the conversation so far:
{conversation_history}

Here is the latest game output:
{game_output}

Below is a list of all available commands that you can use:

=== Direction Commands ===
- north (n): Move north.
- south (s): Move south.
- east (e): Move east.
- west (w): Move west.
- northeast (ne): Move northeast.
- northwest (nw): Move northwest.
- southeast (se): Move southeast.
- southwest (sw): Move southwest.
- up (u): Move up.
- down (d): Move down.
- look (l): Look around at your current location.
- save: Save state to a file.
- restore: Restore a saved state.
- restart: Restart the game.
- verbose: Give a full description after each command.
- score: Display score and ranking.
- diagnose: Describe your health.
- brief: Give a brief description upon first entering an area.
- superbrief: Never describe an area.
- quit (q): Quit the game.
- climb: Climb (up).
- g: Redo the last command.
- go (direction): Go toward a specified direction (e.g., west/east/north/south/in/out/into).
- enter: Enter a place (e.g., window).
- in: Go into something (e.g., window).
- out: Go out of a place (e.g., kitchen).
- hi / hello: Say hello.

=== Item Commands ===
- get / take / grab (item): Remove an item from the current room and add it to your inventory.
- get / take / grab all: Take all takeable objects in the room.
- throw (item) at (location): Throw the item at something.
- open (container): Open a container (whether in the room or your inventory).
- open (exit): Open an exit for travel.
- read (item): Read what is written on a readable item.
- drop (item): Remove an item from your inventory and leave it in the room.
- put (item) in (container): Place an item from your inventory into a container.
- turn (control) with (item): Attempt to operate a control with an item.
- turn on (item): Turn on an item.
- turn off (item): Turn off an item.
- move (object): Move a large object that cannot be picked up.
- attack (creature) with (item): Attack a creature with an item.
- examine (object): Examine or look at an object, item, or location.
- inventory (i): Show the contents of your inventory.
- eat: Eat an item (specifically food).
- shout, yell, scream: Exclaim loudly.
- close [Door]: Close a door.
- tie (item) to (object): Tie an item to another object.
- pick (item): Take or get an item.
- kill self with (weapon): Humorously commit suicide.
- break (item) with (item): Break an item using another item.
- kill (creature) with (item): Attack a creature with an item.
- pray: Pray (typically when in a temple).
- drink: Drink an item.
- smell: Smell an item.
- cut (object/item) with (weapon): Cut an object or item. If the object/item equals "self", you commit suicide.
- bar: Bar bar...
- listen (target): Listen to a creature or an item.

=== Other Commands ===
- (none): "I beg your pardon?" (for unrecognized commands)
- Zork: "At your service!"
- f%&$/s@^#/damn: A random comment (e.g., "Such language in a high-class establishment like this!")
- jump: A random comment (e.g., "Are you proud of yourself?")
- swing (item): Swoosh!

=== Wand Commands (if you possess the wand) ===
- fall: Make the target fall when they move.
- fantasize: Make the target hallucinate.
- fear: Make the target afraid and run from the room.
- feeble: Make the target weak and unable to carry much or fight.
- fence: Prevent the target from leaving the room.
- ferment: Make the target drunk.
- fierce: Make the target angry.
- filch: Steal from the target.
- fireproof: Make the target fireproof.
- float: Make an object float.
- fluoresce: Make an object glow with light.
- free: Free the target (the genie uses this if given the chance).
- freeze: Make the target unable to move.
- frobizz: (Undefined action.)
- frobnoid: (Undefined action.)
- frobozzle: (Undefined action.)
- fry: Destroy the target.
- fudge: "A strong odor of chocolate permeates the room."
- fumble: Reduce the target's carrying capacity and occasionally make them drop items.

Using the above commands, along with the conversation history and the latest game output, think step by step to arrive at the best next command.

Format your response exactly as follows:

Reasoning:
<your chain-of-thought here>

Command:
<the final command here>
"""
