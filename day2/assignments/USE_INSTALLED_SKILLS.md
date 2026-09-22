# Day 2 — Hands-on: Using the Installed Skills

`install-necessary-skills.md` had you install four skills: **grilling**
(from the `mattpocock-skills` plugin), **prd**,
**subagent-driven-development**, and **documentation-and-adrs**. This
session chains them into a real pipeline —
**decision → PRD → ADR → specs → tickets → execution → re-check → triage** —
so you can see each skill's output become the next skill's input,
rather than trying each one in isolation. Copy-paste each prompt, run
it, read what comes back, and let that reading decide your next move.

Before starting, confirm all four are present:
```
/skills
```
If any is missing, go back to `install-necessary-skills.md` and finish
that step first — don't continue on a partial install.

## Step 0 — Validate each skill actually works
Being *listed* in `/skills` isn't the same as actually firing when
invoked. Smoke-test each one individually, on something trivial and
disposable, before trusting any of them with the real scenario in
Steps 1–8.

**Validate `grilling`:**
> Use the grilling skill to stress-test this claim: "Friday is always
> the best day to ship."

Observe: does it actually push back with real questions, or just agree
and restate your claim?

**Validate `prd`:**
> Use the prd skill to draft a one-page PRD for a trivial feature: a
> button labeled "Say hello" that prints "hello" when clicked.

Observe: does the output actually follow a PRD structure (goals,
requirements, etc.), not just a plain description of a button?

**Validate `subagent-driven-development`:**
> Use the subagent-driven-development skill to create two throwaway
> files, `tmp/a.txt` and `tmp/b.txt`, each containing a different
> one-line joke — dispatch a separate subagent for each file.

Observe: do you actually see two distinct subagent invocations, or did
Claude just write both files itself? Ask directly if unsure:
> Did you use two subagents for that, or one, or none?

**Validate `documentation-and-adrs`:**
> Use the documentation-and-adrs skill to write a throwaway ADR for
> the (fake) decision to use tabs over spaces in this repo.

Observe: does it produce an actual ADR-shaped file (context, decision,
consequences, alternatives), saved to disk, not just a chat opinion?

**Decide:** if any of the four didn't behave as its name implies —
didn't push back, didn't structure as a PRD, didn't spawn subagents,
didn't write a real ADR — stop here and go back to
`install-necessary-skills.md` to reinstall or troubleshoot that one
skill specifically. Don't carry a broken skill into Steps 1–8, where a
failure would be harder to tell apart from a bad prompt.

**Cleanup:** delete the throwaway output before continuing:
> Delete `tmp/a.txt`, `tmp/b.txt`, and the tabs-vs-spaces ADR file you
> just created for this validation — none of them are part of the
> real exercise.

## Step 1 — `grilling`: stress-test a decision
Recall the Data Governance policy in `GOVERNANCE.md`. Give Claude a
plan that cuts a corner on it, and ask it to grill you on it:
> I'm building the marketing dashboard from `data/customers.csv` and
> I'm planning to include the `email` column unmasked, since it'll
> save a step if marketing ever needs to follow up directly. Use the
> grilling skill to stress-test this plan with me.

**Observe:** does it find your exact figure out why this breaks the
governance policy? Note which question actually changed your mind, if
one did. **Decide:** state your revised plan in one sentence based on
what came up.

**Implementation prompt** — a decision only exists if it survives the
session. Persist it before moving on:
> Write our revised plan from this discussion to
> `decisions/dashboard-email-decision.md` — one paragraph, plain
> language, no need for it to be a formal doc yet.

Confirm the file actually exists (`ls decisions/`) before Step 2.

## Step 2 — `prd`: turn the revised decision into a PRD
Take the revised plan from Step 1 and turn it into a real requirements
doc:
> Use the prd skill to draft a PRD for a "marketing loyalty dashboard"
> feature, built from `data/customers.csv`, that respects the
> governance policy's masking rules from Step 1.

**Observe:** find the sections the skill produced (goals, non-goals,
requirements, etc. — the exact structure depends on the skill). Check
one thing specifically: does the PRD explicitly call out which columns
are excluded/masked and why, or did that detail get lost in translation
from Step 1? If it's missing, tell Claude what's missing and have it
revise the PRD before moving on.

