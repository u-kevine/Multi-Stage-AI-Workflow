import json

import pytest

from triage.config import ROOT
from triage.evaluate import evaluate
from triage.normalize import load_tickets
from triage.pipeline import TriagePipeline
from triage.providers.base import ChatProvider
from triage.providers.mock import MockProvider
from triage.report import write_outputs
from triage.validate import ValidationError, parse_json, validate_reply, validate_triage

TICKETS = load_tickets(ROOT / "data" / "tickets.json")
META = {"provider": "mock", "input": "test", "started_at": "now", "duration_s": 0.0}


def run(**mock_kwargs):
    return TriagePipeline(MockProvider(**mock_kwargs)).run(TICKETS)


def by_id(results):
    return {r["ticket_id"]: r for r in results}


# ---------- end-to-end ----------

def test_full_batch_end_to_end(tmp_path):
    results, rejected = run()
    assert len(results) == 16
    assert {r["ticket_id"] for r in rejected} == {"TCK-1017", "TCK-1018"}
    assert sum(r["triage"]["escalate"] for r in results) == 8
    assert all(r["status"] != "routed_to_human" for r in results)
    write_outputs(results, rejected, tmp_path, META)
    for name in ("triaged_tickets.json", "escalations.csv", "workflow_report.md"):
        assert (tmp_path / name).exists()
    csv_lines = (tmp_path / "escalations.csv").read_text().strip().splitlines()
    assert len(csv_lines) == 1 + 8 + 2  # header + escalated + rejected


def test_business_rules_hold_for_every_result():
    results, _ = run()
    for r in results:
        if r["triage"]["priority"] == "urgent":
            assert r["triage"]["escalate"] is True
        assert 0 < len(r["draft_reply"].split()) < 120
        expected = "needs_human_review" if r["triage"]["escalate"] else "ready_for_agent_approval"
        assert r["status"] == expected


def test_prompt_injection_ticket_is_not_downgraded():
    r = by_id(run()[0])["TCK-1016"]
    assert r["triage"]["priority"] == "urgent" and r["triage"]["escalate"]


# ---------- retry and human routing ----------

def test_invalid_output_is_retried_and_recovers():
    r = by_id(run(fail_first=["TCK-1005"])[0])["TCK-1005"]
    assert r["retries"] == 1
    assert r["status"] == "ready_for_agent_approval"


def test_double_failure_routes_to_human_and_batch_continues():
    results, _ = run(always_fail=["TCK-1003"])
    r = by_id(results)["TCK-1003"]
    assert r["status"] == "routed_to_human"
    assert "Invalid priority" in r["errors"][0]
    assert len(results) == 16


def test_provider_exception_does_not_crash_batch():
    class Broken(ChatProvider):
        name = "broken"
        def complete(self, prompt):
            raise ConnectionError("network down")
    results, _ = TriagePipeline(Broken()).run(TICKETS[:3])
    assert [r["status"] for r in results] == ["routed_to_human"] * 3
    assert "network down" in results[0]["errors"][0]


def test_retry_prompt_contains_validator_error():
    seen = []
    class Spy(MockProvider):
        def complete(self, prompt):
            seen.append(prompt)
            return super().complete(prompt)
    TriagePipeline(Spy(fail_first=["TCK-1001"])).run(TICKETS[:1])
    assert "rejected by the validator" in seen[1] and "critical" in seen[1]


# ---------- inputs ----------

def test_empty_input_produces_empty_report(tmp_path):
    results, rejected = TriagePipeline(MockProvider()).run([])
    write_outputs(results, rejected, tmp_path, META)
    report = (tmp_path / "workflow_report.md").read_text()
    assert "| Processed | 0 |" in report


def test_csv_input(tmp_path):
    p = tmp_path / "t.csv"
    p.write_text("ticket_id,subject,message\nTCK-1003,Export,How do I export?\n,No id,hello\n")
    results, rejected = TriagePipeline(MockProvider()).run(load_tickets(p))
    assert len(results) == 1 and len(rejected) == 1


def test_duplicate_ids_rejected():
    results, rejected = TriagePipeline(MockProvider()).run([TICKETS[0], TICKETS[0]])
    assert len(results) == 1 and rejected[0]["error"] == "Duplicate ticket_id"


def test_unknown_ticket_still_processed_by_mock():
    t = {"ticket_id": "NEW-1", "subject": "Question", "message": "Do you have an API?"}
    results, _ = TriagePipeline(MockProvider()).run([t])
    assert results[0]["status"] == "ready_for_agent_approval"


# ---------- validator ----------

GOOD = {"ticket_id": "X", "category": "billing", "priority": "low",
        "sentiment": "neutral", "escalate": False, "reason": "ok"}


def test_fenced_json_is_parsed():
    assert parse_json('```json\n{"a": 1}\n```') == {"a": 1}


@pytest.mark.parametrize("patch,msg", [
    ({"priority": "critical"}, "Invalid priority"),
    ({"category": "sales"}, "Invalid category"),
    ({"priority": "urgent", "escalate": False}, "urgent tickets"),
    ({"escalate": "yes"}, "true or false"),
    ({"ticket_id": "Y"}, "mismatch"),
])
def test_triage_validator_rejects(patch, msg):
    with pytest.raises(ValidationError, match=msg):
        validate_triage({**GOOD, **patch}, "X")


def test_triage_validator_drops_extra_keys():
    assert "confidence" not in validate_triage({**GOOD, "confidence": 0.9}, "X")


@pytest.mark.parametrize("reply,msg", [
    ("", "empty"),
    ("word " * 130, "under 120"),
    ("We will refund you within 24 hours.", "unsupported promise"),
])
def test_reply_validator_rejects(reply, msg):
    with pytest.raises(ValidationError, match=msg):
        validate_reply({"reply": reply})


def test_evaluate_reports_full_agreement_for_mock(tmp_path):
    results, rejected = run()
    write_outputs(results, rejected, tmp_path, META)
    res = evaluate(tmp_path / "triaged_tickets.json", ROOT / "data" / "golden_triage_results.json")
    assert res["compared"] == 16 and res["mismatches"] == 0
