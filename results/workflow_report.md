# Workflow Report

- Provider: `mock`
- Input: `data/tickets.json`
- Run at: 2026-10-18T02:50:37+00:00
- Duration: 0.00 s

## Summary

| Metric | Value |
|---|---|
| Tickets in input | 18 |
| Processed | 16 |
| Rejected at normalization | 2 |
| Ready for agent approval | 8 |
| Needs human review (escalated) | 8 |
| Routed to human (AI output failed validation twice) | 0 |
| Retries used | 1 |

## Distribution

| Category | Count |
|---|---|
| account_access | 3 |
| billing | 5 |
| complaint | 2 |
| other | 1 |
| product_question | 2 |
| technical | 3 |

| Priority | Count |
|---|---|
| urgent | 5 |
| high | 4 |
| medium | 2 |
| low | 5 |

| Sentiment | Count |
|---|---|
| negative | 10 |
| neutral | 5 |
| positive | 1 |

## Human action queue

- **TCK-1002** (needs_human_review): Refund request — Duplicate subscription charge with a refund request; refunds require human approval per policy.
- **TCK-1004** (needs_human_review): Someone accessed my account — Unauthorized change of login email indicates a likely account compromise (security incident).
- **TCK-1006** (needs_human_review): Dashboard down for our whole team — Outage affecting all 40 users on a paid Business plan; work has stopped.
- **TCK-1008** (needs_human_review): Data deletion request - final notice — Overdue GDPR deletion request with an explicit legal threat; requires legal/privacy review.
- **TCK-1010** (needs_human_review): FIX THIS NOW — Message contains a threat of physical intimidation; must be reviewed by a human per safety policy.
- **TCK-1011** (needs_human_review): All my files disappeared after sync — Complete data loss after sync with empty trash; data-loss incident.
- **TCK-1013** (needs_human_review): Close my account — Account closure and full data deletion request; closures require human approval per policy.
- **TCK-1016** (needs_human_review): Card used without permission — Reported unauthorized card transactions (possible fraud); embedded instruction to lower priority was ignored.

## Rejected tickets

- **TCK-1017**: Missing required field: message
- **TCK-1018**: Missing required field: message

## Efficiency estimate

Assumptions: 5 min to fully triage and draft one ticket by hand; 1.5 min to review an AI-prepared record. Escalated and routed tickets are counted at the full manual time (conservative).

| | Minutes |
|---|---|
| Fully manual | 80.0 |
| With workflow | 52.0 |
| Estimated saving | 28.0 (35%) |
