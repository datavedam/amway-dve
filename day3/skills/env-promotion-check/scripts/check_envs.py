#!/usr/bin/env python3
"""Check that every {{key}} a bundle uses resolves in every env folder it ships.

Reads keys from sources/**/*.camel.yaml and .support/application.properties.
Looks them up in variables/<env>/{properties,configs}/*.y*ml and secrets/<env>/*.y*ml.
Also flags secret-looking keys (password|secret|token|key) stored under variables/
with a real value. A value that is only a {{reference}} (to a secret binding) is fine.

Keys the platform injects (the common block: kafka.*, pvf.*, cache.*, ...) are shown
as "platform" instead of MISSING — the same list validate_bundle.py uses.

Usage:
  python check_envs.py <bundle-root>
  python check_envs.py selftest
Exit 0 = every key resolves in every env and no secret is in variables/, 1 otherwise.
"""
import glob
import os
import re
import sys

import yaml

ENV_ORDER = ["dv", "ts1", "ts2", "ts3", "qa1", "qa2", "perf", "pd"]
PLACEHOLDER = re.compile(r"\{\{\s*\??([A-Za-z0-9_.\-]+)\s*\}\}")
SECRETISH = re.compile(r"(password|secret|token|(^|[._])key($|[._]))", re.I)
REFERENCE = re.compile(r"^\s*\{\{\s*\??[A-Za-z0-9_.\-]+\s*\}\}\s*$")
# Same as KNOWN_PREFIXES in camel-integration-author/scripts/validate_bundle.py:
# keys injected by the platform common block, not by the bundle.
PLATFORM_PREFIXES = (
    "kafka.", "pvf.", "api.jwks_", "cache.", "truststore.", "storage.",
    "iconfig.", "camel.", "bundle.", "mount.", "resource.",
)


def used_keys(root):
    keys = set()
    files = glob.glob(os.path.join(root, "sources", "**", "*.camel.yaml"), recursive=True)
    props = os.path.join(root, ".support", "application.properties")
    if os.path.exists(props):
        files.append(props)
    for f in files:
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                if line.lstrip().startswith("#"):
                    continue
                keys.update(PLACEHOLDER.findall(line))
    return sorted(keys)


def _load_keys(path):
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return data if isinstance(data, dict) else {}


def env_keys(root):
    envs = {}
    for env in ENV_ORDER:
        vdir = os.path.join(root, "variables", env)
        sdir = os.path.join(root, "secrets", env)
        if not (os.path.isdir(vdir) or os.path.isdir(sdir)):
            continue
        variables, secrets = {}, {}
        for sub in ("properties", "configs"):
            for f in glob.glob(os.path.join(vdir, sub, "*.y*ml")):
                for k, v in _load_keys(f).items():
                    variables[k] = (v, os.path.relpath(f, root))
        for f in glob.glob(os.path.join(sdir, "*.y*ml")):
            for k in _load_keys(f):
                secrets[k] = os.path.relpath(f, root)
        envs[env] = (variables, secrets)
    return envs


def check(root):
    keys = used_keys(root)
    envs = env_keys(root)
    missing, leaks = [], []
    matrix = []
    for k in keys:
        row = []
        for env, (variables, secrets) in envs.items():
            if k in secrets:
                row.append("secret")
            elif k in variables:
                row.append("var")
            elif k.startswith(PLATFORM_PREFIXES):
                row.append("platform")
            else:
                row.append("MISSING")
                missing.append((k, env))
        matrix.append((k, row))
    for env, (variables, _) in envs.items():
        for k, (v, f) in variables.items():
            is_ref = isinstance(v, str) and REFERENCE.match(v)
            if SECRETISH.search(k) and not is_ref and not (isinstance(v, dict) and "secret" in v):
                leaks.append((env, k, f))
    return keys, list(envs), matrix, missing, leaks


def run(root):
    keys, envs, matrix, missing, leaks = check(root)
    if not envs:
        print("ERROR no env folders found under variables/ or secrets/")
        return 1
    w = max([len(k) for k in keys] + [4])
    print("key".ljust(w) + "  " + "  ".join(e.ljust(7) for e in envs))
    for k, row in matrix:
        print(k.ljust(w) + "  " + "  ".join(c.ljust(7) for c in row))
    print()
    for k, env in missing:
        print(f"ERROR {{{{{k}}}}} has no value in {env}")
    for env, k, f in leaks:
        print(f"ERROR secret-looking key '{k}' stored in plain variables ({f}) — move to secrets/{env}/ with secret:/field:")
    ok = not missing and not leaks
    print("PASS" if ok else f"FAIL ({len(missing)} missing, {len(leaks)} secret-in-variables)")
    return 0 if ok else 1


def selftest():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.join(here, "..", "assets", "fixture-bundle")
    keys, envs, _, missing, leaks = check(root)
    assert envs == ["dv", "qa1"], envs
    assert "oebs.staging.insert" in keys and "kafka.secret" in keys, keys
    assert missing == [("oebs.staging.insert", "qa1")], missing
    assert [(e, k) for e, k, _ in leaks] == [("qa1", "kafka.secret")], leaks
    assert not SECRETISH.search("kafka.bootstrap") and SECRETISH.search("api.key")
    assert REFERENCE.match("{{i3343k.kafka.secret}}") and not REFERENCE.match("s3cr3t")
    assert "kafka.cluster_bootstrap".startswith(PLATFORM_PREFIXES)
    print("selftest PASS (fixture: 1 missing key in qa1, 1 secret in variables)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(selftest() if sys.argv[1] == "selftest" else run(sys.argv[1]))
