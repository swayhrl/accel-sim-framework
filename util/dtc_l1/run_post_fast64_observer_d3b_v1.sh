#!/usr/bin/env bash
# Future-only D3B controller.  It deliberately delegates immutable run
# receipts to the qualified v1 runner rather than modifying its bytes.
set -euo pipefail

self_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
exec "$self_dir/run_post_fast64_observer_qual_v1.sh" "$@"
