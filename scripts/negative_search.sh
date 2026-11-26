#!/usr/bin/env bash
# Reproducible negative searches against the pinned postfiatd checkout.
# Writes outputs/negative_search.log (or $MEASUREMENT_OUTDIR).
# PIN: path to the checkout (default ~/workspace/postfiatd-pin-0085a1f).
# If the checkout is absent, clone postfiatd at the pinned commit into
# .deps/postfiatd-pin and grep that instead.
set -euo pipefail
cd "$(dirname "$0")/.."
PIN="${PIN:-$HOME/workspace/postfiatd-pin-0085a1f}"
PIN_COMMIT="0085a1ff885d6a446369cf73a4430f75af22be55"
OUTDIR="${MEASUREMENT_OUTDIR:-outputs}"
mkdir -p "$OUTDIR"
LOG="$OUTDIR/negative_search.log"

if [ ! -d "$PIN" ]; then
  echo "[step] checkout absent; fetching postfiatd at $PIN_COMMIT into .deps/postfiatd-pin"
  mkdir -p .deps
  git init -q .deps/postfiatd-pin
  git -C .deps/postfiatd-pin remote add origin https://github.com/postfiatorg/postfiatd.git
  if git -C .deps/postfiatd-pin fetch -q --depth 1 origin "$PIN_COMMIT" \
     && git -C .deps/postfiatd-pin checkout -q "$PIN_COMMIT"; then
    echo "[step] shallow fetch succeeded"
  else
    echo "[step] shallow fetch failed; falling back to a full clone"
    rm -rf .deps/postfiatd-pin
    git clone -q https://github.com/postfiatorg/postfiatd.git .deps/postfiatd-pin
    git -C .deps/postfiatd-pin checkout -q "$PIN_COMMIT"
  fi
  PIN=".deps/postfiatd-pin"
fi

{
echo "[step] negative_search start"
echo "[step] pin: $PIN_COMMIT"
echo "[step] N-1 per-method authentication beyond the table roles (auth/password in src/xrpld/rpc/):"
grep -rni "admin_password\|passwordUnrequired" "$PIN/src/xrpld/rpc/" | sed "s|$PIN/||" | head -20
echo "[step] N-1 count: $(grep -rni 'admin_password\|passwordUnrequired' "$PIN/src/xrpld/rpc/" | wc -l) hits (all plumbing — port/client setup and role checks, no per-method auth)"
echo "[step] N-2 public RPC rate limiting (rate.limit|throttl in src/xrpld/rpc/):"
grep -rni "rate.limit\|ratelimit\|throttl" "$PIN/src/xrpld/rpc/" | sed "s|$PIN/||" | head -5 || true
echo "[step] N-2 count in rpc/: $(grep -rni 'rate.limit\|ratelimit\|throttl' "$PIN/src/xrpld/rpc/" | wc -l)"
echo "[step] N-2b same terms across all of src/:"
grep -rni "rate.limit\|ratelimit" "$PIN/src/" --include="*.cpp" --include="*.h" | grep -v test | sed "s|$PIN/||" | head -10
echo "[step] N-3 api/tasks in the pinned tree:"
grep -rn "api/tasks" "$PIN/src" "$PIN/include" | sed "s|$PIN/||" | head -5 || true
echo "[step] N-3 count: $(grep -rn 'api/tasks' "$PIN/src" "$PIN/include" | wc -l)"
echo "[step] N-4 switch to disable sign/submit on a public node:"
grep -rni "disable.*sign\|sign.*disable\|allow_sign\|allow_submit" "$PIN/src/xrpld/rpc/" | sed "s|$PIN/||" | head -5 || true
echo "[step] N-4 count: $(grep -rni 'disable.*sign\|sign.*disable\|allow_sign\|allow_submit' "$PIN/src/xrpld/rpc/" | wc -l)"
echo "[step] N-5 per-method allowlist/blocklist in rpc/:"
grep -rni "allowlist\|allow_list\|blocklist\|block_list\|denylist" "$PIN/src/xrpld/rpc/" | sed "s|$PIN/||" | head -5 || true
echo "[step] N-5 count: $(grep -rni 'allowlist\|allow_list\|blocklist\|block_list\|denylist' "$PIN/src/xrpld/rpc/" | wc -l)"
echo "[step] N-6 who can emit HTTP 403 in-tree (403/forbidden in src/xrpld/rpc/ + server):"
grep -rn "403\|forbidden" "$PIN/src/xrpld/rpc/" 2>/dev/null | grep -vi "test" | sed "s|$PIN/||" | head -10
echo "[step] N-6 count: $(grep -rn '403\|forbidden' "$PIN/src/xrpld/rpc/" 2>/dev/null | grep -vi test | wc -l)"
echo "[step] N-7 admin password optional (passwordUnrequiredOrSentCorrect):"
grep -n "passwordUnrequiredOrSentCorrect" "$PIN/src/xrpld/rpc/detail/Role.cpp" | sed "s|$PIN/||"
echo "[step] negative_search done"
} | tee "$LOG"
