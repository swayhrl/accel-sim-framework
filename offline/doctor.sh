#!/usr/bin/env bash
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"; bundle="${OFFLINE_BUNDLE_ROOT:-$(cd "$repo/.." && pwd)}"; out="${1:-$repo/docs-local/reports/ENVIRONMENT.md}"
cuda="${CUDA_INSTALL_PATH:-$bundle/toolchain/cuda-12.4}"; bison="$bundle/toolchain/bison-3.8.2/bin/bison"; flex="$bundle/toolchain/flex-2.6.4/bin/flex"
mkdir -p "$(dirname "$out")"
{ echo '# Offline-Sim environment'; echo; printf '| component | status | value |\n|---|---|---|\n'; for item in "CUDA nvcc|$cuda/bin/nvcc" "CUDA ptxas|$cuda/bin/ptxas" "CUDA cuobjdump|$cuda/bin/cuobjdump" "Bison|$bison" "Flex|$flex" "Python|$(command -v python3)" "CMake|$(command -v cmake)"; do n=${item%%|*}; p=${item#*|}; if test -x "$p"; then printf '| %s | PASS | `%s` |\n' "$n" "$p"; else printf '| %s | FAIL | `%s` |\n' "$n" "$p"; fi; done; } > "$out"
