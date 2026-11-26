#!/usr/bin/env python3
"""Bounded, non-destructive live probe of the public testnet JSON-RPC surface.

Reads data/method_inventory.json (probe_class + probe_params per method),
issues exactly one request per PROBE/REFUSAL method, plus one small bounded
burst (12 x server_info, 0.25 s apart) to observe rate-limit behavior.
Never calls SKIP methods (state-changing / secret-bearing).

Outputs (OUTDIR, default outputs/; override with MEASUREMENT_OUTDIR):
  rpc_probe.log       verbose per-step log (one line per request + summary)
  rpc_probe_raw.json  one record per request (method, class, http status,
                      JSON status/error, response bytes, latency, body)

Usage: python3 scripts/probe_rpc.py [--rpc URL] [--outdir DIR]
Default RPC: https://rpc.testnet.postfiat.org
"""
import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RPC_URL = os.environ.get("RPC_URL", "https://rpc.testnet.postfiat.org")
BURST_N = 12
BURST_DELAY = 0.25
CALL_DELAY = 0.15
TIMEOUT = 20
BODY_CAP = 65536


def log_line(f, line):
    print(line, flush=True)
    f.write(line + "\n")
    f.flush()


def post_rpc(url, method, params, timeout=TIMEOUT):
    """One RPC call, up to 8 attempts.

    Returns immediately for HTTP 200 (result or error-result) and HTTP 403
    (the refusal) — the two meaningful outcomes. Any other status (e.g. a
    transient 308 redirect with an empty body from the proxy, observed for
    peer_reservations_list and unl_list during verification) or a transport
    error is retried; after 8 attempts the last observed result is
    returned, so a stable behavior change is still recorded and still
    fails the checks.
    """
    body = json.dumps({"method": method, "params": [params]}).encode()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"})
    last = None
    last_error = None
    for attempt in range(8):  # 8 attempts, bounded; transient flakes happen
        t0 = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read()
                res = {"http": r.status, "body": raw,
                       "latency_ms": round((time.monotonic() - t0) * 1000, 1),
                       "transport_error": None,
                       "server_header": r.headers.get("Server"),
                       "content_type": r.headers.get("Content-Type")}
        except urllib.error.HTTPError as e:
            raw = e.read()
            res = {"http": e.code, "body": raw,
                   "latency_ms": round((time.monotonic() - t0) * 1000, 1),
                   "transport_error": None,
                   "server_header": e.headers.get("Server"),
                   "content_type": e.headers.get("Content-Type")}
        except Exception as e:  # noqa: BLE001 - bounded retry, then record
            last_error = type(e).__name__ + ": " + str(e)
            time.sleep(min(2.0 ** attempt, 30.0))
            continue
        if res["http"] in (200, 403):
            res["attempts"] = attempt + 1
            return res
        last = res
        time.sleep(min(2.0 ** attempt, 30.0))
    if last is not None:
        last["attempts"] = 8
        return last
    return {"http": None, "body": b"",
            "latency_ms": round((time.monotonic() - t0) * 1000, 1),
            "transport_error": last_error,
            "server_header": None, "content_type": None, "attempts": 8}


