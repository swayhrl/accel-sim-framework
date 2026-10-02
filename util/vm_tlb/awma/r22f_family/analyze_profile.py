#!/usr/bin/env python3
"""CPU-only source-backed R22F one-profile family attribution and response."""

import collections
import csv
import hashlib
import json
import sqlite3
import statistics
from pathlib import Path

ROOT = Path("/data/c16/awma/r22f_r21a_family_localization_20261002")
RAW = ROOT / "raw"
PACK = Path("/home/huangrulin/workspace/worktrees/accel-sim-awma-r22f-r21a-family-localization-109-v1/docs/vm_tlb/review_packs/AWMA_R22F_R21A_FAMILY_LOCALIZATION_109_V1")
DB = RAW / "R22F_ONE_PROFILE.sqlite"
FAMILIES = ["F_TP_FORWARD", "F_TP_FORCE_BACKWARD", "F_DET_AUX", "F_NON_TP", "F_MIXED"]


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 << 20), b""):
            h.update(block)
    return h.hexdigest()


def tsv(path, rows, fields):
    with Path(path).open("w", newline="") as stream:
        out = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        out.writeheader(); out.writerows(rows)


def med_mad(values):
    med = statistics.median(values)
    return med, statistics.median(abs(v-med) for v in values)


def classify(kernels, arm):
    for index, row in enumerate(kernels):
        name = row["function"]
        if name.startswith("forward("):
            row["family"] = "F_TP_FORWARD"
            row["reason"] = "OEQ JIT convolution.hpp::exec_conv forward; two interaction layers"
            if index < 1 or "FillFunctor<float>" not in kernels[index-1]["function"]:
                raise RuntimeError("OEQ forward output-zeroing adjacency not closed")
            kernels[index-1]["family"] = "F_TP_FORWARD"
            kernels[index-1]["reason"] = "OEQ torch_core.hpp::jit_conv_forward tensor_zeros_like L3_out"
        elif name.startswith("backward("):
            row["family"] = "F_TP_FORCE_BACKWARD"
            row["reason"] = "OEQ JIT convolution.hpp::backward for first-order forces"
            if index < 2 or any("FillFunctor<float>" not in kernels[j]["function"] for j in (index-2,index-1)):
                raise RuntimeError("OEQ backward two gradient-output zeroing launches not closed")
            for j in (index-2,index-1):
                kernels[j]["family"] = "F_TP_FORCE_BACKWARD"
                kernels[j]["reason"] = "OEQ torch_core.hpp::jit_conv_backward tensor_zeros_like L1/L2 gradients"
        elif name.startswith("fixup_forward("):
            row["family"] = "F_DET_AUX" if arm == "Dready" else "F_TP_FORWARD"
            row["reason"] = "nonempty deterministic fixup_forward" if arm == "Dready" else "atomic template empty fixup_forward launch"
        elif name.startswith("fixup_backward("):
            row["family"] = "F_DET_AUX" if arm == "Dready" else "F_TP_FORCE_BACKWARD"
            row["reason"] = "nonempty deterministic fixup_backward" if arm == "Dready" else "atomic template empty fixup_backward launch"
    for row in kernels:
        if row.get("family"):
            continue
        if "jit_conv" in row["function"]:
            row["family"] = "F_MIXED"
            row["reason"] = "AOT fused name mentions jit_conv and other semantics; target/non-target inseparable"
        else:
            row["family"] = "F_NON_TP"
            row["reason"] = "not OEQ JIT convolution or source-linked init/fixup; AOT/CUDA model remainder"
    counts = collections.Counter(r["function"].split("(")[0] for r in kernels)
    required = {"forward":2, "backward":2, "fixup_forward":2, "fixup_backward":2}
    for name, expected in required.items():
        if counts[name] != expected:
            raise RuntimeError(f"OEQ two-layer membership drift: {arm} {name} {counts[name]} != {expected}")
    if sum("FillFunctor<float>" in r["function"] and r["family"] in ("F_TP_FORWARD", "F_TP_FORCE_BACKWARD") for r in kernels) != 6:
        raise RuntimeError("OEQ six source-backed zeroing launches not closed")


