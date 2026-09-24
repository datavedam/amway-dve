# I3343 today: Hybris salesorder → OrderUDM

> **Training stand-in.** This is NOT Amway's real I3343 mapping. It describes the
> made-up sample messages in `samples/`. Replace it with the real mapping document
> when your team runs this on real messages.

This is how the **current** I3343 turns a Hybris salesorder into an OrderUDM.
I1001 reads the OrderUDM and writes it to OEBS staging. **I1001 must not see any
difference after the switch to I3343K.**

| OrderUDM field | From the Hybris message | Rule |
|---|---|---|
| `orderId` | `orderCode` | copy |
| `affiliate` | `affiliate` | copy (already upper case, e.g. `TH`) |
| `distributorId` | `aboNumber` | copy — the ABO number |
| `orderDate` | `placedDate` | copy — the time the order was **placed** (UTC) |
| `currency` | `currencyIso` | copy |
| `promotionCode` | `voucherCode` | copy; **`""` (empty string) when there is no voucher** — never null, never missing |
| `sourceSystem` | — | always `"HYBRIS"` |
| `lines[]` | `entries[]` | one line per entry, same order |
| `lines[].lineNo` | `entryNumber` | **`entryNumber + 1`** — numbering starts at 1 |
| `lines[].itemCode` | `entries[].productCode` | copy |
| `lines[].quantity` | `entries[].quantity` | copy — a number |
| `lines[].unitPrice` | `entries[].basePrice` | copy — a **string** with two decimals, e.g. `"450.00"` |

Hybris only ever sent **active** order lines. Cancelled lines never reached I3343.

Examples: every `samples/hybris-input/S<n>.json` produced `samples/recorded-orderudm/S<n>.json`.
