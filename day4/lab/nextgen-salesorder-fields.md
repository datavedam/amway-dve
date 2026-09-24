# NextGen Commerce salesorder: the new source for I3343K

> **Training stand-in.** Made-up field names that match `samples/nextgen-input/`.
> Replace with the real NextGen Commerce contract (Schema Registry) when available.

Topic (from the target diagram): `commerce_prod_aff_salesorder_pub_v1` — see the
OPEN questions about `prod` vs `pd` and `affiliate` vs `aff`.

| Field | Meaning | Watch out |
|---|---|---|
| `order.id` | Order number, e.g. `SO-TH-100001` | |
| `order.createdAt` | When the **cart** was created | not the order date |
| `order.submittedAt` | When the order was **placed** (UTC) | |
| `order.currency` | ISO currency | |
| `affiliateCode` | Market, upper case, e.g. `TH` | |
| `customer.id` | NextGen's **internal** customer id (a UUID) | not the ABO number |
| `customer.aboId` | The ABO number | |
| `promotion.code` | Voucher code | `promotion` can be missing, or `code` can be `null` |
| `items[]` | Order lines, in order | includes **cancelled** lines |
| `items[].sku` | Product code | |
| `items[].qty` | Quantity (number) | |
| `items[].price` | Unit price, string with two decimals | |
| `items[].status` | `ACTIVE` or `CANCELLED` | Hybris never sent cancelled lines |
