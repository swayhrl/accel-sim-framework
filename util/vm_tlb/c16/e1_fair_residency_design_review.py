#!/usr/bin/env python3
"""Build the C16 E1 target-class fair-residency design review.

This tool is deliberately read-only with respect to the native producer, Core,
and Lane-4 run.  It extracts frozen source/receipt evidence from exact Git
objects, derives structural bounds, and writes a design-review pack.  It does
not read Lane-4 partial outputs, implement a cache mechanism, or launch timing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path


GOAL = "C16_E1_TARGET_CLASS_FAIR_RESIDENCY_DESIGN_REVIEW_V1"
FINAL_LABEL = "TARGET_CLASS_FAIRNESS_MECHANISM_JUSTIFIED"
FRAMEWORK_HEAD = "4214398782159022907081dbcc36854cf21fb4b5"
NATIVE_HEAD = "86ef7dcfb49241bd87ff4a8d59b4d950d53de0a5"
CORE_HEAD = "a2322069b9701597db7019080b5b54d29518e3a2"
LANE4_CORE_HEAD = "0271de82432db004beed43280ed01057246a0f2c"
SIDECAR_SHA = "6c60839714d136b9f6f596218588e658e245e0b7cc6f8e8550cce8d683ce13c6"
MANIFEST_SHA = "db3bdbb0295a47a6aa4644508ea1895779c987f2f77cd96f184c67b8a10ab389"
REGION_BYTES = 33_947_648
LINE_BYTES = 128
REGION_LINES = REGION_BYTES // LINE_BYTES
CLASS_COUNT = 28
FAMILY_LINES = REGION_LINES * CLASS_COUNT
SUBPARTITIONS = 16
SETS_PER_SUBPARTITION = 2048
WAYS = 16

BUDGETS = [
    ("B8", 8 << 20),
    ("B16", 16 << 20),
    ("B24", 24 << 20),
    ("BFULL", REGION_BYTES),
]

NATIVE_ROOT = "docs/vm_tlb/review_packs/C16_E1_RESIDENCY_COST_BENEFIT_CLOSURE_109_V1"
NATIVE_POLICY = "util/vm_tlb/c16/e1_cost_benefit_natural.py"
NATIVE_HELPER = "util/vm_tlb/c16/e1_cuda_persistence.py"
NATIVE_CPP = "util/vm_tlb/c16/e1_cuda_persistence_helper.cpp"
NATIVE_CONTRACT = f"{NATIVE_ROOT}/BUDGET_MATRIX_CONTRACT.json"
CHAR_ROOT = "docs/vm_tlb/review_packs/C16_E1_TRACE_REUSE_SET_PRESSURE_CHARACTERIZATION_174NEW_V1"
EXISTING_LITERATURE_COMMIT = "4cf2ee8294fbf761f735ae7089313a048ba0066b"
EXISTING_LITERATURE_PATH = "docs/vm_tlb/review_packs/AWMA_LITERATURE_GUIDED_MECHANISM_EXPLORATION_V1/REPORT.md"
M3_REFERENCE_PATH = "docs/vm_tlb/chatgpt_handoff/stage_specs/M3_REFERENCE_MATERIALS.md"

PRIMARY_SOURCES = [
    {
        "id": "CUDA_L2_ACCESS_POLICY_WINDOW",
        "title": "CUDA C++ Programming Guide: L2 Policy for Persisting Accesses",
        "url": "https://docs.nvidia.com/cuda/archive/12.5.1/cuda-c-programming-guide/index.html#l2-policy-for-persisting-accesses",
        "kind": "OFFICIAL_VENDOR_DOCUMENTATION",
        "verified_claim": "hitRatio selects an approximately random fraction of accesses for hitProp; persisting accesses have priority in a shared set-aside and unused capacity remains usable by normal/streaming accesses.",
    },
    {
        "id": "PTX_CREATEPOLICY_FRACTIONAL",
        "title": "Parallel Thread Execution ISA: createpolicy",
        "url": "https://docs.nvidia.com/cuda/archive/13.0.0/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-createpolicy",
        "kind": "OFFICIAL_VENDOR_ISA",
        "verified_claim": "fractional cache policy applies primary eviction priority with the specified probability and secondary priority to the remainder; it is an eviction-priority hint, not a semantic-class quota.",
    },
    {
        "id": "AUTOSCRATCH_MLSYS_2023",
        "title": "AutoScratch: ML-Optimized Cache Management for Inference-Oriented GPUs",
        "url": "https://proceedings.mlsys.org/paper_files/paper/2023/file/9d32b9324a89001520ae456b9e5ec73b-Paper-mlsys2023.pdf",
        "kind": "PRIMARY_PAPER",
        "verified_claim": "uses ML to select address slices for L2 residency/pinning in inference, with configurations kept static within an iteration; it optimizes selection rather than equal-share fairness among sequential semantic classes.",
    },
    {
        "id": "PCAL_HPCA_2015",
        "title": "Priority-Based Cache Allocation in Throughput Processors",
        "url": "https://research.nvidia.com/sites/default/files/pubs/2015-02_Priority-based-cache-allocation/li_and_rhu.hpca2015.pdf",
        "doi": "10.1109/HPCA.2015.7056024",
        "kind": "PRIMARY_PAPER",
        "verified_claim": "uses thread/warp priority tokens and non-polluting allocation, with optional priority-marked blocks; priority allocation and opportunistic borrowing are known concepts.",
    },
    {
        "id": "ORCHESTRATED_GPU_CACHE_TVLSI_2014",
        "title": "Orchestrating Cache Management and Memory Scheduling for GPGPU Applications",
        "url": "https://icas.tsinghua-sz.edu.cn/WebPublications/PaperDetail/768?unit=1002",
        "doi": "10.1109/TVLSI.2013.2278025",
        "kind": "PRIMARY_AUTHOR_INSTITUTION_PAGE_AND_PAPER",
        "verified_claim": "assigns request/cache-line priorities, permits replacement by lower or equal priority, and bypasses when no eligible victim exists; priority and bypass are known dimensions.",
    },
    {
        "id": "LOCALITY_DRIVEN_GPU_BYPASS_ICS_2015",
        "title": "Locality-Driven Dynamic GPU Cache Bypassing",
        "url": "https://research.nvidia.com/publication/2015-06_locality-driven-dynamic-gpu-cache-bypassing",
        "kind": "PRIMARY_AUTHOR_INSTITUTION_PAGE",
        "verified_claim": "filters low-reuse accesses from L1 insertion using locality monitoring; bypass admission is known but it does not provide equal semantic-class residency shares.",
    },
]


class ReviewError(RuntimeError):
    pass


def need(value: bool, message: str) -> None:
    if not value:
        raise ReviewError(message)


def git(repo: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *arguments], text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
    )
    return completed.stdout


def git_text(repo: Path, commit: str, path: str) -> str:
    return git(repo, "show", f"{commit}:{path}")


def git_json(repo: Path, commit: str, path: str):
    return json.loads(git_text(repo, commit, path))


def git_blob(repo: Path, commit: str, path: str) -> str:
    return git(repo, "rev-parse", f"{commit}:{path}").strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def native_evidence(framework: Path) -> tuple[dict, list[dict], dict]:
    contract = git_json(framework, NATIVE_HEAD, NATIVE_CONTRACT)
    need(contract["protected_family"] == "all 28 up_proj qweight regions", "native family drift")
    need(contract["selected_module_count"] == CLASS_COUNT, "native class count drift")
    need("requested_budget_bytes / (28 * exact_up_proj_qweight_bytes)" in contract["hit_ratio_formula"],
         "native hitRatio formula drift")

    policy_source = git_text(framework, NATIVE_HEAD, NATIVE_POLICY)
    helper_source = git_text(framework, NATIVE_HEAD, NATIVE_HELPER)
    cpp_source = git_text(framework, NATIVE_HEAD, NATIVE_CPP)
    for token in (
        "requested/(28*33_947_648)",
        "helper.update_access_policy",
        "expected_updates=0 if cfg['mode']=='AUTHORITY' else 140",
    ):
        need(token in policy_source, f"native policy source drift: {token}")
    for token in (
        "clear stream access-policy before condition",
        "reset persisting L2 before condition",
        "set persisting-L2 limit",
        "cudaAccessPropertyPersisting",
        "cudaAccessPropertyStreaming",
    ):
        need(token in helper_source, f"native helper source drift: {token}")
    need("cudaStreamSetAttribute" in cpp_source and "cudaDeviceSetLimit" in cpp_source,
         "native CUDA API helper drift")

    rows = []
    for name, requested in BUDGETS:
        receipt_path = f"{NATIVE_ROOT}/RAW_NATIVE_FAIR_{name}_run0.json"
        receipt = git_json(framework, NATIVE_HEAD, receipt_path)
        need(receipt["status"] == "PASS" and receipt["budget_name"] == name,
             f"native receipt identity drift {name}")
        expected_ratio = requested / (CLASS_COUNT * REGION_BYTES)
        need(math.isclose(receipt["hit_ratio"], expected_ratio, rel_tol=0, abs_tol=1e-15),
             f"native hitRatio drift {name}")
        need(receipt["policy_transition_count"] == 140, f"native transition count drift {name}")
        need(len(receipt["policy_transitions"]) == 140, f"native transition vector drift {name}")
        need(all(item["num_bytes"] == REGION_BYTES for item in receipt["policy_transitions"]),
             f"native window size drift {name}")
        need(all(item["hit_property"] == "cudaAccessPropertyPersisting" and
                 item["miss_property"] == "cudaAccessPropertyStreaming"
                 for item in receipt["policy_transitions"]),
             f"native property drift {name}")
        policy_receipt = receipt["policy_receipt"]
        need(policy_receipt["requested_setaside_bytes"] == requested,
             f"native requested setaside drift {name}")
        need(policy_receipt["actual_setaside_after_reset_bytes"] == 0,
             f"native reset closure drift {name}")
        rows.append({
            "budget": name,
            "requested_setaside_bytes": requested,
            "actual_setaside_bytes": int(policy_receipt["actual_setaside_bytes"]),
            "requested_lines_128b": requested // LINE_BYTES,
            "actual_setaside_lines_128b": int(policy_receipt["actual_setaside_bytes"]) // LINE_BYTES,
            "hit_ratio": receipt["hit_ratio"],
            "full_region_window_bytes_each_update": REGION_BYTES,
            "policy_update_count": 140,
            "phase_order": ["PREFILL", "D0", "D1", "D2", "D3"],
            "layer_order_each_phase": list(range(CLASS_COUNT)),
            "first_update": receipt["policy_transitions"][0]["label"],
            "last_update": receipt["policy_transitions"][-1]["label"],
            "expected_persisting_opportunity_lines_per_region_per_full_stream":
                receipt["hit_ratio"] * REGION_LINES,
            "actual_setaside_matches_request": int(policy_receipt["actual_setaside_bytes"]) == requested,
            "receipt_git_path": receipt_path,
            "receipt_blob": git_blob(framework, NATIVE_HEAD, receipt_path),
        })
    source = {
        "framework_commit": NATIVE_HEAD,
        "contract_path": NATIVE_CONTRACT,
        "contract_blob": git_blob(framework, NATIVE_HEAD, NATIVE_CONTRACT),
        "policy_path": NATIVE_POLICY,
        "policy_blob": git_blob(framework, NATIVE_HEAD, NATIVE_POLICY),
        "helper_path": NATIVE_HELPER,
        "helper_blob": git_blob(framework, NATIVE_HEAD, NATIVE_HELPER),
        "helper_cpp_path": NATIVE_CPP,
        "helper_cpp_blob": git_blob(framework, NATIVE_HEAD, NATIVE_CPP),
    }
    return contract, rows, source


def m1_evidence(core: Path, lane4_core: Path) -> dict:
    need(git(core, "rev-parse", CORE_HEAD).strip() == CORE_HEAD, "M1 Core commit absent")
    need(git(lane4_core, "rev-parse", LANE4_CORE_HEAD).strip() == LANE4_CORE_HEAD,
         "Lane4 Core commit absent")
    cc_path = "src/gpgpu-sim/oracle_elastic_residency.cc"
    hh_path = "src/gpgpu-sim/oracle_elastic_residency.h"
    cache_path = "src/gpgpu-sim/gpu-cache.cc"
    cc = git_text(core, CORE_HEAD, cc_path)
    hh = git_text(core, CORE_HEAD, hh_path)
    cache = git_text(core, CORE_HEAD, cache_path)
    lane4_cache = git_text(lane4_core, LANE4_CORE_HEAD, cache_path)
    need("uint64_t quotient = m_global_lines / l2_instances" in cc, "M1 quotient drift")
    need("uint64_t remainder = m_global_lines % l2_instances" in cc, "M1 remainder drift")
    need("unsigned target_class;" in hh, "M1 interval class metadata absent")
    candidate = hh[hh.index("struct candidate"):hh.index("enum selection_status")]
    need("target_class" not in candidate, "M1 candidate unexpectedly class-aware")
    chooser = cc[cc.index("selection choose_victim"):cc.index("admission decide_fill_admission")]
    need("target_class" not in chooser, "M1 victim chooser unexpectedly class-aware")
    need("choose_oldest(protected_rows, policy)" in chooser, "M1 protected recency drift")
    need("QUOTA_FULL_NO_LOCAL_PROTECTED_VICTIM" in chooser, "M1 denial drift")
    need("oracle_set_pending(protect_fill, oracle_target_class)" in cache,
         "M1 target class line metadata drift")
    lane4_diff = git(lane4_core, "diff", "--name-status", CORE_HEAD, LANE4_CORE_HEAD)
    need("oracle_elastic_residency.cc" not in lane4_diff and
         "oracle_elastic_residency.h" not in lane4_diff,
         "Lane4 modified policy authority unexpectedly")
    policy_snippets = (
        "oracle_elastic_residency::choose_victim(\n          eligible, target,",
        "oracle_elastic_residency::decide_fill_admission(\n                oracle_target,",
        "candidate.protected_line = line->oracle_protected();",
    )
    for snippet in policy_snippets:
        need(snippet in cache and snippet in lane4_cache,
             "Lane4 cache policy callsite semantic drift")
    need("oracle_elastic_l2_class_occupancy" in lane4_cache,
         "Lane4 class-occupancy telemetry absent")
    return {
        "core_commit": CORE_HEAD,
        "lane4_execution_core": LANE4_CORE_HEAD,
        "lane4_oracle_policy_module_unchanged_from_scientific_core": True,
        "lane4_cache_policy_callsite_semantics_match": True,
        "lane4_delta_interpretation": "gpu-cache/gpu-sim changes add or repair diagnostics and occupancy accounting; class identity still does not enter candidate construction, choose_victim, or decide_fill_admission",
        "lane4_diff_name_status": lane4_diff.strip().splitlines(),
        "source_blobs": {
            cc_path: git_blob(core, CORE_HEAD, cc_path),
            hh_path: git_blob(core, CORE_HEAD, hh_path),
            cache_path: git_blob(core, CORE_HEAD, cache_path),
            "src/gpgpu-sim/gpu-cache.h": git_blob(core, CORE_HEAD, "src/gpgpu-sim/gpu-cache.h"),
        },
        "source_anchors": {
            "quota_distribution": f"{cc_path}:250-289",
            "interval_lookup_and_class_decode": f"{cc_path}:292-343",
            "victim_rule": f"{cc_path}:345-408",
            "admission_denials": f"{cc_path}:410-431",
            "eligible_global_read_only": f"{cc_path}:434-437",
            "set_local_probe_and_candidate_build": f"{cache_path}:464-529",
            "class_metadata_and_fill": f"{cache_path}:547-643",
        },
    }


def budget_semantics(native_rows: list[dict]) -> list[dict]:
    by_name = {row["budget"]: row for row in native_rows}
    rows = []
    for name, requested_bytes in BUDGETS:
        lines = requested_bytes // LINE_BYTES
        quotient, remainder = divmod(lines, SUBPARTITIONS)
        one_class = min(lines, REGION_LINES)
        row = {
            "budget": name,
            "requested_bytes": requested_bytes,
            "requested_lines_128b": lines,
            "m1_per_subpartition_quotient_lines": quotient,
            "m1_per_subpartition_remainder_lines": remainder,
            "m1_one_class_max_protected_lines_target_only": one_class,
            "m1_one_class_max_fraction_of_global_quota": one_class / lines,
            "m1_one_class_qweight_fraction": one_class / REGION_LINES,
            "conditional_full_stream_pool_turns": REGION_LINES / lines,
            "conditional_L1_through_L27_pool_turns": (CLASS_COUNT - 1) * REGION_LINES / lines,
            "native_requested_setaside_bytes": by_name[name]["requested_setaside_bytes"],
            "native_actual_setaside_bytes": by_name[name]["actual_setaside_bytes"],
            "native_hit_ratio": by_name[name]["hit_ratio"],
            "native_expected_persisting_opportunity_lines_per_region":
                by_name[name]["expected_persisting_opportunity_lines_per_region_per_full_stream"],
            "native_expected_all_28_opportunity_lines":
                by_name[name]["expected_persisting_opportunity_lines_per_region_per_full_stream"] * CLASS_COUNT,
        }
        need(math.isclose(row["native_expected_all_28_opportunity_lines"], lines,
                          rel_tol=0, abs_tol=1e-8), f"native opportunity closure {name}")
        rows.append(row)
    return rows


def native_vs_m1(contract: dict, native_rows: list[dict], native_source: dict,
                 m1: dict, budget_rows: list[dict]) -> dict:
    return {
        "schema": "C16_E1_NATIVE_VS_M1_RESIDENCY_SEMANTICS_V1",
        "status": "PASS",
        "claim_boundary": "VERIFIED_CODE_AND_NATIVE_RECEIPT_SEMANTICS_NOT_ACTUAL_L2_RESIDENCY",
        "native_cuda": {
            "source": native_source,
            "contract": contract,
            "budgets": native_rows,
            "per_region_semantics": {
                "window": "one exact full 33,947,648-byte up_proj.qweight region",
                "updates": "the same stream access-policy window is overwritten immediately before every up_proj invocation",
                "hit_property": "cudaAccessPropertyPersisting",
                "miss_property": "cudaAccessPropertyStreaming",
                "distribution": "each of the 28 regions receives the same approximate per-access probability hitRatio; CUDA does not promise an exact per-region quota, exact cardinality, or survival floor",
                "reset": "stream policy, persisting L2 state, and set-aside are cleared only at condition boundaries",
            },
        },
        "current_m1": {
            "source": m1,
            "global_quota": "one global protected-line budget, divided quotient/remainder over 16 subpartitions",
            "per_target_class_quota": None,
            "protected_protected_rule": "oldest protected eligible victim in the addressed set under baseline LRU/FIFO recency",
            "target_class_metadata": "decoded from the sidecar and stored on protected/pending lines; Lane4 can report occupancy by class",
            "target_class_use_in_victim_choice": False,
            "admission_denials": [
                "QUOTA_FULL_BASELINE_INVALID_PRIORITY",
                "QUOTA_FULL_NO_LOCAL_PROTECTED_VICTIM",
            ],
            "ordinary_borrowing": "ordinary fills may use unused protected capacity and fall back to protected victims if a set has no normal victim",
        },
        "budget_comparison": budget_rows,
        "semantic_conclusion": "Native CUDA configures equal fractional opportunity at every class occurrence; M1 instead makes every target eligible for one shared recency pool. Neither CUDA nor this review proves exact fair occupancy, but the two admission semantics are structurally different.",
    }


def churn_analysis(budget_rows: list[dict]) -> dict:
    return {
        "schema": "C16_E1_TARGET_TARGET_CHURN_ANALYSIS_V1",
        "status": "PASS",
        "claim_boundary": "STRUCTURAL_CURRENT_POLICY_ANALYSIS_NOT_OBSERVED_L2_EVICTION",
        "frozen_facts": {
            "target_classes": CLASS_COUNT,
            "lines_per_class": REGION_LINES,
            "all_classes_lines": FAMILY_LINES,
            "all_classes_cover_all_subpartition_sets": True,
            "next_reuse_touches_all_class_lines": True,
            "later_classes_between_L0_reuses": CLASS_COUNT - 1,
            "later_class_lines_between_L0_reuses": (CLASS_COUNT - 1) * REGION_LINES,
            "minimum_lines_per_class_per_set": 8,
            "maximum_lines_per_class_per_set": 9,
        },
        "budgets": budget_rows,
        "exact_structural_statements": [
            "Before quota saturation, every eligible target miss may become protected regardless of class.",
            "At quota saturation, every newly protected target fill necessarily removes a protected victim in the same set.",
            "Victim selection has no class identity, class occupancy, minimum share, or age-by-class input.",
            "The guaranteed minimum surviving lines for any older class is zero under the current policy.",
            "A full first class stream can occupy the entire requested protected quota in the target-only case (or all class lines for BFULL).",
            "No current mechanism preserves proportional representation of older classes.",
        ],
        "ideal_target_only_all_miss_proof": {
            "assumptions": "Only target qweight streams are present; every unique qweight line reaches L2 as a miss/fill; baseline recency is not refreshed by skipped or filtered L0 accesses.",
            "after_L0": "Each set has at most 9 protected L0 lines.",
            "after_L1": "L0 and L1 contribute at least 8+8 lines per set, so every 16-way set is full; excess L1 fills may already replace protected L0 lines.",
            "after_L2": "With no invalid way and full quota, each set receives at least 8 L2 target fills; protected victims are preferred, so at most one of the original at-most-9 L0 protected lines can remain.",
            "after_L3": "At least 8 more target fills per set eliminate any remaining original L0 protected line.",
            "latest_layer_with_zero_original_L0_protected_lines": 3,
        },
        "conditional_turnover_interpretation": "Pool-turn counts assume later target lines reach L2 as target misses and find local protected victims. They quantify possible/conditional protected-protected turnover, not observed eviction.",
        "L0_survival_conclusion": "Under the stated ideal target-only all-miss assumptions, original L0 protected lines are eliminated by the end of L3. Survival through L1-L27 therefore requires filtering/hits/skipped accesses, admission denial, or another effect not supplied by target-class fairness in M1.",
    }


def design_space(budget_rows: list[dict]) -> dict:
    hit_ratios = {row["budget"]: row["native_hit_ratio"] for row in budget_rows}
    designs = [
        {
            "id": "M1",
            "name": "GLOBAL_ELASTIC_RECENCY",
            "metadata": "protected/pending bit, target_class tag, global/per-subpartition occupancy and quota",
            "admission": "all target global-read misses are eligible; protect below quota; at full quota protect only when replacing a local protected victim",
            "victim": "invalid/normal/protected preference with baseline oldest protected victim; class ignored",
            "borrowing": "ordinary lines borrow unused quota and may fall back to protected victims",
            "quota": "hard global bound distributed over subpartitions; no class share",
            "fairness": "none; a recent class can occupy the whole pool",
            "ordinary_behavior": "elastic borrowing retained",
            "complexity": "current baseline",
            "cuda_relation": "does not model hitRatio fractional admission",
            "new_dimension": False,
        },
        {
            "id": "M1F",
            "name": "GLOBAL_ELASTIC_FRACTIONAL_ADMISSION",
            "metadata": "existing target_class and line address plus one stable hash seed/threshold; no 28 occupancy counters",
            "admission": "a target line is protection-eligible only when stable_hash(class,line) is below the budget-specific fraction; failed/ineligible admission is ordinary and never stalls",
            "victim": "unchanged M1 set-local victim rule",
            "borrowing": "unchanged ordinary borrowing and hard global bound",
            "quota": "global elastic quota; each class has an approximately equal, stable eligible subset of expected size global_quota/28",
            "fairness": "statistical/stable opportunity fairness; limits one class injection but does not guarantee an exact occupancy floor",
            "ordinary_behavior": "unchanged",
            "complexity": "low: one hash/threshold decision on target admission",
            "cuda_relation": "direct modeling analogue of CUDA/PTX fractional eviction-priority assignment, but deterministic stability is an explicit simulator modeling decision",
            "new_dimension": "fractional target admission versus M1 all-target admission",
            "budget_fractions": hit_ratios,
        },
        {
            "id": "M1Q",
            "name": "ELASTIC_PER_CLASS_SOFT_QUOTA",
            "metadata": "existing per-line class plus 28 protected-occupancy counters per subpartition and soft-share accounting",
            "admission": "under-share classes may protect; over-share classes borrow only unused global capacity; at full quota protect only with a safe same-set victim",
            "victim": "prefer same-class or over-share protected victims; never evict an under-share class solely to admit an over-share class; otherwise fail safe unprotected",
            "borrowing": "ordinary borrowing retained; target-class excess borrowing is reclaimable",
            "quota": "hard global bound plus soft per-class shares, no static way partition",
            "fairness": "stronger proportional protection than M1F but still constrained by set-local victim availability",
            "ordinary_behavior": "current ordinary preference/fallback can be retained",
            "complexity": "moderate: counters, share comparison, class-aware victim filtering",
            "cuda_relation": "not an exposed CUDA guarantee; stronger than hitRatio and PTX fractional priority",
            "new_dimension": "class-aware occupancy/admission/replacement",
        },
        {
            "id": "OPTIONAL_NEXT_REUSE",
            "name": "NEXT_REUSE_AWARE_CLASS_SELECTION",
            "metadata": "per-class predicted/known next-reuse distance and selector state",
            "admission": "protect classes chosen by next-reuse utility",
            "victim": "prefer classes with later predicted reuse",
            "borrowing": "can retain elastic global borrowing",
            "quota": "global or soft-class bound",
            "fairness": "not fairness; utility prioritization may intentionally be unequal",
            "ordinary_behavior": "requires an additional policy contract",
            "complexity": "high and potentially oracle/future-aware",
            "cuda_relation": "not equivalent to hitRatio",
            "new_dimension": "future/utility prediction",
        },
    ]
    return {
        "schema": "C16_E1_FAIR_RESIDENCY_DESIGN_SPACE_V1",
        "status": "PASS",
        "constraints": [
            "ordinary borrowing",
            "no static partition",
            "hard global occupancy bound",
            "set-local replacement",
            "no stalls or cross-set victim",
            "fail-safe unprotected admission",
        ],
        "designs": designs,
        "minimum_recommendation": "M1F",
        "escalation_if_hard_representation_is_required": "M1Q",
        "do_not_start": "OPTIONAL_NEXT_REUSE",
    }


def related_work(framework: Path) -> dict:
    existing_report = git_text(framework, EXISTING_LITERATURE_COMMIT, EXISTING_LITERATURE_PATH)
    m3_reference = git_text(framework, FRAMEWORK_HEAD, M3_REFERENCE_PATH)
    need("bounded primary-source check" in existing_report and
         "Current GPGPU-Sim components" in m3_reference,
         "existing related-work note authority drift")
    rows = [
        {
            "source_id": "CUDA_L2_ACCESS_POLICY_WINDOW",
            "known_element": "shared persisting set-aside, unused-capacity borrowing, per-access fractional persisting/streaming property",
            "collision": "M1F fractional admission is not novel as a broad concept",
            "not_provided": "semantic target-class occupancy quota, survival floor, or class-aware victim selection",
        },
        {
            "source_id": "PTX_CREATEPOLICY_FRACTIONAL",
            "known_element": "fractional evict_last/secondary eviction priority probability",
            "collision": "fractional priority assignment is ISA-supported prior art",
            "not_provided": "global occupancy accounting or fairness across 28 sequential semantic objects",
        },
        {
            "source_id": "AUTOSCRATCH_MLSYS_2023",
            "known_element": "learned selection and pinning of address slices under L2 residency capacity",
            "collision": "object/slice selection for inference residency is established",
            "not_provided": "online equal-opportunity turnover control among all qweight classes with no training/search",
        },
        {
            "source_id": "PCAL_HPCA_2015",
            "known_element": "priority-marked cache blocks, non-polluting threads, and optional opportunistic allocation",
            "collision": "priority protection and borrowing/nonpollution are established",
            "not_provided": "semantic-object fractional fairness in a global protected pool",
        },
        {
            "source_id": "ORCHESTRATED_GPU_CACHE_TVLSI_2014",
            "known_element": "multi-level request/line priority and bypass when no lower/equal-priority victim exists",
            "collision": "priority-aware replacement and fail-safe bypass are established",
            "not_provided": "equal-share target classes or CUDA-hitRatio-aligned admission",
        },
        {
            "source_id": "LOCALITY_DRIVEN_GPU_BYPASS_ICS_2015",
            "known_element": "reuse/locality-based insertion filtering and bypass",
            "collision": "admission filtering is established",
            "not_provided": "fairness between equally designated target classes at L2",
        },
    ]
    return {
        "schema": "C16_E1_RELATED_WORK_COLLISION_MATRIX_V1",
        "status": "PASS",
        "scope": "BOUNDED_COLLISION_CHECK_NOT_EXHAUSTIVE_PRIOR_ART_OR_NOVELTY_REVIEW",
        "existing_repository_notes_reviewed": [
            {
                "commit": EXISTING_LITERATURE_COMMIT,
                "path": EXISTING_LITERATURE_PATH,
                "blob": git_blob(framework, EXISTING_LITERATURE_COMMIT, EXISTING_LITERATURE_PATH),
                "relevance": "existing bounded VM/TLB mechanism literature method and claim-boundary precedent; it does not cover target-class L2 residency fairness",
            },
            {
                "commit": FRAMEWORK_HEAD,
                "path": M3_REFERENCE_PATH,
                "blob": git_blob(framework, FRAMEWORK_HEAD, M3_REFERENCE_PATH),
                "relevance": "existing project reference-material and evidence-label discipline; no target-class cache-residency design",
            },
        ],
        "sources": PRIMARY_SOURCES,
        "rows": rows,
        "known_elements": [
            "fractional eviction-priority assignment",
            "persisting versus streaming priority",
            "address-slice residency/pinning",
            "priority-aware replacement",
            "cache admission filtering and bypass",
            "opportunistic use of otherwise unused cache capacity",
        ],
        "problem_specific_combination_not_established_by_checked_sources": "stable equal fractional opportunity across 28 sequential full-set qweight classes while preserving a hard global bound, ordinary borrowing, set-local no-stall replacement, and explicit old-class survival telemetry",
        "novelty_claim": False,
    }


def lane4_contract() -> dict:
    return {
        "schema": "C16_E1_LANE4_INTERPRETATION_CONTRACT_V1",
        "status": "PREREGISTERED_BEFORE_LANE4_COMPLETION",
        "lane4_core": LANE4_CORE_HEAD,
        "partial_data_used": False,
        "required_counters": [
            "protected_protected_replacements",
            "per-class protected occupancy and L0 survival",
            "target accesses/hits/misses/protected fills/hits",
            "target_protection_admission_denied",
            "denial_quota_full_invalid_priority",
            "denial_quota_full_no_local_protected",
            "normal_fallback_protected_victims",
            "timing result bound to completed run identity",
        ],
        "branches": [
            {
                "id": 1,
                "observation": "high protected-to-protected churn and low old-class survival",
                "interpretation": "supports target-class fairness as a realized M1 limitation",
                "next_check": "M1F first; use M1Q only if hard representation is required",
            },
            {
                "id": 2,
                "observation": "low churn, good L0 survival, and no timing gain",
                "interpretation": "fairness is not the explanation for absent gain",
                "next_check": "critical-path coverage, reuse value, and collateral costs",
            },
            {
                "id": 3,
                "observation": "high L0 survival and positive local timing",
                "interpretation": "current M1 may already be sufficient; do not add fairness complexity",
                "next_check": "whole-decode collateral and repeatability",
            },
            {
                "id": 4,
                "observation": "target protection is low because admission denial dominates",
                "interpretation": "admission realization precedes fairness",
                "next_check": "separate invalid-priority and no-local-protected-victim denial before changing class policy",
            },
        ],
    }


def recommendation() -> dict:
    return {
        "schema": "C16_E1_TARGET_CLASS_FAIR_RESIDENCY_RECOMMENDATION_V1",
        "status": "PASS",
        "final_label": FINAL_LABEL,
        "recommended_next_mechanism": "M1F_GLOBAL_ELASTIC_FRACTIONAL_ADMISSION",
        "why": [
            "M1 victim/admission decisions are provably class-blind even though class metadata exists.",
            "One target class can occupy the entire protected quota in the target-only case.",
            "All 27 later target classes share every set and collectively present 7,160,832 additional target lines before L0 reuse.",
            "Native CUDA applies the same small fractional hitRatio opportunity to every region occurrence rather than making all lines immediately protection-eligible.",
            "M1F is the smallest design that restores that admission dimension without partitions, stalls, cross-set victims, or loss of ordinary borrowing.",
        ],
        "qualification": "The structural mechanism dimension is justified; its performance relevance is not established until the preregistered completed Lane4 counters are reviewed.",
        "m1q_status": "contingency if M1F does not provide adequate old-class representation or if Lane4 establishes a need for a hard soft-share floor",
        "implementation_authorized": False,
        "timing_authorized": False,
    }


def markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |",
             "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def write_markdown(output: Path, semantics: dict, churn: dict, designs: dict,
                   related: dict, lane4: dict, rec: dict) -> None:
    budget_rows = semantics["budget_comparison"]
    native_table = markdown_table(
        ["Budget", "Requested B", "Actual CUDA B", "hitRatio", "M1 lines/SP", "M1 one-class max", "27-later conditional turns"],
        [[row["budget"], row["requested_bytes"], row["native_actual_setaside_bytes"],
          f'{row["native_hit_ratio"]:.12f}', row["m1_per_subpartition_quotient_lines"],
          row["m1_one_class_max_protected_lines_target_only"],
          f'{row["conditional_L1_through_L27_pool_turns"]:.6f}'] for row in budget_rows],
    )
    (output / "NATIVE_VS_M1_RESIDENCY_SEMANTICS.md").write_text(f"""# Native CUDA versus current M1 residency semantics

