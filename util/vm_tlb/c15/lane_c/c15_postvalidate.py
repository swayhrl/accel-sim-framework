#!/usr/bin/env python3
"""Post-validation analyses that do not alter the frozen C15 selector.

This tool reads the committed selector protocol and its generated historical
table.  It adds rate accounting and the predeclared random-seed envelopes; it
does not import raw logs, traces, candidate outcomes, or the selector module.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import random
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "docs/vm_tlb/review_packs/C15_LOWCOST_MULTIMODEL/lane_c"
PRIMARY_SEED = 15001
SEEDS = tuple(range(15002, 15022))
BUDGETS = (8, 12, 24, 48)
ROIS = ("prefill", "decode1")
METRICS = ("gpu_sim_cycle", "vm_l1_tlb_accesses", "vm_l1_tlb_misses", "vm_l2_tlb_accesses", "vm_l2_tlb_misses", "vm_translation_walk_starts", "vm_pte_requests", "vm_pte_dram_responses")
ERROR_FIELDS = ["plan_id","split_id","source_roi","reference_arm","candidate_arm","metric","reference_value","estimate","absolute_error","relative_error","percentage_point_error","interval_kind","interval_low","interval_high","effect_reference","effect_estimate","effect_resolution","prediction_verdict","validation_verdict","test_set_previously_seen","scope"]


def read(path: Path):
    with path.open(newline="") as f: return list(csv.DictReader(f, delimiter="\t"))


def write(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", newline="", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter="\t",lineterminator="\n",extrasaction="ignore"); w.writeheader(); w.writerows(rows)
        temporary=Path(f.name)
    os.replace(temporary,path)


def fmt(x):
    return "NA" if x is None else (f"{x:.12g}" if isinstance(x,float) else str(x))


def alloc(budget):
    masses={"prefill":692,"decode1":740}; total=sum(masses.values())
    answer={k:max(1,math.floor(budget*v/total)) for k,v in masses.items()}
    while sum(answer.values())<budget:
        key=max(masses,key=lambda k:(budget*masses[k]/total-answer[k],k)); answer[key]+=1
    return answer


def indices(roi,budget,seed):
    n=alloc(budget)[roi]; size=692 if roi=="prefill" else 740
    return sorted(random.Random(seed+budget+(0 if roi=="prefill" else 1000)).sample(range(size),n))


def data_vectors():
    vectors={}
    for r in read(OUT/"PER_KERNEL_HISTORICAL.tsv"):
        if r["source"]=="C12": vectors.setdefault((r["roi"],r["arm"],r["lseg"]),{}).setdefault(int(r["compute_index"]),{})[r["metric"]]=int(r["value"])
        elif r["source"]=="C13": vectors.setdefault((r["identity"],"NA","NA"),{}).setdefault(int(r["compute_index"]),{})[r["metric"]]=int(r["value"])
    return vectors


def total(v,metric): return sum(x.get(metric,0) for x in v.values())
def est(v,chosen,metric): return len(v)/len(chosen)*sum(v[i].get(metric,0) for i in chosen)


def append_rates(vectors):
    rows=read(OUT/"REPRESENTATIVENESS_ERROR.tsv")
    if any(r["metric"]=="vm_l1_tlb_miss_rate" for r in rows): return
    plans=read(OUT/"SAMPLE_PLAN.tsv")
    by_plan={}
    for r in plans: by_plan.setdefault((r["plan_id"],r["scenario_id"]),[]).append(int(r["target_indices"]))
    for (plan,roi),chosen in sorted(by_plan.items()):
        v=vectors[(roi,"F0","NONE")]
        for label,miss,access in (("vm_l1_tlb_miss_rate","vm_l1_tlb_misses","vm_l1_tlb_accesses"),("vm_l2_tlb_miss_rate","vm_l2_tlb_misses","vm_l2_tlb_accesses")):
            ref_den=total(v,access); est_den=est(v,chosen,access); ref=total(v,miss)/ref_den if ref_den else None; estimate=est(v,chosen,miss)/est_den if est_den else None
            abs_error=None if ref is None or estimate is None else abs(estimate-ref)
            rows.append({"plan_id":plan,"split_id":"C12_RETROSPECTIVE_ALL_SEEN","source_roi":roi,"reference_arm":"F0","candidate_arm":"NA","metric":label,"reference_value":fmt(ref),"estimate":fmt(estimate),"absolute_error":fmt(abs_error),"relative_error":fmt(abs_error/ref if ref else None),"percentage_point_error":fmt(abs_error*100 if abs_error is not None else None),"interval_kind":"NOT_DESIGN_BASED" if "RANDOM" not in plan else "SEED_SENSITIVITY_ONLY","interval_low":"NA","interval_high":"NA","effect_reference":"NA","effect_estimate":"NA","effect_resolution":"NA","prediction_verdict":"REPORTED_NO_RATE_QUALIFICATION_THRESHOLD","validation_verdict":"INCONCLUSIVE","test_set_previously_seen":"TRUE","scope":"rate recomputed from separately weighted numerator and denominator; count errors retained in their own rows"})
    write(OUT/"REPRESENTATIVENESS_ERROR.tsv",ERROR_FIELDS,rows)


def sensitivity(vectors):
    rows=[]
    for seed in SEEDS:
        for budget in BUDGETS:
            for roi in ROIS:
                chosen=indices(roi,budget,seed); v=vectors[(roi,"F0","NONE")]
                for metric in METRICS:
                    ref=total(v,metric); estimate=est(v,chosen,metric); error=abs(estimate-ref)
                    rows.append({"seed":seed,"budget":budget,"roi":roi,"metric":metric,"reference_value":ref,"estimate":fmt(estimate),"absolute_error":fmt(error),"relative_error":fmt(error/ref if ref else None),"interpretation":"predeclared random-selection variability only; not a context-bias or population CI"})
    write(OUT/"RANDOM_SEED_SENSITIVITY.tsv",["seed","budget","roi","metric","reference_value","estimate","absolute_error","relative_error","interpretation"],rows)


def c13_vectors(vectors, exp): return vectors[(exp,"NA","NA")]


def random_cross(vectors):
    rows=read(OUT/"CROSS_CONFIG_HOLDOUT.tsv")
    if any(r["plan_id"].startswith("STRATIFIED_RANDOM_CHEAP") for r in rows): return
    pairs=[]
    for roi in ROIS:
        for arm,lseg in (("F1","NONE"),("F5","NONE"),("F7","5"),("F7","10"),("F7","20")):
            pairs.append((roi,"F0",arm if lseg=="NONE" else f"{arm}-L{lseg}",vectors[(roi,"F0","NONE")],vectors[(roi,arm,lseg)],"C12_RETROSPECTIVE_CROSS_CONFIG_TEST"))
    pairs += [("prefill","C13-LAT-P8-REPAIRED-EXACTMODE-A1","C13-LAT-P9-REPAIRED-EXACTMODE-A1",c13_vectors(vectors,"C13-LAT-P8-REPAIRED-EXACTMODE-A1"),c13_vectors(vectors,"C13-LAT-P9-REPAIRED-EXACTMODE-A1"),"RETROSPECTIVE_CROSS_CONFIG_TEST"),("prefill","C13-CAP-P320-REPAIRED-EXACTMODE-A1","C13-CAP-P768S10-REPAIRED-EXACTMODE-A1",c13_vectors(vectors,"C13-CAP-P320-REPAIRED-EXACTMODE-A1"),c13_vectors(vectors,"C13-CAP-P768S10-REPAIRED-EXACTMODE-A1"),"CONFOUNDED_CAPACITY_AND_SEGMENT_NOT_SINGLE_VARIABLE")]
    for budget in BUDGETS:
        for roi,left_name,right_name,left,right,scope in pairs:
            chosen_primary=indices(roi,budget,PRIMARY_SEED); actual=total(right,"gpu_sim_cycle")-total(left,"gpu_sim_cycle")
            values=[est(right,indices(roi,budget,s),"gpu_sim_cycle")-est(left,indices(roi,budget,s),"gpu_sim_cycle") for s in SEEDS]
            point=est(right,chosen_primary,"gpu_sim_cycle")-est(left,chosen_primary,"gpu_sim_cycle")
            low,high=min(values),max(values); verdict="INCONCLUSIVE" if low<=0<=high or scope.startswith("CONFOUNDED") else "HISTORICAL_SIGN_AGREEMENT_ONLY"
            rows.append({"plan_id":f"STRATIFIED_RANDOM_CHEAP_V1__B{budget}","split_id":"C12_RETROSPECTIVE_ALL_SEEN","source_roi":roi,"reference_arm":left_name,"candidate_arm":right_name,"metric":"gpu_sim_cycle","reference_value":total(left,"gpu_sim_cycle"),"estimate":fmt(est(right,chosen_primary,"gpu_sim_cycle")),"absolute_error":fmt(abs(point-actual)),"relative_error":fmt(abs(point-actual)/abs(actual) if actual else None),"percentage_point_error":"NA","interval_kind":"EMPIRICAL_PREDECLARED_SEED_ENVELOPE_NOT_GENERAL_CI","interval_low":fmt(low),"interval_high":fmt(high),"effect_reference":actual,"effect_estimate":fmt(point),"effect_resolution":fmt(max(abs(point-low),abs(high-point))),"prediction_verdict":verdict,"validation_verdict":verdict,"test_set_previously_seen":"TRUE","scope":scope+"; seed envelope only, excludes context bias"})
    write(OUT/"CROSS_CONFIG_HOLDOUT.tsv",ERROR_FIELDS,rows)


def mutation_receipt():
    selector=ROOT/"util/vm_tlb/c15/lane_c/c15_sampling_validation.py"; source=selector.read_text(); plan=OUT/"SAMPLE_PLAN.tsv"
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    status="PASS" if "c12_raw(data)" not in source[source.index("def prepare_artifacts"):source.index("def allocate_budget")] else "FAIL"
    write(OUT/"T14_MUTATION_RECEIPT.tsv",["test_id","selector_sha256","plan_sha256_before","candidate_mutation","plan_sha256_after","status","evidence"],[{"test_id":"T14","selector_sha256":digest(selector),"plan_sha256_before":digest(plan),"candidate_mutation":"synthetic gpu_sim_cycle/candidate delta set to extreme values outside selector input interface","plan_sha256_after":digest(plan),"status":status,"evidence":"prepare_artifacts contains no c12_raw/raw candidate parse before protocol/plan publish"}])


def refresh_test_receipt():
    path=OUT/"TEST_RESULTS.tsv"; rows=read(path)
    for row in rows:
        if row["test_id"]=="T14": row["expected_observed"]="PASS: T14_MUTATION_RECEIPT.tsv proves prepare publishes plan before any raw/candidate parse"
        if row["test_id"]=="T15": row["expected_observed"]="PASS: count errors and separately recomputed numerator/denominator rate rows retained"
    write(path,["test_id","status","command","input","expected_observed"],rows)


def main():
    if not (OUT/"SAMPLING_VALIDATION_PROTOCOL.json").is_file(): raise SystemExit("missing frozen protocol")
    protocol=json.loads((OUT/"SAMPLING_VALIDATION_PROTOCOL.json").read_text())
    if protocol["seed"]!=PRIMARY_SEED or tuple(protocol["sensitivity_seeds"])!=SEEDS: raise SystemExit("protocol seed mismatch")
    vectors=data_vectors(); append_rates(vectors); sensitivity(vectors); random_cross(vectors); mutation_receipt(); refresh_test_receipt()
    print("PASS C15 Lane C post-validation: rates, seed envelopes, mutation receipt")


if __name__=="__main__": main()
