---
name: env-promotion-check
description: Before promoting a Camel bundle to the next environment, check that every {{key}} the bundle uses has a value in every env folder (dv, ts1-3, qa1-2, perf, pd), and that no password, secret, token, or key sits in plain variables instead of secrets/. Use when the user says "promote to qa", "ready for pd", "check the env configs", "missing property in qa1", or before merging staging_dv into staging_ts. Do NOT use for editing secrets, touching Delinea Secret Server, merging branches, or deploying — this skill only reads and reports.
---

# Env promotion check

Stage 6 of the integration lifecycle. A `{{key}}` with no value fails the bundle at startup —
in the environment you just promoted to. This check finds that before the merge.

## What it checks
- Every `{{key}}` / `{{?key}}` used in `sources/**/*.camel.yaml` and `.support/application.properties`.
- For each env folder present (`variables/<env>/properties/`, `variables/<env>/configs/`,
  `secrets/<env>/`), whether the key has a value.
- Keys that look secret (`password`, `secret`, `token`, `key`) stored under `variables/` as a plain
  value. Secrets belong in `secrets/<env>/` with a Delinea `secret:` / `field:` binding.

## Rules
- Read only. The agent never writes to `secrets/`, never edits a pd file, and never merges.
  Promotion order is `staging_dv → staging_ts → staging_qa → main`; a human merges.
- Report every gap. Propose the fix (which file, which key), but a DevOps / apps admin approves
  any change to configs or secrets.
- Keys bound inside a route-template instance (`camel.route-template[...]`) still need a value if
  they are written as `{{key}}`.

## Workflow
1. Run from the repo root:
   ```
   python scripts/check_envs.py <bundle-root>
   ```
2. Read the matrix: `var` = found in variables, `secret` = found in secrets, `MISSING` = no value.
3. For each ERROR, name the file to add the key to. Secret-looking keys go to `secrets/<env>/`.
4. Re-run until PASS. Paste the final output into the promotion review.

## Demo (class)
`python scripts/check_envs.py assets/fixture-bundle` — finds one key missing in `qa1` and one
secret stored in plain variables.

## Self-test
`python scripts/check_envs.py selftest`
