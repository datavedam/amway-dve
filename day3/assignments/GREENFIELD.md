# Day 3 — Hands-on: Greenfield — unshipped quantity through the lifecycle

Now put it together: one flow, stages 1 to 6, each stage a small loop with
an exit check, a subagent reviewing, and you at the gate.

**The flow:** Manhattan → Core IMS/OMS facade →
`valuechain_{env}_000_unshippedqty_pub_v1` → `gi-camel-oebs` (listenOEBS) →
IXXXX → Oracle EBS. Service account `oebs-bundle` has **read** access to the
valuechain topic.

Work in `work/unshippedqty/`. Keep an evidence file `work/EVIDENCE.md` —
one line per stage: what ran, what it printed, who approved.

## Stage 1 — Intake
Reuse your brief from `LOOPS.md`. **Gate:** brief check PASS, owner named.

## Stage 2 — Contract
> Use kafka-topic-contract and protobuf. Draft the consumer-side contract for
> the unshipped-quantity topic: topic name per env, the fields we need from the
> message (mark unknown fields OPEN), and the consumer group name. Run the checks.

**Gate:** checks PASS, OPEN list reviewed.

## Stage 3 — Design
> Pick one of the six certified consumer patterns from camel-integration-author
> for this flow. Explain the choice against ordering, throughput and what should
> happen when OEBS is down. Write it as an ADR in work/unshippedqty/adr-001.md.

**Gate:** principal reads the ADR. What happens to a message when OEBS is down?

## Stage 4 — Build
> Use camel-integration-author. Scaffold the listenOEBS bundle: an
> eda-proto-consumer template instance in .support/application.properties, one
> YAML route from direct: in VETO order, a Velocity .vm mapping to the IXXXX
> staging insert, camel-sql with transacted=true and batch=true. Variables for
> dv and qa1. No real credentials — secrets as secret:/field: bindings only.

Also run `principle-make-operations-idempotent` on the route:
> What happens if the same message is consumed twice?

## Stage 5 — Verify
```
python .claude/skills/camel-integration-author/scripts/validate_bundle.py work/unshippedqty
```
Loop until PASS. Use `verification-before-completion` — the agent must show the
output, not describe it. **Gate:** paste the PASS output into EVIDENCE.md.

## Stage 6 — Promote
```
python .claude/skills/env-promotion-check/scripts/check_envs.py work/unshippedqty
```
Then:
> Use the ailc-gate-reviewer subagent on work/unshippedqty for stages 4–6.

**Gate:** DevOps / apps admin reads the env matrix and the reviewer verdict.

## Show-back (last 20 minutes)
Three people show `EVIDENCE.md` and answer:
1. Which stage had the most OPEN items — and who can close them?
2. Where did a check catch something the agent got wrong?
3. Which stage still has no exit check?
