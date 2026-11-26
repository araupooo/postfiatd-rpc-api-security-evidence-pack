#!/usr/bin/env bash
# Reproduce the pack from a fresh clone:
#  1. verify digests of the vendored files,
#  2. verify excerpts (structure) and the method inventory,
#  3. re-run the live RPC + API probes into a scratch dir,
#  4. re-run the negative searches into the scratch dir,
#  5. verify the scratch probe outputs against the plan.
# Live probes need network access to https://rpc.testnet.postfiat.org and
# https://tasknode.postfiat.org. The selfcheck log is deterministic: it
# contains only check lines (no timestamps, latencies, or ledger numbers).
set -euo pipefail
cd "$(dirname "$0")"
SCRATCH="${MEASUREMENT_OUTDIR:-$(mktemp -d)}"
LOG="outputs/reproduce_selfcheck.log"
{
echo "[step] reproduce start"
echo "[step] scratch dir: <scratch>"
echo "[step] digests"
bash verify_digests.sh
echo "[step] excerpts (structure)"
python3 scripts/check_excerpts.py
echo "[step] inventory"
python3 scripts/check_inventory.py
echo "[step] live RPC probe (scratch)"
MEASUREMENT_OUTDIR="$SCRATCH" python3 scripts/probe_rpc.py > "$SCRATCH/rpc_stdout.txt" 2>&1
echo "[step] live RPC probe: PASS"
echo "[step] live API probe (scratch)"
MEASUREMENT_OUTDIR="$SCRATCH" python3 scripts/probe_api.py > "$SCRATCH/api_stdout.txt" 2>&1
echo "[step] live API probe: PASS"
echo "[step] negative search (scratch)"
MEASUREMENT_OUTDIR="$SCRATCH" bash scripts/negative_search.sh > "$SCRATCH/neg_stdout.txt" 2>&1
echo "[step] negative search: PASS"
echo "[step] measurements (scratch)"
MEASUREMENT_OUTDIR="$SCRATCH" python3 scripts/check_measurements.py --outdir "$SCRATCH"
echo "REPRODUCE OK"
} | tee "$LOG"
