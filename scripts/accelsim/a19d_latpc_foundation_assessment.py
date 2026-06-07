#!/usr/bin/env python3
from __future__ import annotations

import sys
import time

sys.dont_write_bytecode = True

from a17_a18_latpc_lib import REPORT_DIR, ensure_local_dirs, latest, read_csv, rel, ts, write_csv, write_json, write_stage_report


def main() -> int:
    ensure_local_dirs()
    stamp = ts()
    start = time.time()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    hook_path = latest("A19C_latpc_hook_mapping_*.csv")
    csv_path = REPORT_DIR / f"A19D_latpc_foundation_assessment_{stamp}.csv"
    json_path = REPORT_DIR / f"A19D_latpc_foundation_readiness_{stamp}.json"
    report = REPORT_DIR / f"A19D_latpc_foundation_assessment_{stamp}.md"
    status = "PASS_WITH_WARNINGS"
    blocker = "core VM/TLB/PTW/PWC substrate incomplete"
    mode = "PARTIAL_FOUNDATION_ADDRESS_ONLY"
    rows: list[dict[str, str]] = []
    if not hook_path:
        status = "BLOCKED_NO_A19C"
        blocker = "missing A19C hook mapping"
        mode = "BLOCKED_NO_HOOK_MAPPING"
    else:
        hooks = read_csv(hook_path)
        for hook in hooks:
            availability = hook["availability"]
            if availability == "IMPLEMENTED":
                a20_feasibility = "usable_for_metadata_or_existing_stats"
                risk_level = "LOW"
            elif availability == "APPROXIMATED":
                a20_feasibility = "usable_only_for_design_or_explicit_approximate_experiment"
                risk_level = "MEDIUM"
            elif availability == "DEFERRED":
                a20_feasibility = "requires_mechanism_work"
                risk_level = "HIGH"
            else:
                a20_feasibility = "requires_foundation_substrate_before_faithful_LATPC"
                risk_level = "HIGH"
            rows.append(
                {
                    "target_field": hook["target_field"],
                    "mapped_module": hook["mapped_module"],
                    "availability": availability,
                    "a20_feasibility": a20_feasibility,
                    "risk_level": risk_level,
                    "risk": hook["risk"],
                    "recommended_next_step": hook["a20_action"],
                }
            )
        unavailable = len([r for r in rows if r["availability"] == "UNAVAILABLE"])
        approx = len([r for r in rows if r["availability"] == "APPROXIMATED"])
        if unavailable >= 3:
            mode = "PARTIAL_FOUNDATION_ADDRESS_ONLY"
        elif approx:
            mode = "PARTIAL_FOUNDATION_APPROXIMATE_VM"
        else:
            mode = "A20_FOUNDATION_READY"
            status = "PASS"
            blocker = "none"
    readiness = {
        "readiness_mode": mode,
        "status": status,
        "faithful_a20_latpc_mechanism_feasible_without_new_substrate": False if mode != "A20_FOUNDATION_READY" else True,
        "allowed_a20_direction": "metadata/stats and design; faithful LATPC requires explicit VM/TLB/PTW/PWC substrate work first",
        "forbidden_in_a19": "LATPC mechanism implementation, timing/control behavior change",
        "blocker": blocker,
        "assessment_csv": rel(csv_path),
    }
    write_csv(
        csv_path,
        rows,
        ["target_field", "mapped_module", "availability", "a20_feasibility", "risk_level", "risk", "recommended_next_step"],
    )
    write_json(json_path, readiness)
    extra = f"""## A19D Readiness Mode

`{mode}`

## Recommendation

A20 is not ready for a faithful LATPC mechanism on existing localized support
alone. It can proceed only if A20 first defines/adds a VM/TLB/PTW/PWC substrate
or explicitly runs an approximate address-derived experiment with no paper
speedup claim.
"""
    write_stage_report(
        report,
        "A19D LATPC Foundation Assessment",
        status,
        start_iso,
        start,
        ["python3 scripts/accelsim/a19d_latpc_foundation_assessment.py"],
        [rel(hook_path) if hook_path else ""],
        [rel(csv_path), rel(json_path), rel(report)],
        blocker,
        [
            "Assessment only; no simulator source or timing behavior is changed.",
            "Readiness is conservative because PTW/PWC/L2 TLB paths were not localized.",
        ],
        extra,
    )
    print(f"A19D status: {status}")
    print(f"A19D readiness mode: {mode}")
    print(f"A19D report: {rel(report)}")
    return 0 if not status.startswith("BLOCKED") else 1


if __name__ == "__main__":
    raise SystemExit(main())
