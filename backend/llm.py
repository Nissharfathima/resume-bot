"""The ONLY file that talks to the LLM.

It uses the OpenAI client, which Gemini, OpenAI and Claude all accept.
The URL, key and model come from config.py, so nothing here is provider-specific.
"""

from openai import OpenAI

from backend.config import Settings


class LLM:
    def __init__(self, settings: Settings):
        self.model = settings.model
        # timeout: give up after 45 seconds instead of the default 10 minutes,
        # so the chat page shows an error rather than hanging forever.
        self.client = OpenAI(
            api_key=settings.api_key,
            base_url=settings.base_url,
            timeout=45,
            max_retries=1,
        )

    def chat(self, system_prompt: str, messages: list[dict]) -> str:
        """Send the system prompt plus the conversation, and return the reply text.

        messages looks like: [{"role": "user", "content": "..."}, {"role": "assistant", ...}]
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system_prompt}, *messages],
            temperature=0.2,  # low = more factual, less creative
        )
        return (response.choices[0].message.content or "").strip()
