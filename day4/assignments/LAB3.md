# Day 4 — Lab 3: Brownfield — move I3343 to I3343K without I1001 noticing

**The change** (from your two diagrams in `lab/`):

| | Today | Target |
|---|---|---|
| Source | Hybris `commerce_env_affiliate_salesorder_pub_v1` | NextGen Commerce `commerce_prod_aff_salesorder_pub_v1` |
| Translator | **I3343** → `translateAndPublishOrderUDM` | **I3343K** (Camel bundle) |
| Output | OrderUDM | topic `commerce_pd_aff_orderudm_pub_v1` → OrderUDM |
| Consumer | I1001 → OEBS | **I1001 → OEBS — must not see any difference** |

**The rule for the whole lab:** the agent may change the structure, never the data.
The one intended change is in [`lab/change-request-i3343k.md`](../lab/change-request-i3343k.md).

Work in `day4/`. Put everything you produce in `work/`. Keep `work/EVIDENCE.md` as
you go — one row per step: what ran, the real output (pasted), who approved.

> The sample messages in `lab/samples/` and the mapping document
> `lab/legacy-i3343-mapping.md` are **made-up training data**, not real Amway orders.

| Part | Step | Time | Exit check |
|---|---|---|---|
| **3A Plan the change** | 1. Impact | 15 min | Impact list, every consumer with its source, unknowns OPEN |
| | 2. Change brief | 10 min | `check_brief.py` PASS |
| | 3. Freeze the contract | 10 min | Frozen field list signed; topic-name findings recorded |
| | 4. Switchover ADR | 15 min | ADR signed |
| **3B Build and prove** | 5. Build I3343K | 30 min | `validate_bundle.py` PASS |
| | 6. Parity | 25 min | `PARITY PASS` |
| | 7. Gate | 5 min | Reviewer verdict for stage 8 |
| **3C Switchover and rollback** | 8. Release + runbook | 25 min | `check_envs.py` PASS; runbook with rollback and an owner |

---

## Setup (5 min, before 3A)
```
cd training/repo/amway-dve && git pull && cd day4
mkdir -p .claude/skills .claude/agents work
cp -r ../day3/skills/* .claude/skills/          # inumber-intake, kafka-topic-contract, env-promotion-check
cp -r skills/parity-check .claude/skills/
cp agents/ailc-gate-reviewer.md .claude/agents/  # this version adds stage 8
cp lab-settings.json .claude/settings.json      # deny: reading solutions/, editing lab/samples/
cp -r <path-to-your-gi-ai-skills>/camel-integration-author .claude/skills/
```
The deny rules are the Day 2 permissions at work: the agent can't peek at the
answers, and it can't change the recording to make parity pass.

Check with `/skills`. Test the parity script once:
```
uv run --with airspeed --with pyyaml python .claude/skills/parity-check/scripts/parity_check.py selftest
```

---

## 3A — Plan the change

### 1. Impact — who gets hit? (15 min)
```
/graphify lab
/graphify query "Which systems and interfaces read the salesorder topic, and which read the OrderUDM output of I3343?"
/graphify path "NextGen Commerce" "OEBS"
```
Then ask Claude:
> Write work/impact.md: every consumer of the salesorder source topic and of the
> OrderUDM output, each with where you found it. Anything the material doesn't
> confirm is OPEN.

**Exit:** `work/impact.md` exists. **Observe:** only **I3343** is confirmed as a reader
of the salesorder topic. GWMS (receives the order over REST), BlueYonder (fulfilment
events) and the data team are **OPEN** — the material doesn't say whether they read it.
Either way, I3343K gets its own **new consumer group** and never touches the existing ones.

### 2. Change brief (10 min)
> Use the inumber-intake skill. Write the brief for the change "I3343 → I3343K,
> source Hybris → NextGen Commerce" to work/i3343k-brief.md. Mark anything the
> diagrams don't tell you as OPEN.

Fill in owner and gate owner yourself, then:
```
python .claude/skills/inumber-intake/scripts/check_brief.py work/i3343k-brief.md
```

### 3. Freeze the contract (10 min)
> Read lab/legacy-i3343-mapping.md and lab/samples/recorded-orderudm/. Write
> work/frozen-contract.md: every OrderUDM field I1001 receives, its type, and an
> example value. These are the fields that must not change.