Claim boundary: verified code and frozen native receipts; not actual L2 residency.

{native_table}

Native CUDA overwrites one stream access-policy window immediately before each of 28 `up_proj` invocations in `PREFILL`, `D0`, `D1`, `D2`, and `D3` (140 updates). Each window covers the complete 33,947,648-byte qweight and uses the same budget-derived `hitRatio`, `Persisting` hit property, and `Streaming` miss property. Official CUDA documentation describes approximately random per-access classification, so this proves equal configured opportunity, not exact equal occupancy or survival.

M1 divides one exact protected-line quota over 16 subpartitions. It has no class quota. At full quota, a target can remain protected only by replacing a protected victim in the same set; the oldest protected candidate under baseline recency wins. Class identity is stored for metadata/telemetry but does not enter victim selection.
""", encoding="utf-8")

    (output / "TARGET_TARGET_CHURN_ANALYSIS.md").write_text(f"""# Structural target-target churn analysis

Claim boundary: structural current-policy analysis, not observed eviction.

After one full target-only qweight stream, one class can occupy 100% of B8/B16/B24 protected quota and all BFULL capacity. Every later qweight covers every target set. Conditional on later target references reaching L2 as misses and finding local protected victims, one full later stream turns the pool {budget_rows[0]['conditional_full_stream_pool_turns']:.6f}× at B8, {budget_rows[1]['conditional_full_stream_pool_turns']:.6f}× at B16, {budget_rows[2]['conditional_full_stream_pool_turns']:.6f}× at B24, and 1× at BFULL.

