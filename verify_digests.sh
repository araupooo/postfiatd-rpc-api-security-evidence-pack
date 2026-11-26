#!/usr/bin/env bash
# Verify every file listed in SHA256SUMS against its recorded digest.
# Excludes (by design): SHA256SUMS itself and outputs/reproduce_selfcheck.log
# (the selfcheck log embeds the digest output and can never match its own
# recorded hash; it is verified by byte-identical regeneration instead).
set -euo pipefail
cd "$(dirname "$0")"
sha256sum -c SHA256SUMS
