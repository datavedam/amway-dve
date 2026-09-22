# Data Governance Policy — Customer Data

Applies to any job or query that reads `data/customers.csv` or a table
with the same schema. This is the reference policy trainees check code
against in the Day 2 data assignments — treat it the way you'd treat a
real company data-handling policy handed to you before writing a pipeline.

## 1. Classification

Every column is classified into exactly one tier:

| Tier | Definition |
|---|---|
| **Public** | Safe to appear in any report, dashboard, or log, to any audience. |
| **Internal** | Safe within the company, not for external sharing; no direct harm to an individual if exposed internally. |
| **Restricted (PII)** | Can identify or directly contact a specific person, or cause harm if exposed. Requires a control (see Section 3) before it leaves the system it was collected in. |

## 2. Column classification — `data/customers.csv`

| Column | Tier | Reason |
|---|---|---|
| `customer_id` | Internal | Identifies a record, not a person, without a lookup. |
| `full_name` | Restricted (PII) | Directly identifies a person. |
| `email` | Restricted (PII) | Directly identifies and can contact a person. |
| `phone` | Restricted (PII) | Directly identifies and can contact a person. |
| `ssn` | Restricted (PII) | Government identifier; highest-sensitivity field in this dataset. |
| `date_of_birth` | Restricted (PII) | Combined with name/location, re-identifies a person. |
| `country` | Internal | Aggregate-safe; not identifying on its own at this granularity. |
| `signup_channel` | Public | Operational metadata, not personal. |
| `lifetime_spend` | Internal | Business metric; sensitive in aggregate reporting context but not personally identifying on its own. |

## 3. Required controls, by tier

| Tier | Allowed in a report/dashboard output? | Required control |
|---|---|---|
| Public | Yes, unrestricted. | None. |
| Internal | Yes, to employees only. | Must not be sent outside the company or to unauthenticated audiences. |
| Restricted (PII) | Only if the report's stated audience has a documented, specific need for that exact field. | Must be masked, tokenized, or dropped before the field leaves the pipeline — see Section 4. Never pass through unmodified into a downstream report "just in case it's needed." |

## 4. Approved controls for Restricted (PII) fields

Pick the weakest control that still satisfies the report's actual need —
don't default to the strongest one everywhere:

- **Drop** — remove the column entirely. Use when the report doesn't need
  it (e.g. a loyalty-tier count by region doesn't need `email` or `ssn`).
- **Mask** — show a partial/redacted value (e.g. `***-**-1123` for SSN,
  `a***@example.com` for email). Use when a human reviewer needs to
  recognize *which* record without needing the full value.
- **Tokenize/hash** — replace with a stable, non-reversible identifier.
  Use when downstream logic needs to match records across runs but never
  needs the real value (e.g. joining loyalty history across nightly runs).
- **Restrict access** — keep the real value, but only in a system with
  row/column-level access control and an audit log, never in a
  general-audience report or dashboard.

## 5. Audience matters

A field's required control depends on who reads the output, not just
what the field is:

- **Marketing dashboard** (this training's scenario) — no Restricted
  field should appear in plain form. `full_name` may be acceptable
  masked to first-name-only if the report is genuinely about individual
  outreach; `email`, `phone`, `ssn`, `date_of_birth` should be dropped
  entirely — marketing doesn't need them to report loyalty tiers by
  region.
- **Compliance/fraud investigation tooling** — may justify Restricted
  access to `ssn` under the "restrict access" control, with an audit log.
- **Any external or unauthenticated destination** — Restricted fields are
  never allowed, full stop, regardless of masking.

## 6. How to use this in the Day 2 assignments

When Claude reviews `scripts/sample_etl.py`'s `report = joined.select(...)`
line, or `sql/slow_orders_query.sql`'s `SELECT *`, check each selected
column against Section 2's tier and Section 3's required control for
that tier — not against a rule you invent on the spot. If a Restricted
column reaches the report unmasked, that's a policy violation, not a
judgment call.
