"""Anthropic Claude. Env: ANTHROPIC_API_KEY, ANTHROPIC_MODEL."""
import os

from .base import ChatProvider


class AnthropicProvider(ChatProvider):
    name = "anthropic"

    def __init__(self):
        import anthropic  # lazy import: optional dependency
        self.client = anthropic.Anthropic()
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")

    def complete(self, prompt):
        msg = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
