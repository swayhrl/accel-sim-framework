#!/usr/bin/env bash
# Test-only harmless child for receipt collision regression.  It ignores all
# simulator-shaped arguments and creates the preselected terminal receipt name.
set -euo pipefail

test -n "${FAST64_RECEIPT_COLLISION_DIR:-}"
: >"$FAST64_RECEIPT_COLLISION_DIR/RUN_TERMINAL.tsv"
