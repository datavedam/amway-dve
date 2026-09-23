# Day 3 — Hands-on: Skills across the lifecycle

Your team already did the hard part: `camel-integration-author` turns your
Confluence standards into rules the agent follows, and `validate_bundle.py`
turns the rules that must never break into a check. That covers **stage 4**.
This session maps the other seven stages and fills one gap.

## Step 1 — See how your skill is built
Ask Claude:
> Open .claude/skills/camel-integration-author. For each of SKILL.md,
> reference/, assets/ and scripts/, tell me in one line what kind of
> knowledge lives there.

**Observe:** you should get four layers:

| Layer | Holds | Example from your skill |
|---|---|---|
| `SKILL.md` | Judgment — how to decide | VETO order, template-instances-only |
| `reference/` | Facts, read only when needed | Certified components, bean FQCNs, port map |
| `assets/` | Boilerplate to copy | Route templates, bundle skeleton |
| `scripts/` | Rules that must never break | `validate_bundle.py` |

Rule of thumb: **if a rule can be checked by a script, it belongs in a script.**

## Step 2 — Find where it will hurt
Ask Claude:
> Review camel-integration-author as a skill. Does its description say when
> NOT to use it? Are there test prompts? Can the copied route templates drift
> from their source? Give me three concrete improvements.

**Observe:** skills have their own lifecycle — author, test, review, publish,
keep in sync, retire. Who owns yours?

## Step 3 — Map coverage
Ask Claude:
> Using day3/README.md's eight AILC stages, build a table: stage | skill that
> covers it (ours, public, or day3/skills) | still a gap.

## Step 4 — Write one gap skill (pairs, 30 minutes)
Pick one:

| Skill | Stage | What its script checks |
|---|---|---|
| `consumer-pattern-picker` | 3 | Maps ordering / throughput / failure needs to one of the 6 certified consumer patterns and writes its properties (`breakOnFirstError=true` whenever `pollOnError` is `RETRY` or `ERROR_HANDLER`) |
| `oebs-staging-interface` | 4 | `camel-sql` only, `transacted=true`, `batch=true`, no DB call inside a split; your staging-table conventions (OPEN — you write them) |
| `exception-event-alerting` | 7 | ExceptionEvent published to the app error topic; non-prod severity is `"3"` |
| `integration-runbook` | 7 | Runbook generated from the bundle: topics, consumer group, error topic, replay endpoint, owners |

Use the skill creator:
```
/skill-creator
```
Your skill must have:
- a description with **when to use** and **when NOT to use**
- the rules in `SKILL.md`, facts in `reference/`
- a script with a `selftest` for anything mechanical

## Step 5 — Test the trigger, not just the content
Write 3 prompts that **should** fire your skill and 2 that **should not**
(for example, an MFT request should not fire a Camel skill). Run all five in
a fresh session.

**Observe:** did it fire on the right ones only? If not, fix the description —
that line decides when the skill loads.
