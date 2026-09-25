---
name: parity-check
description: Prove that a changed integration still produces the same data as the old one — render the new Velocity mapping against new-source messages and compare every field with what the old flow produced. Use when migrating or re-platforming a flow (e.g. I3343 → I3343K), changing a source system, or asked "does the new mapping match the old", "parity", "old vs new output", "prove nothing changed for the consumer". Do NOT use for greenfield flows with no old output to compare against, or for reviewing schema compatibility (use kafka-topic-contract / kafka-schema-review).
---

# Parity check

Brownfield rule: **the structure may change, the data may not.** The consumer
(here I1001 → OEBS) must not be able to tell the old flow from the new one.

## How it works
1. Old flow's outputs are the **recording** (`recorded-orderudm/`) — in real life,
   captured by Pipeline Recorder.
2. The new mapping (`.vm`) is rendered against the **same orders from the new source**
   (`nextgen-input/`).
3. Every field is compared. Types count: `2` is not `"2"`, `null` is not `""`.
4. A difference is only accepted if it is listed in `allowed-differences.yaml`
   **with a reason and the name of the person who approved it**.

## Run it
```
uv run --with airspeed --with pyyaml python .claude/skills/parity-check/scripts/parity_check.py \
  run --vm <path/to/mapping.vm> --samples lab/samples --allowed <path/to/allowed-differences.yaml>
```
One message at a time: `... parity_check.py render --vm <file.vm> --input lab/samples/nextgen-input/S1.json`
Self-check: `... parity_check.py selftest`

## Loop
Run → read each `FAIL` line (`path: old=… new=…`) → find the rule in the old mapping
document that explains the old value → fix the mapping → run again. Stop at
`PARITY PASS`, or after 3 attempts return the remaining differences.

## Rules
- **Never edit the recording or the input samples** to make parity pass.
- **Never add a data field to the allowed list** to make parity pass — unless the
  change request requires that change; then a named person signs it. Otherwise allowed
  differences are structure/metadata only, and a person signs each one.
- Unknown rule? Mark it OPEN and ask — don't guess from the sample values.
- Paste the final `PARITY PASS` line into EVIDENCE.md.

## Honest limit
The script renders Velocity with `airspeed` (Python), not Camel's engine. It covers
the map style your team uses (`$out.put`, `$list.add`, `#foreach`, `#if`,
`$foreach.count`). The real parity run replays recorded messages through the
running bundle: `POST /api/replay/{route_id}`.
