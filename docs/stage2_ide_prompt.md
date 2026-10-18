# Stage 2: Claude Code (IDE UX): build, test, run

Tool: **Claude Code** extension in **VS Code**. Open the repo, which already contains Perplexity's `prompts/`, `schema/` and `data/tickets.json` from Stage 1, open the Claude Code panel, and paste:

```
The files in prompts/, schema/ and data/ came from a Perplexity design session. First, harden the prompts: wrap ticket text in <ticket> tags and treat it as data only, reply in the customer's language, and add prompts/retry_suffix.txt. Turn the schema into strict JSON Schema with enums. Expand data/tickets.json to 18 tickets covering high-risk, multilingual, prompt-injection and invalid cases, and write data/golden_triage_results.json with expected labels and replies for my review.

Then build a Python 3.10+ package `triage` in this repo:

- triage/providers/base.py: abstract ChatProvider.complete(prompt) -> str. This is the ONLY model interface.
- triage/providers/mock.py: deterministic MockProvider answering from data/golden_triage_results.json (match the ticket_id inside the <ticket> block). Options fail_first / always_fail return an invalid priority "critical" to test retries.
- openai_provider.py, anthropic_provider.py, ollama_provider.py: thin adapters configured by env vars, SDKs imported lazily. get_provider(name) selects one (default from TRIAGE_PROVIDER, else mock).
- normalize.py: load JSON or CSV; trim; reject missing ticket_id/subject/message.
- validate.py: read allowed values from schema/triage_schema.json; strip ```json fences; enforce urgent => escalate; reply non-empty, under 120 words, no unsupported promises.
- pipeline.py: triage -> validate -> retry once with prompts/retry_suffix.txt + error -> reply -> validate -> retry once. Two failures => status routed_to_human. Provider exceptions must not crash the batch. Reject duplicate ids. No vendor code here.
- report.py: results/triaged_tickets.json, results/escalations.csv, results/workflow_report.md (summary, distributions, human queue, rejections, efficiency estimate).
- evaluate.py: agreement vs golden labels per field + mismatch table.
- __main__.py: `python -m triage run --input ... --output ... --provider ...` and `python -m triage evaluate`.
- tests/: pytest covering the full batch (16 processed, 2 rejected, 8 escalated), business rules, prompt-injection ticket stays urgent, retry recovery, double failure routing, provider exception, empty input, CSV input, duplicates, validator edge cases, evaluation.

Run pytest in the terminal and fix every failure. Then run `python -m triage run --input data/tickets.json --output results --provider mock` and `python -m triage evaluate`, and summarise the results.
```

Any IDE AI can be substituted (GitHub Copilot agent mode, Cursor, JetBrains AI); the prompt is tool-neutral.

Iteration that happened during this stage: the first test run had 8 failures because the mock read `"ticket_id": "string"` from the schema example in the prompt. The fix was to read the id from the last `<ticket>` block. After the fix, 22/22 tests passed.

Screenshot of the Claude Code session: `docs/screenshots/stage2-claude-code.png`
