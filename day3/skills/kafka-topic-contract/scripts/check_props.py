#!/usr/bin/env python3
"""Check producer serializer settings in a properties file.

Flags, per producer route-template instance (template-id eda-proto-producer) and per
any key ending in auto.register.schemas:
  - auto.register.schemas present and not "false"  -> ERROR
  - a producer with no subject.name.strategy key    -> ERROR
  - subject.name.strategy not AmwaySubjectNameStrategy -> WARN

Usage:
  python check_props.py <application.properties>
  python check_props.py selftest
"""
import re
import sys

AMWAY_STRATEGY = "com.amway.kafka.custom.serializers.subject.AmwaySubjectNameStrategy"
TPL = re.compile(r"^camel\.route-template\[(?P<id>[^\]]+)\]\.(?P<param>.+)$")


def parse(text):
    props = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(("#", "!")) or "=" not in line:
            continue
        k, v = line.split("=", 1)
        props[k.strip()] = v.strip()
    return props


def check(text):
    props = parse(text)
    errors, warnings = [], []
    for k, v in props.items():
        if k.endswith("auto.register.schemas") and v.lower() != "false":
            errors.append(f"{k}={v} — must be false (never auto-register schemas)")
    instances = {}
    for k, v in props.items():
        m = TPL.match(k)
        if m:
            instances.setdefault(m.group("id"), {})[m.group("param")] = v
    for iid, params in instances.items():
        if params.get("template-id") != "eda-proto-producer":
            continue
        strat = [v for p, v in params.items() if p.endswith("subject.name.strategy")]
        if not strat:
            errors.append(f"producer [{iid}] has no subject.name.strategy")
        elif strat[0] != AMWAY_STRATEGY:
            warnings.append(f"producer [{iid}] strategy {strat[0]} is not {AMWAY_STRATEGY}")
        ars = [v for p, v in params.items() if p.endswith("auto.register.schemas")]
        if not ars:
            warnings.append(f"producer [{iid}] does not set auto.register.schemas=false explicitly")
    return errors, warnings


def run(path):
    with open(path, encoding="utf-8") as fh:
        errors, warnings = check(fh.read())
    for w in warnings:
        print("WARN  " + w)
    for e in errors:
        print("ERROR " + e)
    print("FAIL" if errors else "PASS")
    return 1 if errors else 0


def selftest():
    good = f"""camel.route-template[pub1].template-id=eda-proto-producer
camel.route-template[pub1].kafka.value.subject.name.strategy={AMWAY_STRATEGY}
camel.route-template[pub1].kafka.auto.register.schemas=false
"""
    assert check(good) == ([], []), check(good)
    e, _ = check(good.replace("schemas=false", "schemas=true"))
    assert e and "must be false" in e[0], e
    e, _ = check("camel.route-template[p].template-id=eda-proto-producer\n")
    assert any("subject.name.strategy" in x for x in e), e
    e, w = check("camel.route-template[c].template-id=eda-proto-consumer\n")
    assert not e and not w, (e, w)
    print("selftest PASS (4 cases)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(selftest() if sys.argv[1] == "selftest" else run(sys.argv[1]))
