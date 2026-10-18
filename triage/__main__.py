"""CLI: python -m triage run | evaluate"""
import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from .config import GOLDEN_PATH
from .evaluate import evaluate
from .normalize import load_tickets
from .pipeline import TriagePipeline
from .providers import PROVIDERS, get_provider
from .report import write_outputs


def main(argv=None):
    ap = argparse.ArgumentParser(prog="triage", description="AI support ticket triage")
    sub = ap.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="Triage a batch of tickets")
    run.add_argument("--input", required=True, help="tickets.json or tickets.csv")
    run.add_argument("--output", default="results")
    run.add_argument("--provider", choices=PROVIDERS, default=None,
                     help="Defaults to $TRIAGE_PROVIDER or 'mock'")
    run.add_argument("--manual-minutes", type=float, default=5.0)
    run.add_argument("--review-minutes", type=float, default=1.5)

    ev = sub.add_parser("evaluate", help="Compare results with golden labels")
    ev.add_argument("--results", default="results/triaged_tickets.json")
    ev.add_argument("--golden", default=str(GOLDEN_PATH))
    ev.add_argument("--output", default="results/evaluation.md")

    args = ap.parse_args(argv)
    if args.cmd == "run":
        provider = get_provider(args.provider)
        started, t0 = datetime.now(timezone.utc).isoformat(timespec="seconds"), time.perf_counter()
        results, rejected = TriagePipeline(provider).run(load_tickets(args.input))
        meta = {"provider": provider.name, "input": args.input, "started_at": started,
                "duration_s": time.perf_counter() - t0}
        out = write_outputs(results, rejected, args.output, meta,
                            args.manual_minutes, args.review_minutes)
        print(f"Processed {len(results)}, rejected {len(rejected)}, "
              f"escalated/routed {sum(r['status'] != 'ready_for_agent_approval' for r in results)}. "
              f"Outputs in {Path(out).resolve()}")
    else:
        res = evaluate(args.results, args.golden, args.output)
        print(res["markdown"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