**Implementation prompt** — check whether the skill actually wrote a
file or just printed the PRD in chat:
> Did you save that PRD to a file, or was that only printed in chat?
> If it wasn't saved, write it now to `docs/prd/marketing-loyalty-dashboard.md`.

Confirm with `ls docs/prd/` that the file is really there before
Step 3 — Step 3 will build from this file, not from chat history.

## Step 3 — `documentation-and-adrs`: record the decision
The choice from Step 1 (drop `email` instead of masking or including
it) is exactly the kind of decision an ADR exists to capture — and it
belongs on record *before* anything gets built from it, not after.
Ask:
> Use the documentation-and-adrs skill to write an ADR documenting the
> decision to drop PII columns entirely from the marketing dashboard,
> including the alternative (masking) we rejected in Step 1 and why.

**Observe:** find the file it wrote and check it actually references
the *specific* alternative you discussed in Step 1 (masking) rather
than a generic "we chose to be careful with data" — a good ADR names
the road not taken, not just the road taken.

**Implementation prompt** — ADRs are only useful if they live in a
predictable, versioned location. Confirm and, if needed, fix that:
> Where exactly did you save that ADR? If it's not under a folder like
> `docs/adr/`, move it there now, following whatever numbering
> convention the documentation-and-adrs skill expects.

Confirm with `ls docs/adr/` that a real, numbered ADR file exists
before Step 4.

## Step 4 — `subagent-driven-development`: turn the PRD + ADR into specs
Before any code gets written, break the PRD and ADR into separate,
scoped spec files — one per piece of work, not one giant spec covering
everything:
> Use the subagent-driven-development skill to read
> `docs/prd/marketing-loyalty-dashboard.md` and the ADR in `docs/adr/`,
> then write two separate spec files under `specs/`: one,
> `specs/data-pipeline.md`, scoped to reading `data/customers.csv` and
> producing masked/dropped output per the ADR; the other,
> `specs/ui-dashboard.md`, scoped to the UI that renders that output.
> Don't implement anything yet — specs only.

**Observe:** open both files. Check two things specifically: (1) are
they actually two separate files scoped to one concern each, rather
than one combined spec Claude split cosmetically, and (2) does
`specs/data-pipeline.md` explicitly restate the *drop, not mask*
decision from the ADR, or did that constraint get diluted on the way
from ADR → spec? If either check fails, tell Claude exactly what's
wrong and have it rewrite before moving on.

**Implementation prompt** — confirm these are real files, not chat
output:
> List the exact contents of the `specs/` folder right now.

Confirm with `ls specs/` yourself as well before Step 5.

