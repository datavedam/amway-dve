# Day 3 — Lab 2: Greenfield — build it and prove it (stages 4–7)

**Goal:** the listenOEBS bundle for the unshipped-quantity flow, built from your
Lab 1 plan pack, with evidence for every stage and a sign-off at the end.

**The flow:** Manhattan → Core IMS/OMS facade →
`valuechain_{env}_000_unshippedqty_pub_v1` → `gi-camel-oebs` (listenOEBS) →
IXXXX → Oracle EBS. Service account `oebs-bundle` has **read** access to the topic.

Work in `work/unshippedqty/`. Keep `work/EVIDENCE.md` as you go:

```markdown
| Stage | Check run | Output (paste the real lines) | Approved by |
|---|---|---|---|
| 4 Build   | idempotency review         |  |  |
| 5 Verify  | validate_bundle.py + reviewer |  |  |
| 6 Promote | check_envs.py + pd hook    |  |  |
| 7 Operate | alert setting + runbook    |  |  |
```

| Step | Time | Exit evidence |
|---|---|---|
| 1. Build | 30 min | Bundle exists; idempotency review answered |
| 2. Test | 20 min | `validate_bundle.py` PASS + reviewer verdict |
| 3. Release | 20 min | `check_envs.py` PASS; hook blocks the pd write |
| 4. Run | 10 min | Severity `"3"` in non-prod; runbook with an owner |
| 5. Approve | 10 min | Signed `EVIDENCE.md` |

---

## 1. Build (30 min)
Give the agent your plan, not a one-liner:
> Use camel-integration-author. Read work/unshippedqty-brief.md,
> work/producer.properties and work/adr-001.md. Scaffold the listenOEBS bundle in
> work/unshippedqty/: an eda-proto-consumer template instance in
> .support/application.properties using the consumer pattern from the ADR; one
> YAML route from direct: in VETO order (validate, enrich, transform,
> orchestrate); a Velocity .vm mapping to the IXXXX staging insert under mounts/;
> camel-sql with transacted=true and batch=true. Variables for dv and qa1.
> No real credentials — secrets as secret:/field: bindings only. Mark anything
> the plan doesn't tell you as OPEN.

Open each file and check it against the rule it should follow. Then:
> Use principle-make-operations-idempotent on this route. What happens if the
> same message is consumed twice? Fix it if the answer is "a duplicate row".

## 2. Test (20 min)
```
python .claude/skills/camel-integration-author/scripts/validate_bundle.py work/unshippedqty
```
Loop until PASS. Use `verification-before-completion` — the agent must show the
output, not describe it. Then:
> Use the ailc-gate-reviewer subagent on work/unshippedqty for stages 4 and 5.

Paste the PASS lines and the verdict table into `EVIDENCE.md`.

## 3. Release (20 min)
```
python .claude/skills/env-promotion-check/scripts/check_envs.py work/unshippedqty
```
Fix every missing key and every secret-looking value in `variables/` until PASS.

Then extend your **Day 2 hook**: ask Claude to add `secrets/pd/**` to the
PreToolUse hook that blocks `*.env` writes. Test it:
> Create work/unshippedqty/secrets/pd/oebs.yml with password: test

It must be blocked before anything touches disk. Paste the block message into
`EVIDENCE.md`.

## 4. Run (10 min)
> Check this bundle's ExceptionEvent alerting: is it published to the app's
> error topic, and is the non-prod severity "3"? Then use the runbook skill to
> write work/unshippedqty/RUNBOOK.md from the bundle: topic, consumer group,
> error topic, replay endpoint (POST /api/replay/{route_id}), what happens when
> OEBS is down (from your ADR), and the owner.

## 5. Approve (10 min)
> Use the ailc-gate-reviewer subagent on work/unshippedqty for stages 4–7.

A DevOps / apps admin person (or a lead) reads `EVIDENCE.md` and the verdict,
and signs the last column. **No evidence, no signature.**

---

## Show-back
Three people show `EVIDENCE.md` and answer:
1. What did a check catch that the agent got wrong?
2. Which stage still has no check — only someone's opinion?
3. What will you use on your own work next week?
