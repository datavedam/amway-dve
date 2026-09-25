# The salesorder in the estate (from the Day 1 order flow)

Simplified from "Integration Architecture NextGen+Thailand", shared on the prep call.
Correct anything that is wrong — this is your architecture.

- An ABO places an order in NG Commerce. It is published to Kafka topic `salesorder_pub_v1`
  (current Hybris topic on the brownfield diagram: `commerce_env_affiliate_salesorder_pub_v1`),
  with a schema contract in Schema Registry.
- **GWMS** receives the order over REST through **I2441, I3409, I3410**.
- The finance path: **I3343** translates the order to the canonical model (OrderUDM) via
  `translateAndPublishOrderUDM`; **I1001** writes the OrderUDM to **OEBS** staging tables over JDBC.
- The **IMS/OMS facade** (`bundle-*` microservices) sends fulfilment events to **BlueYonder**
  through **I3392**.
- The **data team** reads the events into **BigQuery** (Spark/Beam).

Brownfield change (target diagram): NextGen Commerce topic `commerce_prod_aff_salesorder_pub_v1`
→ **I3343K** → topic `commerce_pd_aff_orderudm_pub_v1` → OrderUDM → **I1001** → **OEBS**.

OPEN: what does the K in I3343K mean? Is I3343 on webMethods today? Does anything
besides I1001 read OrderUDM? Which environment names are right (`prod` or `pd`)?