## Step 5 — Turn the specs into tickets
Specs describe a whole component; tickets are the individually
completable chunks of work inside it. Break each spec down further,
before any execution happens:
> Use the subagent-driven-development skill to break
> `specs/data-pipeline.md` and `specs/ui-dashboard.md` down into
> individual tickets under `tickets/` — one ticket per concrete,
> independently-completable task (e.g. "read and mask
> `customers.csv`", "write `dashboard/data.json`", "render the bar
> chart", "add the country-filter dropdown"). Each ticket must say
> which spec it came from.

**Observe:** open `tickets/`. Check two things: (1) is each ticket
actually smaller than its parent spec — a real task, not just the
spec file copy-pasted with a new name — and (2) does each ticket that
touches the data still carry forward the *drop, not mask* constraint,
or did that get lost going spec → ticket? If either check fails, send
Claude back to redo the breakdown before Step 6.

**Implementation prompt** — confirm these are real files, not chat
output:
> List the exact contents of the `tickets/` folder right now.

Confirm with `ls tickets/` yourself as well before Step 6.

## Step 6 — Execute the tickets using subagents
Now actually build — one subagent per ticket, not one subagent doing
everything:
> Use the subagent-driven-development skill to execute every ticket in
> `tickets/`. Dispatch a separate subagent per ticket, so the
> data-pipeline tickets produce `scripts/loyalty_report.py` (reads
> `data/customers.csv`, writes `dashboard/data.json`) and the
> UI tickets produce `dashboard/index.html` (loads `data.json`,
> renders a bar chart with a country-filter dropdown).

**Observe:** watch how the work actually gets split up — do you see
one distinguishable subagent invocation per ticket, or did everything
come from a single pass despite the skill being active? Ask directly
if you're not sure:
> Did you dispatch a separate subagent per ticket? How many ran, and
> which ticket did each one implement?

**Implementation prompt** — a dashboard isn't real until you've
actually looked at it rendered, not just read the HTML source:
> Run the script to generate `dashboard/data.json`, then open
> `dashboard/index.html` for me (or tell me the exact command to open
> it, e.g. `open dashboard/index.html` on Mac).

Open it in your browser. **Observe:** does the bar chart actually
render with real counts from `data/customers.csv`, does the country
dropdown actually filter it, and — check this specifically — are any
Restricted (PII) columns visible anywhere in the page source
(View Source / Inspect)? If yes, that's a governance violation baked
into the UI itself, not just the data pipeline — send Claude back to
fix it (updating the ticket/spec too, if that was the source of the
gap) and reload the page to confirm.

## Step 7 — Chain reaction: feed the ADR back into `grilling`
Close the loop on the decision itself, now that it's actually been
built. Ask:
> Take the ADR from Step 3 and use the grilling skill again to
> stress-test whether it actually holds up — is dropping `email`
> entirely the right call, or should it have been masked instead so
> marketing can still request follow-up through a controlled channel?

**Observe:** did grilling surface a real gap you hadn't considered
(e.g. "what if a legitimate audience *does* need masked email"), or
did it just restate Step 1? **Decide** whether the ADR needs a
revision based on this second pass, and if so, ask Claude to update it.

**Implementation prompt** — if this pass changed your mind at all,
that change must land in the actual ADR file on disk, not just in
chat:
> Update the ADR file itself in `docs/adr/` to reflect whatever this
> grilling pass changed — don't leave the on-disk version out of date
> with what we just decided.

Confirm by opening the ADR file directly and checking its content
matches this conversation, not the original Step 3 version.

## Step 8 — Triage: three bug reports land at once
No new skill to install here — triage is a judgment exercise using the
skills you already have. Copy-paste three fictitious bug reports
against the dashboard from Step 6, all at once:
> Three bug reports just came in for the loyalty dashboard:
> 1. The country dropdown lists countries with zero customers,
>    cluttering the list.
> 2. `dashboard/data.json` may have been regenerated from a cached
>    copy of `customers.csv` from before we dropped the `email`
>    column — someone thinks it might still contain email addresses.
> 3. The bar chart's Y-axis is missing a label.
>
> Triage these three: assign each a severity (critical/high/low) and
> tell me which one you'd fix right now versus later, and why.

**Observe:** does it correctly flag #2 as critical regardless of it
being unconfirmed — a *possible* PII leak gets triaged as urgent
precisely because it hasn't been verified yet, not despite that — while
#3 gets correctly ranked as low? If it ranks #1 or #3 above #2, that's
a real miscalibration worth noticing, not just accepting.

**Decide:** if you disagree with any severity it assigned, push back
before moving on — this triage call is what the next two prompts act
on.

**Verify prompt** — don't let "may have" stay a guess:
> Actually check: run a search over `dashboard/data.json` for
> anything that looks like an email address, and tell me definitively
> whether report #2 is real or a false alarm.

**Implementation prompt** — fix whatever triage confirmed as
critical, using the skill built for exactly this:
> Use the subagent-driven-development skill to fix the critical issue
> from this triage (report #2 if confirmed, otherwise the
> highest-severity confirmed one), then re-generate
> `dashboard/data.json` and confirm the fix by re-running the same
> search you just ran.

Then close the loop the same way Step 3 did:
> Use the documentation-and-adrs skill to write a short incident note
> for this triage — what was reported, what was confirmed true, what
> was fixed, and what turned out to be a false alarm.

Confirm with `ls docs/adr/` (or wherever it saved the incident note)
that it's a real file, not just a chat summary.

## Reflection table
Fill this in after running all eight steps:

| Skill | What you asked it to do | What it actually produced | Did it need a redo? |
|---|---|---|---|
| grilling | | | |
| prd | | | |
| documentation-and-adrs | | | |
| subagent-driven-development (specs) | | | |
| subagent-driven-development (tickets) | | | |
| subagent-driven-development (execute) | | | |
| grilling (2nd pass) | | | |
| triage (Step 8) | | | |
