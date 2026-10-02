#!/usr/bin/env python3
"""CPU-only R22F scientific report; never runs CUDA or new measurement."""

import csv
import hashlib
import json
import statistics
from pathlib import Path

ROOT = Path("/data/c16/awma/r22f_r21a_family_localization_20261002")
RAW = ROOT / "raw"
PARENT = Path("/data/c16/awma/r21a_oeq_graph_readiness_20261002")
PACK = Path("/home/huangrulin/workspace/worktrees/accel-sim-awma-r22f-r21a-family-localization-109-v1/docs/vm_tlb/review_packs/AWMA_R22F_R21A_FAMILY_LOCALIZATION_109_V1")
FINAL_LABEL = "R22F_R21A_FAMILY_RESULT_MIXED"


def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda:stream.read(8<<20),b""):
            h.update(block)
    return h.hexdigest()


def jwrite(name,value):
    (PACK/name).write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")


def metric(prof,base,cand,name):
    matches=[r for r in prof["responses"] if r["baseline"]==base and r["candidate"]==cand and r["metric"]==name]
    if len(matches)!=1: raise RuntimeError(f"Metric missing {base} {cand} {name}")
    return matches[0]


def complete(form,base,cand,timer):
    matches=[r for r in form["responses"] if r["baseline"]==base and r["candidate"]==cand and r["timer"]==timer]
    if len(matches)!=1: raise RuntimeError(f"Complete timing missing {base} {cand} {timer}")
    return matches[0]


