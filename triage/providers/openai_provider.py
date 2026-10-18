"""OpenAI or any OpenAI-compatible endpoint (Gemini, Groq, LM Studio, vLLM...).

Env: OPENAI_API_KEY, OPENAI_MODEL (default gpt-4o-mini), OPENAI_BASE_URL (optional).
"""
import os

from .base import ChatProvider


class OpenAIProvider(ChatProvider):
    name = "openai"

    def __init__(self):
        from openai import OpenAI  # lazy import: optional dependency
        self.client = OpenAI(base_url=os.getenv("OPENAI_BASE_URL") or None)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def complete(self, prompt):
        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content
