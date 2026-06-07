#!/usr/bin/env python3
from __future__ import annotations

import sys
import time

sys.dont_write_bytecode = True
from a20_a23_latpc_vm_lib import REPORT_DIR, clean, ensure_dirs, latest, rel, selected_workload, stage_report, ts, write_csv


def main() -> int:
    ensure_dirs()
    stamp = ts()
    start = time.time()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    selected = selected_workload()
    a19 = latest("A19D_latpc_foundation_assessment_*.md")
    csv_path = REPORT_DIR / f"A20A_latpc_vm_substrate_requirements_{stamp}.csv"
    report = REPORT_DIR / f"A20A_latpc_vm_substrate_requirements_{stamp}.md"
    rows = [
        ("REQ_001", "address_observation", "observe effective per-lane memory addresses without affecting memory issue", "A19 address hook", "Regularity Detector input", "use generate_mem_accesses hook", "feed future detector", "approximate if not true VA", "default disabled"),
        ("REQ_002", "vpn_derivation", "derive VPN as address >> page_shift", "A19 address-only foundation", "shadow VM stats", "implement in shadow helper", "reuse for LATC/LATP shadow", "effective address may not be architectural VA", "configurable page_shift"),
        ("REQ_003", "page_size_config", "provide page_shift env knob", "A19 missing VM config", "sensitivity", "ACCELSIM_LATPC_SHADOW_PAGE_SHIFT", "2MB sensitivity later", "paper alignment requires care", "default 12"),
        ("REQ_004", "per_sm_l1_tlb", "model shadow L1 TLB", "A19 L1 TLB unavailable", "translation locality", "fully associative LRU", "baseline for LATC", "SM id unavailable may force global approximation", "default 32 entries"),
        ("REQ_005", "global_l2_tlb", "model global shadow L2 TLB", "A19 L2 TLB unavailable", "hierarchy stats", "fully associative LRU", "LATC/LATP stats", "not real timing", "default 1024 entries"),
        ("REQ_006", "l1_tlb_mshr_shadow", "track outstanding VPNs and MSHR failures", "A19 real TLB MSHR unavailable", "MSHR pressure", "shadow MSHR map", "LATC shadow compression", "not real MSHR", "default 16"),
        ("REQ_007", "l2_tlb_mshr_shadow", "reserve field and env for L2 MSHR", "A19 unavailable", "future LATC", "defer detailed L2 MSHR", "future extension", "scope risk", "default 128"),
        ("REQ_008", "ptw_shadow_queue", "model shadow page walk queue", "A19 PTW unavailable", "PTW pressure", "completion queue", "LATP shadow batching", "not real PTW", "default 128"),
        ("REQ_009", "ptw_shadow_completion", "complete walks into shadow TLBs", "A19 PTW unavailable", "stats self-consistency", "walker next-available cycles", "LATP shadow", "event index approximate", "default latency 300"),
        ("REQ_010", "pwc_optional", "print PWC counters and mark deferred", "A19 PWC unavailable", "paper gap", "zero counters first", "future PWC", "not implemented", "pwc_enable 0"),
        ("REQ_011", "stats_print", "print raw latpc_shadow/vm/tlb/ptw/pwc stats", "A18 print path", "validation", "gpu_print_stat hook", "reporting", "wall-clock only", "stable names"),
        ("REQ_012", "runner_env_enable", "runner controls env rows", "A16 runner", "bounded NW", "new A21C runner", "future matrix", "env mistakes", "default disabled"),
        ("REQ_013", "behavior_equivalence", "shadow enabled must not alter cycles/instructions/IPC/L2", "A18 equivalence", "safety", "A22A exact comparison", "baseline guarantee", "failure blocks", "strict tolerance"),
        ("REQ_014", "sensitivity_knobs", "small/default/large TLB knobs", "A20 master", "sanity", "A22B", "future tuning", "weak trend possible", "bounded only"),
        ("REQ_015", "review_pack_patch_capture", "capture source patch and reports", "A19 closeout", "review", "A23B pack", "audit", "runtime not committed", "explicit git add only"),
    ]
    dict_rows = [{"requirement_id": r[0], "component": r[1], "requirement": r[2], "source_from_a19": r[3], "needed_for": r[4], "a20_a23_action": r[5], "future_latpc_action": r[6], "risk": r[7], "notes": r[8]} for r in rows]
    write_csv(csv_path, dict_rows, ["requirement_id", "component", "requirement", "source_from_a19", "needed_for", "a20_a23_action", "future_latpc_action", "risk", "notes"])
    status = "PASS" if a19 else "PASS_WITH_WARNINGS"
    report.write_text(f"""# A20A LATPC VM Substrate Requirements

- Status: {status}
- Selected workload: {clean(selected.get('selected_workload')) or 'nw'} / {clean(selected.get('paper_workload')) or 'NW'}
- A19 foundation input: `{rel(a19) if a19 else 'reconstructed'}`

## A19 Starting Point

A19 found address observation and stats print plumbing, but no complete active
L1/L2 TLB, TLB MSHR, PTW, page-walk queue, or PWC foundation.

## Why Not Implement LATPC Directly

LATPC requires translation-specific state. The current localized support is not
enough to implement Regularity Detector, LATC, or LATP as paper mechanisms
without inventing hidden timing behavior. A shadow VM substrate is therefore
needed first.

## Shadow VM Substrate Definition

The substrate observes addresses, derives VPN-like values, updates side-model
TLB/MSHR/PTW/PWC counters, and prints raw stats. It must not affect real memory
requests, scheduling, latency, cache/TLB behavior, replay, or IPC.

## Success Criteria

- Shadow default disabled.
- Shadow enabled emits non-trivial VM/TLB/PTW stats.
- Baseline and shadow runs are behavior-equivalent on NW.
- Outputs clearly distinguish shadow analysis from timing reproduction.
""")
    stage_report(report, "A20A LATPC VM Substrate Requirements", status, start_iso, start, ["python3 scripts/accelsim/a20a_latpc_vm_substrate_requirements.py"], [rel(a19) if a19 else "", clean(selected.get("_source_path"))], [rel(csv_path), rel(report)], "none", ["Design/reporting only.", "No simulator source is changed."])
    print(f"A20A status: {status}")
    print(f"A20A report: {rel(report)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
