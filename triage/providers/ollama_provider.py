"""Local models via Ollama (free, offline). Env: OLLAMA_HOST, OLLAMA_MODEL.
Uses only the standard library."""
import json
import os
import urllib.request

from .base import ChatProvider


class OllamaProvider(ChatProvider):
    name = "ollama"

    def __init__(self):
        self.host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.1")

    def complete(self, prompt):
        body = json.dumps({"model": self.model, "prompt": prompt,
                           "format": "json", "stream": False,
                           "options": {"temperature": 0}}).encode()
        req = urllib.request.Request(f"{self.host}/api/generate", data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())["response"]