Across L1-L27 before L0 reuse, the corresponding conditional turnovers are {budget_rows[0]['conditional_L1_through_L27_pool_turns']:.6f}×, {budget_rows[1]['conditional_L1_through_L27_pool_turns']:.6f}×, {budget_rows[2]['conditional_L1_through_L27_pool_turns']:.6f}×, and 27×. M1 provides no proportional-representation floor; the guaranteed old-class survival lower bound is zero. L0 survival therefore depends on filtering, hits, skipped accesses, denial, or another effect—not a fairness property of M1.

The ideal all-miss proof is stronger. L0 contributes at most 9 protected lines to any set. After L1, every set is full because both classes contribute at least 8 lines. L2 then supplies at least 8 target fills per set and M1 prefers protected victims at full quota, leaving at most one original L0 line per set. L3 supplies at least 8 more fills and removes that remainder. Thus original L0 protection is zero by the end of L3 under the stated assumptions; this is a structural proof, not a Lane4 observed-eviction result.
""", encoding="utf-8")

    design_rows = []
    for item in designs["designs"]:
        design_rows.append([item["id"], item["name"], item["fairness"], item["complexity"], item["new_dimension"]])
    (output / "FAIR_RESIDENCY_DESIGN_SPACE.md").write_text("""# Fair-residency design space

