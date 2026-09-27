#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
output=${1:-$root/trace_pressure_scanner}
${CXX:-g++} -std=c++17 -O3 -DNDEBUG -Wall -Wextra -Werror \
  "$root/trace_pressure_scanner.cc" -o "$output"
echo "TRACE_PRESSURE_SCANNER_BUILD_PASS $output"
