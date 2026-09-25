# Day 5 — Quick lab: prove I1001 won't notice (1 hour)

**The change:** the salesorder source moves from Hybris to NextGen Commerce and
I3343 becomes I3343K. **What I1001 receives must not change** — except the one
field the change request asks for (`sourceSystem`).

**The rule:** the agent may change the structure, never the data. Parity proves it.

You work in `day4/` — the diagrams, sample orders, old mapping rules and change
request are all in `day4/lab/`. Everything you produce goes in `day4/work/`.
Keep `work/EVIDENCE.md` as you go: what ran, the real output (pasted), who approved.

> The sample orders and the old mapping rules are **made-up training data**, not real
> Amway orders or the real I3343 mapping.

| Time | Step | Exit check |
|---|---|---|
| 5 min | Setup | `selftest PASS` |
| 8 min | 1. Impact | Every consumer listed with its source; unknowns OPEN |
| 7 min | 2. Freeze the contract | A person signs the frozen list |
| 18 min | 3. Write the mapping | `render` works on S1 |
| 14 min | 4. Parity loop + the signed difference | `PARITY PASS (6/6 …)` in EVIDENCE.md |
| 3 min | 5. Gate | Reviewer verdict |

---

## Setup (5 min)
```
cd training/repo/amway-dve && git pull
cd day4
bash ../day5/setup.sh
```
It copies the skills, the gate reviewer and the lab's **deny rules** (the agent can't
read `solutions/` or edit `lab/samples/`), puts a starter mapping in
`work/salesorder-to-orderudm.vm`, and ends with `selftest PASS`.
Then start Claude Code in `day4/` and check `/skills`.

## 1. Impact — who gets hit? (8 min)
Ask Claude:
> Read lab/order-flow.md and the two diagrams in lab/. Write work/impact.md: every
> consumer of the salesorder source topic and of the OrderUDM output, each with where
> you found it. Anything the material doesn't confirm is OPEN.

**Observe:** GWMS, BlueYonder and the data team read the same salesorder events —
that's why I3343K needs a **new consumer group**.
(If graphify is installed from Day 3: `/graphify lab` then `/graphify query "..."` works too.)

## 2. Freeze the contract (7 min)
> Read lab/legacy-i3343-mapping.md and lab/samples/recorded-orderudm/. Write
> work/frozen-contract.md: every OrderUDM field I1001 receives, its type and an
> example value — the fields that must not change.

**Exit:** a lead (or your pair) signs the bottom of `frozen-contract.md`.

## 3. Write the mapping (18 min)
The starter `work/salesorder-to-orderudm.vm` already maps `orderId`, `affiliate` and
`currency` in your team's map style. Ask Claude:
> Use the parity-check skill. Finish work/salesorder-to-orderudm.vm from
> lab/legacy-i3343-mapping.md, lab/nextgen-salesorder-fields.md and
> lab/change-request-i3343k.md. Keep the Velocity map style. Don't run parity yet.

Check that it renders:
```
uv run --with airspeed --with pyyaml python .claude/skills/parity-check/scripts/parity_check.py \
  render --vm work/salesorder-to-orderudm.vm --input lab/samples/nextgen-input/S1.json
```

## 4. Parity loop (14 min)
```
uv run --with airspeed --with pyyaml python .claude/skills/parity-check/scripts/parity_check.py \
  run --vm work/salesorder-to-orderudm.vm --samples lab/samples
```
Read every `FAIL` line — `path: old=… new=…`. Then:
> For each difference, find the rule in lab/legacy-i3343-mapping.md that explains the
> old value, fix the mapping, and run parity again. Never change the samples or the recording.

When only `sourceSystem` is left (`HYBRIS` → `NGC`, as the change request asks), a
**person** decides it's allowed:
```
cp .claude/skills/parity-check/reference/allowed-differences.example.yaml work/allowed-differences.yaml
```
Fill in the reason and a real name, then run again with
`--allowed work/allowed-differences.yaml`.

**Exit:** `PARITY PASS (6/6 samples match; 6 allowed difference(s) accepted)` pasted into EVIDENCE.md.

## 5. Gate (3 min)
> Use the ailc-gate-reviewer subagent on work/ for stage 8: impact list, frozen
> contract and parity.

It will mark the ADR and the new consumer group OPEN — you didn't do those today.
That's correct: it reports, it doesn't approve.

---

## Stretch — the whole bundle
Follow step 5 of `day4/assignments/LAB3.md`: build I3343K with `camel-integration-author`
and loop on `validate_bundle.py`. You'll need your team's copy of the skill.

## Show-back
1. What did parity catch that looked right when you wrote it?
2. Which OPEN question needs someone outside this room — and who?
