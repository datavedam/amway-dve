# Day 3 — Hands-on: Small loops with exit checks

One giant prompt — "build me the unshipped-quantity integration" — fails in
ways you can't see. Instead, each AILC stage is a **small loop**: the agent
works, a script checks, the agent fixes, until the script says PASS — or it
stops and asks you. The script is the exit, not the agent's opinion.

## Step 1 — Intake loop (stage 1)
Ask Claude:
> Use the inumber-intake skill. Read lab/greenfield-unshippedqty.png and write
> the brief for this flow to work/unshippedqty-brief.md. Mark anything the
> diagram doesn't tell you as OPEN. Then run the brief check and fix until it
> passes.

**Observe:**
- Which fields came back OPEN? (Volume? Ordering? IXXXX details? Owner?)
- Did the check fail first and pass after a fix? That is one loop.
- Did it invent anything? Anything not in the diagram should be OPEN.

## Step 2 — You close the gate
Fill in the OPEN fields you know (owner, gate owner) yourself. Run:
```
python .claude/skills/inumber-intake/scripts/check_brief.py work/unshippedqty-brief.md
```
**Observe:** the agent drafted; you decided. The brief is now evidence.

## Step 3 — Contract loop (stage 2)
Ask Claude:
> Use the kafka-topic-contract skill. Check the topic name
> valuechain_{env}_000_unshippedqty_pub_v1 and the salesorder topic
> commerce_{env}_aff_salesorder_pub_v1 against the naming rule. Explain
> anything that doesn't match.

**Observe:** both pass — but the third segment is `000` in one and `aff` in the
other. The DRAFT rule in `reference/naming.yaml` is too loose to catch a wrong
value there. **Agree as a room what that segment means**, tighten the rule, and
re-run — that is the gate for stage 2.

## Step 4 — A producer contract that should fail
Ask Claude:
> Write a producer properties file for this topic that sets
> auto.register.schemas=true, then run check_props.py on it. Then fix it.

**Observe:** the check catches the one setting your standards forbid, and the
fix sets `AmwaySubjectNameStrategy`. The loop ran red → green.

## Step 5 — Name the loop pattern
Ask Claude:
> For each of the eight AILC stages, what is the exit check? Which ones are
> scripts, which are human sign-offs, and which don't exist yet?

**Discuss:** every stage without an exit check is a stage where "done" means
"the agent said so".
