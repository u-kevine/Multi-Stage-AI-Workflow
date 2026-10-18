"""Deterministic offline provider backed by the Stage 1 golden labels.

Lets the whole workflow run and be tested with no API key or network.
fail_first / always_fail inject invalid output to exercise the retry and
human-routing paths.
"""
import json
import re
from pathlib import Path

from ..config import GOLDEN_PATH
from .base import ChatProvider

_ID_RE = re.compile(r'"ticket_id":\s*"([^"]+)"')


class MockProvider(ChatProvider):
    name = "mock"

    def __init__(self, golden_path=GOLDEN_PATH, fail_first=(), always_fail=()):
        data = json.loads(Path(golden_path).read_text(encoding="utf-8"))
        self.golden = {r["ticket_id"]: r for r in data["results"]}
        self.fail_first = set(fail_first)
        self.always_fail = set(always_fail)
        self.calls = {}

    def complete(self, prompt):
        m = _ID_RE.search(prompt)
        tid = m.group(1) if m else "unknown"
        kind = "reply" if "Triage result:" in prompt else "triage"
        self.calls[(tid, kind)] = self.calls.get((tid, kind), 0) + 1
        rec = self.golden.get(tid)

        if kind == "triage":
            triage = rec["triage"] if rec else {
                "ticket_id": tid, "category": "other", "priority": "medium",
                "sentiment": "neutral", "escalate": False,
                "reason": "Mock provider has no reference label for this ticket."}
            first = self.calls[(tid, kind)] == 1
            if tid in self.always_fail or (tid in self.fail_first and first):
                return json.dumps({**triage, "priority": "critical"})  # invalid enum
            return "```json\n" + json.dumps(triage, ensure_ascii=False) + "\n```"

        reply = rec["draft_reply"] if rec else (
            "Thanks for contacting us. A member of our team will review your "
            "message and follow up with you.")
        return json.dumps({"reply": reply}, ensure_ascii=False)