def main():
    prof=json.loads((PACK/"PROFILE_RECEIPT.json").read_text())
    formal=json.loads((PACK/"COMPLETE_RESPONSE_SUMMARY.json").read_text())
    aorder=json.loads((RAW/"AORDER_QUALIFICATION_STATUS.json").read_text())
    parent_graph=json.loads((PARENT/"raw/DISCOVERY_GRAPH_AUTHORITY.json").read_text())
    parent_model=json.loads((PARENT/"raw/RUNTIME_ADMISSION.json").read_text())
    parent_timing=json.loads((PARENT/"raw/DREADY_TIMING_STATUS.json").read_text())
    current_profile=json.loads((RAW/"PROFILE_RUN_STATUS.json").read_text())
    current_formal=json.loads((RAW/"FORMAL_RUN_STATUS.json").read_text())
    if prof["status"]!="FAMILY_ATTRIBUTION_QUALIFIED" or formal["status"]!="FORMAL_COMPLETE_72_NUMERIC_PASS":
        raise RuntimeError("Main evidence incomplete")
    if aorder["status"]!="AORDER_QUALIFIED" or aorder["repeat_count"]!=5 or not all(r["numerical_pass"] for r in aorder["rows"]):
        raise RuntimeError("Aorder not qualified")
    if current_profile["measured_count"]!=36 or current_formal["formal_count"]!=72:
        raise RuntimeError("R22F sample count changed")
    if parent_timing["classification_if_stop"]!="R21A_RESULT_MIXED_NEEDS_REVIEW":
        raise RuntimeError("R21A history changed")
    if any(RAW.glob("DONLINE*")) or any(RAW.glob("HOLDOUT*")):
        raise RuntimeError("Forbidden downstream run exists")
    parent={"stage":"AWMA_R22F_R21A_FAMILY_LOCALIZATION_109_V1",
            "starting_commit":"c4feee715bdb659d6549fc1f1af229b3604a93a0",
            "starting_tree":"c060bf90a0492ce9cf8ecb367cd7bd770a9fc041",
            "scientific_parent":"62af34149d45e9862d5a1e255e2a51ca88a3c4c7",
            "parent_frozen_label":"R21A_RESULT_MIXED_NEEDS_REVIEW",
            "model_id":"nequip.net:mir-group/NequIP-OAM-S:0.1",
            "model_package_sha256":sha(PARENT/"model/NequIP-OAM-S-0.1.nequip.zip"),
            "input_repo_commit":"8f90935ba42fd9e03df323cf03428c456d87b881",
            "input_blob":"baac4e23364d00d29b2410fa60a92ade0cbf35a3",
            "input_sha256":sha(PARENT/"source/nequip-tutorial/sitraj.xyz"),
            "frame_index":55,"atom_count":64,"directed_edge_count":1394,
            "natural_graph_sha256":sha(PARENT/"raw/DISCOVERY_NATURAL_GRAPH.npz"),
            "sorted_graph_sha256":sha(PARENT/"raw/DISCOVERY_DETERMINISTIC_FULLSORT_GRAPH_READY.npz"),
            "A0_AOT_sha256":sha(PARENT/"compile/A0_ATOMIC_DISCOVERYDATA.nequip.pt2"),
            "Dready_AOT_sha256":sha(PARENT/"compile/DREADY_OAM_S.nequip.pt2"),
            "reference":"same packaged e3nn OAM-S weights; five frozen reference outputs",
            "dtype":"float32","TF32":"OFF","atol":5e-5,"rtol":5e-5,
            "natural_receiver_major":parent_graph["natural_receiver_major"],
            "natural_sender_within_receiver_monotonic":parent_graph["natural_sender_within_receiver_monotonic"]}
    jwrite("PARENT_AUTHORITY.json",parent)
    env={"node":"109","gpu":parent_model["GPU_name"],"SM":"89","driver":parent_model["driver_line"],
         "python":parent_model["python"],"torch_cuda_runtime":parent_model["torch_cuda_runtime"],
         "packages":parent_model["packages"],"source_commits":parent_model["source_commits"],
         "compiled_mode":"same NequIP AOTInductor ASE CUDA (Aorder reuses A0 package); TF32 OFF",
         "nsys_version":"2024.6.2.225-246235244400v0",
         "nsys_graph_node_ids_present":prof["graph_node_ids_present"],
         "lock_receipts":{m:json.loads((RAW/f"LOCK_{m}.json").read_text()) for m in ("aorder","profile","formal")},
         "profiler_jobs":1,"NCU":0,"NVBit":0,"SASS":0,"Accel_Sim":0,"node174_compute":0}
    jwrite("ENVIRONMENT_RECEIPT.json",env)
    with (PACK/"AORDER_CORRECTNESS.tsv").open("w",newline="") as stream:
        fields=["repeat","status","output_path","output_sha256","first_energy_mismatch","first_force_mismatch"]
        writer=csv.DictWriter(stream,fieldnames=fields,delimiter="\t",lineterminator="\n");writer.writeheader()
        for row in aorder["rows"]:
            writer.writerow({"repeat":row["repeat"],"status":"PASS" if row["numerical_pass"] else "FAIL",
                             "output_path":row["output_path"],"output_sha256":row["output_sha256"],
                             "first_energy_mismatch":json.dumps(row["first_energy_mismatch"]),
                             "first_force_mismatch":json.dumps(row["first_force_mismatch"])})
    p_f=metric(prof,"Aorder","Dready","F_TP_FORWARD_us")
    p_b=metric(prof,"Aorder","Dready","F_TP_FORCE_BACKWARD_us")
    p_g=metric(prof,"Aorder","Dready","gross_TP_us")
    p_a=metric(prof,"Aorder","Dready","F_DET_AUX_us")
    p_n=metric(prof,"Aorder","Dready","net_target_resolved_us")
    p_m=metric(prof,"Aorder","Dready","F_MIXED_us")
    p_nm=metric(prof,"Aorder","Dready","net_target_plus_unresolved_mixed_upper_us")
    p_nt=metric(prof,"Aorder","Dready","F_NON_TP_us")
    p_gpu=metric(prof,"Aorder","Dready","complete_profiled_gpu_us")
    f_order=complete(formal,"A0","Aorder","wall_ms")
    f_same=complete(formal,"Aorder","Dready","wall_ms")
    f_official=complete(formal,"A0","Dready","wall_ms")
    non_target_worst=min(x["gap_us_baseline_minus_candidate"] for x in p_nt["blocks"])
    non_target_best=max(x["gap_us_baseline_minus_candidate"] for x in p_nt["blocks"])
    run={"status":FINAL_LABEL,"scientific_evidence_level":"profiled_family_diagnostic_plus_uninstrumented_complete_region",
         "Aorder_five_numerical_pass":True,"profile_bundle_invocations":36,
         "profiled_kernel_launches":prof["total_attributed_kernel_launches"],
         "profile_family_assigned_or_explicit_mixed_minimum":prof["minimum_assigned_or_explicit_mixed_fraction"],
         "formal_sample_count":72,"formal_all_numeric_pass":True,
         "profiled_Aorder_to_Dready":{"TP_forward_saved_us":p_f["median_gap_us"],
            "TP_force_backward_saved_us":p_b["median_gap_us"],"gross_TP_saved_us":p_g["median_gap_us"],
            "mandatory_det_aux_added_us":-p_a["median_gap_us"],
            "resolved_net_target_added_us":-p_n["median_gap_us"],
            "net_including_all_unresolved_mixed_as_target_still_added_us":-p_nm["median_gap_us"],
            "unresolved_mixed_reduction_us":p_m["median_gap_us"],
            "non_target_median_saved_us":p_nt["median_gap_us"],
            "non_target_worst_block_saved_us":non_target_worst,
            "non_target_best_block_saved_us":non_target_best,
            "complete_profiled_GPU_added_us":-p_gpu["median_gap_us"]},
         "unprofiled_Aorder_to_Dready_wall_saved_ms":f_same["median_gap_ms"],
         "unprofiled_Aorder_to_Dready_wall_relative_gain":f_same["median_relative_gain"],
         "unprofiled_Aorder_to_Dready_class":f_same["classification"],
         "unprofiled_A0_to_Dready_wall_saved_ms":f_official["median_gap_ms"],
         "unprofiled_A0_to_Dready_wall_relative_gain":f_official["median_relative_gain"],
         "unprofiled_A0_to_Dready_class":f_official["classification"],
         "unprofiled_A0_to_Aorder_class":f_order["classification"],
         "profiled_kernel_sum_not_wall_contribution":True,
         "Donline":False,"old_holdout_opened":False,"R21A_history_changed":False,
         "no_additional_scientific_profile_or_timing_after_decision":True}
    jwrite("RUN_RECEIPTS.json",run)
    (PACK/"PROFILE_COMMAND.txt").write_text("nsys profile --trace=cuda,nvtx --cuda-graph-trace=node --sample=none --cpuctxsw=none --force-overwrite=true -o /data/c16/awma/r22f_r21a_family_localization_20261002/raw/R22F_ONE_PROFILE /data/c16/awma/r21a_oeq_graph_readiness_20261002/env/bin/python util/vm_tlb/awma/r22f_family/r22f_runner.py profile --with-aorder\n")
    (PACK/"COMPLETE_RESPONSE_SUMMARY.md").write_text(f"""# Uninstrumented complete energy+force region\n\nAll 72 formal outputs passed the unchanged `5e-5` energy/force contract. Four groups, six samples per arm/group, five warmups per arm; wall and CUDA-event raw values are in `FORMAL_COMPLETE_TIMING.tsv`.\n\n| Contrast | Median wall gap (baseline − candidate) | Median relative gain | Four-group classification |\n|---|---:|---:|---|\n| A0 → Aorder | {f_order['median_gap_ms']*1000:.3f} µs | {f_order['median_relative_gain']*100:.3f}% | {f_order['classification']} |\n| Aorder → Dready | {f_same['median_gap_ms']*1000:.3f} µs | {f_same['median_relative_gain']*100:.3f}% | {f_same['classification']} |\n| A0 → Dready | {f_official['median_gap_ms']*1000:.3f} µs | {f_official['median_relative_gain']*100:.3f}% | {f_official['classification']} |\n\nA0 → Dready has four favorable group directions but its median wall gap {f_official['median_gap_ms']*1000:.3f} µs is below 3× the larger-arm group-MAD estimate ({3*f_official['larger_arm_group_MAD_estimate_ms']*1000:.3f} µs). The CUDA-event comparison is CLEAR_FASTER but does not change the preregistered primary wall classification. Aorder isolates ready-state graph ordering: its A0 comparison is MIXED/near zero, not proof of no ordering effect. R21A's historical 4.7047% is retained separately and not pooled.\n""")
    (PACK/"NEXT_STEP_PROPOSAL.md").write_text("""# One bounded future diagnostic proposal — not authorized here\n\nBefore an online graph-preparation net-cost claim, reconcile the sign difference between the source-attributed NSYS kernel-duration diagnostic and uninstrumented complete-region latency *without changing OAM-S, frame, graph, AOT mode or OEQ implementation*. A separately approved, preregistered low-overhead launch-gap/family-timing control should quantify whether host/runtime scheduling or profiled deterministic fixup inflation explains it. The closest current software capabilities are OEQ's existing atomic aggregation, sorted deterministic aggregation and its source-defined fixup; no hardware novelty follows from these data. If that control cannot close the discrepancy, keep graph-readiness net-cost UNKNOWN. Do not automatically run Donline, independent geometries, another NSYS job, NCU or 174.\n""")
    (PACK/"FINAL_DECISION.md").write_text(f"""# R22F final scientific decision\n\n`{FINAL_LABEL}`. R21A remains `R21A_RESULT_MIXED_NEEDS_REVIEW`.\n\nThe source-backed profiled TP forward and force-backward families improved against sorted-graph atomic Aorder by {p_f['median_gap_us']:.3f} and {p_b['median_gap_us']:.3f} µs; gross TP path saved {p_g['median_gap_us']:.3f} µs. The direct JIT TP main kernels alone saved only 0.529 µs; about 2.848 µs of the gross path change is removal of atomic empty fixup launches. Deterministic mandatory real fixups added {-p_a['median_gap_us']:.3f} µs (forward 10.368, backward 19.776), so the resolved *profiled* net target family became {-p_n['median_gap_us']:.3f} µs more expensive. Even assigning all unresolved mixed-family advantage to target leaves {-p_nm['median_gap_us']:.3f} µs extra profiled cost. Non-target changed by {p_nt['median_gap_us']:.3f} µs median benefit ({p_nt['relative_gain']*100:.3f}%), worst block {non_target_worst:.3f} µs benefit; no stable non-target regression was observed.\n\nThe independently uninstrumented complete region conflicts in sign with the profiled GPU duration sum: Aorder→Dready wall was {f_same['median_gap_ms']*1000:.3f} µs / {f_same['median_relative_gain']*100:.3f}% faster and CLEAR; official A0→Dready was {f_official['median_gap_ms']*1000:.3f} µs / {f_official['median_relative_gain']*100:.3f}% faster by median but MIXED under 3×MAD. Ordering-only A0→Aorder was MIXED and near zero. Profiled duration sums ({-p_gpu['median_gap_us']:.3f} µs additional GPU service for Dready) cannot be subtracted from uninstrumented wall to explain the discrepancy.\n\nThus gross TP response exists, but no stable positive *net target-family* response has been established after mandatory deterministic auxiliary work; the complete official-baseline wall response also remains mixed. This is a bounded Native family localization, not an online graph-preparation payoff, cross-frame/model result, deployment or hardware claim. No new samples are added after this decision.\n""")
    (PACK/"README.md").write_text(f"""# AWMA R22F R21A family localization\n\nFinal status: `{FINAL_LABEL}`. Source/model/input/AOT identity is in `PARENT_AUTHORITY.json`; R21A historical result is unchanged. `FAMILY_CONTRACT.md`, `AORDER_CONTRACT.md` and `MEASUREMENT_CONTRACT.md` were frozen before the single profile.\n\nAorder uses the exact Dready sorted graph but the accepted A0 atomic AOT package, so ordering and aggregation are structurally separated. Five Aorder calls and all 72 formal energy+force outputs passed the unchanged numerical contract. One NSYS job supplied source-backed per-launch family attribution (36 invocations, 4,332 launches); its duration sums are **profiled diagnostics only**. `FAMILY_MEMBERS.tsv`, `PROFILED_FAMILY_TIMING.tsv`, `FAMILY_RESPONSE_SUMMARY.tsv` and the additive TP-main/fixup substrata show the calculation. `FORMAL_COMPLETE_TIMING.tsv` and `COMPLETE_RESPONSE_SUMMARY.*` provide uninstrumented wall/CUDA-event data.\n\nThe critical unresolved point is profiled net target-family cost worsening while the uninstrumented Aorder→Dready complete region improved. No Donline/old holdout, NCU/NVBit/SASS/Accel-Sim or node174 compute was run. Raw NSYS, SQLite, every output and lock receipts are indexed in `RAW_DATA_INDEX.tsv` on node164.\n""")
    print(json.dumps({"status":FINAL_LABEL,"non_target_worst_block_gap_us":non_target_worst,
                      "prof_net_target_added_us":-p_n["median_gap_us"],
                      "complete_Aorder_Dready_wall_gain":f_same["median_relative_gain"]},sort_keys=True))


if __name__=="__main__": main()
