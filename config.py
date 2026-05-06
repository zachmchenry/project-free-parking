"""
Application configuration.

All runtime choices that an instructional designer or developer might
want to change live in this file. To swap providers, edit ACTIVE_PROVIDER.
To swap models within a provider, edit the relevant *_MODEL constant.

Environment variables (API keys, AWS region) are read by the providers
themselves — this file is just for in-code defaults.
"""
import os

# ---- Active provider ----
# One of: "claude", "openai", "bedrock", "gemini"
# Override at runtime with the LLM_PROVIDER environment variable.
ACTIVE_PROVIDER = os.environ.get("LLM_PROVIDER", "claude")

# ---- Admin configuration ----
# The web UI never exposes provider selection to trainees. Set
# ADMIN_PASSWORD to enable the protected /admin page for provider/model
# changes. Runtime changes are persisted here so Docker volumes can keep
# them across container restarts.
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
ADMIN_SETTINGS_PATH = os.environ.get(
    "ADMIN_SETTINGS_PATH",
    "admin_settings.json",
)

# ---- Per-provider model selection ----
# Adjust these to use different models within each provider.
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")
BEDROCK_MODEL_ID = os.environ.get(
    "BEDROCK_MODEL_ID",
    "anthropic.claude-sonnet-4-5-v2:0",
)
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

# ---- Off-topic cut-off mechanism ----
# Maximum off-topic messages before the persona politely withdraws.
# Reset to 0 whenever an on-topic message arrives.
OFF_TOPIC_LIMIT = 4

# Whether to use an LLM-as-judge for off-topic detection (recommended)
# vs. a keyword-based fallback. Keyword fallback exists for rapid
# local testing without making extra API calls.
USE_LLM_OFFTOPIC_CLASSIFIER = True

# ---- Generation parameters ----
MAX_TOKENS = 600         # persona responses are short; this is plenty
TEMPERATURE = 0.7        # some variability, not so much it goes off-character

# ---- Storage ----
# Path to SQLite file for conversation logs.
DB_PATH = os.environ.get("CHATBOT_DB", "chatbot_sessions.db")

# ---- Server ----
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "5000"))
DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
