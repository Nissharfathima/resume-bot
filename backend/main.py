"""The FastAPI backend.

Run it with:  .venv\\Scripts\\python -m uvicorn backend.main:app --reload
Then open http://localhost:8000/docs to try the API in your browser.
"""

import logging
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.config import DATA_DIR, load_settings
from backend.knowledge import load_knowledge
from backend.llm import LLM
from backend.prompt import build_system_prompt

logger = logging.getLogger("resume-bot")

# This runs once when the server starts: load settings, read the data files,
# and build the system prompt. Every request then reuses them.
settings = load_settings()
llm = LLM(settings)
SYSTEM_PROMPT = build_system_prompt(load_knowledge(DATA_DIR))

app = FastAPI(title="Resume Bot")


# These classes describe what the JSON going in and out of /chat looks like.
# FastAPI uses them to check requests automatically.
class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[Message] = []


class ChatResponse(BaseModel):
    answer: str


@app.get("/health")
def health():
    """A quick check that the server is up. It doesn't call the LLM."""
    return {"status": "ok", "provider": settings.provider, "model": settings.model}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # Earlier turns plus the new question, so the bot can follow up on context.
    messages = [m.model_dump() for m in request.history]
    messages.append({"role": "user", "content": request.message})

    try:
        answer = llm.chat(SYSTEM_PROMPT, messages)
    except Exception as exc:
        # Log only the error type, so a key can't leak into the logs.
        logger.error("LLM call failed: %s", type(exc).__name__)
        raise HTTPException(status_code=502, detail="The language model is unavailable. Please try again.")

    return ChatResponse(answer=answer)
