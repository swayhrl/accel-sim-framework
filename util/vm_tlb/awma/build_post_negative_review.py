#!/usr/bin/env python3
"""Build hash closure for the post-negative pivot review pack."""

from __future__ import annotations

import csv
import hashlib
import subprocess
from pathlib import Path


REPO = Path("/root/workspace/accel-sim-framework-awma-post-negative-problem-pivot-v1")
PACK = REPO / "docs/vm_tlb/review_packs/AWMA_POST_NEGATIVE_PROBLEM_PIVOT_V1"
GIT_SOURCES = [
    ("f25312635dae33342d6540be92467c6ed67fdb0d", "docs/vm_tlb/review_packs/AWMA_AI_UVM_MODEL_DERIVED_CHARACTERIZATION_V1/REPORT.md", "ACCEPTED_UVM_REPORT"),
    ("f25312635dae33342d6540be92467c6ed67fdb0d", "docs/vm_tlb/review_packs/AWMA_AI_UVM_MODEL_DERIVED_CHARACTERIZATION_V1/FINAL_DECISION.md", "ACCEPTED_UVM_DECISION"),
    ("f25312635dae33342d6540be92467c6ed67fdb0d", "docs/vm_tlb/review_packs/AWMA_AI_UVM_MODEL_DERIVED_CHARACTERIZATION_V1/SHA256SUMS", "ACCEPTED_UVM_MANIFEST"),
    ("d116e64b6c2d7faab1babc56c966ff4c1d628904", "docs/vm_tlb/review_packs/AWMA_AI_GPU_RESOURCE_BOTTLENECK_CHARACTERIZATION_V1/REPORT.md", "ACCEPTED_RESOURCE_REPORT"),
    ("d116e64b6c2d7faab1babc56c966ff4c1d628904", "docs/vm_tlb/review_packs/AWMA_AI_GPU_RESOURCE_BOTTLENECK_CHARACTERIZATION_V1/RESOURCE_SATURATION_MAP.tsv", "ACCEPTED_RESOURCE_MAP"),
    ("d116e64b6c2d7faab1babc56c966ff4c1d628904", "docs/vm_tlb/review_packs/AWMA_AI_GPU_RESOURCE_BOTTLENECK_CHARACTERIZATION_V1/SHA256SUMS", "ACCEPTED_RESOURCE_MANIFEST"),
    ("3e29f234a971e2be68076eef22a05391cf9e4b67", "docs/vm_tlb/review_packs/AWMA_AI_TRANSLATION_NATIVE_RESIDUAL_174NEW_V1/REPORT.md", "ACCEPTED_TRANSLATION_REPORT"),
    ("9efe8236e0c6338addfef5480e1da91bffb504eb", "docs/vm_tlb/review_packs/AWMA_INTRAWARP_TRANSLATION_BASELINE_AND_RESIDUAL_V1/REPORT.md", "ACCEPTED_CLASSIC_BASELINE_REPORT"),
]
TREE_SOURCES = [
    ("docs/vm_tlb/review_packs/C16_FIRST_V2_FORMAL_INGEST_174NEW_V1/FINAL_DECISION.json", "C16_OBJECT_ACCEPTANCE"),
    ("docs/vm_tlb/review_packs/C16_FIRST_V2_FORMAL_INGEST_174NEW_V1/OBJECT_ATTRIBUTION.tsv", "C16_OBJECT_RESULT"),
    ("docs/vm_tlb/review_packs/C16_FIRST_V2_FORMAL_INGEST_174NEW_V1/PRODUCER_CONSUMER_CROSSCHECK.tsv", "C16_OBJECT_CROSSCHECK"),
    ("docs/vm_tlb/review_packs/AWMA_FIRST_CURRENT_MODEL_BASELINE_SIM_174NEW_V1/SIM_EVIDENCE_RECORD.json", "Q05_OBJECT_ACCEPTANCE"),
    ("docs/vm_tlb/review_packs/AWMA_FIRST_CURRENT_MODEL_BASELINE_SIM_174NEW_V1/object-map.tsv", "Q05_OBJECT_MAP"),
    ("docs/vm_tlb/review_packs/AWMA_FIRST_CURRENT_MODEL_BASELINE_SIM_174NEW_V1/raw/replay_1/telemetry/L1D_OBJECT_STATS.tsv", "Q05_OBJECT_STATS"),
    ("docs/vm_tlb/review_packs/AWMA_Q05_CONTEXTUAL_WARM_PREFIX_REPLAY_174NEW_V1/WARM_PREFIX_RESULTS.tsv", "CONTEXT_INPUT"),
    ("docs/vm_tlb/review_packs/AWMA_Q05_CONTEXTUAL_WARM_PREFIX_REPLAY_174NEW_V1/Q05_TRANSLATION_RESULTS.tsv", "CONTEXT_INPUT"),
    ("docs/vm_tlb/review_packs/AWMA_Q05_CONTEXTUAL_WARM_PREFIX_REPLAY_174NEW_V1/Q05_DATA_CACHE_RESULTS.tsv", "CONTEXT_INPUT"),
    ("docs/vm_tlb/review_packs/AWMA_Q05_CONTEXTUAL_WARM_PREFIX_REPLAY_174NEW_V1/TRANSLATION_RELEVANT_PAGE_OVERLAP_4K.tsv", "CONTEXT_INPUT"),
    ("docs/vm_tlb/review_packs/AWMA_Q05_CONTEXTUAL_WARM_PREFIX_REPLAY_174NEW_V1/TRANSLATION_RELEVANT_PAGE_OVERLAP_64K.tsv", "CONTEXT_INPUT"),
    ("docs/vm_tlb/review_packs/AWMA_Q05_CONTEXTUAL_WARM_PREFIX_REPLAY_174NEW_V1/F0_KERNEL_BOUNDARY_STATE_MATRIX_FINAL.tsv", "CONTEXT_INPUT"),
    ("docs/vm_tlb/codex_handoff/c16/autodl_wave1/P3_AWQ_S2_TEXT_G1_CHECKPOINT.json", "AWQ_NATIVE_ACCEPTANCE"),
    ("docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/lane_g_wave1_native/direct_semantic_p3_awq_s2/SEMANTIC_EVIDENCE_RECEIPT.json", "AWQ_SEMANTIC_BOUNDARY"),
    ("docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/lane_g_wave1_native/direct_semantic_p3_awq_s2/SEMANTIC_COVERAGE.tsv", "AWQ_SEMANTIC_BOUNDARY"),
    ("docs/vm_tlb/codex_handoff/c16/autodl_wave1/P2_RAW_S0_RESOURCE_ADMISSION.json", "RAW7B_BLOCKER"),
    ("docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_nvbit175_full_multimodel_campaign/CAMPAIGN_FINAL_REPORT.md", "PROVISIONAL_EXCLUSION"),
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    rows = []
    for commit, path, role in GIT_SOURCES:
        data = subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=REPO)
        rows.append({"authority": commit, "artifact": f"git:{commit}:{path}", "role": role,
                     "sha256": digest(data), "bytes": len(data)})
    for relative, role in TREE_SOURCES:
        path = REPO / relative; data = path.read_bytes()
        rows.append({"authority": "22004807cabb09e8795e0c61f5dc679aa3f37007", "artifact": str(path),
                     "role": role, "sha256": digest(data), "bytes": len(data)})
    for name in ["CONTEXT_PREFIX_DIAGNOSTIC.tsv", "CONTEXT_MATCHED_PAIR_RESULTS.tsv",
                 "CONTEXT_CORRELATION_SUMMARY.tsv", "CONTEXT_DIAGNOSTIC_RECEIPT.json"]:
        path = PACK / name; data = path.read_bytes()
        rows.append({"authority": "THIS_STAGE", "artifact": str(path), "role": "DERIVED_DIAGNOSTIC",
                     "sha256": digest(data), "bytes": len(data)})
    with (PACK / "RAW_DATA_INDEX.tsv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, ["authority", "artifact", "role", "sha256", "bytes"],
                                delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    manifest = []
    for path in sorted(PACK.iterdir()):
        if path.is_file() and path.name != "SHA256SUMS":
            manifest.append(f"{digest(path.read_bytes())}  {path.name}")
    (PACK / "SHA256SUMS").write_text("\n".join(manifest) + "\n")
    print(f"raw={len(rows)} manifest={len(manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
