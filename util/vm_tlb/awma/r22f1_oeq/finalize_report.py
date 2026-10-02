#!/usr/bin/env python3
"""CPU-only R22F1 compact scientific report and exact authority bindings."""

import csv
import hashlib
import json
import statistics
import subprocess
from pathlib import Path

import numpy as np

ROOT=Path("/data/c16/awma/r22f1_oeq_lowoverhead_replay_20261002")
RAW=ROOT/"raw"
PARENT=Path("/data/c16/awma/r21a_oeq_graph_readiness_20261002")
R22F=Path("/home/huangrulin/workspace/worktrees/accel-sim-awma-r22f-r21a-family-localization-109-v1/docs/vm_tlb/review_packs/AWMA_R22F_R21A_FAMILY_LOCALIZATION_109_V1")
PACK=Path("/home/huangrulin/workspace/worktrees/accel-sim-awma-r22f1-oeq-lowoverhead-replay-109-v1/docs/vm_tlb/review_packs/AWMA_R22F1_OEQ_LOWOVERHEAD_REPLAY_109_V1")
LABEL="R22F1_FAMILY_GAP_UNRESOLVED"


def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda:stream.read(8<<20),b""):
            h.update(block)
    return h.hexdigest()


def jwrite(name,value): (PACK/name).write_text(json.dumps(value,indent=2,sort_keys=True,default=str)+"\n")


def tsv(name,rows,fields):
    with (PACK/name).open("w",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=fields,delimiter="\t",lineterminator="\n")
        writer.writeheader();writer.writerows(rows)


def cmp_field(a,b):
    mask=~np.isfinite(b)|~np.isclose(a,b,atol=5e-5,rtol=5e-5)
    first=None
    if np.any(mask):
        idx=tuple(int(i) for i in np.argwhere(mask)[0])
        first={"index":idx,"atomic":float(a[idx]),"deterministic":float(b[idx])}
    return first,float(np.max(np.abs(a-b)))


def find_scope(decision,scope):
    found=[r for r in decision["comparisons"] if r["scope"]==scope]
    if len(found)!=1: raise RuntimeError(f"scope not unique: {scope}")
    return found[0]


