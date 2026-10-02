#!/usr/bin/env python3
"""CPU-only R22F formal complete-region paired summary."""

import csv
import json
import statistics
from pathlib import Path

ROOT = Path("/data/c16/awma/r22f_r21a_family_localization_20261002")
RAW = ROOT / "raw"
PACK = Path("/home/huangrulin/workspace/worktrees/accel-sim-awma-r22f-r21a-family-localization-109-v1/docs/vm_tlb/review_packs/AWMA_R22F_R21A_FAMILY_LOCALIZATION_109_V1")


def median_mad(values):
    median = statistics.median(values)
    return median, statistics.median(abs(x-median) for x in values)


def response(rows, baseline, candidate, timer):
    blocks=[]
    for group in range(4):
        values={arm:[float(x[timer]) for x in rows if int(x["group"])==group and x["arm"]==arm]
                for arm in (baseline,candidate)}
        if any(len(v)!=6 for v in values.values()):
            raise RuntimeError("Formal group shape mismatch")
        med={arm:median_mad(values[arm])[0] for arm in values}
        mad={arm:median_mad(values[arm])[1] for arm in values}
        blocks.append({"group":group, "baseline_median_ms":med[baseline],"candidate_median_ms":med[candidate],
                       "baseline_MAD_ms":mad[baseline],"candidate_MAD_ms":mad[candidate],
                       "gap_ms_baseline_minus_candidate":med[baseline]-med[candidate],
                       "relative_gain":(med[baseline]-med[candidate])/med[baseline]})
    gaps=[x["gap_ms_baseline_minus_candidate"] for x in blocks]
    larger_arm_group_mad=max(statistics.median(x["baseline_MAD_ms"] for x in blocks),
                             statistics.median(x["candidate_MAD_ms"] for x in blocks))
    median_gap=statistics.median(gaps)
    return {"baseline":baseline,"candidate":candidate,"timer":timer,"groups":blocks,
            "median_gap_ms":median_gap,
            "median_relative_gain":statistics.median(x["relative_gain"] for x in blocks),
            "direction_all_groups":all(g>0 for g in gaps) or all(g<0 for g in gaps),
            "larger_arm_group_MAD_estimate_ms":larger_arm_group_mad,
            "classification":"CLEAR_FASTER" if all(g>0 for g in gaps) and median_gap>3*larger_arm_group_mad else
                             "CLEAR_SLOWER" if all(g<0 for g in gaps) and -median_gap>3*larger_arm_group_mad else
                             "NO_RESPONSE" if median_gap==0 else "MIXED"}


def main():
    if (PACK/"MEASUREMENT_CONTRACT.md").stat().st_mtime >= (RAW/"FORMAL_RUN_STATUS.json").stat().st_mtime:
        raise RuntimeError("Measurement protocol was not frozen")
    status=json.loads((RAW/"FORMAL_RUN_STATUS.json").read_text())
    if status["status"]!="FORMAL_COMPLETE" or status["formal_count"]!=72:
        raise RuntimeError("Formal run incomplete")
    with (RAW/"FORMAL_COMPLETE_TIMING.tsv").open(newline="") as stream:
        rows=list(csv.DictReader(stream,delimiter="\t"))
    if len(rows)!=72 or not all(x["numerical_pass"]=="True" for x in rows):
        raise RuntimeError("Formal sample/numerical closure failed")
    report={"status":"FORMAL_COMPLETE_72_NUMERIC_PASS", "sample_count":72,
            "protocol":"4 groups x 6 formal samples per arm, 5 warmups per arm, uninstrumented, same AOT mode",
            "responses":[response(rows,base,cand,timer)
                         for base,cand in (("A0","Aorder"),("Aorder","Dready"),("A0","Dready"))
                         for timer in ("wall_ms","cuda_event_ms")]}
    (PACK/"FORMAL_COMPLETE_TIMING.tsv").write_bytes((RAW/"FORMAL_COMPLETE_TIMING.tsv").read_bytes())
    (PACK/"COMPLETE_RESPONSE_SUMMARY.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":report["status"],"responses":[{key:r[key] for key in
          ("baseline","candidate","timer","median_gap_ms","median_relative_gain","classification","larger_arm_group_MAD_estimate_ms")}
          for r in report["responses"]]},sort_keys=True))


if __name__=="__main__":
    main()
