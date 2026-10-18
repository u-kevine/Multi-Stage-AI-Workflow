"""Core workflow: normalize -> triage -> validate (retry) -> draft reply -> validate (retry).

Contains no vendor-specific code; every model call goes through ChatProvider.complete().
"""
import json

from .config import PROMPTS_DIR
from .normalize import normalize_ticket
from .validate import ValidationError, parse_json, validate_reply, validate_triage


def render(template, **values):
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    return template


class TriagePipeline:
    def __init__(self, provider, max_attempts=2, prompts_dir=PROMPTS_DIR):
        self.provider = provider
        self.max_attempts = max_attempts
        self.triage_tpl = (prompts_dir / "triage_prompt.txt").read_text(encoding="utf-8")
        self.reply_tpl = (prompts_dir / "reply_prompt.txt").read_text(encoding="utf-8")
        self.retry_tpl = (prompts_dir / "retry_suffix.txt").read_text(encoding="utf-8")

    def _ask(self, prompt, validator):
        """Call the model, validate, retry with the error appended.
        Returns (value or None, retries_used, last_error)."""
        current, last_error = prompt, None
        for attempt in range(1, self.max_attempts + 1):
            try:
                return validator(parse_json(self.provider.complete(current))), attempt - 1, None
            except ValidationError as e:
                last_error = str(e)
                current = prompt + render(self.retry_tpl, error=last_error)
            except Exception as e:  # network/auth/provider failure: never crash the batch
                last_error = f"Provider error: {type(e).__name__}: {e}"
                current = prompt
        return None, self.max_attempts - 1, last_error

    def process_ticket(self, ticket):
        ticket_json = json.dumps(ticket, ensure_ascii=False, indent=2)
        record = {**ticket, "triage": None, "draft_reply": None, "retries": 0, "errors": []}

        triage, retries, err = self._ask(
            render(self.triage_tpl, ticket=ticket_json),
            lambda obj: validate_triage(obj, ticket["ticket_id"]))
        record["retries"] += retries
        if triage is None:
            record["status"] = "routed_to_human"
            record["errors"].append(f"triage failed: {err}")
            return record
        record["triage"] = triage

        reply, retries, err = self._ask(
            render(self.reply_tpl, ticket=ticket_json,
                   triage_json=json.dumps(triage, ensure_ascii=False)),
            validate_reply)
        record["retries"] += retries
        if reply is None:
            record["status"] = "routed_to_human"
            record["errors"].append(f"reply failed: {err}")
            return record

        record["draft_reply"] = reply
        record["status"] = "needs_human_review" if triage["escalate"] else "ready_for_agent_approval"
        return record

    def run(self, raw_tickets):
        """Process a batch. Returns (results, rejected). One bad ticket never stops the batch."""
        results, rejected, seen = [], [], set()
        for index, raw in enumerate(raw_tickets, start=1):
            raw_id = str(raw.get("ticket_id", "")).strip() if isinstance(raw, dict) else ""
            try:
                ticket = normalize_ticket(raw)
            except ValueError as e:
                rejected.append({"ticket_id": raw_id or f"row-{index}", "error": str(e)})
                continue
            if ticket["ticket_id"] in seen:
                rejected.append({"ticket_id": ticket["ticket_id"], "error": "Duplicate ticket_id"})
                continue
            seen.add(ticket["ticket_id"])
            results.append(self.process_ticket(ticket))
        return results, rejected
