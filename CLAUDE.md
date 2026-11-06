# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A personal resume chatbot that answers recruiter questions about Nisshar Fathima (targeting AI Engineer / Applied AI roles).

Status: v1. There's no test suite yet, and no git repo.

## Commands (Windows, from the repo root)

```
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m uvicorn backend.main:app --reload     # API on :8000 (/docs, /health, POST /chat)
.venv\Scripts\python -m streamlit run frontend/app.py          # chat UI on :8501
```

## Architecture

- `frontend/app.py` (Streamlit) → HTTP `POST /chat {message, history}` → `backend/main.py` (FastAPI) → `backend/llm.py` → LLM.
- At import time, `backend/main.py` loads settings (`config.py`), extracts every `.docx`/`.pdf`/`.md` in `data/` (`knowledge.py`), and builds one system prompt (`prompt.py`). Data changes need a backend restart.
- The whole knowledge base is stuffed into the system prompt; there's no RAG/vector store.
- Provider presets (base URL, key env var, default model) live in `PROVIDERS` in `backend/config.py`, selected by `LLM_PROVIDER` / `LLM_MODEL` in `.env`. `backend/llm.py` is the only module that calls the LLM.
- The fallback string lives in `FALLBACK` in `backend/prompt.py`.

## Stack

- Python 3.12
- FastAPI backend (chat API + LLM calls)
- Streamlit chat UI (talks to the FastAPI backend; it doesn't call the LLM directly)
- LLM: Gemini free tier through the **OpenAI-compatible client** (`openai` Python package pointed at Gemini's OpenAI-compatible base URL)

## Rules

### Secrets
- The API key is read from `.env` as `GEMINI_API_KEY`. Never hard-code, log, or print keys, including in error messages or debug output.
- `.gitignore` already excludes `.env*`, `venv/`, and `__pycache__/`. Check it before adding any new secret-bearing files.

### LLM provider is a config setting
- Keep provider choice (provider name, model, base URL, API-key env var name) in config/env, not scattered through code. The goal is to switch to OpenAI or Claude later by changing config, not rewriting call sites.
- Route all LLM calls through a single module/function so that's the only place that knows about the provider.

### Bot behavior
- Speaks **about** Nisshar in the third person (e.g. "Nisshar has experience in…"), never as Nisshar. Refer to Nisshar by name; confirm preferred pronouns with the user before putting any in the system prompt.
- Answers **only** from files in `data/`. No outside knowledge, no guessing.
- When the answer isn't in the data, or is unclear, reply exactly: "I don't have that information"

### Docs & explanations
- The user is learning. Explain code simply: plain-language comments where logic isn't obvious, and short explanations of what changed and why.
- Keep `README.md` up to date (setup, how to run, how it works) whenever setup steps, commands, or architecture change.

## Data sources (`data/`)

- `data/Nisshar_Fathima.docx`: the resume, the main knowledge source. It's a Word file, so it needs text extraction (e.g. `python-docx`) before use.
- `data/faq.md`: hand-written facts not on the resume (target roles, location, notice period, strengths). Prefer these when they overlap with the resume.
