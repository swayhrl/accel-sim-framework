#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$root/cache/wheelhouse" "$root/vendor" "$root/docs-local/reports" "$root/cache/assets"
test -f "$root/cache/sources/pybind11-v2.13.6.tar.gz"
test "$(sha256sum "$root/cache/sources/pybind11-v2.13.6.tar.gz" | awk '{print $1}')" = "e08cb87f4773da97fa7b5f035de8763abc656d87d5773e62f6da0587d1f0ec20"
rm -rf "$root/vendor/pybind11-2.13.6"; tar -xzf "$root/cache/sources/pybind11-v2.13.6.tar.gz" -C "$root/vendor"; mv "$root/vendor/pybind11-2.13.6" "$root/vendor/pybind11-2.13.6" 2>/dev/null || true
"$root/offline/doctor.sh"
