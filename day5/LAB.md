# Day 5 — Brownfield lab: change the salesorder flow without I1001 noticing

**The aim:** move the salesorder flow from Hybris to NextGen, and have Claude **prove**
that I1001 receives exactly the same data as before — only `sourceSystem` changes, and
a person signs off on that one difference.

Everything happens **inside Claude**. You paste one prompt per round; Claude reads the
files, writes the outputs and runs the checks.

> Everything in `lab/` is **made-up training data** shaped like your flow
> (orders, old mapping rules, change request) — not real Amway data.

---

## Start (the only thing you type outside Claude)
Open a terminal (Git Bash on Windows) and start Claude in the lab folder:
```
cd training/repo/amway-dve/day5
claude
```
(If `day5` doesn't exist yet, start `claude` in `training/repo/amway-dve` — the setup prompt pulls it.)

## Round 0 — Set up
> Run git stash and git pull in this repo. Then, from the day5 folder, run
> bash setup.sh and tell me whether it ended with "selftest PASS".
> If it failed, tell me why and fix it.

**Then restart Claude once** so it loads the new skills and reviewer: type `/exit`,
make sure you're in `amway-dve/day5`, and run `claude` again.

**You should see:** `selftest PASS`. If Claude says it can't download packages
(network/proxy), pair up with a neighbour.

---

## Round 1 — Who depends on this flow?
> Read lab/order-flow.md and the two diagrams in lab/. Write work/impact.md: every
> consumer of the salesorder source topic and of the OrderUDM output, each with where
> you found it. Anything the material doesn't confirm is OPEN. Add a row to
> work/EVIDENCE.md for this round.

**You should see:** I3343 (reads the salesorder topic) and I1001 (reads OrderUDM)
confirmed; GWMS, BlueYonder and the data team **OPEN**.
**What it means:** we can't rule them out, so I3343K gets its **own new consumer group**
and never disturbs an existing reader.

## Round 2 — What must not change?
> Read lab/samples/recorded-orderudm/ (what I1001 actually receives today) and
> lab/change-request-i3343k.md. Write work/frozen-contract.md: every OrderUDM field
> I1001 receives, its type and an example value — the fields that must not change.
> sourceSystem is the exception: it changes from HYBRIS to NGC, as the change request
> requires. List it as the one proposed difference, not as frozen. End the file with an
> empty line "Signed:" for a person to fill in. Then run the kafka-topic-contract
> check on the three topic names in the change request and explain the result. Add a
> row to work/EVIDENCE.md.

Then **you** fill in the `Signed:` line with your name and the time.

**You should see:** the frozen fields, with `sourceSystem` listed separately. The topic
check **FAILs** all three names on purpose: the diagrams use real environment names
instead of `{env}`, and `prod`/`pd`, `affiliate`/`aff` disagree — open questions for
your Kafka owners.

## Round 3 — Build the new mapping
> Use the parity-check skill. Finish work/salesorder-to-orderudm.vm from
> lab/nextgen-salesorder-fields.md and lab/change-request-i3343k.md. Keep the Velocity
> map style. Then show me what it produces for lab/samples/nextgen-input/S1.json and
> S4.json. Add a row to work/EVIDENCE.md.

**You should see:** one OrderUDM per order, with `"sourceSystem": "NGC"` and a `lines` list.
It looks right — but looking right isn't proof.

## Round 4 — Prove it with parity
> Run parity on work/salesorder-to-orderudm.vm against lab/samples and show me every
> difference. Then run parity on demo/naive-draft.vm and explain each
> difference and what I1001 would get wrong. Add a row to work/EVIDENCE.md.

**You should see:**
- **Your mapping:** most likely only `sourceSystem: old="HYBRIS" new="NGC"` on all six
  orders — the change we asked for. Your mapping is otherwise right.
- **The naive draft:** **30 differences**. The four that matter:

| Difference | What went wrong | What I1001 would get wrong |
|---|---|---|
| `distributorId` | used NextGen's internal customer id, not the ABO number | order lands on the wrong distributor |
| `orderDate` (S6) | used cart-created time, not order-placed time | the **date** shifts by a day |
| `promotionCode` | `null` instead of `""` | I1001 may reject it |
| `lines` 2 → 3 | cancelled lines were sent | a cancelled item gets staged in OEBS |

## Round 5 — A person signs the one difference
> Create work/allowed-differences.yaml from
> .claude/skills/parity-check/reference/allowed-differences.example.yaml for
> sourceSystem, with reason "The change request requires NGC. Whether I1001 uses
> sourceSystem is OPEN — ask the I1001 owner." and approved_by "<your name>".
> Then rerun parity with --allowed work/allowed-differences.yaml. Add a row to
> work/EVIDENCE.md.

(Replace `<your name>` with your real name before you send it.)

**You should see:** **`PARITY PASS (6/6 samples match; 6 allowed difference(s) accepted)`**.
**What it means:** the agent can't decide a data change is OK — a named person does.
A placeholder or no name makes it fail.

## Round 6 — The gate
> Use the ailc-gate-reviewer subagent on work/ for stage 8: impact list, frozen
> contract and parity. The ADR and the new consumer group are not part of today's
> lab: report them OPEN.

**You should see:** Parity **PASS**; the allowed difference **OPEN** (until the I1001
owner confirms); ADR and new consumer group **OPEN**; impact list and frozen contract
PASS or OPEN; plus a Notes list of other gaps. The reviewer reports — it never approves.

---

## What you leave with
Your `work/` folder: the impact list, the signed frozen contract, the new mapping,
**parity PASS 6/6 with one signed difference**, and the gate's verdict with its OPEN
list — proof that I1001 won't notice, and exactly what's still open and who closes it.

**The method, for any change to a running flow** (this one, or a webMethods → Camel
move): find who depends on it → freeze what they receive → build the change → prove it
with parity → a person signs each intended difference.

## Show-back
1. Which difference would you have missed without parity (yours, or the naive draft's)?
2. Which OPEN item needs someone outside this room — and who?
