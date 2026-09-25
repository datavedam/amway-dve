# Day 5 — Brownfield lab: change the salesorder flow without I1001 noticing

Two hours. We walk it together: in every round the facilitator explains **why**
(one slide), you **do** the step, then we look at **what you should see**.
This sheet has everything you need if you fall behind or want to redo a step.

---

## The story in one minute

Today the salesorder flow looks like this:

```
Hybris  →  salesorder topic  →  I3343 (translate)  →  OrderUDM  →  I1001  →  OEBS staging
```

The business is moving the source to **NextGen Commerce**, and I3343 is being
rebuilt as **I3343K** (a Camel bundle):

```
NextGen Commerce  →  new salesorder topic  →  I3343K  →  OrderUDM topic  →  I1001  →  OEBS staging
```

I1001 and OEBS **don't change**. They must keep receiving exactly the same OrderUDM
data. The change request asks for **one** difference only: the field `sourceSystem`
changes from `"HYBRIS"` to `"NGC"`.

**The rule for today:** the structure may change (new source, new message shape, new
translator). The data I1001 receives may not — except that one signed difference.

**How we prove it — parity:** take the same orders, put them through the old flow and
the new mapping, and compare the outputs field by field. If they match, I1001 won't
notice.

> Everything in `day4/lab/` is **made-up training data** (orders, old mapping rules,
> change request). It is shaped like your flow, but it is not real Amway data.

---

## Before you start

You need: the `amway-dve` repo from Day 1, Claude Code, and `uv` (both checked on Day 1).
On **Windows**, use **Git Bash** for every command in this sheet, as on Day 1.

### What's where
You work inside `amway-dve/day4/`. Everything you write goes in `day4/work/`.

| File | What it is |
|---|---|
| `lab/brownfield-salesorder-flow.png` | Today's flow (from your architecture) |
| `lab/brownfield-salesorder-target.png` | The target flow |
| `lab/order-flow.md` | Who else uses the salesorder events (from the Day 1 order flow) |
| `lab/change-request-i3343k.md` | What changes, and what must not |
| `lab/nextgen-salesorder-fields.md` | The **new** message: NextGen fields and what they mean |
| `lab/legacy-i3343-mapping.md` | The **old** rules: how I3343 builds OrderUDM today |
| `lab/samples/nextgen-input/S1–S6.json` | Six orders as NextGen will send them |
| `lab/samples/recorded-orderudm/S1–S6.json` | What the old I3343 produced for the same six orders (the "recording") |
| `work/EVIDENCE.md` | Your evidence log — one row per round |

### How to paste a prompt into Claude Code
Every "Ask Claude" block below is one prompt. Copy the whole block (all lines) and
paste it as one message.

### The two commands you will run most
Both run from `day4/`. They are long; copy them exactly.

**Render** — show what your mapping produces for one order:
```
uv run --with airspeed --with pyyaml python .claude/skills/parity-check/scripts/parity_check.py render --vm work/salesorder-to-orderudm.vm --input lab/samples/nextgen-input/S1.json
```

**Parity** — compare your mapping with the recording, for all six orders:
```
uv run --with airspeed --with pyyaml python .claude/skills/parity-check/scripts/parity_check.py run --vm work/salesorder-to-orderudm.vm --samples lab/samples
```
Each difference prints as `path: old=… new=…` — `old` is what I1001 gets today,
`new` is what your mapping would send.

---

## Round 0 — Set up (0:00–0:10)

