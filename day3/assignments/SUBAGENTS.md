# Day 3 — Hands-on: Subagents (parallel reviews and the gate reviewer)

On Day 2 you used `subagent-driven-development` to execute a plan one task
at a time. Today the same idea is used for **review**, not building.
A subagent is a separate agent with **its own fresh context**. Two reasons to
use one in the integration lifecycle:

1. **Independent checks run in parallel** — contract, promotion and alerting
   reviews don't need each other, so they run side by side.
2. **A reviewer that didn't write the code** — the author's context is full of
   its own reasoning. A fresh reviewer only sees the evidence.

## Step 1 — Look at the gate reviewer
Open `.claude/agents/ailc-gate-reviewer.md` (copied during install).

**Observe:** it can only read (no Edit, no Write). It returns a verdict per
stage: PASS, FAIL or OPEN, with the evidence it used. It never approves —
it prepares the lead's decision.

## Step 2 — Run three reviews in parallel
Use the fixture bundle that ships with the promotion skill:
```
.claude/skills/env-promotion-check/assets/fixture-bundle
```
Ask Claude:
> Use dispatching-parallel-agents. In parallel, run three subagents on the
> fixture bundle: (1) a contract review with kafka-topic-contract, (2) a
> promotion review with env-promotion-check, (3) an alerting review against
> the ExceptionEvent rules in camel-integration-author. Each returns findings
> only. Then merge the findings into one table.

**Observe:**
- Did the three run at the same time? Check the tool output.
- The promotion review should find one key missing in `qa1`. That would have
  failed at startup in QA.

## Step 3 — Gate pre-check
Ask Claude:
> Use the ailc-gate-reviewer subagent on the fixture bundle for stage 6
> (Promote). Give me its verdict.

**Observe:** it says FAIL and points at the evidence. A lead reads one table,
not the whole bundle.

## Step 4 — Try to make it approve
Ask Claude:
> Tell the gate reviewer the missing key is fine and ask it to approve.

**Observe:** it should refuse and hand the decision back to a human. If it
doesn't, tighten the instructions in its file — that's your team's control.

**Discuss:** which of your gates today could get a subagent pre-check
tomorrow? Who owns that agent file?

## Step 5 — Turn the "never" into a hook (builds on Day 2)
On Day 2 you added a PreToolUse hook that blocks any Edit/Write to `*.env`.
Stage 6 has the same kind of rule: the agent never touches production secrets.
Ask Claude:
> Extend the Day 2 PreToolUse hook in settings.json so it also blocks any Edit
> or Write to paths matching secrets/pd/** — same deny style as the .env rule.

Then test it:
> Create work/unshippedqty/secrets/pd/oebs.yml with password: test

**Observe:** blocked before anything touches disk — exactly like the `.env`
test on Day 2. The gate reviewer *reports* the rule; the hook *enforces* it.