def main():
    capture=json.loads((RAW/"TP_CAPTURE_STATUS.json").read_text())
    qualify=json.loads((RAW/"REPLAY_QUALIFICATION_STATUS.json").read_text())
    timing=json.loads((RAW/"REPLAY_TIMING_STATUS.json").read_text())
    decision=json.loads((PACK/"REPLAY_DECISION.json").read_text())
    freeze=json.loads((PACK/"BACKWARD_MODE_FREEZE.json").read_text())
    runtime=json.loads((PARENT/"raw/RUNTIME_ADMISSION.json").read_text())
    if (capture["status"],qualify["status"],timing["status"],decision["status"])!=("TP_CAPTURE_QUALIFIED","REPLAY_QUALIFIED","REPLAY_TIMING_COMPLETE",LABEL):
        raise RuntimeError("Scientific STOP authority not closed")
    if freeze["mode"]!="BUNDLE32" or len(capture["records"])!=2 or len(timing["rows"])!=320:
        raise RuntimeError("Call multiplicity/protocol drift")
    if (PACK/"REPLAY_MEASUREMENT_CONTRACT.md").stat().st_mtime >= (RAW/"REPLAY_TIMING_STATUS.json").stat().st_mtime:
        raise RuntimeError("Measurement contract not frozen")
    if any(RAW.glob("DONLINE*")) or any(RAW.glob("HOLDOUT*")):
        raise RuntimeError("Forbidden later stage executed")
    parent={"stage":"AWMA_R22F1_OEQ_LOWOVERHEAD_REPLAY_109_V1",
            "starting_commit":"a6ac7ae69fcbc978ce50e5cac926234b823edcf0",
            "starting_tree":"6c1fbfa0f0a6ff14dd553487cff0b5997c0e398e",
            "scientific_parent":"df0e8edd009ee1a56ba65b25b319e8a852f74d27",
            "parent_label":"R22F_R21A_FAMILY_RESULT_MIXED",
            "R21A_historical_label":"R21A_RESULT_MIXED_NEEDS_REVIEW",
            "model_id":"nequip.net:mir-group/NequIP-OAM-S:0.1",
            "model_package_sha256":sha(PARENT/"model/NequIP-OAM-S-0.1.nequip.zip"),
            "input_sha256":sha(PARENT/"source/nequip-tutorial/sitraj.xyz"),
            "frame_index":55,"atom_count":64,"directed_edges":1394,
            "sorted_graph_sha256":sha(PARENT/"raw/DISCOVERY_DETERMINISTIC_FULLSORT_GRAPH_READY.npz"),
            "source_commits":runtime["source_commits"],"dtype":"float32","TF32":"OFF",
            "numerical_atol":5e-5,"numerical_rtol":5e-5,
            "parent_profile_receipt_sha256":sha(R22F/"PROFILE_RECEIPT.json"),
            "parent_complete_summary_sha256":sha(R22F/"COMPLETE_RESPONSE_SUMMARY.json")}
    jwrite("PARENT_AUTHORITY.json",parent)
    capture_compact={"status":capture["status"],"capture_source":capture["capture_source"],
                     "observed_TP_call_count":capture["observed_call_count"],
                     "model_package_sha256":capture["model_sha256"],
                     "sorted_graph_sha256":capture["sorted_graph_sha256"],
                     "full_energy_force_output_sha256":capture["full_model_output_sha256"],
                     "full_energy_first_mismatch":capture["full_model_energy_first_mismatch"],
                     "full_forces_first_mismatch":capture["full_model_forces_first_mismatch"],
                     "capture_status_sha256":sha(RAW/"TP_CAPTURE_STATUS.json"),
                     "records":[{"call_index":r["call_index"],"callsite":r["callsite"],
                                 "payload_sha256":r["payload_sha256"],"tensor_sha256":r["tensor_sha256"],
                                 "upstream_gradient_observation_count":r["upstream_gradient_observation_count"]}
                                for r in capture["records"]]}
    jwrite("TP_CAPTURE_AUTHORITY.json",capture_compact)
    call_rows=[]
    for r in capture["records"]:
        call_rows.append({"call_index":r["call_index"],"callsite":r["callsite"],
            "forward_multiplicity":1,"force_backward_multiplicity":1,
            "X_shape":json.dumps(r["tensor_shapes"]["X"]),"Y_shape":json.dumps(r["tensor_shapes"]["Y"]),
            "W_shape":json.dumps(r["tensor_shapes"]["W"]),"upstream_shape":json.dumps(r["tensor_shapes"]["upstream_0"]),
            "requires_grad":json.dumps(r["requires_grad"],sort_keys=True),
            "TPProblem_repr_sha256":hashlib.sha256(r["OEQ_problem_repr"].encode()).hexdigest(),
            "atomic_JIT_hash":r["OEQ_JIT_hash"],"atomic_workspace_bytes":r["workspace_size_bytes"],
            "payload_sha256":r["payload_sha256"]})
    tsv("TP_CALL_RECORDS.tsv",call_rows,list(call_rows[0]))
    impl=[]
    for r in qualify["rows"]:
        if "arm" not in r: continue
        impl.append({"call_index":r["call_index"],"callsite":r["callsite"],"arm":r["arm"],
            "deterministic":r["input_args"]["deterministic"],"kahan":r["input_args"]["kahan"],
            "torch_op":r["input_args"]["torch_op"],"OEQ_JIT_hash":r["OEQ_hash"],
            "OEQ_kernel_string_sha256":r["kernel_string_sha256"],
            "same_problem_repr_sha256":r["problem_repr_sha256"],
            "workspace_size_bytes":r["workspace_size_bytes"],
            "output_payload_sha256":r["output_sha256"]})
    tsv("REPLAY_IMPLEMENTATION_IDENTITY.tsv",impl,list(impl[0]))
    correctness=[]
    for r in capture["records"]:
        idx=r["call_index"]
        with np.load(RAW/f"REPLAY_QUAL_CALL_{idx:02d}_Aorder.npz",allow_pickle=False) as a, \
             np.load(RAW/f"REPLAY_QUAL_CALL_{idx:02d}_Dready.npz",allow_pickle=False) as d:
            if set(a.files)!=set(d.files): raise RuntimeError("Correctness field set mismatch")
            for field in a.files:
                first,max_abs=cmp_field(a[field],d[field])
                correctness.append({"call_index":idx,"callsite":r["callsite"],"field":field,
                    "status":"PASS" if first is None else "FAIL","max_abs_diff":max_abs,
                    "first_mismatch":json.dumps(first),"atomic_payload_sha256":sha(RAW/f"REPLAY_QUAL_CALL_{idx:02d}_Aorder.npz"),
                    "det_payload_sha256":sha(RAW/f"REPLAY_QUAL_CALL_{idx:02d}_Dready.npz")})
    if any(x["status"]!="PASS" for x in correctness): raise RuntimeError("Numerical source mismatch")
    tsv("REPLAY_CORRECTNESS.tsv",correctness,list(correctness[0]))
    direct_fixup=[{"status":"FIXUP_DIRECT_TIMING_NOT_AVAILABLE",
                   "source_reason":"pinned OEQ PyTorch operator exposes complete jit_conv_forward/backward, not a supported exact fixup-only API",
                   "parent_NSYS_det_fixup_forward_us":"10.368_PROFILED_ONLY",
                   "parent_NSYS_det_fixup_backward_us":"19.776_PROFILED_ONLY",
                   "R22F1_direct_fixup_cuda_event_us":"NOT_MEASURED"}]
    tsv("FIXUP_TIMING.tsv",direct_fixup,list(direct_fixup[0]))
    env={"node":"109","GPU":runtime["GPU_name"],"SM":"89","driver":runtime["driver_line"],
         "python":runtime["python"],"torch_cuda_runtime":runtime["torch_cuda_runtime"],
         "packages":runtime["packages"],"source_commits":runtime["source_commits"],
         "lock_receipts":{m:json.loads((RAW/f"LOCK_{m}.json").read_text()) for m in ("CAPTURE","QUALIFY","TIMING")},
         "new_profiler_jobs":0,"NCU":0,"NVBit":0,"SASS":0,"Accel_Sim":0,"node174_compute":0}
    jwrite("ENVIRONMENT_RECEIPT.json",env)
    fwd=find_scope(decision,"forward_all_real_calls")
    bwd=find_scope(decision,"backward_all_real_calls")
    primary=decision["combined"]
    c0=find_scope(decision,"combined_call_0")
    c1=find_scope(decision,"combined_call_1")
    (PACK/"EVIDENCE_RECONCILIATION.md").write_text(f"""# Three evidence levels — no arithmetic pooling\n\n| Evidence | Aorder→Dready result | Evidence level |\n|---|---:|---|\n| R22F NSYS, source-attributed resolved net TP family | Dready **+26.752 µs** profiled kernel-duration cost, including real deterministic fixup +30.160 µs | Instrumented family diagnostic |\n| R22F1 exact-input low-overhead CUDA-event replay | Dready {primary['median_gap_us']:+.3f} µs saved by median; 5 group gaps {[round(x['gap_us_Aorder_minus_Dready'],3) for x in primary['groups']]} µs; larger-arm aggregate MAD {primary['larger_arm_group_MAD_estimate_us']:.3f} µs | Standalone exact-call family replay, mixed |\n| R22F uninstrumented complete OAM-S energy+force | Dready **13.955 µs / 2.878%** faster, CLEAR | Full-model ready-graph boundary |\n\nThe exact two real callsites (one per layer) and their real upstream VJPs were used in both arms. Same-input forward/required gradients passed `atol=rtol=5e-5`; 32-state backward canary passed. Forward aggregate gap {fwd['median_gap_us']:+.3f} µs and backward aggregate gap {bwd['median_gap_us']:+.3f} µs are individually mixed. Callsite combined gaps are {c0['median_gap_us']:+.3f} and {c1['median_gap_us']:+.3f} µs, neither stable.\n\nThe direct fixup API was unavailable, so the actual low-overhead fixup-only service time is **UNKNOWN**; the parent 30.160 µs is an NSYS diagnostic, not a measured R22F1 cost. The new family replay does not establish the parent's positive full-model effect as TP-family benefit, nor does it establish that the profiled negative family cost persists without NSYS. Different scheduling, launch gaps and graph context are possible explanations, not proven causes. No Donline or old holdout was run.\n""")
    (PACK/"NEXT_STEP_PROPOSAL.md").write_text("""# Decision-boundary handoff\n\nNo online graph-preparation net-cost validation is justified by this Goal: the exact-input family sign remains unresolved under the frozen 5-group noise rule. Stop without additional samples, profiling, model/frame changes or hardware work. Any later attempt to reconcile standalone replay with the full-model AOT context needs a separately approved preregistered contract; this pack does not authorize one.\n""")
    (PACK/"FINAL_DECISION.md").write_text(f"""# R22F1 scientific STOP\n\n`{LABEL}`.\n\nThe real sorted-graph OAM-S frame55 energy→forces execution yielded exactly two TP callsites, layer0 and layer1, each with one forward and one force backward. Each exact input, TPProblem/JIT identity and real backward upstream gradient is hash-closed. Atomic Aorder and deterministic Dready on those same tensors passed forward and required-gradient `5e-5` comparisons.\n\nWithout any new profiler, bundled CUDA-event replay gave aggregate forward Aorder−Dready {fwd['median_gap_us']:+.3f} µs, backward {bwd['median_gap_us']:+.3f} µs, combined {primary['median_gap_us']:+.3f} µs ({primary['median_relative_gain']*100:+.3f}%). Combined group gaps changed sign; the 3×MAD gate failed. This cannot affirm either a positive or negative same-input TP-family cost. Exact direct fixup timing was unavailable, so its low-overhead isolated cost remains unknown.\n\nR22F's NSYS diagnostic (+26.752 µs deterministic net TP cost) and full-model uninstrumented ready-graph benefit (13.955 µs / 2.878%) remain observations at different boundaries. R22F1 does not turn either into a causal explanation. Do not run Donline or pursue an R21A target-family mechanism on this evidence.\n""")
    (PACK/"README.md").write_text(f"""# AWMA R22F1 OEQ exact-input low-overhead replay\n\nStatus `{LABEL}`. Fixed OAM-S:0.1, real `sitraj.xyz` frame55, accepted sorted graph/permutation, pinned OEQ/NequIP, float32 and TF32 OFF. One non-timed complete energy+force call captured both true OEQ TP callsites and their force VJP upstream gradients; all tensors and outputs are hashed.\n\nSame-input Aorder/Dready standalone output and force-required gradients qualified. Backward mode was frozen as 32-state bundle before timing. Formal forward and backward each used 10 warmups/arm/callsite and 5 groups ×8 one-event-pair 32-replay bundles/arm/callsite. All 320 formal outputs/gradients passed numerical checks. The combined family sign remained mixed. No new NSYS/NCU/NVBit/SASS, Donline, old holdout, Accel-Sim or node174 compute.\n\n`TP_CALL_RECORDS.tsv`, `REPLAY_IMPLEMENTATION_IDENTITY.tsv`, `REPLAY_CORRECTNESS.tsv`, `FORWARD_TIMING.tsv`, `BACKWARD_TIMING.tsv` and `REPLAY_DECISION.json` give compact evidence. Large exact tensors, every formal output and timing status are indexed on node164.\n""")
    processes=subprocess.check_output(["nvidia-smi","--query-compute-apps=pid","--format=csv,noheader,nounits"],text=True).strip().splitlines()
    run={"status":LABEL,"captured_real_call_count":len(capture["records"]),
         "capture_energy_force_numerical_pass":True,"same_input_forward_and_required_grad_pass":True,
         "backward_mode":"BUNDLE32","formal_forward_bundles":160,"formal_backward_bundles":160,
         "all_320_formal_numerical_pass":True,"combined_median_gap_us":primary["median_gap_us"],
         "combined_group_gap_us":[x["gap_us_Aorder_minus_Dready"] for x in primary["groups"]],
         "combined_larger_arm_MAD_us":primary["larger_arm_group_MAD_estimate_us"],
         "direct_fixup":"FIXUP_DIRECT_TIMING_NOT_AVAILABLE","Donline":False,"old_holdout":False,
         "new_NSYS":0,"NCU":0,"NVBit":0,"SASS":0,"Accel_Sim":0,"node174_compute":0,
         "current_GPU_compute_pids":processes,"lock_receipts":env["lock_receipts"],
         "first_mismatch":None}
    jwrite("RUN_RECEIPTS.json",run)
    print(json.dumps({"status":LABEL,"call_count":len(capture["records"]),
                      "combined_gap_us":primary["median_gap_us"],"formal_bundles":320},sort_keys=True))


if __name__=="__main__": main()
