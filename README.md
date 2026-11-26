# Postfiatd RPC and API Security Evidence Pack

Public, commit-pinned evidence pack assessing postfiatd's public testnet
JSON-RPC surface and the agent API through pinned-source analysis and bounded,
non-destructive live probes.

Pinned postfiatd revision: `0085a1ff885d6a446369cf73a4430f75af22be55`
(2026-10-10). Probe window: 2026-11-26T04:17:28Z (RPC) / 04:18:58Z (agent API).

## Headline findings

- **15 findings: HIGH 1, MEDIUM 4, LOW 6, INFO 4.** Overall scorecard: **2.5 / 5**.
- **A-01 (HIGH):** GET /api/tasks returns internal task state (eligibility
  policy, gates, dailyRewardCap 8, per-wallet sync status) without any
  authentication — fresh re-probe, the finding persists from the prior window.
  No per-user data leaked (walletAddress null, empty lists).
- **74 RPC methods inventoried** (72 table entries + `ledger` + `version`):
  ADMIN 23, USER 51. 68 called, 6 skipped (state-changing / secret-bearing /
  heavy). Outcomes: 21 true results, 24 error-results, **23 x HTTP 403**,
  0 x 401, 0 x 429. 12-request burst: 12 x 200, 0 x 429.
- **The HTTP 403 for ADMIN methods is emitted by rippled itself**
  (ServerHandler.cpp:752-757 via the in-tree FORBID path), not by the proxy.
  All 68 RPC responses carry `Server: Caddy`.
- **No public RPC rate limiting exists in the pinned tree** (0 hits in
  `src/xrpld/rpc/`); only overlay manifest rate limiting and
  ValidatorExclusionManager change throttling exist tree-wide.
- **No in-tree switch to disable sign/submit** on a public node (0 hits);
  `sign`, `sign_for`, `submit`, `submit_multisigned`, `channel_authorize`,
  and `simulate` are reachable USER methods (not called, by design).
- **Live re-verification of prior packs:** 101 amendments (64 enabled / 37
  disabled, 0 changes); `exclusion_info` confirms PF_AccountExclusion is
  disabled; `manifest` returns details for the validator master key
  (domain app.w.ai, seq 1).

## Contents

- `docs/` — claim index (CLAIMS.md), remediation (REMEDIATION.md), risk
  register (RISK_REGISTER.md), scorecard (SCORECARD.md), roadmap (ROADMAP.md),
  sources (SOURCES.md), reproduction (REPRODUCTION.md), failure modes
  (FAILURE_MODES.md), method inventory (METHOD_INVENTORY.md), probe report
  (PROBE_REPORT.md).
- `data/` — method_inventory.json (74 methods), risk_register.json (15
  findings, every one with a `source_ref`), scorecard.json, roadmap.json,
  source_excerpts.json (19 verbatim excerpts from the pinned revision).
- `outputs/` — rpc_probe.log, rpc_probe_raw.json, api_probe.log,
  api_probe_raw.json, negative_search.log, environment.txt,
  reproduce_selfcheck.log.
- `scripts/` — probe_rpc.py, probe_api.py, negative_search.sh,
  build_excerpts.py, check_excerpts.py, check_inventory.py,
  check_measurements.py.
- `reproduce.sh`, `verify_digests.sh`, `SHA256SUMS`, `.github/workflows/ci.yml`.

## Reproduce

```bash
bash verify_digests.sh
bash reproduce.sh   # re-runs live probes into a scratch dir; expect REPRODUCE OK
```

See `docs/REPRODUCTION.md` for the full procedure and
`docs/FAILURE_MODES.md` for what a FAIL means (a changed live surface is a
correct FAIL, not a broken pack).

## Honest limits

- No rate-limit threshold is claimed ([UNSUPPORTED] U-01): zero 429s is
  absence of a signal, not a measured limit.
- Whether the public RPC port has an admin password configured is not
  observable from outside (U-02). No claim is made about other public nodes
  (U-03) or about authenticated /api/tasks behavior (U-05).
- The 122-request figure from the prior window is carried forward as
  [UNSUPPORTED] (U-07); it was not re-measured here.
- This pack proposes no wire format; the five open design decisions
  (D-01..D-05) in `data/roadmap.json` are labelled as such.
