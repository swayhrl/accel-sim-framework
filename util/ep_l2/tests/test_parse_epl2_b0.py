#!/usr/bin/env python3
import csv
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PARSER = ROOT / "util/ep_l2/parse_epl2_b0.py"

LOG = """EPL2B0V1|scope=application|interval=application_cumulative|slice=0|kernel_uid=18446744073709551615|start_cycle=0|completion_cycle=12|overlap_detected=0|samples=12|line_mshr_avg=1|line_mshr_p95=2|line_mshr_max=2|descriptor_avg=2|descriptor_p95=3|descriptor_max=3|wad_avg=0|wad_p95=0|wad_max=0|resident_payload_avg=1|resident_payload_p95=1|resident_payload_max=1|bypass_payload_avg=0|bypass_payload_p95=0|bypass_payload_max=0|missq_avg=0|missq_max=1|lowerq_avg=0|lowerq_max=1|block_descriptor=2|block_wad=0|block_payload=1|block_bank=1|block_l1=0|block_lower=3|bank_requests=5|bank_grants=4|bank_conflicts=1
EPL2B0V1|scope=application|interval=application_cumulative|slice=0|kernel_uid=18446744073709551615|start_cycle=0|completion_cycle=24|overlap_detected=0|samples=24|line_mshr_avg=1|line_mshr_p95=2|line_mshr_max=2|descriptor_avg=2|descriptor_p95=3|descriptor_max=3|wad_avg=0|wad_p95=0|wad_max=0|resident_payload_avg=1|resident_payload_p95=1|resident_payload_max=1|bypass_payload_avg=0|bypass_payload_p95=0|bypass_payload_max=0|missq_avg=0|missq_max=1|lowerq_avg=0|lowerq_max=1|block_descriptor=4|block_wad=0|block_payload=2|block_bank=2|block_l1=0|block_lower=6|bank_requests=10|bank_grants=8|bank_conflicts=2
EPL2B0V1|scope=kernel|interval=kernel_shared_delta|slice=0|kernel_uid=7|start_cycle=2|completion_cycle=12|overlap_detected=1|samples=10|line_mshr_avg=1|bank_requests=5|bank_grants=4|bank_conflicts=1|block_descriptor=2|block_wad=0|block_payload=1|block_bank=1|block_l1=0|block_lower=3
EPL2B0V1|INVARIANT|slice=0|kernel_uid=7|line_mshr_used=0|line_mshr_capacity=128|descriptor_used=0|descriptor_free=256|descriptor_capacity=256|wad_live=2|wad_capacity=128|resident_live=1|resident_capacity=1024|bypass_live=0|bypass_capacity=128|bank_pending=0|resident_tag_payload_consistent=1|payload_double_owner=0|terminal_clean=0
EPL2B0V1|INVARIANT|slice=0|kernel_uid=18446744073709551615|line_mshr_used=0|line_mshr_capacity=128|descriptor_used=0|descriptor_free=256|descriptor_capacity=256|wad_live=2|wad_capacity=128|resident_live=1|resident_capacity=1024|bypass_live=0|bypass_capacity=128|bank_pending=0|resident_tag_payload_consistent=1|payload_double_owner=0|terminal_clean=0
EPL2B0V1|INVARIANT|slice=0|kernel_uid=18446744073709551615|line_mshr_used=0|line_mshr_capacity=128|descriptor_used=0|descriptor_free=256|descriptor_capacity=256|wad_live=0|wad_capacity=128|resident_live=1|resident_capacity=1024|bypass_live=0|bypass_capacity=128|bank_pending=0|resident_tag_payload_consistent=1|payload_double_owner=0|terminal_clean=1
EPL2L1V1|scope=application|kernel_uid=18446744073709551615|accesses=8|misses=2|bank_conflicts=1
EPL2DRAMV1|scope=application|channel=0|successful_read_bytes=32|bandwidth_util=0.5
EPL2DRAMV1|scope=window|interval=5000_cycle|channel=0|window_start_cycle=0|window_end_cycle=5000|dram_cycles=5000|scheduler_occ_avg=1|returnq_occ_avg=0|successful_read_bytes=16|bandwidth_util=0.25
"""

with tempfile.TemporaryDirectory() as temp:
    temp = Path(temp); log = temp / "run.log"; out = temp / "out"
    log.write_text(LOG)
    subprocess.check_call(["python3", str(PARSER), str(log), "--out", str(out),
                           "--framework-commit", "framework", "--core-commit", "core"])
    assert set(p.name for p in out.iterdir()) == {"target_summary.csv", "target_slice.csv", "target_kernel.csv", "target_window.csv", "target_bank.csv", "target_l1.csv", "target_dram.csv", "manifest.json"}
    summary = next(csv.DictReader((out / "target_summary.csv").open()))
    assert summary["bank_conflicts"] == "2"
    assert summary["c7d_dram_scheduler_full_block"] == "NOT_EMITTED_BY_EPL2B0V1"
    assert summary["slice_count"] == "1"
    assert summary["terminal_invariant_records"] == "1"
    assert summary["invariants_terminal_clean"] == "1"
    kernel = next(csv.DictReader((out / "target_kernel.csv").open()))
    assert kernel["overlap_detected"] == "1"
    assert next(csv.DictReader((out / "target_l1.csv").open()))["accesses"] == "8"
    dram = list(csv.DictReader((out / "target_dram.csv").open()))
    assert dram[0]["bandwidth_util"] == "0.5"
    assert dram[1]["scope"] == "window"
    assert dram[1]["interval"] == "5000_cycle"
    assert json.loads((out / "manifest.json").read_text())["schema_version"] == "EPL2B0V1"
print("EPL2B0V1 parser regression: PASS")
