"""
Persona modules. Each module exports:
    SYSTEM_PROMPT       The full prompt to send to the model.
    PERSONA_NAME        Display name (for the UI header).
    PERSONA_ROLE        Display subtitle (for the UI header).
    PERSONA_AVATAR_INITIAL  Single character for the avatar bubble.
    OPENING_MESSAGE     The first message the bot sends when a session
                        starts.

The five Project Free Parking personas:
    diane    — Diane Foster, parent of three (target customer)
    sarah    — Sarah Park, Hasbro Senior PM (sponsor)
    marcus   — Marcus Webb, board game community manager
    theo     — Theo Larsen, age 11 (secondary user)
    choi     — Mrs. Eleanor Choi, retired teacher / game club

To deploy a different persona, change the import in app.py from
`from personas import diane` to your chosen module.

To create a new persona, copy any of the existing files and edit
PERSONA_BLOCK along with the four display constants. Do NOT modify
_spine.py for persona-specific behavior — the spine is shared across
all personas and changes there propagate everywhere.
"""
from . import diane, sarah, marcus, theo, choi

# Convenience registry — useful if you build a UI that lets the
# trainee pick a persona at runtime. Not used by the current app
# (which pins a single persona via `from personas import diane` in
# app.py), but kept here so it's easy to wire up later.
ALL_PERSONAS = {
    "diane":  diane,
    "sarah":  sarah,
    "marcus": marcus,
    "theo":   theo,
    "choi":   choi,
}

__all__ = ["diane", "sarah", "marcus", "theo", "choi", "ALL_PERSONAS"]
