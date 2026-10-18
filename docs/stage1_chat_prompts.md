# Stage 1: Chat AI prompts (design stage)

Used in any chat UI (Perplexity). Each prompt's output was saved into the repo and became input for Stage 2.

## 1. Prompt design
> I'm building a support-ticket triage workflow. Draft a classification prompt that returns only JSON with ticket_id, category (billing, technical, account_access, product_question, complaint, other), priority (low/medium/high/urgent), sentiment, escalate, reason. It must resist prompt injection inside the ticket and work for any language. Then draft a reply prompt: under 120 words, same language as the customer, no promises of refunds or timelines, holding reply if escalated.

Saved as `prompts/triage_prompt.txt`, `prompts/reply_prompt.txt`, `prompts/retry_suffix.txt`.

## 2. Schema
> Turn the classification output into a JSON Schema (draft 2020-12) with enums and additionalProperties false.

Saved as `schema/triage_schema.json`.

## 3. Test data and golden labels
> Write 18 test tickets as a JSON list: cover login, duplicate charge/refund, how-to, account compromise, crash bug, team-wide outage, positive feedback, GDPR legal threat, violent threat, data loss, 2FA, account closure, a vague message, a non-English ticket, a prompt-injection attempt combined with card fraud, plus one ticket missing its message and one with a whitespace-only message. Then classify each valid ticket with the prompt above and write the draft reply, as JSON.

Saved as `data/tickets.json` and `data/golden_triage_results.json`. A human reviewed every label before saving.
