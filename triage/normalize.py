"""Stage: input loading and normalization (no AI involved)."""
import csv
import json
from pathlib import Path

REQUIRED_FIELDS = ("ticket_id", "subject", "message")


def load_tickets(path):
    """Load tickets from a JSON list or a CSV file with a header row."""
    p = Path(path)
    if p.suffix.lower() == ".csv":
        with p.open(newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Input JSON must be a list of ticket objects")
    return data


def normalize_ticket(raw):
    """Trim whitespace, fill optional defaults, reject tickets missing required fields."""
    if not isinstance(raw, dict):
        raise ValueError("Ticket is not an object")
    clean = {k: ("" if v is None else str(v).strip()) for k, v in raw.items()}
    for field in REQUIRED_FIELDS:
        if not clean.get(field):
            raise ValueError(f"Missing required field: {field}")
    return {
        "ticket_id": clean["ticket_id"],
        "customer_name": clean.get("customer_name") or "Customer",
        "subject": clean["subject"],
        "message": clean["message"],
        "channel": clean.get("channel") or "unknown",
    }
