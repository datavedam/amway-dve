# Change request: I3343 → I3343K

> **Training stand-in.** A made-up change request for the lab. Replace with the real one.

**What changes**
- Source: Hybris `commerce_env_affiliate_salesorder_pub_v1` → NextGen Commerce
  `commerce_prod_aff_salesorder_pub_v1` (names as on the target diagram; see OPEN questions).
- Translator: I3343 → **I3343K**, a Camel bundle that publishes OrderUDM to
  `commerce_pd_aff_orderudm_pub_v1`.
- **`OrderUDM.sourceSystem` must say where the order came from: `"NGC"` for NextGen
  Commerce** (today it is always `"HYBRIS"`). Requested by: OPEN.

**What must not change**
- Every other OrderUDM field I1001 receives: same values, same types, same line order.
- I1001, OEBS staging, and every other consumer of the salesorder topic.

**Acceptance**
- Parity on recorded traffic: the only difference from the old output is
  `sourceSystem`, written down and signed by a principal after confirming I1001
  does not depend on it.
- Switchover and rollback agreed in an ADR.
