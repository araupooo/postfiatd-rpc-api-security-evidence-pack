# Reproduction

## Quick check (no network, no checkout)

```bash
bash verify_digests.sh
python3 scripts/check_excerpts.py
python3 scripts/check_inventory.py
python3 scripts/check_measurements.py
```

- `verify_digests.sh` checks every file in SHA256SUMS (all digests must be OK).
- `check_excerpts.py` checks the structure of `data/source_excerpts.json`.
  Add `--pin <checkout>` to verify every excerpt verbatim against a checkout
  of the pinned postfiatd revision `0085a1ff885d6a446369cf73a4430f75af22be55`.
- `check_inventory.py` verifies every inventory row against the vendored
  handler table excerpt (E-01). Add `--pin <checkout>` to re-verify the
  table excerpt itself first.
- `check_measurements.py` verifies the probe outputs against the plan in
  `data/method_inventory.json` (one record per method, no SKIP method called,
  bursts complete, all REFUSAL records HTTP 403, P-04 HTTP 200).

## Full reproduction (live probes)

```bash
bash reproduce.sh
```

This re-runs the RPC probe (68 calls + 12-request burst) and the API probe
(6 probes + 5-request burst) and the negative searches into a scratch
directory, then runs all checks against the scratch outputs. It needs network
access to https://rpc.testnet.postfiat.org and https://tasknode.postfiat.org.
The vendored probe logs in `outputs/` are NOT overwritten; fresh runs go to
the scratch dir. The selfcheck log (`outputs/reproduce_selfcheck.log`) is
deterministic — it contains only check lines, no timestamps, latencies, or
ledger numbers — so re-running reproduce.sh produces a byte-identical log.

Expected result: `REPRODUCE OK` at the end of the log, and the log's hash
must match the recorded selfcheck hash (see PACK-READY.md).

## Negative searches

```bash
bash scripts/negative_search.sh
```

Runs greps N-1..N-7 against the checkout at `~/workspace/postfiatd-pin-0085a1f`
(or `PIN=<path>`). If the checkout is absent, it clones postfiatd at the
pinned commit into `.deps/postfiatd-pin` and greps that instead. Output goes
to `outputs/negative_search.log` (or `$MEASUREMENT_OUTDIR`).

## CI

`.github/workflows/ci.yml` runs `bash reproduce.sh` on ubuntu-latest with
Python 3.12. It needs no secrets and no local checkout: the negative searches
clone the pinned revision into `.deps/` when the checkout is absent.

## Notes

- `scripts/__pycache__` regenerates on reproduce runs; it is not part of the
  pack and must not be uploaded.
- `outputs/reproduce_selfcheck.log` is excluded from SHA256SUMS by design: it
  embeds the digest output and can never match its own recorded hash. It is
  verified by byte-identical regeneration instead.
- `.deps/` (the shallow checkout used by the negative searches) and
  `scripts/__pycache__` are excluded from SHA256SUMS too. Regenerate the
  manifest with:
  `find . -type f -not -name SHA256SUMS -not -name reproduce_selfcheck.log -not -path './.deps/*' -not -path './scripts/__pycache__/*' | sort | while read -r f; do sha256sum "$f"; done > SHA256SUMS`
- Measurement logs re-run by reproduce.sh go to a scratch dir and never
  overwrite the vendored logs.
