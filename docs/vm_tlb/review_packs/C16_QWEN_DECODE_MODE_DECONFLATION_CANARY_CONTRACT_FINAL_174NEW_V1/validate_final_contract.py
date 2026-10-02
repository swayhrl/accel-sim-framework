#!/usr/bin/env python3
"""CPU-only exact-promotion check: no scientific diff from the approved draft."""

import copy
import hashlib
import json
import pathlib
import subprocess


ROOT = pathlib.Path(__file__).resolve().parent
DESIGN = "dd4a4f48f200b9c35ea094b4eac5bfffc722cb2a"
DRAFT_PATH = "docs/vm_tlb/review_packs/C16_QWEN_DECODE_EXECUTION_MODE_DECONFLATION_DESIGN_174NEW_V1/C16_QWEN_DECODE_COMPILED_NO_CUDAGRAPH_CANARY_109_DRAFT.json"
FINAL_NAME = "C16_QWEN_DECODE_COMPILED_NO_CUDAGRAPH_CANARY_109_V1.json"


def git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()


def main():
    assert git("cat-file", "-t", DESIGN) == "commit"
    draft_bytes = subprocess.check_output(["git", "show", f"{DESIGN}:{DRAFT_PATH}"])
    draft = json.loads(draft_bytes)
    final_bytes = (ROOT / FINAL_NAME).read_bytes()
    final = json.loads(final_bytes)
    receipt = json.loads((ROOT / "CONTRACT_FINALIZATION_RECEIPT.json").read_text())
    decision = json.loads((ROOT / "FINAL_DECISION.json").read_text())
    assert git("rev-parse", f"{DESIGN}^{{tree}}") == receipt["design_tree"]
    assert git("rev-parse", f"{DESIGN}:{DRAFT_PATH}") == receipt["draft_git_blob_sha1"] == receipt["provided_digest_value"]
    assert len(receipt["provided_digest_value"]) == 40
    assert hashlib.sha256(draft_bytes).hexdigest() == receipt["draft_actual_sha256"]
    assert hashlib.sha256(final_bytes).hexdigest() == receipt["final_contract_sha256"]
    assert draft["status"] == "DRAFT_FOR_PROJECT_APPROVAL" and draft["execution_authorized"] is False
    assert final["status"] == "AUTHORIZED_BY_PROJECT_REVIEW" and final["execution_authorized"] is True
    assert draft["automatic_gpu_start"] is final["automatic_gpu_start"] is False
    assert final["schema"] == "C16_QWEN_DECODE_COMPILED_NO_CUDAGRAPH_CANARY_109_V1"
    assert final["authority"]["design_commit"] == DESIGN
    adjusted = copy.deepcopy(final)
    adjusted["schema"] = draft["schema"]
    adjusted["status"] = draft["status"]
    adjusted["execution_authorized"] = draft["execution_authorized"]
    del adjusted["authority"]["design_commit"]
    assert adjusted == draft, "scientific or execution design changed beyond authorized metadata"
    assert receipt["authorized_metadata_changes_only"] == ["schema", "status", "execution_authorized", "authority.design_commit"]
    assert receipt["scientific_fields_unchanged"] is True
    assert final["scope"]["points_in_order"] == decision["point_allowlist_in_order"] == ["MP02", "MP03"]
    assert final["execution"]["gpu_active_seconds_cap"] == decision["gpu_active_seconds_cap"] == 120
    assert final["correctness"]["atol"] == 0.05 and final["correctness"]["rtol"] == 0.01
    assert final["modes"]["MODE_C_HISTORICAL_FAILED"]["execute"] is False
    assert final["execution"]["semantic_observer"] == "FORBIDDEN"
    assert final["execution"]["nsys_ncu_nvbit_sass_accelsim"] == "FORBIDDEN"
    assert final["stage_sequence"]["if_mp02_fail"].startswith("STOP")
    assert decision["status"] == "MODE_DECONFLATION_CANARY_CONTRACT_FINALIZED"
    assert decision["gpu_used_in_this_goal"] is False and decision["automatic_gpu_start"] is False
    print("PASS: draft blob identity and SHA256, exact metadata-only promotion, scope, tolerance and no automatic GPU start")


if __name__ == "__main__":
    main()