""" + markdown_table(["ID", "Design", "Fairness", "Complexity", "New dimension"], design_rows) + """

Recommendation: implement nothing in this Goal. If Lane4 supports realized class churn after admission is healthy, evaluate M1F first. M1F uses a stable class/address hash and the frozen budget fraction to select the protection-eligible subset; all non-selected/failed fills remain ordinary. M1Q is the escalation path when a hard soft-share floor is required. Future-aware selection is intentionally deferred.
""", encoding="utf-8")

    related_rows = [[row["source_id"], row["known_element"], row["collision"], row["not_provided"]]
                    for row in related["rows"]]
    source_lines = "\n".join(f'- [{item["title"]}]({item["url"]})' for item in related["sources"])
    (output / "RELATED_WORK_COLLISION_MATRIX.md").write_text("""# Related-work collision matrix

This is a bounded collision check, not an exhaustive prior-art or novelty review.

""" + markdown_table(["Source", "Known element", "Collision", "Not provided"], related_rows) +
        "\n\n## Primary sources\n\n" + source_lines +
        "\n\nNo novelty claim is made. The checked sources establish the component ideas; they do not establish the exact 28-class problem-specific combination reviewed here.\n",
        encoding="utf-8")

    lane_rows = [[row["id"], row["observation"], row["interpretation"], row["next_check"]]
                 for row in lane4["branches"]]
    (output / "LANE4_INTERPRETATION_CONTRACT.md").write_text("""# Lane 4 interpretation contract

