#!/usr/bin/env python3
"""Additive source-backed TP-main versus empty/real fixup decomposition."""

import csv
import json
from collections import defaultdict
from pathlib import Path

from analyze_profile import response, tsv

ROOT = Path("/data/c16/awma/r22f_r21a_family_localization_20261002")
RAW = ROOT / "raw"
PACK = Path("/home/huangrulin/workspace/worktrees/accel-sim-awma-r22f-r21a-family-localization-109-v1/docs/vm_tlb/review_packs/AWMA_R22F_R21A_FAMILY_LOCALIZATION_109_V1")


def main():
    with (RAW/"PROFILE_KERNELS.tsv").open(newline="") as stream:
        kernels=list(csv.DictReader(stream,delimiter="\t"))
    rows=defaultdict(lambda: {"TP_main_forward_us":0.0,"TP_main_backward_us":0.0,
                              "atomic_empty_fixup_forward_us":0.0,"atomic_empty_fixup_backward_us":0.0,
                              "det_real_fixup_forward_us":0.0,"det_real_fixup_backward_us":0.0})
    for k in kernels:
        key=(k["arm"],int(k["block"]),int(k["repeat"]))
        item=rows[key]
        name=k["function"]
        duration=float(k["duration_us"])
        if name.startswith("forward("):
            item["TP_main_forward_us"]+=duration
        elif name.startswith("backward("):
            item["TP_main_backward_us"]+=duration
        elif name.startswith("fixup_forward("):
            item["det_real_fixup_forward_us" if k["arm"]=="Dready" else "atomic_empty_fixup_forward_us"]+=duration
        elif name.startswith("fixup_backward("):
            item["det_real_fixup_backward_us" if k["arm"]=="Dready" else "atomic_empty_fixup_backward_us"]+=duration
    complete=[]
    for (arm,block,repeat),v in sorted(rows.items()):
        entry={"arm":arm,"block":block,"repeat":repeat,**v,
               "TP_main_total_us":v["TP_main_forward_us"]+v["TP_main_backward_us"],
               "atomic_empty_fixup_total_us":v["atomic_empty_fixup_forward_us"]+v["atomic_empty_fixup_backward_us"],
               "det_real_fixup_total_us":v["det_real_fixup_forward_us"]+v["det_real_fixup_backward_us"]}
        complete.append(entry)
    tsv(PACK/"FAMILY_SUBSTRATA.tsv",complete,list(complete[0]))
    metrics=["TP_main_forward_us","TP_main_backward_us","TP_main_total_us",
             "atomic_empty_fixup_total_us","det_real_fixup_forward_us","det_real_fixup_backward_us","det_real_fixup_total_us"]
    summaries=[]
    for baseline,candidate in (("A0","Aorder"),("Aorder","Dready"),("A0","Dready")):
        for metric in metrics:
            r=response(complete,baseline,candidate,metric)
            summaries.append({key:r[key] for key in ("baseline","candidate","metric","median_gap_us","relative_gain",
                                                    "direction_all_blocks","stable_positive","stable_regression","larger_arm_block_MAD_estimate_us")})
    tsv(PACK/"FAMILY_SUBSTRATA_SUMMARY.tsv",summaries,list(summaries[0]))
    print(json.dumps([row for row in summaries if row["baseline"]=="Aorder" and row["candidate"]=="Dready"],sort_keys=True))


if __name__=="__main__": main()
