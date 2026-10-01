#!/usr/bin/env python3
"""Finalize the successful V2 canary/formal result before raw publication."""

import argparse
import hashlib
import json
import shutil
from pathlib import Path


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--raw", type=Path, required=True)
    p.add_argument("--pack", type=Path, required=True)
    p.add_argument("--remote-path", required=True)
    args = p.parse_args()
    source = json.loads((args.pack / "SOURCE_PREFLIGHT_V2.json").read_text())
    canary = json.loads((args.raw / "B0_B1_TIMELINE_CANARY.json").read_text())
    b0 = json.loads((args.raw / "canary_b0.json").read_text())
    b1 = json.loads((args.raw / "canary_b1_v2.json").read_text())
    primary = json.loads((args.pack / "PRIMARY_BOOTSTRAP.json").read_text())
    duration = json.loads((args.pack / "KERNEL_DURATION_RESPONSE.json").read_text())
    overlap = json.loads((args.pack / "OVERLAP_SUMMARY.json").read_text())
    heldout = json.loads((args.pack / "HELDOUT_V2.json").read_text())
    final = json.loads((args.pack / "FINAL_DECISION.json").read_text())
    receipt = json.loads((args.raw / "GPU_LOCK_RECEIPT.json").read_text())
    formal = sorted(args.raw.glob("formal_block*_pos*_*.json"))
    if len(formal) != 48 or any(json.loads(path.read_text())["status"] != "PASS" for path in formal):
        raise RuntimeError("formal sample closure failed")
    if canary["status"] != "PASS" or b0["generated_token_ids_D0_D3"] != [23578,11,323,3950] or b1["generated_token_ids_D0_D3"] != [23578,11,323,3950]:
        raise RuntimeError("Stage 1 gate is not PASS")
    for raw_name, pack_name in [
        ("B0_B1_TIMELINE_CANARY.json", "STAGE1_CANARY_GATE.json"),
        ("B1_GATE_UP_OVERLAP.tsv", "B1_GATE_UP_OVERLAP.tsv"),
        ("CANARY_KERNEL_DURATIONS.tsv", "CANARY_KERNEL_DURATIONS.tsv"),
        ("GPU_LOCK_RECEIPT.json", "GPU_LOCK_RECEIPT.json"),
    ]:
        shutil.copyfile(args.raw / raw_name, args.pack / pack_name)
    dump(args.pack / "TIMELINE_CANARY_B0.json", {
        "status": b0["status"], "arm": "B0", "tokens": b0["generated_token_ids_D0_D3"],
        "decode_wall_ms_canary_excluded": b0["decode_wall_ms"],
        "call_order_count": len(b0["call_order"]), "projection_occurrences": len(b0["occurrences"]),
        "raw_json_sha256": sha(args.raw / "canary_b0.json"),
    })
    dump(args.pack / "TIMELINE_CANARY_B1_V2.json", {
        "status": b1["status"], "arm": "B1_V2", "tokens": b1["generated_token_ids_D0_D3"],
        "decode_wall_ms_canary_excluded": b1["decode_wall_ms"],
        "call_order_count": len(b1["call_order"]), "projection_occurrences": len(b1["occurrences"]),
        "overlap_count": overlap["overlap_count"], "total_overlap_ns": overlap["total_overlap_ns"],
        "raw_json_sha256": sha(args.raw / "canary_b1_v2.json"),
    })
    authority = {
        "status": "PASS", "task": "C16_FFN_GATE_UP_CONCURRENCY_NATIVE_DIAGNOSTIC_V2",
        "authority_commit": "ee8cadd4a9a0be31186fcc0bdc8fb47dd515dbf8",
        "authority_tree": "44fcf5e689125061a3a80bcb677a8a5292a68a32",
        "contract_sha256": "15ab771a848f67b4017e8bece742bba5cebc253f99e885f380bd4abc2d2b0b5c",
        "base_v1_commit": "ef517d8e5a0e3659abe71b49beeba1559cd5f2ce",
        "base_v1_status": "CORRECTNESS_MISMATCH_STOP",
        "base_v1_overlap_scientific_use": "NONE",
        "result_runner_sha256": source["result_runner_sha256"],
        "execution_scope_correction": source["execution_scope_correction"],
        "scientific_target_change": source["scientific_target_change"],
        "merged_baseline_status": "CORRECTNESS_TOLERANCE_FAILED_STOP",
        "merged_canary_performance_use_in_v2": "NONE",
        "raw_node109": str(args.raw), "raw_node164": args.remote_path,
    }
    dump(args.pack / "SOURCE_AND_AUTHORITY.json", authority)
    protocol = {"status": "PASS", "stage1": "1x B0 + 1x B1_V2 NSYS cuda,nvtx",
                "stage1_before_formal": True, "formal_order": "12 blocks B0,B1,B1,B0",
                "fresh_process_per_sample": True, "b0_samples": 24, "b1_samples": 24,
                "bootstrap_unit": "complete ABBA block", "bootstrap_resamples": 1000,
                "bootstrap_seed": 20261001, "oracle_saving_ms": 7.732849,
                "heldout": "D3 plus layers 14-27, no extra GPU run"}
    dump(args.pack / "MEASUREMENT_PROTOCOL.json", protocol)
    audit = f"""# V2 implementation and result audit\n\n- V1 remains frozen at `CORRECTNESS_MISMATCH_STOP`; its overlap has no scientific use.\n- GNU patch applied the exact authorized two-line scope correction. Runner SHA is `{source['result_runner_sha256']}`.\n- PREFILL calls the saved bound original forward. D0–D3 retain two producer streams and the original event DAG.\n- Stage 1 passed tokens, 420 call order entries, 336 exact projection identities, module/policy semantics, and kernel name/grid/block inventories.\n- B1_V2 overlap occurred in {overlap['overlap_count']}/112 windows ({overlap['total_overlap_ns']} ns total).\n- Formal completed 24 B0 and 24 B1 samples in 12 complete ABBA blocks.\n- B1 is slower: saving {primary['observed']['saving_ms']:.6f} ms, speedup {primary['observed']['speedup']:.6f}x.\n- Gate and up duration ratios are {duration['gate']['b1_over_b0']:.6f}x and {duration['up']['b1_over_b0']:.6f}x.\n- Decision: `{final['decision']}`. No NCU or follow-up experiment was launched.\n"""
    (args.pack / "IMPLEMENTATION_AND_RESULT_AUDIT.md").write_text(audit)
    interpretation = {
        "status": "PASS", "decision": final["decision"],
        "whole_decode": primary["observed"], "whole_decode_bootstrap": primary["bootstrap"],
        "overlap": overlap, "kernel_duration": duration,
        "oracle_realization_fraction": final["oracle_realization_fraction"],
        "heldout": heldout, "negative_result_preserved": final["negative_result_preserved"],
        "claim": "current separated AutoAWQ runtime shows limited overlap and resource-contention-consistent slowdown",
        "claims_forbidden": ["new concurrency mechanism", "hardware necessity", "merged baseline performance ranking"],
        "automatic_followup": False,
    }
    dump(args.pack / "FINAL_INTERPRETATION.json", interpretation)
    build = {"status": "PASS", "runner_sha256": sha(args.repo / "util/vm_tlb/c16/e1_operator_family_natural.py"),
             "tool_sha256": {path.name: sha(path) for path in sorted((args.repo / "util/vm_tlb/c16/ffn_gate_up_concurrency_v2").glob("*")) if path.is_file()},
             "inherited_v1_harness_sha256": {name: sha(args.repo / "util/vm_tlb/c16/ffn_gate_up_concurrency" / name) for name in ("concurrency_canary.py", "postprocess.py", "raw_manifest.py")},
             "python": "/data/c16/env/c16-awq-v6/bin/python", "nsys": "/usr/local/bin/nsys"}
    dump(args.pack / "BUILD_RECEIPT.json", build)
    tests = {"status": "PASS", "source_preflight": source["status"], "stage1": canary["status"],
             "formal_sample_count": len(formal), "postprocess": primary["status"],
             "gpu_lock_released": receipt["released"], "gpu_wall_seconds": receipt["gpu_wall_seconds"],
             "forbidden_tools_used": []}
    dump(args.pack / "TESTS.json", tests)
    readme = """# C16 FFN gate/up concurrency native diagnostic V2 — Lane 7\n\nThe exact authorized prefill scope repair closed V2 correctness. Stage 1 and all 48 formal samples passed. B1_V2 produced limited real overlap but was slower than B0, with significant gate/up duration inflation. The accepted interpretation is resource-contention-limited software concurrency for the current separated AutoAWQ runtime. No hardware or novelty claim follows.\n"""
    (args.pack / "README.md").write_text(readme)
    final_status = {"status": "PASS", "decision": final["decision"], "formal_samples": len(formal),
                    "stage1": "PASS", "gpu_lock_released": receipt["released"],
                    "automatic_followup": False}
    dump(args.raw / "FINAL_STATUS.json", final_status)
    print(json.dumps(final_status, sort_keys=True))


if __name__ == "__main__":
    main()
