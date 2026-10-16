# B16/U_WB producer release

Status: **PRODUCER_READY_FOR_INDEPENDENT_VALIDATION**.
Runtime-ready means executable and producer-gated, not independently accepted.

Frozen Framework runtime: `37dec04d223ae65167c5584e56887c74f6540d27`.
Frozen Core runtime: `126394be46b15f55b9756d43eb9ca9a9baae1c84`.
Binary SHA256: `0b504f5573ea0721709bc3439334f7f97a177286eaf73a36876403c7c9228698`.
Immutable local binary: `/workspace/results/ep_l2_ft20261016/lane1/binaries/release-126394be.out`.
Exact ordered config bytes, logical names, environment hashes and full feature
vectors for B16/U_WB16 and B8/U_WB8 are in BASELINE_CONTRACT_V1.json.

## Executed gates

- Six fresh old/new all-OFF full-application qualification runs: all normal
  hardware-drained terminal/parser gates PASS. For vectorAdd_4M, cfd_097k, sad,
  cycles/instructions and all seven scientific CSV families are byte-exact.
  The fresh old controls also reproduce retained historical CSVs exactly.
- Eight production l2_cache access/copy/issue/fill/response scenario groups PASS.
- Four real memory_sub_partition/L2interface/lower/set_done modes PASS:
  static C8/C16 staging peaks 8/16; unified pressure cases peak 126 and drain.
- Four illegal mode/budget combinations reject. Four existing Core directed
  executables PASS. Eight fail-closed terminal parser tests PASS.
- Final directed checks were repeated from immutable binary snapshots with
  commands and binary/log SHA256 captured, avoiding live rebuild ambiguity.

These are correctness/boundary results; reduced-geometry pressure fixtures are
not application speedups. Version-reference evidence does not claim arbitrary
32-byte/atomic numerical reconstruction from dataless SASS traces.

## Lane 5 handoff

Run the independent gates and normalize an independent release against these
exact bytes. B16/U_WB16 five-workload formal assignments remain Lane 5-owned;
Lane 1 has not claimed those formal keys. Do not wait for TVD/RO. The terminal
adapter emits true source-mapped token/queue/WB/role closure; independent data
qualification is consumed from Lane 5 evidence, never fabricated by the producer.
If U_WB shows a meaningful workload effect, execute the contracted equal-total
static redivision/copy attribution before making a capacity-sharing claim.

Review pack: docs/ep_l2/review_packs/FT20261016_LANE1_WBUF_RELEASE_r2/.
TVD/RO are separate subsequent integration stages; feature bits remain OFF in
this frozen release. Do not overwrite its binary or inputs while it serves runs.
