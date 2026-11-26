# Roadmap

Machine-readable form: `data/roadmap.json`.

## S0 — Immediate

- Require authentication on GET /api/tasks (A-01). Until then, do not treat its response as private.
- Proxy-block `sign`, `sign_for`, `submit`, `submit_multisigned`, `channel_authorize`, and `simulate` on the public RPC endpoint (R-01). These must never be reachable without a credential.

## S1 — Short-term

- Set `admin_user` / `admin_password` on every public port and restrict admin nets to operator IPs (R-03).
- Publish the 403/401 refusal matrix (which methods refuse, with which code) so operators and clients can rely on it (R-05).

## S2 — Near-term

- Add RPC rate limiting with published thresholds and burst policy (R-02). Until a threshold is published, the limit is [UNSUPPORTED].
- Add the same rate limiting to the agent API (A-01 follow-up).

## S3 — Medium-term

- Add a per-method allowlist/blocklist configuration for public nodes (R-04).
- Deprecate `transaction_entry` or implement it; note the websocket-only transport requirement for `subscribe`/`unsubscribe` in the table (R-08, R-10).

## S4 — Long-term

- Align the `ledger` table role with the in-handler gate (make `ledger` full/accounts ADMIN in the table, or document the second gate) (R-05).
- Reduce `server_info` / `manifest` fingerprinting on public endpoints (R-06, R-07).
- Re-probe on a schedule and publish the results.

## Open design decisions

| ID | Decision |
|---|---|
| D-01 | Auth scheme for /api/tasks (API key vs wallet signature vs session cookie). Unspecified in this pack. |
| D-02 | Rate-limit thresholds and burst policy for RPC and the agent API. Unspecified; operator decision. |
| D-03 | Whether sign/submit should be removed from the public handler table or blocked at the proxy. Unspecified. |
| D-04 | Admin password policy (rotation, storage, length). Unspecified. |
| D-05 | Whether `ledger` full/accounts should be ADMIN in the table. Unspecified. |
