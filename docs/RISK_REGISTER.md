# Risk Register

Authoritative machine-readable form: `data/risk_register.json` (every finding
carries a `source_ref`). Totals: 15 findings — HIGH 1, MEDIUM 4, LOW 6,
INFO 4. Probe window 2026-11-26T04:17:28Z (RPC) / 04:18:58Z (agent API).
Pinned postfiatd revision: `0085a1ff885d6a446369cf73a4430f75af22be55`.

| ID | Severity | Title |
|---|---|---|
| A-01 | HIGH | GET /api/tasks returns internal task state without authentication |
| R-01 | MEDIUM | State-changing and secret-bearing methods are reachable on the public RPC endpoint |
| R-02 | MEDIUM | No public RPC rate limiting exists in the pinned tree |
| R-03 | MEDIUM | Admin authentication degrades to an IP allowlist when no admin password is configured |
| R-04 | MEDIUM | No per-method authentication beyond the table roles; all 51 USER methods are open to any caller |
| R-05 | LOW | ledger full/accounts is gated by a second, in-handler check the table does not show |
| R-06 | LOW | server_info leaks node fingerprinting data to anyone |
| R-07 | LOW | manifest returns any validator's manifest to any caller, enabling validator enumeration |
| R-08 | LOW | transaction_entry is listed in the table but not implemented |
| R-09 | LOW | Agent API serves the SPA shell for unknown paths, masking 404s |
| R-10 | LOW | subscribe/unsubscribe are websocket-only but listed as plain USER methods |
| R-11 | INFO | feature listing is role-aware (a working control) |
| R-12 | INFO | exclusion_info confirms PF_AccountExclusion is disabled (re-verifies the governance pack live) |
| R-13 | INFO | The public RPC sits behind Caddy, but the observed 403s are rippled's own |
| R-14 | INFO | No per-user data leaked in any probe |

Full detail (including the severity rationale and the exact `source_ref` for
each finding) is in `docs/REMEDIATION.md` and `data/risk_register.json`.
