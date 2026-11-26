#!/usr/bin/env python3
"""Bounded, non-destructive re-probe of the agent API surface.

Repeats the T11 probe set (6 requests) with fresh data, plus a small
bounded burst (5 x GET /api/tasks, 0.5 s apart) to observe rate-limit
behavior. Read-only; no credentials, no state changes.

Outputs (OUTDIR, default outputs/; override with MEASUREMENT_OUTDIR):
  api_probe.log       verbose per-step log (one line per request + summary)
  api_probe_raw.json  one record per request (path, method, http status,
                      headers of interest, response bytes, top-level keys,
                      null-valued fields, body)

Usage: python3 scripts/probe_api.py [--base URL] [--outdir DIR]
Default base: https://tasknode.postfiat.org
"""
import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.environ.get("API_BASE", "https://tasknode.postfiat.org")
TIMEOUT = 20
BURST_N = 5
BURST_DELAY = 0.5
BODY_CAP = 65536

PROBES = [
    ("P-01", "GET", "/"),
    ("P-02", "GET", "/robots.txt"),
    ("P-03", "GET", "/api"),
    ("P-04", "GET", "/api/tasks"),
    ("P-05", "POST", "/api/tasks"),
    ("P-06", "POST", "/api/tasks"),
]


def log_line(f, line):
    print(line, flush=True)
    f.write(line + "\n")
    f.flush()


def fetch(base, method, path, timeout=TIMEOUT):
    """One API call, up to 8 attempts.

    Returns immediately for HTTP 200, 401, 403, 404, and 405 — the meaningful
    outcomes for this API. Any other status (e.g. a transient 308/502 from
    the proxy) or a transport error is retried; after 5 attempts the last
    observed result is returned, so a stable behavior change is still
    recorded and still fails the checks.
    """
    url = base + path
    data = b"{}" if method == "POST" else None
    headers = {"Content-Type": "application/json"} if method == "POST" else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    last = None
    last_error = None
    for attempt in range(8):  # 8 attempts, bounded; transient flakes happen
        t0 = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read()
                res = {"http": r.status, "body": raw,
                       "headers": dict(r.headers),
                       "latency_ms": round((time.monotonic() - t0) * 1000, 1),
                       "transport_error": None}
        except urllib.error.HTTPError as e:
            raw = e.read()
            res = {"http": e.code, "body": raw,
                   "headers": dict(e.headers),
                   "latency_ms": round((time.monotonic() - t0) * 1000, 1),
                   "transport_error": None}
        except Exception as e:  # noqa: BLE001 - bounded retry, then record
            last_error = type(e).__name__ + ": " + str(e)
            time.sleep(min(2.0 ** attempt, 30.0))
            continue
        if res["http"] in (200, 401, 403, 404, 405):
            res["attempts"] = attempt + 1
            return res
        last = res
        time.sleep(min(2.0 ** attempt, 30.0))
    if last is not None:
        last["attempts"] = 8
        return last
    return {"http": None, "body": b"", "headers": {},
            "latency_ms": round((time.monotonic() - t0) * 1000, 1),
            "transport_error": last_error, "attempts": 8}


def summarize_body(body):
    try:
        j = json.loads(body)
    except Exception:
        return {"json": False, "top_keys": [], "null_fields": [],
                "truncated_body": body[:400].decode("utf-8", "replace")}
    if isinstance(j, dict):
        nulls = [k for k, v in j.items() if v is None]
        return {"json": True, "top_keys": sorted(j.keys()),
                "null_fields": sorted(nulls),
                "truncated_body": None, "full": j}
    return {"json": True, "top_keys": [], "null_fields": [],
            "truncated_body": None, "full": j}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=BASE)
    ap.add_argument("--outdir", default=os.path.join(HERE, "outputs"))
    args = ap.parse_args()
    outdir = os.environ.get("MEASUREMENT_OUTDIR", args.outdir)
    os.makedirs(outdir, exist_ok=True)

    log_path = os.path.join(outdir, "api_probe.log")
    raw_path = os.path.join(outdir, "api_probe_raw.json")
    records = []
    t_start = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    with open(log_path, "w") as lf:
        log_line(lf, f"[step] api_probe start: {t_start}")
        log_line(lf, f"[step] base: {args.base}")
        log_line(lf, "[step] plan: 6 probes (P-01..P-06, same set as the "
                     "prior window) + a 5-request GET /api/tasks burst "
                     "(0.5 s apart); read-only, no credentials")
        for pid, method, path in PROBES:
            res = fetch(args.base, method, path)
            summ = summarize_body(res["body"])
            body_text = res["body"].decode("utf-8", "replace")
            truncated = len(res["body"]) > BODY_CAP
            if truncated:
                body_text = body_text[:BODY_CAP]
            tag = "UNAUTHENTICATED-JSON-READ" if (
                path == "/api/tasks" and method == "GET"
                and res["http"] == 200 and summ.get("json")) else ""
            rec = {"probe": pid, "method": method, "path": path,
                   "http": res["http"], "bytes": len(res["body"]),
                   "latency_ms": res["latency_ms"],
                   "transport_error": res["transport_error"],
                   "attempts": res.get("attempts", 1),
                   "server_header": res["headers"].get("Server"),
                   "content_type": res["headers"].get("Content-Type"),
                   "top_keys": summ.get("top_keys"),
                   "null_fields": summ.get("null_fields"),
                   "tag": tag, "truncated": truncated,
                   "body": body_text}
            records.append(rec)
            log_line(lf, f"[step] {pid} {method} {path} -> {res['http']} "
                         f"bytes={len(res['body'])} "
                         f"latency_ms={res['latency_ms']} {tag}")
            time.sleep(0.2)

        log_line(lf, f"[step] burst start: {BURST_N} x GET /api/tasks, "
                     f"{BURST_DELAY} s apart")
        burst = []
        for i in range(BURST_N):
            res = fetch(args.base, "GET", "/api/tasks")
            burst.append({"i": i + 1, "http": res["http"],
                          "bytes": len(res["body"]),
                          "latency_ms": res["latency_ms"],
                          "transport_error": res["transport_error"]})
            log_line(lf, f"[step] burst {i + 1}/{BURST_N}: "
                         f"http={res['http']} bytes={len(res['body'])} "
                         f"latency_ms={res['latency_ms']}")
            if i < BURST_N - 1:
                time.sleep(BURST_DELAY)
        log_line(lf, "[step] burst done")

        p04 = next(r for r in records if r["probe"] == "P-04")
        n_2xx = sum(1 for r in records if r["http"] and 200 <= r["http"] < 300)
        n_405 = sum(1 for r in records if r["http"] == 405)
        log_line(lf, f"[step] summary: probes=6 http2xx={n_2xx} http405={n_405} "
                     f"p04_http={p04['http']} p04_bytes={p04['bytes']} "
                     f"p04_top_keys={','.join(p04['top_keys'] or [])} "
                     f"burst_429={sum(1 for b in burst if b['http'] == 429)}")
        log_line(lf, "[step] api_probe done")

    with open(raw_path, "w") as f:
        json.dump({"base": args.base, "started_utc": t_start,
                   "burst_n": BURST_N, "burst_delay_s": BURST_DELAY,
                   "records": records, "burst": burst}, f, indent=1)
        f.write("\n")
    print(f"api_probe: P-04 http={p04['http']}, "
          f"burst_429={sum(1 for b in burst if b['http'] == 429)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