def response(rows, baseline, candidate, metric):
    blocks = []
    for block in range(3):
        values = {arm: [r[metric] for r in rows if r["arm"] == arm and r["block"] == block]
                  for arm in (baseline,candidate)}
        if any(len(v)!=4 for v in values.values()):
            raise RuntimeError("Profile block shape drift")
        med = {arm: med_mad(values[arm])[0] for arm in values}
        mad = {arm: med_mad(values[arm])[1] for arm in values}
        blocks.append({"block":block, "baseline_median_us":med[baseline], "candidate_median_us":med[candidate],
                       "baseline_MAD_us":mad[baseline], "candidate_MAD_us":mad[candidate],
                       "gap_us_baseline_minus_candidate":med[baseline]-med[candidate]})
    gaps = [x["gap_us_baseline_minus_candidate"] for x in blocks]
    median_gap = statistics.median(gaps)
    larger_arm_block_MAD_estimate = max(statistics.median(x["baseline_MAD_us"] for x in blocks),
                                        statistics.median(x["candidate_MAD_us"] for x in blocks))
    base_median = statistics.median(x["baseline_median_us"] for x in blocks)
    return {"baseline":baseline, "candidate":candidate, "metric":metric,
            "blocks":blocks, "median_gap_us":median_gap, "relative_gain":median_gap/base_median if base_median else None,
            "direction_all_blocks":all(g>0 for g in gaps) or all(g<0 for g in gaps),
            "stable_positive":all(g>0 for g in gaps) and median_gap>3*larger_arm_block_MAD_estimate,
            "stable_regression":all(g<0 for g in gaps) and -median_gap>3*larger_arm_block_MAD_estimate,
            "larger_arm_block_MAD_estimate_us":larger_arm_block_MAD_estimate,
            "noise_rule": "all_3_block_medians_same_direction_and_median_absolute_gap_gt_3x_max_of_arm_median_block_MAD"}


