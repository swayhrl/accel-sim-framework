#!/usr/bin/env python3
"""Emit reviewable metadata for the isolated AWMA runtime recovery attempt."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
PACK=ROOT/"docs/vm_tlb/review_packs/AWMA_NEW_SIM_BASELINE_174NEW_V1"
REPORT=ROOT/"docs/vm_tlb/codex_handoff/awma/NEW_SIM_BASELINE_174NEW_REPORT.md"
NODE=Path("/root/share/mnt164/huangrulin/c16_ai_workload")
def put(p,t):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists() and p.read_text()!=t: raise RuntimeError("conflicting generated artifact "+str(p))
 p.write_text(t)
def main():
 status="AWMA_SIM_RUNTIME_RECOVERY_BLOCKED_EXTERNAL_DEPENDENCY"
 common="Status: "+status+". No C12 or other admitted historical traceg.xz payload/list is readable from 174-new shared or node164 AWMA namespaces; no trace semantics were fabricated.\n"
 docs={
"README.md":"# AWMA NEW_SIM_BASELINE 174-new V1\n\n"+common,
"SOURCE_ANCHORS.md":"# Source anchors\n\nFramework tree 09cc2f029022c660a3f827af9abded0fb34bdb41. VM Core source archive commit 5ba17a1ba88b8e8ec0f9505a7e684c81df8f0b7d. Non-VM 7be87f53 was rejected because it rejects gpgpu_vm_mode.\n",
"EXECUTION_CONTEXT.md":"# Execution context\n\nSeparate worktree and private build/toolchain under .awma_runtime. No 109 GPU or Native/Qwen worktree/process was used or modified. Build concurrency j2.\n",
"TOOLCHAIN_COMPATIBILITY_MATRIX.tsv":"candidate\tresult\nCUDA 12.4 isolated nvcc\tPASS\nzlib 1.3.1 user-space\tPASS\nGNU m4 1.4.19 user-space\tPASS\nGNU bison 3.8.2 user-space\tPASS\nflex 2.6.4 user-space\tPASS\nVM Core 5ba17a\tBUILT_VM_CONFIG_PARSE_PASS\n",
"TOOLCHAIN_RECEIPT.md":"# Toolchain receipt\n\nCUDA nvcc 12.4.131 archive SHA256 7ffba1ada0e4b8c17e451ac7a60d386aa2642ecd08d71202a0b100c98bd74681. All dependencies were installed under the isolated worktree, never system-wide.\n",
"SOURCE_BASELINE_SELECTION.md":"# Baseline source selection\n\nSelected 5ba17a M1-M3 VM Core because source registers gpgpu_vm_mode and accepts VM config. 7be87f is explicitly rejected as non-VM.\n",
"SEMANTIC_PATCH_AUDIT.md":"# Semantic patch audit\n\nNo simulator semantic code change. Build-only dependency wiring: private CUDA, zlib, m4, bison, flex, and GL runtime. Consumer contract adds required sync_control semantics only.\n",
"BUILD_RECEIPT.md":"# Build receipt\n\nBinary gpu-simulator/bin/release/accel-sim.out SHA256 3f13f849164aa1bd255d3e7c4d44a15db77ba925d3e5f2fc1412d7ddd6d6fe8c. Isolated build logs are .awma_runtime/build-*.log and remain outside Git.\n",
"BINARY_RECEIPT.md":"# Binary receipt\n\nStartup succeeds with private runtime library path. VM-disabled and VM-ideal configs parse and print gpgpu_vm_mode; no long trace replay was claimed.\n",
"SIM_INPUT_ADMISSION_REGRESSION.tsv":"case\tresult\nsync_control absent\tREJECTED\nC16WARP1/MREF\tREJECTED_NOT_PROVEN_LOSSLESS\nhash mismatch\tREJECTED\n",
"SMOKE_LADDER_RESULTS.tsv":"step\tresult\nbinary startup\tPASS\nVM-disabled config parse\tPASS\nVM-enabled config parse\tPASS\nreal trace parser\tBLOCKED_EXTERNAL_TRACE\nhistorical Prefill/Decode\tBLOCKED_EXTERNAL_TRACE\n",
"C12_PREFILL_CALIBRATION.tsv":"anchor\tresult\nC12 Prefill F0\tBLOCKED_INPUT_OR_RUNTIME; exact trace payload/list unavailable\n",
"C12_DECODE_CALIBRATION.tsv":"anchor\tresult\nC12 Decode1 F0\tBLOCKED_INPUT_OR_RUNTIME; exact trace payload/list unavailable\n",
"BASELINE_QUALIFICATION_DECISION.json":json.dumps({"status":status,"qualified":False,"blocker":"admitted historical traceg.xz payload/list unavailable","next_action":"provide hash-bound C12 Prefill and Decode trace/list roots"})+"\n",
"SIM_COMPAT_CAPTURE_CONSUMER_V2.md":"# Consumer V2\n\nSIM_COMPAT_CAPTURE_V1 now requires explicit sync_control semantics; omission fails admission regression.\n",
"EXTERNAL_BLOCKER.md":"# External blocker\n\nRequired artifact: hash-bound historical C12 Prefill F0 and Decode1 F0 kernelslist.g plus referenced traceg.xz payload roots (or an admitted equivalent trace bundle). Shared and node164 AWMA namespace searches found none. Without these, parser smoke, bounded replay, telemetry and calibration cannot be truthfully closed.\n",
"TEST_AND_REGRESSION_SUMMARY.md":"# Tests\n\nFoundation Python regression passes after sync_control omission negative test. VM config parse confirms required option recognition.\n",
"OPEN_ISSUES.md":"# Open issues\n\nNo formal baseline claim until exact admitted historical inputs are supplied. No current-model capture was attempted.\n"}
 for n,t in docs.items(): put(PACK/n,t)
 put(REPORT,"# NEW_SIM_BASELINE 174-new Report\n\n"+common)
 meta={"status":status,"binary_sha256":"3f13f849164aa1bd255d3e7c4d44a15db77ba925d3e5f2fc1412d7ddd6d6fe8c","core_sha":"5ba17a1ba88b8e8ec0f9505a7e684c81df8f0b7d"}
 put(NODE/"provenance/awma/simulation/AWMA_NEW_SIM_BASELINE_174NEW_V1.json",json.dumps(meta,sort_keys=True)+"\n")
 sums=[hashlib.sha256(p.read_bytes()).hexdigest()+"  "+p.name for p in sorted(PACK.iterdir()) if p.name!="SHA256SUMS"]; put(PACK/"SHA256SUMS","\n".join(sums)+"\n")
if __name__=="__main__":main()
