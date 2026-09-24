"""Generates the training sample messages. MADE-UP DATA — not real Amway orders.

For each order: the Hybris message the old I3343 consumed, the NextGen message the
new I3343K will consume (same order, new structure), and the OrderUDM the old
I3343 produced (the "recording" parity compares against).
Run from this folder: python generate.py
"""
import json, pathlib

ORDERS = [  # (id, affiliate, abo, uuid, created, submitted, currency, promo, items)
    ("SO-TH-100001", "TH", "7001234", "c1f0a2e4-0001", "2026-09-20T09:58:12Z", "2026-09-20T10:02:41Z", "THB", "FEST10",
     [("110001", 2, "450.00", "ACTIVE")]),
    ("SO-MY-200045", "MY", "8104455", "c1f0a2e4-0002", "2026-09-20T11:40:03Z", "2026-09-20T11:41:30Z", "MYR", "NEWABO",
     [("120450", 1, "89.90", "ACTIVE"), ("120451", 3, "12.50", "ACTIVE"), ("110001", 1, "450.00", "ACTIVE")]),
    ("SO-TH-100002", "TH", "7009911", "c1f0a2e4-0003", "2026-09-21T02:15:44Z", "2026-09-21T02:16:05Z", "THB", None,
     [("130777", 4, "75.00", "ACTIVE")]),
    ("SO-VN-300310", "VN", "9300310", "c1f0a2e4-0004", "2026-09-21T06:00:00Z", "2026-09-21T06:07:19Z", "VND", "MID-SEPT",
     [("140010", 1, "250000.00", "ACTIVE"), ("140011", 2, "99000.00", "CANCELLED"), ("140012", 1, "45000.00", "ACTIVE")]),
    ("SO-MY-200046", "MY", "8104455", "c1f0a2e4-0005", "2026-09-22T13:30:00Z", "2026-09-22T13:31:12Z", "MYR", "",
     [("120450", 2, "89.90", "ACTIVE")]),
    ("SO-TH-100003", "TH", "7001234", "c1f0a2e4-0006", "2026-09-22T23:55:10Z", "2026-09-23T00:03:02Z", "THB", "FEST10",
     [("150001", 1, "990.00", "CANCELLED"), ("150002", 1, "1234.50", "ACTIVE"), ("110001", 6, "450.00", "ACTIVE")]),
]
here = pathlib.Path(__file__).parent
for n, (oid, aff, abo, uid, created, submitted, cur, promo, items) in enumerate(ORDERS, 1):
    active = [i for i in items if i[3] == "ACTIVE"]
    hybris = {"orderCode": oid, "affiliate": aff, "aboNumber": abo, "placedDate": submitted, "currencyIso": cur,
              "entries": [{"entryNumber": k, "productCode": s, "quantity": q, "basePrice": p}
                          for k, (s, q, p, _) in enumerate(active)]}
    if promo:
        hybris["voucherCode"] = promo
    nextgen = {"order": {"id": oid, "createdAt": created, "submittedAt": submitted, "currency": cur},
               "affiliateCode": aff, "customer": {"id": uid, "aboId": abo},
               "items": [{"sku": s, "qty": q, "price": p, "status": st} for s, q, p, st in items]}
    if promo is not None:
        nextgen["promotion"] = {"code": promo or None}
    recorded = {"orderId": oid, "affiliate": aff, "distributorId": abo, "orderDate": submitted, "currency": cur,
                "promotionCode": promo or "", "sourceSystem": "HYBRIS",
                "lines": [{"lineNo": k + 1, "itemCode": s, "quantity": q, "unitPrice": p}
                          for k, (s, q, p, _) in enumerate(active)]}
    for folder, doc in (("hybris-input", hybris), ("nextgen-input", nextgen), ("recorded-orderudm", recorded)):
        (here / folder / f"S{n}.json").write_text(json.dumps(doc, indent=2) + "\n")
print(f"wrote {len(ORDERS)} samples x 3")
