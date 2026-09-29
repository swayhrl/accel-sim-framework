#!/usr/bin/env python3
"""Compact source/validation/claim receipts for R101R2 Native profile."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path('/data/c16/awma/r101r2_s128_native_profile_20260929')


def read(name: str) -> dict:
    return json.loads((ROOT / name).read_text())


def sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def write(name: str, value: str) -> None:
    (ROOT / name).write_text(value.rstrip() + '\n')


def main() -> None:
    receipt = read('INPUT_AND_PATH_RECEIPT.json')
    assert receipt['status'] == 'R101R2_NATIVE_PROFILE_PASS'
    analysis = read('NCU_ANALYSIS.json')
    metric_set = read('NCU_METRIC_SET.json')
    static = read('STATIC_SASS_RECEIPT.json')
    f = ROOT / 'raw/ncu/F128/F128.ncu-rep'
    k = ROOT / 'raw/ncu/K128/K128.ncu-rep'
    assert f.is_file() and k.is_file()
    profile = {
        'status': 'R101R2_NATIVE_PROFILE_PASS',
        'native_side_classification': 'NATIVE_PROFILE_MIXED',
        'formal_final_ncu_reports': {'F128_sha256': sha(f), 'K128_sha256': sha(k)},
        'attempt0_archive_reason': metric_set['bounded_metric_engineering_retry']['reason'],
        'bounded_retry_one_per_arm': True,
        'accepted_payload_sha256': receipt['accepted_input_payload_sha256'],
        'graph_kernel_counts': analysis['kernel_counts'],
        'unique_selected_static_cubins': static['selected_cubin_count'],
        'unsupported_metric_names': metric_set['unsupported_requested_metrics'],
        'accepted_timing_not_replaced': True,
        'GPU_lock_released_after_each_NCU_run': True,
        'no_model_gradient_holdout_or_simulator_run': True,
    }
    (ROOT / 'PROFILE_COMPLETENESS.json').write_text(json.dumps(profile, indent=2, sort_keys=True) + '\n')
    write('README.md', '''
# AWMA R101R2 S128 Native execution profile — node109

Final status: **`R101R2_NATIVE_PROFILE_PASS`**. Native-side diagnostic label: **`NATIVE_PROFILE_MIXED`**. This pack is for joint review with Lane E's independent O2 result; it does not itself set the final R101R2 research state.

The exact accepted R101 discovery S128 payload (581 BF16 128×128 tiles) and pinned HiMuon source were reused. F128 fused and K128 five-step three-kernel graph outputs matched accepted hashes exactly; a diagnostic NSYS canary matched accepted family/name/grid/block strata. Original R101 graph timing—F128 0.493408 ms versus K128 0.623488 ms, 20.863% improvement—remains the only primary timing authority.

Read `NATIVE_PROFILE_INTERPRETATION.md` first for counter ratios, family decomposition and limitations. `NCU_METRIC_PREREGISTRATION.md` plus `NCU_RAW_METRIC_BINDING.tsv` expose every supported/unsupported metric and its raw unit. `STATIC_SASS_SUMMARY.tsv` is per-binary static code, distinct from `NCU_FAMILY_SUMMARY.tsv` dynamic executed work. The final F128/K128 NCU reports are one bounded metric-engineering retry per arm; ATTEMPT0 is retained under node164 but never mixed into formal totals.

Node164 durable root: `/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r101r2_s128_native_profile_20260929/`. `RAW_DATA_INDEX.tsv` and `SHA256SUMS` close the raw/report identity. No new model, gradient, holdout, mechanism, or Accel-Sim run was performed.
''')
    write('TEST_AND_REGRESSION_SUMMARY.md', f'''
# Tests and regression summary

- Accepted S128 payload SHA and pinned HiMuon source commit/file hashes verified before GPU work; accepted output/timing receipts retained.
- SM89 NCU `all` and `launch` query frozen before profiling; 21 supported profiling metrics plus 2 launch metrics in the final set. Unsupported `smsp__inst_executed_pipe_fp32.sum` and `smsp__warps_issued.sum` recorded explicitly.
- Exact F128/K128 graph outputs and same-map author tolerance passed, including perturb/restore liveness. Diagnostic NSYS showed F128 fused 1 kernel and K128 5 each XXT/BA/BMM-add; exact author name/grid/block matched accepted R101.
- Five unique selected JIT cubins were hash-closed and statically disassembled; library fill cubin marked unavailable, never guessed.
- F128 final NCU report SHA256 `{sha(f)}`; K128 final report SHA256 `{sha(k)}`. Both target receipts verify accepted bitwise outputs; profile kernel strata were independently matched to canary.
- ATTEMPT0 omitted the supported LDGSTS warp-opcode counter. It was archived as metric-engineering obsolete; a single source-motivated same-config retry per arm added only that metric. No counter/timing result guided source or parameter selection.
- Additive counters summed only across launches; occupancy/eligible-warps/register/shared remained per-family medians and ranges. NCU replay duration is not primary timing.
''')
    write('SOURCE_AND_CLAIM_BOUNDARY.md', '''
# Source and claim boundary

Arithmetic remains `tang0389/himuon@af89eda9a0176effed99e1fe19cc1f8a1a2c9588`: 581 accepted S128 BF16 tiles, same 5-step `(3.4445,-4.7750,2.0315)` map. F128 is the author's `ns5_smem` fused path; K128 is the author's compiled XXT → ba_plus_cAA → fused_bmm_add path. Author-listed Triton configs were frozen before profiling solely to match the accepted structural grid/block strata, without timing/counter search. The exact selected cubin/module hashes are in `STATIC_SASS_SUMMARY.tsv`.

This is localization, not a new performance exploration or mechanism. Static SASS is not dynamic execution count. NCU's global LDG/LD counter excludes separate LDGSTS global→shared instructions, so both are reported separately and any sum is explicitly derived. NCU active cycles and replay durations are not the accepted graph elapsed time. Fused and three-kernel arms change compute, instruction issue, global-memory work, cache traffic and occupancy simultaneously; neither Native counters alone nor an unavailable metric may be used to claim a unique cause. Joint R101R2 classification requires Lane E's O2 result. No new L2 mechanism, FULL5 simulator replay, model download or holdout was run here.
''')
    write('EXCLUDED_ATTEMPTS.md', '''
# Excluded profile attempt

Initial F128 and K128 NCU reports passed output/path checks but omitted `smsp__inst_executed_op_ldgsts.sum`, despite this metric being supported. Static SASS exposed a substantial LDGSTS opcode class in K128, which the direct LDG/LD counter does not cover. The first reports, initial metric preregistration and initial aggregates were moved under node164 `raw/ATTEMPT0_OMITTED_LDGSTS_METRIC/` and `raw/ncu/<arm>/ATTEMPT0_OMITTED_LDGSTS_METRIC/` with an explicit OBSOLETE status. Exactly one bounded same-input/source/config metric-engineering retry per arm supplies the final counters. No performance or counter value was used to choose the repair.
''')
    print(json.dumps({'status': profile['status'], 'classification': profile['native_side_classification']}, sort_keys=True))


if __name__ == '__main__':
    main()
