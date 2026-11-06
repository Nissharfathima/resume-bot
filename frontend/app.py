"""The Streamlit chat page.

Run it with:  .venv\\Scripts\\python -m streamlit run frontend/app.py
The backend must be running too: this page sends every question to it.
"""

import os

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

SUGGESTED_QUESTIONS = [
    "What roles is Nisshar looking for?",
    "Summarize Nisshar's experience",
    "What are Nisshar's key skills?",
    "Where is Nisshar based, and what's the notice period?",
    "Tell me about Nisshar's carbon compliance work",
]

st.set_page_config(page_title="Ask about Nisshar", page_icon="💬")
st.title("💬 Ask about Nisshar Fathima")
st.caption("Answers come only from Nisshar's resume and FAQ.")

# Streamlit re-runs this whole file on every click, so the chat history is kept
# in st.session_state, which survives between re-runs.
if "history" not in st.session_state:
    st.session_state.history = []


def ask_backend(question: str) -> str:
    """Send the question (and earlier chat) to the FastAPI /chat endpoint."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={"message": question, "history": st.session_state.history},
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["answer"]
    except requests.RequestException:
        return "⚠️ Couldn't reach the backend. Is it running?"


# Suggested-question buttons, shown until the first question is asked.
clicked = None
if not st.session_state.history:
    st.write("Try one of these:")
    for question in SUGGESTED_QUESTIONS:
        if st.button(question, use_container_width=True):
            clicked = question

# Show the conversation so far.
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# A question can come from the text box or a button.
typed = st.chat_input("Ask a question about Nisshar...")
question = typed or clicked

if question:
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = ask_backend(question)
        st.markdown(answer)

    st.session_state.history.append({"role": "user", "content": question})
    st.session_state.history.append({"role": "assistant", "content": answer})
    st.rerun()  # redraw so the suggestion buttons disappear
