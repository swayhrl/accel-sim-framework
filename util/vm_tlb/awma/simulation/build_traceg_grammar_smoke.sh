#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
output="${1:-${repo_root}/build/awma/traceg_grammar_smoke}"
mkdir -p "$(dirname "$output")"

g++ -std=c++17 -O2 -Wall -Wextra \
  -I "${repo_root}/gpu-simulator/trace-parser" \
  "${repo_root}/util/vm_tlb/awma/simulation/traceg_grammar_smoke.cc" \
  "${repo_root}/gpu-simulator/trace-parser/trace_parser.cc" \
  -o "$output"

sha256sum "$output"