Preregistered without Lane4 partial data.

""" + markdown_table(["Case", "Completed observation", "Interpretation", "Next check"], lane_rows) +
        "\n\nNo partial progress value may be substituted for a completed, provenance-bound observation.\n",
        encoding="utf-8")

    (output / "RECOMMENDATION.md").write_text(f"""# Recommendation

Final label: `{rec['final_label']}`.

Recommended next mechanism, contingent on completed Lane4 interpretation: `M1F_GLOBAL_ELASTIC_FRACTIONAL_ADMISSION`.

The label means that a target-class fairness mechanism dimension is structurally justified for study. It does not mean that fairness has already caused Lane4 timing behavior, that M1F will improve performance, or that M1Q should be implemented now. No candidate implementation or timing run is authorized by this review.
""", encoding="utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--framework-repo", type=Path, required=True)
    parser.add_argument("--core-repo", type=Path, required=True)
    parser.add_argument("--lane4-core-repo", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    need(not args.output_dir.exists(), "output directory must be fresh")
    need(git(args.framework_repo, "cat-file", "-t", FRAMEWORK_HEAD).strip() == "commit",
         "frozen Framework commit absent")
    need(git(args.framework_repo, "cat-file", "-t", NATIVE_HEAD).strip() == "commit",
         "native producer commit absent")

    contract, native_rows, native_source = native_evidence(args.framework_repo)
    m1 = m1_evidence(args.core_repo, args.lane4_core_repo)
    budgets = budget_semantics(native_rows)
    semantics = native_vs_m1(contract, native_rows, native_source, m1, budgets)
    churn = churn_analysis(budgets)
    designs = design_space(budgets)
    related = related_work(args.framework_repo)
    lane4 = lane4_contract()
    rec = recommendation()

    args.output_dir.mkdir(parents=True)
    documents = {
        "NATIVE_VS_M1_RESIDENCY_SEMANTICS.json": semantics,
        "TARGET_TARGET_CHURN_ANALYSIS.json": churn,
        "FAIR_RESIDENCY_DESIGN_SPACE.json": designs,
        "RELATED_WORK_COLLISION_MATRIX.json": related,
        "LANE4_INTERPRETATION_CONTRACT.json": lane4,
        "RECOMMENDATION.json": rec,
    }
    for name, value in documents.items():
        dump(args.output_dir / name, value)
    write_markdown(args.output_dir, semantics, churn, designs, related, lane4, rec)

    dump(args.output_dir / "SOURCE_ANCHORS.json", {
        "schema": "C16_E1_TARGET_CLASS_FAIR_RESIDENCY_SOURCE_ANCHORS_V1",
        "status": "PASS",
        "goal": GOAL,
        "framework_start": FRAMEWORK_HEAD,
        "native_producer": NATIVE_HEAD,
        "core_scientific_implementation": CORE_HEAD,
        "lane4_execution_core": LANE4_CORE_HEAD,
        "trace_manifest_sha256": MANIFEST_SHA,
        "oracle_sidecar_sha256": SIDECAR_SHA,
        "characterization_label": "C16_E1_TRACE_REUSE_SET_PRESSURE_CHARACTERIZED_V1",
        "characterization_pack": CHAR_ROOT,
        "native_source": native_source,
        "m1_source": m1,
        "primary_sources": PRIMARY_SOURCES,
        "lane4_partial_data_used": False,
    })
    (args.output_dir / "CLAIM_BOUNDARY.md").write_text("""# Claim boundary

