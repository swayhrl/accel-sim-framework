#!/usr/bin/env bash
set -euo pipefail
src=/data/c16/awma/qwen25_s2_kernel_census_20260917T101100Z
dest=/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/qwen25_s2_kernel_census_20260917T101100Z
scp /tmp/verify_census_archive.py hrl174new:/tmp/verify_census_archive.py
ssh hrl174new "python3 /tmp/verify_census_archive.py '$dest'" > "$src/NODE164_VERIFY.stdout" 2> "$src/NODE164_VERIFY.stderr"
grep -q NODE164_CENSUS_HASH_VERIFY_PASS "$src/NODE164_VERIFY.stdout"
sha256sum "$src/NODE164_VERIFY.stdout" "$src/NODE164_VERIFY.stderr" > "$src/NODE164_VERIFY_SHA256SUMS"
