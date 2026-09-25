---
name: inumber-intake
description: Turn a new integration request (an email, a ticket, an architecture diagram) into a one-page I-number intake brief before any design or code starts. Use when the user says "new integration", "new I-flow", "intake", "write the brief for IXXXX", "scope this interface", or shares a flow diagram and asks what is needed. Do NOT use for writing Camel routes or bundles (use camel-integration-author), for MFT/Composer configs (use mft-config-generator), or for changing an existing flow.
---

# I-number intake brief

Stage 1 of the integration lifecycle. The output is a brief, not code. Nothing is designed or
built until the brief passes `scripts/check_brief.py` and the gate owner accepts it.

## Rules
- Fill every field in `assets/brief.template.md`. Copy the template; do not change the field names.
- Only write what the request or the diagram actually says. If a fact is not there, write `OPEN`
  and add a matching line under **Open questions** saying who can answer it.
- Never invent a system, topic, table, volume, or owner. `OPEN` is always better than a guess.
- Use the topic name exactly as written on the diagram, with `{env}` kept as a placeholder
  (for example `valuechain_{env}_000_unshippedqty_pub_v1`).
- **Owner** and **Gate owner** must be named people or teams. `OPEN` is not accepted for Owner.
- Failure behaviour must say what happens to a message that cannot be processed
  (retry, stop the consumer, error topic + ExceptionEvent). If unknown, `OPEN`.

## Workflow
1. Read the request and the diagram. List the systems left to right.
2. Copy `assets/brief.template.md` to `briefs/<I-number>-brief.md` (use `IXXXX` if the number is not assigned yet).
3. Fill each field. Mark unknowns `OPEN` and add an open question for each one.
4. Run the check:
   ```
   python scripts/check_brief.py briefs/<I-number>-brief.md
   ```
   Exit code 0 = complete (OPEN fields are listed as warnings). Exit code 1 = a field is empty
   or Owner is missing. Fix and re-run until it passes.
5. Show the brief and the check output to the user. Stop there — the gate owner decides if the
   open questions must be answered before design starts.

## Evidence
The brief file plus the `check_brief.py` output. Paste both into the review.

## Self-test
`python scripts/check_brief.py selftest`
