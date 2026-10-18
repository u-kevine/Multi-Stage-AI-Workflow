"""Schema and business-rule validation for model output.

Allowed values are read from schema/triage_schema.json so the schema file is the
single source of truth for prompts, validation and documentation.
"""
import json
import re

from .config import SCHEMA_PATH

_SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
ALLOWED = {k: set(v["enum"]) for k, v in _SCHEMA["properties"].items() if "enum" in v}
REQUIRED = list(_SCHEMA["required"])
KNOWN_FIELDS = set(_SCHEMA["properties"])

MAX_REPLY_WORDS = 120
UNSUPPORTED_PROMISES = [
    "guaranteed refund", "guarantee a refund", "we will refund", "you will be refunded",
    "refund has been processed", "within 24 hours", "within 48 hours", "by tomorrow",
    "by end of day", "fixed today",
]


class ValidationError(ValueError):
    """Model output failed schema or business-rule checks."""


def strip_fences(text):
    t = text.strip()
    m = re.match(r"^```(?:json)?\s*(.*?)\s*```$", t, re.S | re.I)
    return m.group(1) if m else t


def parse_json(text):
    try:
        obj = json.loads(strip_fences(text))
    except (json.JSONDecodeError, TypeError) as e:
        raise ValidationError(f"Response is not valid JSON: {e}")
    if not isinstance(obj, dict):
        raise ValidationError("Response JSON must be an object")
    return obj


def validate_triage(obj, expected_ticket_id):
    missing = [f for f in REQUIRED if f not in obj]
    if missing:
        raise ValidationError(f"Missing fields: {', '.join(missing)}")
    obj = {k: v for k, v in obj.items() if k in KNOWN_FIELDS}  # drop extra keys
    for f in ("ticket_id", "reason"):
        if not isinstance(obj[f], str) or not obj[f].strip():
            raise ValidationError(f"Field '{f}' must be a non-empty string")
    if obj["ticket_id"] != expected_ticket_id:
        raise ValidationError(
            f"ticket_id mismatch: expected {expected_ticket_id!r}, got {obj['ticket_id']!r}")
    for field, values in ALLOWED.items():
        if obj[field] not in values:
            raise ValidationError(
                f"Invalid {field}: {obj[field]!r}. Allowed: {', '.join(sorted(values))}")
    if not isinstance(obj["escalate"], bool):
        raise ValidationError("Field 'escalate' must be true or false")
    if obj["priority"] == "urgent" and not obj["escalate"]:
        raise ValidationError("Rule violated: urgent tickets must have escalate=true")
    return obj


def validate_reply(obj):
    reply = obj.get("reply")
    if not isinstance(reply, str) or not reply.strip():
        raise ValidationError("Reply is empty")
    words = len(reply.split())
    if words >= MAX_REPLY_WORDS:
        raise ValidationError(f"Reply has {words} words; must be under {MAX_REPLY_WORDS}")
    lowered = reply.lower()
    hits = [p for p in UNSUPPORTED_PROMISES if p in lowered]
    if hits:
        raise ValidationError(f"Reply contains unsupported promise(s): {', '.join(hits)}")
    return reply.strip()