- `VERIFIED_CODE`: frozen source and native receipt semantics.
- `STRUCTURAL_POLICY_ANALYSIS`: consequences of the implemented rules under explicitly stated target-only/full-miss conditions.
- `DESIGN_RECOMMENDATION`: unimplemented candidate for later review.
- No Lane4 partial data, actual L2 eviction/residency, timing result, speedup, hardware mapping probability, or novelty claim is made.
- CUDA `hitRatio` proves approximate probabilistic access-property assignment, not exact per-class occupancy or survival.
- Conditional pool-turn values are not observed replacement counters.
""", encoding="utf-8")
    dump(args.output_dir / "VALIDATION_SUMMARY.json", {
        "schema": "C16_E1_TARGET_CLASS_FAIR_RESIDENCY_VALIDATION_V1",
        "status": "PASS",
        "checks": {
            "native_four_budget_receipts": "PASS",
            "native_140_equal_window_updates": "PASS",
            "m1_class_blind_candidate_and_victim": "PASS",
            "lane4_policy_files_unchanged": "PASS",
            "budget_line_and_turnover_closure": "PASS",
            "lane4_partial_data_excluded": "PASS",
            "primary_source_collision_boundary": "PASS",
            "no_mechanism_or_timing_execution": "PASS",
        },
        "final_label": FINAL_LABEL,
    })
    (args.output_dir / "README.md").write_text(f"""# C16 E1 target-class fair residency design review

