# Day 3 — Lab 1: Plan the flow (stages 1–3)

**Goal:** by lunch you have a signed **plan pack** for the unshipped-quantity flow —
a graph of what exists, a brief, a contract and a design decision (ADR). The
afternoon builds from it.

Every step is a small loop: the agent drafts → a check runs → the agent fixes →
the check passes → you approve. Don't move on until the step's exit check passes.

Work in `day3/`. Put everything you produce in `work/`.

| Step | Time | Exit check |
|---|---|---|
| A. Toolkit | 10 min | `/skills` lists everything |
| B. Graph | 10 min | Answer cites sources; unknowns come back as unknown |
| C. Intake loop | 10 min | `check_brief.py` PASS |
| D. Contract loop | 10 min | `check_topic.py` + `check_props.py` PASS |
| E. Build the missing tool | 15 min | Your skill's selftest PASS; fires only on the right prompts |
| F. Design + gate | 10 min | Gate reviewer verdict + lead sign-off |

---

## A. Toolkit (10 min)
Follow [`../install-skills.md`](../install-skills.md) sections 1–4. Then:
```
/skills
```
**Exit:** you see `camel-integration-author`, `inumber-intake`, `kafka-topic-contract`,
`env-promotion-check`, `graphify`, `skill-creator` and the public skills.

## B. Graph — what exists (10 min)
```
/graphify lab
/graphify query "What reads from or writes to the valuechain unshipped quantity topic, and which service account has access?"
/graphify path "Manhattan" "Oracle E-Business Suite"
```
If you have time, add one real folder of your own: `/graphify <path> --update`.

**Observe:** every fact should point to where it came from. Anything not in the
material should come back as unknown — not invented.

## C. Intake loop — the brief (10 min)
Ask Claude:
> Use the inumber-intake skill. Read lab/greenfield-unshippedqty.png and write
> the brief for this flow to work/unshippedqty-brief.md. Mark anything the
> diagram doesn't tell you as OPEN. Then run the brief check and fix until it passes.

Now fill in the owner and gate owner **yourself**, and run:
```
python .claude/skills/inumber-intake/scripts/check_brief.py work/unshippedqty-brief.md
```
**Exit:** PASS. Count your OPEN items — you'll need them at the gate.

## D. Contract loop — topic and producer settings (10 min)
```
python .claude/skills/kafka-topic-contract/scripts/check_topic.py 'valuechain_{env}_000_unshippedqty_pub_v1' 'commerce_{env}_aff_salesorder_pub_v1'
```
Both pass — but the third segment is `000` in one and `aff` in the other. The
rule in `reference/naming.yaml` is a DRAFT. **As a room, agree what that segment
means**, tighten the rule, re-run.

Then ask Claude:
> Write work/producer.properties for this topic with auto.register.schemas=true,
> run check_props.py on it, then fix it.

**Exit:** both checks PASS after the fix (`auto.register.schemas=false`,
`AmwaySubjectNameStrategy` set).

## E. Build the missing tool — `consumer-pattern-picker` (15 min, pairs)
Stage 3 needs a decision no skill helps with yet: **which of the six certified
consumer patterns fits this flow?** Build that skill now.

```
/skill-creator
```
Ask for a skill named `consumer-pattern-picker` that:
- asks about ordering, throughput, and what must happen when OEBS is down
- picks one of: Serial, Concurrent, Circuit breaker (fail-fast), Circuit breaker
  (half-open), Error handler, Manual commit — using the table in
  `camel-integration-author/reference/authoring-rules.md`
- writes the properties for the chosen pattern
- has a script with a `selftest` that fails if `pollOnError` is `RETRY`,
  `ERROR_HANDLER` or `RECONNECT` without `breakOnFirstError=true`, or if manual
  and auto commit are both on
- says in its description when **not** to use it (e.g. MFT / Composer flows)

**Test the trigger** in a fresh session — 3 prompts that should fire it, 2 that
should not. Fix the description until it fires only on the right ones.

Stuck? A reference version is in `../solutions/consumer-pattern-picker/`.

## F. Design + gate (10 min)
Ask Claude:
> Use consumer-pattern-picker for the unshipped-quantity flow. Then write the
> decision as an ADR in work/adr-001.md: the pattern, why, and what happens to
> a message when OEBS is down.

Then:
> Use the ailc-gate-reviewer subagent on work/ for stages 1–3.

**Exit:** the reviewer's verdict table, and a lead (or your pair) signs the
bottom of `work/adr-001.md` with name and time.

---

## What you take to lunch — the plan pack
```
work/
  unshippedqty-brief.md    stage 1 — PASS, OPEN items listed
  producer.properties      stage 2 — PASS
  adr-001.md               stage 3 — signed
graphify-out/              what exists
```
