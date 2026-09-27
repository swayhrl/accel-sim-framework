#!/usr/bin/env python3
"""Render compact, evidence-backed producer reports after full trace closure."""
from __future__ import annotations

import difflib
import json
from pathlib import Path

ROOT = Path('/data/c16/awma/r101_transient_l2_sim_capture_20260927')
WORKTREE = Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r101-transient-l2-sim-capture-109-v1')
PARENT = Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-producer-authority-v1')


def read(name: str) -> dict:
    return json.loads((ROOT / name).read_text())


def write(name: str, text: str) -> None:
    (ROOT / name).write_text(text.rstrip() + '\n')


def main() -> None:
    manifest = read('SIM_CAPTURE_MANIFEST.json')
    assert manifest['status'] == 'R101_TRANSIENT_SIM_CAPTURE_PASS'
    producer = read('TRACER_SOURCE_AND_BUILD_RECEIPT.json')
    input_ = read('ACCEPTED_INPUT_BINDING.json')
    scope = read('CAPTURE_SCOPE_PREREGISTRATION.json')
    volume = read('VOLUME_ADMISSION.json')
    semantics = read('TRACE_SEMANTIC_SUMMARY.json')
    guard = json.loads((ROOT / 'raw/formal_full5/RESOURCE_GUARD.json').read_text())
    canary1 = json.loads((ROOT / 'raw/canary1/TERMINAL_RECEIPT.json').read_text())
    canary3 = json.loads((ROOT / 'raw/canary_multi/TERMINAL_RECEIPT.json').read_text())
    assert canary1['status'] == canary3['status'] == 'COMPLETE'
    parent = PARENT / 'util/tracer_nvbit/route_b_1771/route_b_tracer.cu'
    current = WORKTREE / 'util/tracer_nvbit/route_b_1771/route_b_tracer.cu'
    delta = ''.join(difflib.unified_diff(parent.read_text().splitlines(keepends=True),
                                         current.read_text().splitlines(keepends=True),
                                         fromfile='accepted_5143/route_b_tracer.cu',
                                         tofile='R101_multi/route_b_tracer.cu'))
    assert 'ROUTE_B_MULTI_SELECTED_COUNT' in delta
    (ROOT / 'build/TRACER_MULTI_EXTENSION.diff').write_text(delta)
    write('README.md', f'''
# AWMA R101 Transient-L2 simulator-native capture — node109 producer

Final state: **`R101_TRANSIENT_SIM_CAPTURE_PASS`**. Stable input identity: `{input_['sim_input_id']}`; capture ID: `{manifest['capture_id']}`. This is the exact accepted R101 discovery L512 BF16 payload, captured anew as simulator-native trace; it is not an algorithm variant or simulator result.

Full-five-step scope was retained: {manifest['selected_kernel_count']} ordered kernel members = 3 normalization plus 5 consecutive XXT → BA → fused_bmm_add iterations on all 44 512×512 tiles. The first two iterations are available as contiguous context/ROI if the consumer preregisters them, but the producer did not shorten or select a favorable iteration. All four real device regions and kernel-boundary lifetime transitions are in `BUFFER_REGION_MAP.tsv` and `REGION_LIFETIME.tsv`.

Every native member is listed in `TRACE_MEMBER_MANIFEST.tsv`, `NATIVE_KERNEL_BINDING.tsv`, and `raw/formal_full5/raw/kernelslist.g`. All 18 terminal receipts are COMPLETE with drop=overflow=0; xz, the accepted traceg grammar validator, independent frozen trace-parser-only harness, output SHA and repeat hash checks passed. The compact review files are here. The original `.trace.xz`, native `.traceg.xz`, profiler-free launch census, canaries, tool binaries/JIT data and logs are under node164 durable root `/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r101_transient_l2_sim_capture_20260927/`, indexed by `RAW_DATA_INDEX.tsv` and `SHA256SUMS`.

Read `EXECUTION_CONTEXT.md`, `TRACER_SOURCE_AND_BUILD_RECEIPT.md`, `TERMINAL_AND_COMPLETENESS.md`, and `CLAIM_BOUNDARY.md` for qualification and limits. No Accel-Sim run or architecture mechanism was performed on 109.
''')
    write('EXECUTION_CONTEXT.md', f'''
# Execution context

- Repository: `swayhrl/accel-sim-framework`; execution branch `hrl/awma-r101-transient-l2-sim-capture-109-v1` from exact handoff `6533872601bb81dae1475b35d365f9dbe418cb23`.
- Node/GPU: `{guard['gpu_identity']}`; all CUDA execution was serial under `/data/c16/locks/c16_gpu_campaign.lock`.
- Input: accepted R101 payload `{input_['payload_sha256']}`, 44×512×512 BF16, Qwen2.5-0.5B-Instruct revision `{input_['model_revision']}`. No model download or gradient generation.
- Arithmetic: pinned HiMuon `{input_['source_commit']}`, five steps, `(3.4445,-4.7750,2.0315)`, XXT → BA → BMM-add; accepted output SHA `{input_['accepted_output_sha256']}`.
- Full capture ROI: `{scope['scope_id']}`; cuProfilerStart just before normalization, cuProfilerStop after fifth BMM-add. Selector is ROI marker plus exact 18-kernel count, **not** the census global launch index. The entire 18-member list was appended by one producer process/context, never concatenated from shards.
- Exact author-listed XXT/BA Triton launch configs were frozen before canaries solely to match accepted R101R1 function/grid/block strata, not selected from performance. The unchanged author kernels and exact output SHA passed the driver audit and payload-free launch census.
- Resource admission: first real complete iteration {volume['first_complete_iteration_raw_bytes']} compressed raw bytes; conservative full estimate {volume['full5_conservative_raw_bound_bytes_six_iteration_equivalents']} bytes versus frozen cap {volume['formal_raw_cap_bytes']}. Formal guard reason: `{guard['triggered_reason']}`; peak raw {guard['peak_raw_bytes']} bytes, peak host RSS {guard['peak_host_rss_bytes']} bytes.
''')
    write('TRACER_SOURCE_AND_BUILD_RECEIPT.md', f'''
# Tracer source and build receipt

Base producer scientific authority: `5143b4e10aaf2fc47bb60492155d2464b0b726fd`, Route-B NVBit 1.7.7.1 SM89. Parent tracer source SHA256 `{producer['parent_route_b_source_sha256']}`; current opt-in multi-ROI source SHA256 `{producer['this_multi_mode_source_sha256']}`; current binary SHA256 `{producer['new_multi_binary_sha256']}`. Exact source diff is `build/TRACER_MULTI_EXTENSION.diff` in node164.

The only producer extension is bounded `ROUTE_B_MULTI_SELECTED_COUNT` gated by cuProfilerStart/Stop: it reopens the accepted per-kernel writer after each terminal closure and appends separate members to the same context's kernelslist. The default historical single-target path is unchanged. Formatter SHA256 `{producer['formatter_unchanged_sha256']}` is byte-identical to accepted. Instrumentation/packet grammar is unchanged; accepted postprocessor SHA256 `{producer['postprocessor_sha256']}` and grammar validator SHA256 `{producer['validator_sha256']}` were reused. Formatter selftest returned `{producer['formatter_selftest']}`.

Historical `NO_EAGER_LOAD=0` grew host RSS before Python's first line under the R101 runtime and was abandoned as an unqualified diagnostic. `NO_EAGER_LOAD=1` was requalified here by a bounded import/CUDA probe, payload-free census, one-kernel canary, three-kernel first-iteration canary and all 18 FORMAL members. This is a runtime compatibility adaptation, not a trace grammar or scientific workload change. The accepted producer worktree/binaries were not modified.
''')
    write('TERMINAL_AND_COMPLETENESS.md', f'''
# Terminal and completeness

FORMAL status **COMPLETE** for all {manifest['selected_kernel_count']} ordered members in one context `{manifest['single_context']}` and stream `{manifest['single_stream']}`. Every member has a matching `ROUTEB_TERMINAL_COMPLETE` after device completion, explicit channel flush, receiver drain, xz close and atomic rename. Reported packets equal accepted and written records for every member. Aggregate drop=0, overflow=0. There were no extra selected kernels.

`kernelslist` and `kernelslist.g` each contain 18 unique, present members; every `.trace.xz` and `.traceg.xz` passed `xz -t`. The accepted full grammar validator and independent frozen trace-parser-only harness each passed 18/18, with the same total dynamic instruction count. Grammar checks memory opcode/byte-width/address syntax and sync/control semantics. Re-reading every traceg produced stable SHA256. `TRACE_SEMANTIC_SUMMARY.json` records {semantics['total_instructions']} validated dynamic instructions, {semantics['total_memory_opcode_count']} memory opcodes and {semantics['total_sync_control_opcode_count']} sync/control opcodes.

The runtime region map was created before cuProfilerStart. A/B/X0/X1 each have actual aligned base, 23,068,672 bytes, BF16 shape/stride and nonoverlapping ranges. `REGION_LIFETIME.tsv` is an 18-boundary join to exact captured kernel IDs; it never encodes per-line future last use.
''')
    write('TEST_AND_REGRESSION_SUMMARY.md', f'''
# Tests and regression summary

1. Accepted input payload and HiMuon source hashes matched their receipts; driver audit reproduced accepted normalization and final output bitwise.
2. Route-B formatter selftest PASS; source diff shows unchanged formatter/packet grammar and an opt-in bounded multi-kernel lifecycle only.
3. Payload-free census identified the frozen 18-kernel ROI; all 15 NS arithmetic function/grid/block strata match accepted R101R1.
4. One-kernel `INSTR_END=8` micro-canary: COMPLETE, zero drop/overflow, native traceg grammar PASS.
5. Three-kernel first-iteration canary: 3/3 COMPLETE and grammar PASS, zero drop/overflow. Its real trace size admitted full five-step capture under the preregistered cap.
6. FORMAL full-five-step: 18/18 terminal/trace/list/xz/grammar/frozen-parser/hash checks PASS, exact accepted output SHA and stable region/lifetime binding. No simulator was run.

Failed or excluded diagnostics are retained under node164 `raw/`: eager normalization bitwise mismatch (compiled accepted-style gate later passed), unfrozen Triton autotune geometry mismatch, and `NO_EAGER_LOAD=0` pre-Python memory growth. No excluded data was promoted as FORMAL evidence.
''')
    write('CLAIM_BOUNDARY.md', '''
# Claim boundary

This is a producer/input qualification only: `R101_TRANSIENT_SIM_CAPTURE_PASS`. Native traffic percentages from R101/R101R1 are reference receipts, not simulator calibration. The region lifetime sidecar states only software-known kernel-boundary LIVE/DEAD status; it does not provide oracle per-line future knowledge. No O1/M1 mechanism, Accel-Sim replay, hardware speedup, paper novelty, or 174-new result is claimed here.
''')
    write('FINAL_DECISION.md', '''
# Final producer decision

`R101_TRANSIENT_SIM_CAPTURE_PASS` — complete hash-closed full-five-step simulator-native input, exact accepted scientific payload and output, qualified Route-B grammar/terminal semantics, and A/B/X0/X1 address/lifetime sidecars. Publish independently of the 174-new science result, then STOP.
''')
    print(json.dumps({'report_files': 7, 'capture_id': manifest['capture_id']}, sort_keys=True))


if __name__ == '__main__':
    main()
