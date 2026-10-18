# Stage 1: Perplexity (Chat UX): design

Tool: **Perplexity** (chat interface). Everything it produced was saved into the repo and handed to Stage 2.

## Prompt used

> Using this rubric [pasted rubric], design an AI workflow project that chains at least two AI UX types. Pick a problem that splits into stages.

Perplexity chose **AI-powered customer support ticket triage** and produced the full first-draft submission, recorded in `docs/stage1_perplexity_output.md`.

## What Perplexity produced → where it lives in the repo

| Perplexity output | Saved as |
|---|---|
| Classification prompt template | `prompts/triage_prompt.txt` (hardened in Stage 2) |
| Reply prompt template | `prompts/reply_prompt.txt` (hardened in Stage 2) |
| Output format (`ticket_id`, `category`, `priority`, `sentiment`, `escalate`, `reason`) | `schema/triage_schema.json` (formalised in Stage 2) |
| Starter tickets TCK-1001, TCK-1002 | `data/tickets.json` (expanded in Stage 2) |
| Operating rules, test plan, draft Python outline | Basis for `docs/stage2_ide_prompt.md` |

## Known gaps handed to Stage 2

- `call_chat_ai()` raised `NotImplementedError`, so the draft could not run.
- The retry-on-invalid-output behaviour was described but not implemented.
- Only 2 test tickets were provided, and the test plan had no expected-answer set.
- The prompts had no protection against instructions embedded in ticket text.

Screenshot of the Perplexity session: `docs/screenshots/stage1-perplexity.png`
