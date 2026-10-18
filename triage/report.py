"""Write triaged_tickets.json, escalations.csv and workflow_report.md."""
import csv
import json
from collections import Counter
from pathlib import Path

STATUSES = ["ready_for_agent_approval", "needs_human_review", "routed_to_human"]


def _table(title, counter, keys=None):
    keys = keys or sorted(counter)
    lines = [f"| {title} | Count |", "|---|---|"]
    lines += [f"| {k} | {counter.get(k, 0)} |" for k in keys]
    return "\n".join(lines) if keys else f"_No {title.lower()} data._"


def write_outputs(results, rejected, out_dir, meta, manual_min=5.0, review_min=1.5):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    (out / "triaged_tickets.json").write_text(
        json.dumps({"meta": meta, "results": results, "rejected": rejected},
                   indent=2, ensure_ascii=False), encoding="utf-8")

    with (out / "escalations.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ticket_id", "status", "category", "priority", "customer_name",
                    "subject", "reason_or_error"])
        for r in results:
            if r["status"] in ("needs_human_review", "routed_to_human"):
                t = r["triage"] or {}
                w.writerow([r["ticket_id"], r["status"], t.get("category", ""),
                            t.get("priority", ""), r["customer_name"], r["subject"],
                            t.get("reason") or "; ".join(r["errors"])])
        for rj in rejected:
            w.writerow([rj["ticket_id"], "rejected", "", "", "", "", rj["error"]])

    triaged = [r["triage"] for r in results if r["triage"]]
    status = Counter(r["status"] for r in results)
    retries = sum(r["retries"] for r in results)
    n = len(results)
    ready = status["ready_for_agent_approval"]
    manual_total = n * manual_min
    assisted_total = ready * review_min + (n - ready) * manual_min
    saved = manual_total - assisted_total

    escal_rows = [f"- **{r['ticket_id']}** ({r['status']}): {r['subject']} — "
                  f"{(r['triage'] or {}).get('reason') or '; '.join(r['errors'])}"
                  for r in results if r["status"] != "ready_for_agent_approval"]
    rej_rows = [f"- **{x['ticket_id']}**: {x['error']}" for x in rejected]

    md = f"""# Workflow Report

- Provider: `{meta['provider']}`
- Input: `{meta['input']}`
- Run at: {meta['started_at']}
- Duration: {meta['duration_s']:.2f} s

## Summary

| Metric | Value |
|---|---|
| Tickets in input | {n + len(rejected)} |
| Processed | {n} |
| Rejected at normalization | {len(rejected)} |
| Ready for agent approval | {ready} |
| Needs human review (escalated) | {status['needs_human_review']} |
| Routed to human (AI output failed validation twice) | {status['routed_to_human']} |
| Retries used | {retries} |

## Distribution

{_table('Category', Counter(t['category'] for t in triaged))}

{_table('Priority', Counter(t['priority'] for t in triaged), ['urgent', 'high', 'medium', 'low'])}

{_table('Sentiment', Counter(t['sentiment'] for t in triaged), ['negative', 'neutral', 'positive'])}

## Human action queue

{chr(10).join(escal_rows) or '_None._'}

## Rejected tickets

{chr(10).join(rej_rows) or '_None._'}

## Efficiency estimate

Assumptions: {manual_min:g} min to fully triage and draft one ticket by hand; {review_min:g} min to review an AI-prepared record. Escalated and routed tickets are counted at the full manual time (conservative).

| | Minutes |
|---|---|
| Fully manual | {manual_total:.1f} |
| With workflow | {assisted_total:.1f} |
| Estimated saving | {saved:.1f} ({(saved / manual_total * 100) if manual_total else 0:.0f}%) |
"""
    (out / "workflow_report.md").write_text(md, encoding="utf-8")
    return out
