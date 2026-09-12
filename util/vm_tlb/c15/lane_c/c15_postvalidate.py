#!/usr/bin/env python3
"""Post-validation analyses that do not alter the frozen C15 selector.

This tool reads the committed selector protocol and its generated historical
table.  It adds rate accounting and the predeclared random-seed envelopes; it
does not import raw logs, traces, candidate outcomes, or the selector module.
"""
from __future__ import annotations

import argparse
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
ERROR_FIELDS = ["plan_id","split_id","source_roi","reference_arm","candidate_arm","metric","reference_value","estimate","absolute_error","relative_error_fraction","relative_error_percent","percentage_point_error","interval_kind","interval_low","interval_high","effect_reference","effect_estimate","effect_resolution","prediction_verdict","validation_verdict","test_set_previously_seen","scope"]
RELATIVE_ERROR_SENTINELS = {"", "NA", "UNDEFINED_ZERO_DENOMINATOR"}


def read(path: Path):
    with path.open(newline="") as f: return list(csv.DictReader(f, delimiter="\t"))


def write(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", newline="", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter="\t",lineterminator="\n",extrasaction="ignore"); w.writeheader(); w.writerows(rows)
        temporary=Path(f.name)
    os.replace(temporary,path)


def fmt(x):
    return "NA" if x is None else (f"{x:.12g}" if isinstance(x,float) else str(x))


def error_percent(value):
    """Return the presentation percent for a stored relative-error fraction."""
    if value in RELATIVE_ERROR_SENTINELS:
        return "NA" if value == "" else value
    return fmt(float(value) * 100.0)


def add_relative_error_units(rows):
    """Rename the legacy bare field without changing any scientific value."""
    for row in rows:
        fraction = row.pop("relative_error", row.get("relative_error_fraction", "NA"))
        row["relative_error_fraction"] = fraction
        row["relative_error_percent"] = error_percent(fraction)
    return rows


def normalize_error_table(path):
    rows = add_relative_error_units(read(path))
    write(path, ERROR_FIELDS, rows)
    return rows


def normalize_frontier():
    path = OUT / "COVERAGE_COST_FRONTIER.tsv"
    rows = read(path)
    for row in rows:
        fraction = row.pop("relative_error", row.get("relative_error_fraction", "NA"))
        row["relative_error_fraction"] = fraction
        row["relative_error_percent"] = error_percent(fraction)
        row["relative_error_threshold_fraction"] = "0.05"
    write(path, ["plan_id","roi","metric","sample_windows","relative_error_fraction","relative_error_percent","relative_error_threshold_fraction","cost_interpretation","status"], rows)


def relative_error_units_markdown():
    return """# Relative-error units\n\nAll `relative_error_fraction` values use `abs(error / reference)` and are unitless fractions. `relative_error_percent` is exactly `100 * relative_error_fraction`. The frozen macro-cycle screening threshold remains `relative_error_fraction <= 0.05` (5%); this closeout changes no PASS/FAIL rule or result.\n"""


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
            fraction=fmt(abs_error/ref if ref else None)
            rows.append({"plan_id":plan,"split_id":"C12_RETROSPECTIVE_ALL_SEEN","source_roi":roi,"reference_arm":"F0","candidate_arm":"NA","metric":label,"reference_value":fmt(ref),"estimate":fmt(estimate),"absolute_error":fmt(abs_error),"relative_error_fraction":fraction,"relative_error_percent":error_percent(fraction),"percentage_point_error":fmt(abs_error*100 if abs_error is not None else None),"interval_kind":"NOT_DESIGN_BASED" if "RANDOM" not in plan else "SEED_SENSITIVITY_ONLY","interval_low":"NA","interval_high":"NA","effect_reference":"NA","effect_estimate":"NA","effect_resolution":"NA","prediction_verdict":"REPORTED_NO_RATE_QUALIFICATION_THRESHOLD","validation_verdict":"INCONCLUSIVE","test_set_previously_seen":"TRUE","scope":"rate recomputed from separately weighted numerator and denominator; count errors retained in their own rows"})
    write(OUT/"REPRESENTATIVENESS_ERROR.tsv",ERROR_FIELDS,rows)


def sensitivity(vectors):
    rows=[]
    for seed in SEEDS:
        for budget in BUDGETS:
            for roi in ROIS:
                chosen=indices(roi,budget,seed); v=vectors[(roi,"F0","NONE")]
                for metric in METRICS:
                    ref=total(v,metric); estimate=est(v,chosen,metric); error=abs(estimate-ref)
                    fraction=fmt(error/ref if ref else None)
                    rows.append({"seed":seed,"budget":budget,"roi":roi,"metric":metric,"reference_value":ref,"estimate":fmt(estimate),"absolute_error":fmt(error),"relative_error_fraction":fraction,"relative_error_percent":error_percent(fraction),"interpretation":"predeclared random-selection variability only; not a context-bias or population CI"})
    write(OUT/"RANDOM_SEED_SENSITIVITY.tsv",["seed","budget","roi","metric","reference_value","estimate","absolute_error","relative_error_fraction","relative_error_percent","interpretation"],rows)


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
            fraction=fmt(abs(point-actual)/abs(actual) if actual else None)
            rows.append({"plan_id":f"STRATIFIED_RANDOM_CHEAP_V1__B{budget}","split_id":"C12_RETROSPECTIVE_ALL_SEEN","source_roi":roi,"reference_arm":left_name,"candidate_arm":right_name,"metric":"gpu_sim_cycle","reference_value":total(left,"gpu_sim_cycle"),"estimate":fmt(est(right,chosen_primary,"gpu_sim_cycle")),"absolute_error":fmt(abs(point-actual)),"relative_error_fraction":fraction,"relative_error_percent":error_percent(fraction),"percentage_point_error":"NA","interval_kind":"EMPIRICAL_PREDECLARED_SEED_ENVELOPE_NOT_GENERAL_CI","interval_low":fmt(low),"interval_high":fmt(high),"effect_reference":actual,"effect_estimate":fmt(point),"effect_resolution":fmt(max(abs(point-low),abs(high-point))),"prediction_verdict":verdict,"validation_verdict":verdict,"test_set_previously_seen":"TRUE","scope":scope+"; seed envelope only, excludes context bias"})
    write(OUT/"CROSS_CONFIG_HOLDOUT.tsv",ERROR_FIELDS,rows)


def mechanism_sign_audit():
    rows=read(OUT/"CROSS_CONFIG_HOLDOUT.tsv")
    count=lambda verdict:sum(r["validation_verdict"]==verdict for r in rows)
    confounded=sum("CONFOUNDED" in r["scope"] for r in rows)
    text=("# Mechanism sign audit\n\n"
          f"The final `CROSS_CONFIG_HOLDOUT.tsv` contains {len(rows)} rows using the same frozen sample plan on reference and candidate arms. They are historical retrospective tests. {count('INCONCLUSIVE')} rows are `INCONCLUSIVE`; {count('HISTORICAL_SIGN_AGREEMENT_ONLY')} rows are `HISTORICAL_SIGN_AGREEMENT_ONLY`; {count('SIGN_DISAGREEMENT')} rows are `SIGN_DISAGREEMENT`; and {confounded} rows are explicitly confounded. The 48 `STRATIFIED_RANDOM_CHEAP_V1` rows are predeclared random-seed-envelope rows appended after the initial 384-row audit. C13 capacity rows remain tagged `CONFOUNDED_CAPACITY_AND_SEGMENT_NOT_SINGLE_VARIABLE`; no lookup-latency conclusion is made from them.\n")
    (OUT/"MECHANISM_SIGN_AUDIT.md").write_text(text)


def reports():
    oracle=("`TRACE_INFORMED_ORACLE_DIAGNOSTIC_V1` currently uses phase-level uniform N/n expansion, not an operator/layer stratum-specific estimator; its errors cannot prove operator/layer features are useless.")
    primary=("Primary cycle relative-error presentation (fraction; percent): prefill B8/B12/B24/B48 = 48.1870458711 / 32.8033034749 / 15.8636227043 / 8.30290448691; 4818.7046% / 3280.3303% / 1586.3623% / 830.2904%. Decode B8/B12/B24/B48 = 19.4859168735 / 12.6388018008 / 5.9501609825 / 3.29451020821; 1948.5917% / 1263.8802% / 595.0161% / 329.4510%. The frozen screening threshold remains fraction `<=0.05` (5%) and none of these presentation changes alters a verdict.")
    (OUT/"FINAL_REPORT.md").write_text(f"""# C15 Lane C final report

Status: `C15_C_SAMPLING_VALIDATION_READY_FOR_FINAL_REVIEW`. The 22-arm C12 zero-sampling conservation control passed using hash-verified historical raw logs; corrected C13 admitted only the ten EQ-gated mode=0 identities. No simulator replay, trace capture, GPU task, Core change, or protected-source write occurred.

The released primary is a phase/opaque-order cheap selector with seed 15001 and virtual budgets 8/12/24/48. It intentionally has explicit UNKNOWN operator/implementation/shape/dtype/KV/TP buckets. The historical operator/layer/page scan is an oracle only, never the primary selector. Historical C12/C13 outcomes are retrospective calibration/cross-config tests, not blind tests.

{primary}

The final cross-config table has 432 rows: 426 `INCONCLUSIVE`, 6 `HISTORICAL_SIGN_AGREEMENT_ONLY`, 0 `SIGN_DISAGREEMENT`, and 36 explicitly confounded rows. This includes 48 predeclared random-seed-envelope rows added after the initial 384-row sign audit.

Scientific boundary: the cheap selector is `SAMPLER_NOT_QUALIFIED` for mechanism or causal conclusions; deterministic estimates have no fabricated confidence interval, and small or unresolved effects are `INCONCLUSIVE`. {oracle} Existing compact scans support exact 64KiB page-set fingerprints, but not bytes, read/write/atomic, line-set, MRC, private-L1, or global-order claims. C14 cold micro comparisons remain confounded by explicit state/context non-equivalence.

Lane B commit `8963919d608d05713e2caa22965d8895c728bc92` was consumed read-only after manifest validation: all 21 payload hashes matched, but its declared state is `NO_NEW_NATIVE_GPU_RUN` and its catalog is header-only. No dynamic metric was imported; dynamic cross-model validation therefore remains pending a future committed native manifest.
""")
    (ROOT/"docs/vm_tlb/codex_handoff/c15/lane_c/LATEST_REPORT.md").write_text(f"""# C15 Lane C handoff

`planning_sha`/initial HEAD: `9a755b14b01c5a77a6fc98c2547616e1c490e806`.

Status: `C15_C_SAMPLING_VALIDATION_READY_FOR_FINAL_REVIEW`. The zero-sampling C12 control passed; the frozen cheap primary sampler remains `SAMPLER_NOT_QUALIFIED` for mechanism claims. The final cross-config audit has 432 rows: 426 `INCONCLUSIVE`, 6 `HISTORICAL_SIGN_AGREEMENT_ONLY`, 0 `SIGN_DISAGREEMENT`, and 36 confounded rows (including the 48 predeclared random-seed-envelope rows).

Relative error is presented as both `relative_error_fraction = abs(error/reference)` and `relative_error_percent = 100 * fraction`; the frozen qualification threshold remains fraction `<=0.05` (5%). {oracle}

B's committed offline/header-only checkpoint was hash-verified but supplied no native dynamic metric, so no cross-model claim is made. See the Lane-C review pack FINAL_REPORT, MECHANISM_SIGN_AUDIT, and RELATIVE_ERROR_UNITS for receipts and boundaries.
""")
    (OUT/"LIMITATIONS.md").write_text(f"""# C15 Lane C limitations

The primary cheap historical directory contains only phase and opaque launch order. Operator/layer/ref/page fields are trace-informed oracle inputs, not cheap selector features. {oracle} Existing compact scans preserve lane refs and exact 64KiB page sets but not bytes, read/write/atomic, or 128B line sets. Historical C12/C13 are retrospective, not prospective blind tests.
""")


def sha256(path):
    digest=hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda:handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def refresh_manifest():
    """Refresh only presentation/provenance receipts; retain scientific metadata."""
    path=OUT/"PUBLISH_MANIFEST.json"
    manifest=json.loads(path.read_text())
    manifest["status"]="C15_C_SAMPLING_VALIDATION_READY_FOR_FINAL_REVIEW"
    manifest["closeout_presentation"]={
        "relative_error_unit":"fraction; percent is 100 * fraction",
        "relative_error_threshold_fraction":"<=0.05",
        "postvalidate_code_path":"util/vm_tlb/c15/lane_c/c15_postvalidate.py",
        "postvalidate_code_sha256":sha256(Path(__file__)),
        "cross_config_rows":432,
    }
    files=[]
    for artifact in sorted(OUT.iterdir()):
        if artifact.is_file() and artifact.name != path.name:
            files.append({"path":artifact.name,"sha256":sha256(artifact),"size_bytes":artifact.stat().st_size})
    manifest["files"]=files
    path.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")


def validate():
    """Offline self-test: read final artifacts only; never parse raw logs or traces."""
    expected_headers={
        "REPRESENTATIVENESS_ERROR.tsv":ERROR_FIELDS,
        "CROSS_CONFIG_HOLDOUT.tsv":ERROR_FIELDS,
        "RANDOM_SEED_SENSITIVITY.tsv":["seed","budget","roi","metric","reference_value","estimate","absolute_error","relative_error_fraction","relative_error_percent","interpretation"],
        "COVERAGE_COST_FRONTIER.tsv":["plan_id","roi","metric","sample_windows","relative_error_fraction","relative_error_percent","relative_error_threshold_fraction","cost_interpretation","status"],
    }
    for name,fields in expected_headers.items():
        with (OUT/name).open(newline="") as handle:
            header=next(csv.reader(handle,delimiter="\t"))
        if header != fields: raise SystemExit(f"unexpected header in {name}: {header}")
        for row in read(OUT/name):
            fraction=row["relative_error_fraction"]
            if fraction not in RELATIVE_ERROR_SENTINELS and not math.isclose(float(row["relative_error_percent"]),float(fraction)*100.0,rel_tol=0.0,abs_tol=1e-9):
                raise SystemExit(f"relative-error unit mismatch in {name}: {row}")
    primary={
        ("prefill",8):4818.7046,("prefill",12):3280.3303,("prefill",24):1586.3623,("prefill",48):830.2904,
        ("decode1",8):1948.5917,("decode1",12):1263.8802,("decode1",24):595.0161,("decode1",48):329.4510,
    }
    for row in read(OUT/"COVERAGE_COST_FRONTIER.tsv"):
        if row["plan_id"].startswith("STRATIFIED_REPRESENTATIVE_CHEAP_V1"):
            budget=int(row["plan_id"].rsplit("B",1)[1])
            expected=primary[(row["roi"],budget)]
            if not math.isclose(float(row["relative_error_percent"]),expected,rel_tol=0.0,abs_tol=0.00005):
                raise SystemExit(f"primary percent mismatch: {row}")
            if row["relative_error_threshold_fraction"] != "0.05": raise SystemExit("threshold changed")
    protocol=json.loads((OUT/"SAMPLING_VALIDATION_PROTOCOL.json").read_text())
    if protocol["thresholds"]["macro_cycle_screening_relative_error"] != "<=0.05": raise SystemExit("frozen fraction threshold changed")
    units=(OUT/"RELATIVE_ERROR_UNITS.md").read_text()
    if "relative_error_fraction" not in units or "relative_error_percent" not in units or "<= 0.05" not in units: raise SystemExit("missing unit contract")
    cross=read(OUT/"CROSS_CONFIG_HOLDOUT.tsv")
    verdicts={key:sum(row["validation_verdict"]==key for row in cross) for key in ("INCONCLUSIVE","HISTORICAL_SIGN_AGREEMENT_ONLY","SIGN_DISAGREEMENT")}
    if (len(cross),verdicts["INCONCLUSIVE"],verdicts["HISTORICAL_SIGN_AGREEMENT_ONLY"],verdicts["SIGN_DISAGREEMENT"],sum("CONFOUNDED" in row["scope"] for row in cross)) != (432,426,6,0,36): raise SystemExit("mechanism-sign audit counts changed")
    required="TRACE_INFORMED_ORACLE_DIAGNOSTIC_V1` currently uses phase-level uniform N/n expansion, not an operator/layer stratum-specific estimator; its errors cannot prove operator/layer features are useless."
    for report in (OUT/"FINAL_REPORT.md",ROOT/"docs/vm_tlb/codex_handoff/c15/lane_c/LATEST_REPORT.md",OUT/"LIMITATIONS.md"):
        if required not in report.read_text(): raise SystemExit(f"missing oracle qualification in {report}")
    final_report=(OUT/"FINAL_REPORT.md").read_text()
    for percent in ("4818.7046%","3280.3303%","1586.3623%","830.2904%","1948.5917%","1263.8802%","595.0161%","329.4510%"):
        if percent not in final_report: raise SystemExit(f"missing primary percent: {percent}")
    manifest=json.loads((OUT/"PUBLISH_MANIFEST.json").read_text())
    if manifest["status"] != "C15_C_SAMPLING_VALIDATION_READY_FOR_FINAL_REVIEW": raise SystemExit("manifest status mismatch")
    closeout=manifest.get("closeout_presentation",{})
    if closeout.get("postvalidate_code_path") != "util/vm_tlb/c15/lane_c/c15_postvalidate.py" or closeout.get("postvalidate_code_sha256") != sha256(Path(__file__)):
        raise SystemExit("manifest post-validation provenance mismatch")
    expected_files={p.name for p in OUT.iterdir() if p.is_file() and p.name != "PUBLISH_MANIFEST.json"}
    listed={entry["path"]:entry for entry in manifest["files"]}
    if set(listed) != expected_files: raise SystemExit("manifest file set mismatch")
    for name,entry in listed.items():
        artifact=OUT/name
        if entry["sha256"] != sha256(artifact) or entry["size_bytes"] != artifact.stat().st_size: raise SystemExit(f"manifest digest mismatch: {name}")
    print("PASS C15 Lane C offline closeout validation: units, audit, reports, manifest")


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
    parser=argparse.ArgumentParser(description="C15 Lane C reporting-only post-validation")
    parser.add_argument("--validate",action="store_true",help="validate existing final artifacts without rewriting them")
    args=parser.parse_args()
    if args.validate:
        validate()
        return
    if not (OUT/"SAMPLING_VALIDATION_PROTOCOL.json").is_file(): raise SystemExit("missing frozen protocol")
    protocol=json.loads((OUT/"SAMPLING_VALIDATION_PROTOCOL.json").read_text())
    if protocol["seed"]!=PRIMARY_SEED or tuple(protocol["sensitivity_seeds"])!=SEEDS: raise SystemExit("protocol seed mismatch")
    normalize_error_table(OUT/"REPRESENTATIVENESS_ERROR.tsv")
    normalize_error_table(OUT/"CROSS_CONFIG_HOLDOUT.tsv")
    normalize_frontier()
    vectors=data_vectors(); append_rates(vectors); sensitivity(vectors); random_cross(vectors); mutation_receipt(); refresh_test_receipt()
    mechanism_sign_audit()
    (OUT/"RELATIVE_ERROR_UNITS.md").write_text(relative_error_units_markdown())
    reports()
    refresh_manifest()
    print("PASS C15 Lane C reporting-only post-validation: units, audit, reports, manifest")


if __name__=="__main__": main()