**What this is about:** get the lab tools into your project: the skills, the gate
reviewer, and **deny rules** (the Day 2 permissions): Claude may not read
`solutions/` or `lab/samples/generate.py` (both give the answers away), and may not
edit `lab/samples/` (you can't make parity pass by changing the recording).

**Do this**
1. Open a terminal (Git Bash on Windows).
2. Run:
   ```
   cd training/repo/amway-dve
   git pull
   cd day4
   bash ../day5/setup.sh
   ```
3. Start Claude Code **in this folder**: `claude`
4. In Claude Code, type `/skills`.

**You should see**
- `setup.sh` ends with `selftest PASS (diff rules, allowed paths, sign-off rules, Velocity rendering)`.
- `/skills` lists `parity-check`, `inumber-intake` and `kafka-topic-contract`.
- `work/` now has `salesorder-to-orderudm.vm` (your starter mapping) and `EVIDENCE.md`.

**If something goes wrong**
- *"Run this from amway-dve/day4"* → you're in the wrong folder: `cd` into `amway-dve/day4`.
- *`uv: command not found`* → install uv (Day 1 check), open a new terminal, rerun.
- *`/skills` doesn't list them* → you started Claude Code in another folder. Exit and run `claude` from `day4/`.
- *"work/ has files from the Day 4 lab"* → you did the Day 4 lab in this folder, and the gate
  would read those files too. Keep them by renaming the folder, then run setup again:
  `mv work work-day4 && bash ../day5/setup.sh`

---

## Round 1 — Who gets hit? (0:10–0:25)

**What this is about:** in brownfield, someone already depends on the flow. Before you
change anything, find out **who reads the salesorder topic and who reads OrderUDM**.
Anything the material doesn't confirm stays **OPEN** — don't guess.

**Do this**
1. Ask Claude:
   > Read lab/order-flow.md and the two diagrams in lab/. Write work/impact.md: every
   > consumer of the salesorder source topic and of the OrderUDM output, each with where
   > you found it. Anything the material doesn't confirm is OPEN.
2. Open `work/impact.md` and read it.

**You should see**
- **I3343** confirmed as the reader of the salesorder topic, and **I1001** as the reader of OrderUDM.
- **GWMS** (gets the order over REST), **BlueYonder** (fulfilment events) and the
  **data team** marked **OPEN**: the material doesn't say whether they read this topic.

**What it means:** because we can't rule them out, I3343K must read with its **own new
consumer group**, so it can never disturb an existing reader.

**Write in EVIDENCE.md:** `| 1 Impact | impact.md written | <list the OPEN items> | <your name> |`

**If something goes wrong:** if Claude lists a system as a confirmed reader, ask it
*"Which line in which file confirms that?"* — if there isn't one, it's OPEN.

---

## Round 2 — What must not change? (0:25–0:40)

**What this is about:** write down exactly what I1001 receives today — every field,
its type, an example — and **freeze** it. The source of truth is the **recording**
(what the old flow really produced), not what anyone remembers. The change request
allows **one** difference: `sourceSystem`.

**Do this**
1. Ask Claude:
   > Read lab/samples/recorded-orderudm/ (what I1001 actually receives today) and
   > lab/change-request-i3343k.md. Write work/frozen-contract.md: every OrderUDM field
   > I1001 receives, its type and an example value — the fields that must not change.
   > sourceSystem is the exception: it changes from HYBRIS to NGC, as the change request
   > requires. List it as the one proposed difference, not as frozen. End the file with
   > an empty line `Signed:` for a person to fill in; don't write a sign-off status yourself.
2. Check the topic names from the two diagrams:
   ```
   uv run --with pyyaml python .claude/skills/kafka-topic-contract/scripts/check_topic.py 'commerce_env_affiliate_salesorder_pub_v1' 'commerce_prod_aff_salesorder_pub_v1' 'commerce_pd_aff_orderudm_pub_v1'
   ```
3. **You** (or your pair) fill in the last line of `work/frozen-contract.md` with your name
   and the time: `Signed: <your name>, <time>`

**You should see**
- `frozen-contract.md` with the frozen fields (`orderId`, `affiliate`, `distributorId`,
  `orderDate`, `currency`, `promotionCode`, and the `lines` fields) and `sourceSystem`
  listed separately as the one proposed difference.
- `check_topic` prints **FAIL** for all three names, because the diagrams use concrete
  environment names (`env`, `prod`, `pd`) instead of `{env}` — that's what the tool prints.
  Separately, `prod`/`pd` and `affiliate`/`aff` disagree between the two diagrams. Both are
  **OPEN questions** for your Kafka owners, not errors to fix today.
- The command ends with FAIL on purpose: that's the finding, not a broken command.

**Write in EVIDENCE.md:** `| 2 Contract | frozen-contract.md signed; check_topic | <paste one FAIL line> | <your name> |`

---

## Round 3 — Write the new mapping (0:40–1:05)

**What this is about:** the mapping turns a NextGen order into an OrderUDM. It's a
Velocity file in your team's **map style**: build `$out` with `put()`, then emit `$out`.
You write it from the **new** field list and the change request.

**Do this**
1. Open `work/salesorder-to-orderudm.vm` — `orderId`, `affiliate` and `currency` are
   already done; the rest is marked `TODO`.
2. Ask Claude:
   > Use the parity-check skill. Finish work/salesorder-to-orderudm.vm from
   > lab/nextgen-salesorder-fields.md and lab/change-request-i3343k.md. Keep the
   > Velocity map style. Don't run parity yet.
3. Run the **render** command (top of this sheet) for S1, then for S4
   (`--input lab/samples/nextgen-input/S4.json`).

**You should see:** one OrderUDM per render, with `orderId`, `distributorId`,
`orderDate`, `promotionCode`, `sourceSystem: "NGC"` and a `lines` list.

**Look at it yourself before round 4.** For S4, ask: how many lines did the order
have, and how many did your mapping send? Which timestamp did it use?

**Write in EVIDENCE.md:** `| 3 Mapping | render S1 and S4 | <paste the sourceSystem line from S1> | <your name> |`

**If something goes wrong**
- *"mapping did not render"* → an `#if` or `#foreach` is missing its `#end`. Ask Claude to fix the syntax only.
- Claude may read the old rules (`lab/legacy-i3343-mapping.md`) by itself through the
  skill — that's fine. It just means your first parity run may already be clean.

---

## Round 4 — Prove it: parity (1:05–1:30)

**What this is about:** a mapping always *looks* right when you write it. Parity is the
proof: the same six orders, the recording vs your mapping, field by field.

**Do this**
1. Run the **parity** command (top of this sheet).
2. Read every `FAIL` line: `path: old=… new=…`.
3. If anything other than `sourceSystem` differs, ask Claude:
   > For each difference, find the rule in lab/legacy-i3343-mapping.md that explains the
   > old value, fix the mapping, and run parity again. Never change the samples or the recording.
4. Now run parity on the facilitator's **naive first draft** — a mapping that looks
   right and is wrong in four places:
   ```
   uv run --with airspeed --with pyyaml python .claude/skills/parity-check/scripts/parity_check.py run --vm ../day5/demo/naive-draft.vm --samples lab/samples
   ```

**You should see**
- **Your mapping:** most likely only `sourceSystem: old="HYBRIS" new="NGC"` on S1–S6,
  then `PARITY FAIL (6 data difference(s) in 6 of 6 samples)`. That's the one change
  the change request asked for — your mapping is otherwise right.
- **The naive draft:** `PARITY FAIL (30 data difference(s) in 6 of 6 samples)`. Find these four:

| Difference | What went wrong | Why I1001 would care |
|---|---|---|
| `distributorId: old="9300310" new="c1f0a2e4-…"` | used `customer.id` (NextGen's internal id) instead of `customer.aboId` | the order lands on the wrong distributor |
| `orderDate: old="…T00:03:02Z" new="…T23:55:10Z"` (S6) | used `createdAt` (cart created) instead of `submittedAt` (order placed) | on S6 the **date** changes — a different business day |
| `promotionCode: old="" new=null` | NextGen can send no promotion; the old flow always sent `""` | I1001 may reject or mishandle `null` |
| `lines.length: old=2 new=3` | NextGen sends **cancelled** lines; Hybris never did | a cancelled item gets staged in OEBS |

**Write in EVIDENCE.md:** `| 4 Parity | parity on my mapping + naive draft | <paste both PARITY lines> | <your name> |`

---

## Round 5 — The one allowed difference (1:30–1:45)

**What this is about:** parity can't decide whether `sourceSystem` changing is fine —
that's a judgement about I1001. **A person** decides, writes down why, and signs.
A placeholder is not a signature.

**Do this**
1. Copy the example file:
   ```
   cp .claude/skills/parity-check/reference/allowed-differences.example.yaml work/allowed-differences.yaml
   ```
2. First, run parity with it **unchanged** (still has `<…>` placeholders):
   ```
   uv run --with airspeed --with pyyaml python .claude/skills/parity-check/scripts/parity_check.py run --vm work/salesorder-to-orderudm.vm --samples lab/samples --allowed work/allowed-differences.yaml
   ```
3. Open `work/allowed-differences.yaml` and replace both placeholders:
   - `reason`: why this difference is allowed. Write only what you know — e.g.
     `"The change request requires NGC. Whether I1001 uses sourceSystem is OPEN — ask the I1001 owner."`
   - `approved_by`: a real person's name.
   - Keep both values in double quotes, as in the example: without them, a `: ` inside
     your text breaks the YAML.
4. Run the same command again.

**You should see**
- Step 2: `PARITY FAIL (allowed-differences file is not signed off)` — placeholders don't count.
- Step 4: `PASS S1 … PASS S6 (1 allowed difference(s))` and
  **`PARITY PASS (6/6 samples match; 6 allowed difference(s) accepted)`**.

**Write in EVIDENCE.md:** `| 5 Allowed difference | parity --allowed | PARITY PASS (6/6 …) | <your name> |`

**Don't:** put any other field in the allowed list to make parity pass. Only a
difference the change request asks for, signed by a named person.

---

## Round 6 — The gate (1:45–1:55)

**What this is about:** a read-only reviewer checks your evidence and reports
PASS / FAIL / OPEN for each item. It **never approves** — a person does.

**Do this** — ask Claude:
> Use the ailc-gate-reviewer subagent on work/ for stage 8: impact list, frozen
> contract and parity. The ADR and the new consumer group are not part of today's
> lab: report them OPEN.

**You should see** a verdict table with:
- **Parity: PASS** (it quotes your `PARITY PASS` line)
- **Allowed difference: OPEN** until the I1001 owner confirms whether I1001 uses
  `sourceSystem` — your own reason says so
- **ADR (switchover and rollback): OPEN** and **new consumer group: OPEN** — not done today
- **Impact list** and **Frozen contract: PASS or OPEN**
- a **Notes** list of other gaps the reviewer noticed (e.g. the topic names or key, owner
  names) — that's fine: they're questions for your real change

That's the reviewer doing its job: it tells you exactly what's still missing and who
has to close it.

**Write in EVIDENCE.md:** `| 6 Gate | ailc-gate-reviewer, stage 8 | <each item and its verdict, e.g. Parity PASS; ADR OPEN; …> | <your name> |`

---

## Close — after today (1:55–2:00)

What a real change still needs before I1001 switches (these are the OPEN items):
1. **Switchover ADR:** run old and new side by side, compare, then switch I1001 — and how to roll back.
2. **Where the new consumer group starts reading** (by default: only new messages).
3. **How your bundles turn the Velocity map into JSON** for `eda-proto-producer` (ask your Camel owners).
4. The real topic names (`prod`/`pd`, `affiliate`/`aff`).

**Show-back:** two pairs put `EVIDENCE.md` on screen:
1. Which difference would you have missed without parity (yours, or the naive draft's)?
2. Which OPEN item needs someone outside this room — and who?

---

## Stretch — the whole bundle
If you finish early: follow step 5 of `day4/assignments/LAB3.md` to build the full
I3343K bundle with your team's `camel-integration-author` skill and loop on
`validate_bundle.py`.