Status: `{FINAL_LABEL}`

Goal: `{GOAL}`

This review establishes a structural target-target fairness gap in current M1 and recommends M1F as the minimum next design, contingent on the preregistered completed Lane4 interpretation. It does not implement M1F/M1Q, read Lane4 partial results, or launch timing.

Review order:

1. `SOURCE_ANCHORS.json`
2. `CLAIM_BOUNDARY.md`
3. `NATIVE_VS_M1_RESIDENCY_SEMANTICS.md` / `.json`
4. `TARGET_TARGET_CHURN_ANALYSIS.md` / `.json`
5. `FAIR_RESIDENCY_DESIGN_SPACE.md` / `.json`
6. `RELATED_WORK_COLLISION_MATRIX.md` / `.json`
7. `LANE4_INTERPRETATION_CONTRACT.md` / `.json`
8. `RECOMMENDATION.md` / `.json`
9. `VALIDATION_SUMMARY.json` and `SHA256SUMS`
""", encoding="utf-8")

    names = sorted(path.name for path in args.output_dir.iterdir()
                   if path.is_file() and path.name != "SHA256SUMS")
    with (args.output_dir / "SHA256SUMS").open("w", encoding="utf-8") as stream:
        for name in names:
            stream.write(f"{sha256(args.output_dir / name)}  {name}\n")
    print(json.dumps({"status": "PASS", "final_label": FINAL_LABEL,
                      "output_dir": str(args.output_dir), "files": len(names) + 1},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