def classify_body(body):
    try:
        j = json.loads(body)
    except Exception:
        return ("unparsable", None, None)
    if "result" in j:
        res = j["result"]
        if isinstance(res, dict) and "error" in res:
            # rippled returns errors inside result with status "error"
            return ("error-result", res.get("error_code", res.get("error")),
                    res)
        return ("result", None, res)
    if "error" in j:
        err = j["error"]
        if isinstance(err, dict):
            return ("error", err.get("error_code", err.get("error")), err)
        return ("error", str(err), err)
    return ("unknown-shape", None, j)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rpc", default=RPC_URL)
    ap.add_argument("--outdir", default=os.path.join(HERE, "outputs"))
    args = ap.parse_args()
    outdir = os.environ.get("MEASUREMENT_OUTDIR", args.outdir)
    os.makedirs(outdir, exist_ok=True)

    inv = json.load(open(os.path.join(HERE, "data", "method_inventory.json")))
    methods = inv["methods"]
    log_path = os.path.join(outdir, "rpc_probe.log")
    raw_path = os.path.join(outdir, "rpc_probe_raw.json")
    records = []
    t_start = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    with open(log_path, "w") as lf:
        log_line(lf, f"[step] rpc_probe start: {t_start}")
        log_line(lf, f"[step] endpoint: {args.rpc}")
        log_line(lf, f"[step] inventory: {len(methods)} methods "
                     f"(PROBE {inv['totals']['probe']}, "
                     f"REFUSAL {inv['totals']['refusal']}, "
                     f"SKIP {inv['totals']['skip']} — SKIP never called)")
        log_line(lf, "[step] plan: one request per PROBE/REFUSAL method, "
                     f"then a {BURST_N}-request server_info burst "
                     f"({BURST_DELAY} s apart); delay {CALL_DELAY} s between calls")

        for m in methods:
            if m["probe_class"] == "SKIP":
                log_line(lf, f"[step] {m['method']}: SKIP — {m['probe_reason']} (not called)")
                records.append({"method": m["method"], "class": "SKIP",
                                "called": False, "reason": m["probe_reason"]})
                continue
            res = post_rpc(args.rpc, m["method"], m["probe_params"])
            kind, code, parsed = classify_body(res["body"])
            body_text = res["body"].decode("utf-8", "replace")
            truncated = len(res["body"]) > BODY_CAP
            if truncated:
                body_text = body_text[:BODY_CAP]
            rec = {"method": m["method"], "class": m["probe_class"],
                   "called": True, "http": res["http"],
                   "outcome": kind, "error_code": code,
                   "response_bytes": len(res["body"]),
                   "latency_ms": res["latency_ms"],
                   "transport_error": res["transport_error"],
                   "attempts": res.get("attempts", 1),
                   "server_header": res.get("server_header"),
                   "content_type": res.get("content_type"),
                   "truncated": truncated, "body": body_text}
            records.append(rec)
            log_line(lf, f"[step] {m['method']} [{m['probe_class']}] "
                         f"http={res['http']} outcome={kind} "
                         f"error={code} bytes={len(res['body'])} "
                         f"latency_ms={res['latency_ms']}")
            time.sleep(CALL_DELAY)

        # Bounded rate-limit burst: 12 x server_info, 0.25 s apart.
        log_line(lf, f"[step] burst start: {BURST_N} x server_info, "
                     f"{BURST_DELAY} s apart")
        burst = []
        for i in range(BURST_N):
            res = post_rpc(args.rpc, "server_info", {})
            kind, code, _ = classify_body(res["body"])
            burst.append({"i": i + 1, "http": res["http"], "outcome": kind,
                          "error_code": code,
                          "latency_ms": res["latency_ms"],
                          "transport_error": res["transport_error"]})
            log_line(lf, f"[step] burst {i + 1}/{BURST_N}: "
                         f"http={res['http']} outcome={kind} "
                         f"latency_ms={res['latency_ms']}")
            if i < BURST_N - 1:
                time.sleep(BURST_DELAY)
        log_line(lf, "[step] burst done")

        n_called = sum(1 for r in records if r.get("called"))
        n_result = sum(1 for r in records if r.get("outcome") == "result")
        n_errres = sum(1 for r in records if r.get("outcome") == "error-result")
        n_error = sum(1 for r in records if r.get("outcome") == "error")
        n_403 = sum(1 for r in records if r.get("http") == 403)
        n_429 = sum(1 for r in records if r.get("http") == 429)
        n_401 = sum(1 for r in records if r.get("http") == 401)
        log_line(lf, f"[step] summary: called={n_called} result={n_result} "
                     f"error-result={n_errres} error={n_error} "
                     f"http403={n_403} http401={n_401} "
                     f"http429={n_429} burst_n={len(burst)} "
                     f"burst_429={sum(1 for b in burst if b['http'] == 429)}")
        log_line(lf, "[step] rpc_probe done")

    with open(raw_path, "w") as f:
        json.dump({"endpoint": args.rpc, "started_utc": t_start,
                   "burst_n": BURST_N, "burst_delay_s": BURST_DELAY,
                   "records": records, "burst": burst}, f, indent=1)
        f.write("\n")
    print(f"rpc_probe: {n_called} called, {n_result} result, "
          f"{n_errres} error-result, {n_error} error, 403={n_403}, 429={n_429}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
