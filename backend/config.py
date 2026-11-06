"""Settings for the app, read from the .env file.

To switch LLM providers, change LLM_PROVIDER in .env. No code changes needed.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# The project's root folder (one level above this "backend" folder).
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Load the variables in .env into os.environ, so os.getenv() can see them.
load_dotenv(PROJECT_ROOT / ".env")

# One entry per provider. Each one speaks the OpenAI API format, so the same
# client code works for all of them; only the URL, key name and model change.
PROVIDERS = {
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "key_env": "GEMINI_API_KEY",
        "default_model": "gemini-3.5-flash",
    },
    "openai": {
        "base_url": None,  # None means "use OpenAI's normal address"
        "key_env": "OPENAI_API_KEY",
        "default_model": "gpt-4o-mini",
    },
    "claude": {
        "base_url": "https://api.anthropic.com/v1/",
        "key_env": "ANTHROPIC_API_KEY",
        "default_model": "claude-haiku-5-5",
    },
}


@dataclass
class Settings:
    provider: str
    model: str
    base_url: str | None
    api_key: str


def load_settings() -> Settings:
    """Work out which provider and model to use, and fetch its API key."""
    provider = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
    if provider not in PROVIDERS:
        raise RuntimeError(
            f"Unknown LLM_PROVIDER '{provider}'. Choose one of: {', '.join(PROVIDERS)}"
        )

    preset = PROVIDERS[provider]
    api_key = os.getenv(preset["key_env"], "").strip()
    if not api_key:
        # Name the missing variable, but never print a key's value.
        raise RuntimeError(f"{preset['key_env']} is not set. Add it to your .env file.")

    model = os.getenv("LLM_MODEL", "").strip() or preset["default_model"]
    return Settings(provider, model, preset["base_url"], api_key)
