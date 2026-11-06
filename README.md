# Resume Bot

A chatbot that answers recruiters' questions about Nisshar Fathima. It answers only from the files in `data/`, and if it doesn't know something it says "I don't have that information".

## How a question becomes an answer

```
You type a question
   │
   ▼
frontend/app.py  (Streamlit chat page)
   │  sends {message, history} as JSON
   ▼
backend/main.py  (FastAPI, POST /chat)
   │  adds the system prompt (rules + resume text)
   ▼
backend/llm.py   (calls Gemini through the OpenAI-compatible client)
   │
   ▼
The answer travels back up to the chat page
```

When the backend starts, it does three things once:
1. `backend/config.py` reads `.env` to work out which provider, model and API key to use.
2. `backend/knowledge.py` extracts plain text from every `.docx`, `.pdf` and `.md` file in `data/`.
3. `backend/prompt.py` wraps that text in the bot's rules: third person, data only, "I don't have that information" when unsure.

## Project layout

| Path | What it does |
|---|---|
| `data/` | The bot's only knowledge: the resume and `faq.md`. Add or edit files here, then restart the backend. |
| `backend/config.py` | Settings and LLM provider presets (Gemini / OpenAI / Claude) |
| `backend/knowledge.py` | Turns data files into text |
| `backend/prompt.py` | The system prompt (the bot's rules) |
| `backend/llm.py` | The only code that calls the LLM |
| `backend/main.py` | The API: `POST /chat` and `GET /health` |
| `frontend/app.py` | The chat page, with suggested-question buttons |

## Setup (one time)

1. Install Python 3.12.
2. Create a virtual environment (a private folder of packages for this project) and install the packages:
   ```
   py -3.12 -m venv .venv
   .venv\Scripts\python -m pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and put your Gemini API key in it. `.env` is in `.gitignore`, so it won't be committed. Never share this key.

## Running it

Start the backend and the chat page in **two separate terminals**:

```
# Terminal 1: the backend API
.venv\Scripts\python -m uvicorn backend.main:app --reload

# Terminal 2: the chat page (opens in your browser)
.venv\Scripts\python -m streamlit run frontend/app.py
```

- Chat page: http://localhost:8501
- API docs, where you can try `/chat` directly: http://localhost:8000/docs

## Switching LLM provider

In `.env`, set `LLM_PROVIDER` to `gemini`, `openai` or `claude`, and add that provider's key (`GEMINI_API_KEY`, `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`). To use a specific model, set `LLM_MODEL` too. Then restart the backend.
