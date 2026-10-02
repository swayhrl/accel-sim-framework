#!/usr/bin/env python3
"""CPU-only frozen R22F1 per-callsite and combined CUDA-event decision."""

import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

ROOT=Path("/data/c16/awma/r22f1_oeq_lowoverhead_replay_20261002")
RAW=ROOT/"raw"
PACK=Path("/home/huangrulin/workspace/worktrees/accel-sim-awma-r22f1-oeq-lowoverhead-replay-109-v1/docs/vm_tlb/review_packs/AWMA_R22F1_OEQ_LOWOVERHEAD_REPLAY_109_V1")


def tsv(path,rows,fields):
    with Path(path).open("w",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=fields,delimiter="\t",lineterminator="\n")
        writer.writeheader();writer.writerows(rows)


def med_mad(values):
    median=statistics.median(values)
    return median,statistics.median(abs(x-median) for x in values)


def compare(groups,scope):
    rows=[]
    for group in range(5):
        subset={arm:next(x for x in groups if x["group"]==group and x["arm"]==arm) for arm in ("Aorder","Dready")}
        base,candidate=subset["Aorder"],subset["Dready"]
        gap=base["event_us"]-candidate["event_us"]
        rows.append({"group":group,"Aorder_us":base["event_us"],"Dready_us":candidate["event_us"],
                     "Aorder_MAD_us":base["MAD_us"],"Dready_MAD_us":candidate["MAD_us"],
                     "gap_us_Aorder_minus_Dready":gap,"relative_gain":gap/base["event_us"]})
    gaps=[x["gap_us_Aorder_minus_Dready"] for x in rows]
    median_gap=statistics.median(gaps)
    larger_arm_mad=max(statistics.median(x["Aorder_MAD_us"] for x in rows),
                       statistics.median(x["Dready_MAD_us"] for x in rows))
    return {"scope":scope,"groups":rows,"median_gap_us":median_gap,
            "median_relative_gain":statistics.median(x["relative_gain"] for x in rows),
            "larger_arm_group_MAD_estimate_us":larger_arm_mad,
            "all_five_Dready_faster":all(g>0 for g in gaps),
            "all_five_Dready_slower":all(g<0 for g in gaps),
            "stable_positive":all(g>0 for g in gaps) and median_gap>3*larger_arm_mad,
            "stable_negative":all(g<0 for g in gaps) and -median_gap>3*larger_arm_mad,
            "noise_rule":"all_5_group_medians_same_direction_and_median_absolute_gap_gt_3x_larger_arm_median_group_MAD"}