Then check the topic names from both diagrams:
```
python .claude/skills/kafka-topic-contract/scripts/check_topic.py 'commerce_env_affiliate_salesorder_pub_v1' 'commerce_prod_aff_salesorder_pub_v1' 'commerce_pd_aff_orderudm_pub_v1'
```
**Observe:** all three fail the draft rule — the diagrams use literal environment
names, and `prod`/`pd`, `affiliate`/`aff` don't agree. Record each one as an OPEN
question in the brief. **Exit:** a principal signs the bottom of `frozen-contract.md`.

### 4. Switchover ADR (10–15 min)
```
/grill-me
```
> Grill me on how to switch I1001 from I3343 to I3343K. Options: switch all at once;
> run both side by side and compare; move one consumer at a time. Cover: where the
> new consumer group starts reading, what happens to orders in flight, and how we roll back.

Then:
> Use documentation-and-adrs. Write the decision to work/adr-002-switchover.md,
> including the rollback.

**Exit:** a principal signs the ADR.

---

## 3B — Build and prove

### 5. Build I3343K (30 min)
> Use camel-integration-author. Scaffold the I3343K bundle in work/i3343k/:
> an eda-proto-consumer template instance for the NextGen salesorder topic with a
> NEW consumer group; one YAML route from direct: in VETO order; the mapping in
> mounts/salesorder-to-orderudm.vm using a Velocity map; an eda-proto-producer
> template instance for the OrderUDM topic with auto.register.schemas=false and
> AmwaySubjectNameStrategy. Variables for dv and qa1, secrets as secret:/field:
> bindings only. Write the mapping from lab/legacy-i3343-mapping.md,
> lab/nextgen-salesorder-fields.md and lab/change-request-i3343k.md. Mark anything
> unknown OPEN.

```
python .claude/skills/camel-integration-author/scripts/validate_bundle.py work/i3343k
```
Loop until PASS.

**OPEN — ask your Camel owners, don't guess:** the mapping skeleton ends with `$out`,
which Camel's Velocity prints as a Java map (`{orderId=…}`), but `eda-proto-producer`
expects **JSON**. How do your bundles turn the map into JSON? Record the question in
`work/i3343k/OPEN.md`. (The parity check below can't see this: it compares the data,
not the format.)

### 6. Parity (25 min)
```
uv run --with airspeed --with pyyaml python .claude/skills/parity-check/scripts/parity_check.py \
  run --vm work/i3343k/mounts/salesorder-to-orderudm.vm --samples lab/samples
```
Read every `FAIL` line — `path: old=… new=…` — and ask Claude:
> Use the parity-check skill. For each difference, find the rule in
> lab/legacy-i3343-mapping.md that explains the old value, fix the mapping, and
> run parity again. Never change the samples or the recording.

The change request says `sourceSystem` must become `NGC`, so a correct mapping
**cannot** pass without a signature: `sourceSystem` will always differ from the
recording (`HYBRIS` → `NGC`). **If parity passes with no allowed differences, check
`sourceSystem` — the mapping probably kept `HYBRIS`.** Is it structure or data? A
person decides. Copy `.claude/skills/parity-check/reference/allowed-differences.example.yaml`
to `work/i3343k/allowed-differences.yaml`, fill in the reason, and have a principal
put their name on it. Run again with `--allowed work/i3343k/allowed-differences.yaml`.

**Exit:** `PARITY PASS (6/6 samples match; …)` pasted into EVIDENCE.md.

### 7. Gate (5 min)
> Use the ailc-gate-reviewer subagent on work/ for stage 8.

---

## 3C — Switchover and rollback (25 min)
```
python .claude/skills/env-promotion-check/scripts/check_envs.py work/i3343k
```
Fix until PASS. Then:
> Write work/i3343k/RUNBOOK.md: source topic and the NEW consumer group, output
> topic, error topic, replay endpoint, the switchover steps from the ADR, the
> rollback steps, and the owner (a person's name).

**Stretch — MCP:** use the `03-sqlite-db` pattern from this morning to put
`lab/samples/recorded-orderudm/` behind a **read-only** MCP tool, and ask Claude to
compare a new output with the recording through that tool — no file or database
access of its own.

---

## Show-back
1. What did parity catch that looked right to you?
2. Which OPEN questions need someone outside this room — and who?
3. What would you need to run this on real I3343 traffic next week?
