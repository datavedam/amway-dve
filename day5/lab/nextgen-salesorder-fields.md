# NextGen Commerce salesorder: the new source for I3343K

> **Training stand-in.** Made-up field names that match `samples/nextgen-input/`.
> Replace with the real NextGen Commerce contract (Schema Registry) when available.

Topic (from the target diagram): `commerce_prod_aff_salesorder_pub_v1` — see the
OPEN questions about `prod` vs `pd` and `affiliate` vs `aff`.

| Field | Type | Description |
|---|---|---|
| `order.id` | string | Order number, e.g. `SO-TH-100001` |
| `order.createdAt` | timestamp (UTC) | When the cart was created |
| `order.submittedAt` | timestamp (UTC) | When the order was placed |
| `order.currency` | string | ISO currency code |
| `affiliateCode` | string | Market code, upper case, e.g. `TH` |
| `customer.id` | string (UUID) | NextGen customer record id |
| `customer.aboId` | string | ABO number |
| `promotion` | object, optional | Present when the order used a promotion |
| `promotion.code` | string or null | Promotion (voucher) code |
| `items[]` | array | Order lines, in order |
| `items[].sku` | string | Product code |
| `items[].qty` | number | Quantity |
| `items[].price` | string | Unit price, two decimals |
| `items[].status` | string | `ACTIVE` or `CANCELLED` |
