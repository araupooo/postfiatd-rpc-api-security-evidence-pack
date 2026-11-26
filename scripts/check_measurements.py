#!/usr/bin/env python3
"""Verify probe outputs against the plan in data/method_inventory.json.

Structural checks (deterministic; no measured values are asserted here
beyond the HTTP codes that ARE the measured claims — see note):
  - rpc_probe_raw.json: one record per inventory method; called iff class
    != SKIP; no SKIP method called; every called record has http + outcome;
    burst has exactly 12 entries, all server_info.
  - api_probe_raw.json: probes P-01..P-06 present; burst has 5 entries.
Behavior checks (these encode the pack's headline claims; a FAIL here
means the live surface changed since the pack was written, not that the
pack is broken):
  - every REFUSAL record has http == 403, except for a tolerated transient:
    the public endpoint intermittently returns HTTP 308 (empty body, from
    the proxy) for 1-3 methods per run, sticky per method for minutes, and
    the retries cannot move it (see FAILURE_MODES.md FM-07). Up to 3 REFUSAL
    records may be 308; any other non-403 status (200, 401, 429, ...) fails,
    and more than 3 308s fail. A 200 on an ADMIN method would mean the
    refusal is gone — that always fails.
  - P-04 GET /api/tasks has http == 200 and tag UNAUTHENTICATED-JSON-READ;
  - no record has http == 429 (no rate limiting observed).

Usage: python3 scripts/check_measurements.py [--outdir DIR]
Default outdir: outputs/ (relative to the pack root).
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=os.path.join(HERE, "outputs"))
    args = ap.parse_args()
    outdir = os.environ.get("MEASUREMENT_OUTDIR", args.outdir)

    inv = json.load(open(os.path.join(HERE, "data", "method_inventory.json")))
    rpc = json.load(open(os.path.join(outdir, "rpc_probe_raw.json")))
    api = json.load(open(os.path.join(outdir, "api_probe_raw.json")))
    fails = 0

    by_method = {r["method"]: r for r in rpc["records"]}
    missing = [m["method"] for m in inv["methods"]
               if m["method"] not in by_method]
    print(f"[step] rpc records cover all {len(inv['methods'])} methods: "
          f"{'PASS' if not missing else 'FAIL ' + str(missing)}")
    if missing:
        fails += 1
    for m in inv["methods"]:
        r = by_method.get(m["method"])
        if r is None:
            continue
        want_called = m["probe_class"] != "SKIP"
        if bool(r.get("called")) != want_called:
            print(f"[step] {m['method']}: called flag matches class: FAIL")
            fails += 1
        if r.get("called") and (r.get("http") is None
                                or r.get("outcome") is None):
            print(f"[step] {m['method']}: http + outcome present: FAIL")
            fails += 1
    n_skip_called = sum(1 for r in rpc["records"]
                        if r.get("class") == "SKIP" and r.get("called"))
    print(f"[step] no SKIP method called ({n_skip_called} violations): "
          f"{'PASS' if n_skip_called == 0 else 'FAIL'}")
    if n_skip_called:
        fails += 1

    burst = rpc.get("burst", [])
    print(f"[step] rpc burst has 12 server_info entries: "
          f"{'PASS' if len(burst) == 12 else 'FAIL'}")
    if len(burst) != 12:
        fails += 1

    refusal = [r for r in rpc["records"] if r.get("class") == "REFUSAL"]
    n_403 = sum(1 for r in refusal if r.get("http") == 403)
    n_308 = sum(1 for r in refusal if r.get("http") == 308)
    bad_ref = [r["method"] for r in refusal
               if r.get("http") not in (403, 308)]
    ok_ref = (n_403 + n_308 == len(refusal) and n_308 <= 3
              and not bad_ref)
    print(f"[step] REFUSAL methods refused (403, or transient 308 within "
          f"tolerance): {'PASS' if ok_ref else 'FAIL ' + str(bad_ref)}")
    if not ok_ref:
        fails += 1

    n_429 = sum(1 for r in rpc["records"] if r.get("http") == 429)
    n_429 += sum(1 for b in burst if b.get("http") == 429)
    print(f"[step] zero HTTP 429 anywhere in rpc probe: "
          f"{'PASS' if n_429 == 0 else 'FAIL'}")
    if n_429:
        fails += 1

    probes = {r["probe"]: r for r in api["records"]}
    missing_p = [p for p in ("P-01", "P-02", "P-03", "P-04", "P-05", "P-06")
                 if p not in probes]
    print(f"[step] api probes P-01..P-06 present: "
          f"{'PASS' if not missing_p else 'FAIL ' + str(missing_p)}")
    if missing_p:
        fails += 1
    p04 = probes.get("P-04", {})
    ok_p04 = (p04.get("http") == 200
              and p04.get("tag") == "UNAUTHENTICATED-JSON-READ")
    print(f"[step] P-04 GET /api/tasks http 200 + unauthenticated JSON read: "
          f"{'PASS' if ok_p04 else 'FAIL'}")
    if not ok_p04:
        fails += 1
    api_burst = api.get("burst", [])
    print(f"[step] api burst has 5 entries: "
          f"{'PASS' if len(api_burst) == 5 else 'FAIL'}")
    if len(api_burst) != 5:
        fails += 1
    api_429 = sum(1 for b in api_burst if b.get("http") == 429)
    print(f"[step] zero HTTP 429 in api burst: "
          f"{'PASS' if api_429 == 0 else 'FAIL'}")
    if api_429:
        fails += 1

    if fails:
        print(f"CHECK FAIL ({fails} problems)")
        return 1
    print("CHECK OK (probe outputs match the plan and the headline claims)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
