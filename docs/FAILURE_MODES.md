# Failure Modes

## FM-01 — Live endpoint down or unreachable

Symptom: probe records show `transport_error` and `http` null; `check_measurements.py` fails on the missing HTTP codes.
Effect: the pack's measured claims cannot be re-verified. The vendored logs
remain valid as a record of the probe window, but the headline claims
(M-02..M-05) would be stale.
Mitigation: re-run `bash reproduce.sh` later; the checks are deterministic and
will pass again once the endpoints are reachable. Each request is attempted
up to 5 times with exponential backoff before a transport error is recorded (the public
endpoint occasionally drops a connection mid-response — observed once each
for `feature` and `server_state` during verification).

## FM-02 — Endpoint behavior changes (a finding is fixed)

Symptom: `check_measurements.py` fails (e.g. P-04 is no longer HTTP 200, or
a REFUSAL record is no longer HTTP 403).
Effect: this is the CORRECT outcome — the pack documents the surface as of
2026-11-26T04:17:28Z. A FAIL here means the live surface changed, not that
the pack is broken. The vendored logs still prove what was observed.
Mitigation: re-probe, write a new pack revision, and update the claim index.

## FM-03 — A method flips between result and error-result between runs

Symptom: outcome tallies in a fresh scratch run differ from the vendored
summary (e.g. 20 results instead of 21).
Effect: none on the checks — `check_measurements.py` asserts structure (one
record per method, no SKIP called, HTTP codes for REFUSAL and P-04), not
outcome tallies. The selfcheck log stays byte-identical because it contains
only check lines, never tallies.
Mitigation: none needed; the vendored log is the record of the probe window.

## FM-04 — Pinned checkout absent on a fresh clone

Symptom: `check_excerpts.py --pin` or `check_inventory.py --pin` cannot find
the checkout.
Effect: structure checks still pass; only the verbatim cross-check is
unavailable.
Mitigation: clone postfiatd at the pinned commit
`0085a1ff885d6a446369cf73a4430f75af22be55` and pass `--pin <path>`.
`scripts/negative_search.sh` does this automatically into `.deps/`.

## FM-05 — Digest mismatch after upload

Symptom: `bash verify_digests.sh` reports FAILED for a file.
Effect: the uploaded copy differs from the pack. Do not submit; re-upload the
affected file and re-verify. Common cause: a file edited after SHA256SUMS was
generated, or a line-ending change during upload.
Mitigation: regenerate SHA256SUMS only after the pack is final, and verify
with a fresh clone before submitting.

## FM-07 — Transient proxy response (308 / dropped connection)

Symptom: a single call returns an unexpected status (e.g. HTTP 308 with an
empty body from Caddy, observed for `peer_reservations_list`, `unl_list`,
`stop`, `validation_create`, `feature`, `log_level`, `validator_votes`,
`channel_verify`, and `peers` across verification runs) or a transport error
(IncompleteRead, RemoteDisconnected — observed for `feature` and
`server_state`). The 308s cluster in time (roughly 1-3 methods per probe run)
and are sticky per method for minutes: eight attempts spanning ~90 s all
returned 308 for the same method, while a direct re-check minutes later
returned the expected code. The pattern is consistent with a pool of backend
nodes behind the proxy where one node redirects (the method is in the JSON
body, so per-method stickiness implies body-aware routing or a sticky hash),
not with a change in rippled's behavior.
Effect: none on the vendored logs. The probe scripts retry each request up
to 8 times with exponential backoff (1, 2, 4, 8, 16, 30, 30 s) and return
immediately only for the meaningful outcomes (RPC: HTTP 200 or 403; API:
200, 401, 403, 404, 405). `check_measurements.py` tolerates up to 3 REFUSAL
records returning 308 (a transient proxy artifact, not a security-relevant
outcome); any other non-403 status on a REFUSAL method (200, 401, 429) always
fails, and more than 3 308s fail. The tolerance is bounded so a wholesale
change (e.g. the endpoint starting to redirect everything) still fails.
Mitigation: none needed beyond the retry logic and the bounded tolerance; if
a 308 persists across 8 attempts spanning ~90 s for more than 3 methods, or
persists across re-runs for the same method, treat it as a real behavior
change and write a new pack revision.

## FM-06 — CI run on a partial-upload commit fails

Symptom: a CI run on an intermediate commit fails with missing files.
Effect: expected. Only the final commit's run matters; intermediate commits
lack files that SHA256SUMS lists.
Mitigation: ignore runs on intermediate commits; check the run on the final
commit only, via the GitHub API (not a browser page view, which can be stale).