def main():
    if (PACK/"FAMILY_CONTRACT.md").stat().st_mtime >= DB.stat().st_mtime:
        raise RuntimeError("Family contract was not frozen before profile")
    status = json.loads((RAW/"PROFILE_RUN_STATUS.json").read_text())
    if status["status"] != "PROFILE_RUN_COMPLETE" or status["measured_count"] != 36:
        raise RuntimeError("One profile bundle incomplete")
    db = sqlite3.connect(DB)
    nvtx = db.execute("SELECT start,end,text FROM NVTX_EVENTS WHERE text LIKE 'R22F|arm=%' ORDER BY start").fetchall()
    if len(nvtx) != 36:
        raise RuntimeError(f"NVTX invocation count {len(nvtx)} !=36")
    kernel_rows = []
    invocation_rows = []
    membership = collections.defaultdict(lambda: {"invocations":set(), "durations":[], "count":0, "reason":None})
    for start,end,label in nvtx:
        tags = dict(part.split("=",1) for part in label.split("|") if "=" in part)
        arm, block, repeat = tags["arm"],int(tags["block"]),int(tags["repeat"])
        if arm not in ("A0","Aorder","Dready"):
            raise RuntimeError("NVTX arm drift")
        records = db.execute("SELECT k.start,k.end,s.value,k.gridX,k.gridY,k.gridZ,k.blockX,k.blockY,k.blockZ,k.graphNodeId,k.correlationId FROM CUPTI_ACTIVITY_KIND_KERNEL k JOIN StringIds s ON k.demangledName=s.id WHERE k.start>=? AND k.end<=? ORDER BY k.start", (start,end)).fetchall()
        kernels=[]
        for index,r in enumerate(records):
            kernels.append({"arm":arm,"block":block,"repeat":repeat,"launch_index":index,
                            "start_ns":r[0],"end_ns":r[1],"duration_us":(r[1]-r[0])/1000,
                            "function":r[2],"grid":f"{r[3]},{r[4]},{r[5]}","block_shape":f"{r[6]},{r[7]},{r[8]}",
                            "graph_node_id":r[9],"correlation_id":r[10]})
        classify(kernels,arm)
        time_by_family = {family:sum(r["duration_us"] for r in kernels if r["family"]==family) for family in FAMILIES}
        total = sum(r["duration_us"] for r in kernels)
        if total <= 0 or sum(time_by_family.values())/total < 0.95:
            raise RuntimeError("Family assignment coverage <95%")
        entry={"arm":arm,"block":block,"repeat":repeat,"nvtx_label":label,"kernel_count":len(kernels),
               "complete_profiled_gpu_us":total,"F_TP_FORWARD_us":time_by_family["F_TP_FORWARD"],
               "F_TP_FORCE_BACKWARD_us":time_by_family["F_TP_FORCE_BACKWARD"],
               "F_DET_AUX_us":time_by_family["F_DET_AUX"],
               "F_MIXED_us":time_by_family["F_MIXED"],"F_NON_TP_us":time_by_family["F_NON_TP"],
               "gross_TP_us":time_by_family["F_TP_FORWARD"]+time_by_family["F_TP_FORCE_BACKWARD"],
               "net_target_resolved_us":sum(time_by_family[f] for f in ("F_TP_FORWARD","F_TP_FORCE_BACKWARD","F_DET_AUX")),
               "net_target_plus_unresolved_mixed_upper_us":sum(time_by_family[f] for f in ("F_TP_FORWARD","F_TP_FORCE_BACKWARD","F_DET_AUX","F_MIXED")),
               "assigned_or_explicit_mixed_fraction":sum(time_by_family.values())/total,
               "gpu_kernel_duration_evidence":"PROFILED_FAMILY_DIAGNOSTIC"}
        invocation_rows.append(entry)
        for row in kernels:
            key=(arm,row["function"],row["grid"],row["block_shape"],row["family"])
            member=membership[key]
            member["invocations"].add((block,repeat))
            member["durations"].append(row["duration_us"])
            member["count"]+=1
            member["reason"]=row["reason"]
            kernel_rows.append(row)
    if any(len([r for r in invocation_rows if r["arm"]==arm]) !=12 for arm in ("A0","Aorder","Dready")):
        raise RuntimeError("Profile balance not closed")
    tsv(RAW/"PROFILE_KERNELS.tsv",kernel_rows,list(kernel_rows[0]))
    tsv(PACK/"PROFILED_FAMILY_TIMING.tsv",invocation_rows,list(invocation_rows[0]))
    member_rows=[]
    for key,value in sorted(membership.items()):
        arm,function,grid,block_shape,family=key
        member_rows.append({"arm":arm,"function":function,"grid":grid,"block":block_shape,"family":family,
                            "observed_launch_count":value["count"],"invocations_present":len(value["invocations"]),
                            "median_launch_duration_us":statistics.median(value["durations"]),
                            "source_attribution":value["reason"]})
    tsv(PACK/"FAMILY_MEMBERS.tsv",member_rows,list(member_rows[0]))
    metrics=["F_TP_FORWARD_us","F_TP_FORCE_BACKWARD_us","F_DET_AUX_us","gross_TP_us","net_target_resolved_us",
             "net_target_plus_unresolved_mixed_upper_us","F_MIXED_us","F_NON_TP_us","complete_profiled_gpu_us"]
    response_rows=[]
    response_json=[]
    for baseline,candidate in (("A0","Aorder"),("Aorder","Dready"),("A0","Dready")):
        for metric in metrics:
            result=response(invocation_rows,baseline,candidate,metric)
            response_json.append(result)
            response_rows.append({key:result[key] for key in ("baseline","candidate","metric","median_gap_us","relative_gain","direction_all_blocks","stable_positive","stable_regression","larger_arm_block_MAD_estimate_us")})
    tsv(PACK/"FAMILY_RESPONSE_SUMMARY.tsv",response_rows,list(response_rows[0]))
    report={"status":"FAMILY_ATTRIBUTION_QUALIFIED","profile_sqlite_sha256":sha(DB),
            "profile_rep_sha256":sha(RAW/"R22F_ONE_PROFILE.nsys-rep"),
            "family_contract_sha256":sha(PACK/"FAMILY_CONTRACT.md"),
            "nvtx_invocations":len(invocation_rows),"total_attributed_kernel_launches":len(kernel_rows),
            "minimum_assigned_or_explicit_mixed_fraction":min(x["assigned_or_explicit_mixed_fraction"] for x in invocation_rows),
            "graph_node_ids_present":sum(x["graph_node_id"] is not None for x in kernel_rows),
            "membership_source":"OEQ exact JIT source/convolution.hpp/torch_core.hpp plus same-invocation ordered launches; AOT fused jit_conv names remain F_MIXED",
            "profiled_time_is_uninstrumented_wall":False,"responses":response_json}
    (PACK/"PROFILE_RECEIPT.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":report["status"],"invocations":len(invocation_rows),"launches":len(kernel_rows),
                      "graph_node_ids_present":report["graph_node_ids_present"],
                      "responses":[{k:r[k] for k in ("baseline","candidate","metric","median_gap_us","relative_gain","stable_positive","stable_regression")}
                                   for r in response_json if r["metric"] in ("gross_TP_us","F_DET_AUX_us","net_target_resolved_us","F_NON_TP_us","F_MIXED_us")]},sort_keys=True))


if __name__=="__main__":
    main()