def main():
    status=json.loads((RAW/"REPLAY_TIMING_STATUS.json").read_text())
    capture=json.loads((RAW/"TP_CAPTURE_STATUS.json").read_text())
    if status["status"]!="REPLAY_TIMING_COMPLETE" or capture["status"]!="TP_CAPTURE_QUALIFIED":
        raise RuntimeError("Replay timing/capture not qualified")
    if status["backward_mode"]!="BUNDLE32" or len(status["rows"])!=320:
        raise RuntimeError("Frozen 32-bundle timing sample count drift")
    for phase in ("FORWARD","BACKWARD"):
        (PACK/f"{phase}_TIMING.tsv").write_bytes((RAW/f"{phase}_TIMING.tsv").read_bytes())
    summaries=[]
    observed=set()
    for phase in ("forward","backward"):
        for record in capture["records"]:
            call=record["call_index"]
            for group in range(5):
                for arm in ("Aorder","Dready"):
                    values=[float(row["event_per_replay_us"]) for row in status["rows"]
                            if row["phase"]==phase and row["call_index"]==call and row["group"]==group and row["arm"]==arm]
                    if len(values)!=8: raise RuntimeError(f"Sample multiplicity drift {phase} {call} {group} {arm}")
                    if not all(row["numeric_pass"] for row in status["rows"] if row["phase"]==phase and row["call_index"]==call and row["group"]==group and row["arm"]==arm):
                        raise RuntimeError("Formal numerical failure")
                    m,mad=med_mad(values)
                    summaries.append({"phase":phase,"call_index":call,"callsite":record["callsite"],
                                      "group":group,"arm":arm,"event_us":m,"MAD_us":mad,
                                      "formal_bundles":8,"replays_per_bundle":32,
                                      "multiplicity_in_full_model":1})
                    observed.add((phase,call,group,arm))
    if len(observed)!=2*len(capture["records"])*5*2:
        raise RuntimeError("Missing callsite/group/arm")
    tsv(PACK/"CALLSITE_GROUP_TIMING.tsv",summaries,list(summaries[0]))
    comparisons=[]
    for phase in ("forward","backward"):
        for record in capture["records"]:
            call=record["call_index"]
            subset=[x for x in summaries if x["phase"]==phase and x["call_index"]==call]
            comparisons.append(compare(subset,f"{phase}_call_{call}"))
        aggregate=[]
        for group in range(5):
            for arm in ("Aorder","Dready"):
                parts=[x for x in summaries if x["phase"]==phase and x["group"]==group and x["arm"]==arm]
                aggregate.append({"group":group,"arm":arm,"event_us":sum(x["event_us"] for x in parts),
                                  "MAD_us":sum(x["MAD_us"] for x in parts)})
        comparisons.append(compare(aggregate,f"{phase}_all_real_calls"))
    by_call=[]
    for record in capture["records"]:
        call=record["call_index"]
        grouped=[]
        for group in range(5):
            for arm in ("Aorder","Dready"):
                parts=[x for x in summaries if x["call_index"]==call and x["group"]==group and x["arm"]==arm]
                grouped.append({"group":group,"arm":arm,"event_us":sum(x["event_us"] for x in parts),
                                "MAD_us":sum(x["MAD_us"] for x in parts)})
        r=compare(grouped,f"combined_call_{call}")
        comparisons.append(r)
        by_call.append(r)
    combined=[]
    for group in range(5):
        for arm in ("Aorder","Dready"):
            parts=[x for x in summaries if x["group"]==group and x["arm"]==arm]
            combined.append({"group":group,"arm":arm,"event_us":sum(x["event_us"] for x in parts),
                             "MAD_us":sum(x["MAD_us"] for x in parts),"actual_TP_calls":len(capture["records"]),
                             "forward_calls":len(capture["records"]),"force_backward_calls":len(capture["records"])})
    primary=compare(combined,"combined_all_actual_call_multiplicities")
    comparisons.append(primary)
    tsv(PACK/"COMBINED_FAMILY_SUMMARY.tsv",combined,list(combined[0]))
    unexplained_opposite=primary["stable_positive"] and any(r["stable_negative"] for r in by_call)
    if primary["stable_positive"] and not unexplained_opposite:
        decision="R22F1_LOWOVERHEAD_FAMILY_RESPONSE_POSITIVE"
    elif primary["stable_negative"]:
        decision="R22F1_TARGET_FAMILY_NET_NEGATIVE"
    else:
        decision="R22F1_FAMILY_GAP_UNRESOLVED"
    report={"status":decision,"real_TP_call_count":len(capture["records"]),
            "backward_mode":"BUNDLE32","formal_forward_samples":160,"formal_backward_samples":160,
            "same_input_numerical_pass":True,"direct_fixup_status":"FIXUP_DIRECT_TIMING_NOT_AVAILABLE",
            "unexplained_stable_opposite_callsite":unexplained_opposite,
            "combined":primary,"comparisons":comparisons}
    (PACK/"REPLAY_DECISION.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":decision,"primary_gap_us":primary["median_gap_us"],
                      "primary_relative_gain":primary["median_relative_gain"],
                      "primary_group_gaps_us":[x["gap_us_Aorder_minus_Dready"] for x in primary["groups"]],
                      "primary_MAD_us":primary["larger_arm_group_MAD_estimate_us"],
                      "comparisons":[{k:r[k] for k in ("scope","median_gap_us","median_relative_gain","stable_positive","stable_negative")}
                                     for r in comparisons]},sort_keys=True))


if __name__=="__main__":main()
