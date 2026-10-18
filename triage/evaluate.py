"""Compare a run's triage output with reference (golden) labels."""
import json
from pathlib import Path

FIELDS = ("category", "priority", "sentiment", "escalate")


def evaluate(results_path, golden_path, out_path=None):
    results = json.loads(Path(results_path).read_text(encoding="utf-8"))["results"]
    golden = {r["ticket_id"]: r["triage"] for r in
              json.loads(Path(golden_path).read_text(encoding="utf-8"))["results"]}
    compared, hits, mismatches = 0, {f: 0 for f in FIELDS}, []
    for r in results:
        g, t = golden.get(r["ticket_id"]), r["triage"]
        if not g or not t:
            continue
        compared += 1
        for f in FIELDS:
            if g[f] == t[f]:
                hits[f] += 1
            else:
                mismatches.append(f"| {r['ticket_id']} | {f} | {g[f]} | {t[f]} |")
    rows = [f"| {f} | {hits[f]}/{compared} | {hits[f] / compared * 100 if compared else 0:.0f}% |"
            for f in FIELDS]
    md = ("# Evaluation vs golden labels\n\n"
          f"Tickets compared: {compared}\n\n| Field | Agreement | % |\n|---|---|---|\n"
          + "\n".join(rows) + "\n\n## Mismatches\n\n"
          + ("| Ticket | Field | Expected | Got |\n|---|---|---|---|\n" + "\n".join(mismatches)
             if mismatches else "_None._") + "\n")
    if out_path:
        Path(out_path).write_text(md, encoding="utf-8")
    return {"compared": compared, "agreement": hits, "mismatches": len(mismatches), "markdown": md}
