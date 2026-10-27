"""Pure offline V2: pinned V1 S/F merge plus same-mode cross-profile comparisons.
No acceptance, model, actor, registry-write or Trace-body operations.
"""
import argparse, csv, hashlib, importlib.util, json, math
from pathlib import Path
PARENT_SHA256="5169bf987ea4e69eb07d1d24d1d8ea2e8dc4c48a5020ddbed01a8060b11d972a"

def load_parent():
    p=Path(__file__).with_name("merge_performance_results.py")
    if hashlib.sha256(p.read_bytes()).hexdigest()!=PARENT_SHA256:raise ValueError("frozen V1 merge bytes changed")
    s=importlib.util.spec_from_file_location("pinned_pure_merge_v1",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def cross_profile(records, reference_profile, contracts, required_by_mode):
    m=load_parent();m.need(isinstance(reference_profile,str)and reference_profile,"reference profile required")
    refs={};rows=[];blocked=[]
    def key(r):return m.digest_bytes(m.canonical({"input":r["input_identity_sha256"],"mode":r["mode"],"source":r["source_identity"],"observer":r["pair_population"]["observer_env"]}))
    for r in records:
        if r["accepted"]and r["profile"]==reference_profile:refs.setdefault(key(r),[]).append(r)
    for r in records:
        if not r["accepted"]or r["profile"]==reference_profile:continue
        rr=refs.get(key(r),[])
        if len(rr)!=1:
            blocked.append({"cohort":r["cohort"],"reason":"REFERENCE_MISSING_OR_MULTIPLE; no fastest replicate selection"});continue
        ref=rr[0];contract=contracts.get(r["profile"])
        if contract is None:
            blocked.append({"cohort":r["cohort"],"reason":"MISSING_EXACT_PROFILE_DELTA_CONTRACT"});continue
        a=ref["pair_population"]["background282"];b=r["pair_population"]["background282"]
        actual={k:{"old":a.get(k),"new":b.get(k)}for k in sorted(set(a)|set(b))if a.get(k)!=b.get(k)}
        observer_keys={"-gpgpu_ep_l2_ms_observer","-gpgpu_ep_l2_b0_stats","-gpgpu_ep_l2_m0a_stats","-gpgpu_l2_char_enable","-gpgpu_memlatency_stat"}
        if observer_keys & set(actual):
            blocked.append({"cohort":r["cohort"],"reason":"OBSERVER_OPTION_PROFILE_MISMATCH"});continue
        expected=dict(contract.get("common_delta",{}));expected.update(contract.get("mode_specific_delta",{}).get(r["mode"],{}))
        expected={k:{"old":a.get(k),"new":v}for k,v in expected.items()if a.get(k)!=v}
        if actual!=expected:
            blocked.append({"cohort":r["cohort"],"reason":"PROFILE_282_DELTA_MISMATCH","actual":actual,"expected":expected});continue
        if (r["instructions"],r["CTA"],r["kernel_count"])!=(ref["instructions"],ref["CTA"],ref["kernel_count"]):
            blocked.append({"cohort":r["cohort"],"reason":"DYNAMIC_POPULATION_MISMATCH"});continue
        ratio=ref["cycles"]/r["cycles"]
        rows.append({"input_identity_sha256":r["input_identity_sha256"],"profile":r["profile"],"reference_profile":reference_profile,"mode":r["mode"],
                     "candidate_cohort":r["cohort"],"reference_cohort":ref["cohort"],"candidate_cycles":r["cycles"],"reference_cycles":ref["cycles"],
                     "same_mode_speedup_reference_over_candidate":ratio,"candidate_cycle_reduction_fraction":1-r["cycles"]/ref["cycles"],"slowdown":ratio<1,
                     "exact_282_background_delta":actual,"source5_digest":m.digest_bytes(m.canonical(r["source_identity"])),
                     "observer_env_digest":m.digest_bytes(m.canonical(r["pair_population"]["observer_env"])),"hardware_cost":contract.get("hardware_cost","UNKNOWN")})
    groups={}
    for r in rows:groups.setdefault((r["profile"],r["mode"],r["source5_digest"],r["observer_env_digest"]),[]).append(r)
    summaries=[]
    for key,rs in sorted(groups.items()):
        required=set(required_by_mode.get(key[1],[]));ids=[r["input_identity_sha256"]for r in rs];m.need(len(ids)==len(set(ids)),"duplicate cross-profile input")
        covered=set(ids);complete=bool(required)and covered==required
        gm=math.exp(sum(math.log(r["same_mode_speedup_reference_over_candidate"])for r in rs)/len(rs))
        summaries.append({"profile":key[0],"mode":key[1],"source5_digest":key[2],"observer_env_digest":key[3],"required_common_count":len(required),"observed_count":len(rs),
                          "missing_inputs":sorted(required-covered),"unexpected_inputs":sorted(covered-required),"full_common_set_GM":gm if complete else None,
                          "observed_set_GM_not_global_claim":gm,"common_set_complete":complete,"slowdown_count":sum(r["slowdown"]for r in rs),
                          "worst_speedup":min(r["same_mode_speedup_reference_over_candidate"]for r in rs),"hardware_cost":rs[0]["hardware_cost"],
                          "cost_Pareto":"Numeric physical area/power/clock feasibility UNKNOWN; resource proxies only, no fabricated scalar cost."})
    return {"rows":rows,"summaries":summaries,"blocked":blocked}

def proxy_pareto(summaries, contracts):
    """Optional resource-vector frontier; never infer mm2/power from entry counts."""
    fronts=[];excluded=[];groups={}
    for r in summaries:
        vector=contracts.get(r["profile"],{}).get("hardware_cost_proxy_vector")
        if not r["common_set_complete"] or not isinstance(vector,dict) or not vector or not all(type(v)in(int,float)and math.isfinite(v)and v>=0 for v in vector.values()):
            excluded.append({"profile":r["profile"],"mode":r["mode"],"reason":"NEEDS_FULL_COMMON_SET_AND_EXPLICIT_NONNEGATIVE_COMMON_COST_PROXY_VECTOR"});continue
        key=(r["mode"],r["source5_digest"],r["observer_env_digest"],tuple(sorted(vector)))
        groups.setdefault(key,[]).append((r,vector))
    for key,rows in groups.items():
        for r,cost in rows:
            dominators=[]
            for other,ocost in rows:
                if other is r:continue
                better_speed=other["full_common_set_GM"]>=r["full_common_set_GM"]
                cheaper=all(ocost[k]<=cost[k]for k in cost)
                strict=other["full_common_set_GM"]>r["full_common_set_GM"] or any(ocost[k]<cost[k]for k in cost)
                if better_speed and cheaper and strict:dominators.append(other["profile"])
            fronts.append({"profile":r["profile"],"mode":r["mode"],"full_common_set_GM":r["full_common_set_GM"],"hardware_cost_proxy_vector":cost,"proxy_nondominated":not dominators,"dominated_by":sorted(dominators),"physical_area_power_frontier":"UNKNOWN"})
    return {"resource_proxy_frontier":fronts,"excluded":excluded,"authority":"DESCRIPTIVE_PROXY_ONLY_NOT_HARDWARE_AREA_OR_POWER_PROOF"}


def merge(manifest):
    m=load_parent();base=m.merge(manifest)
    by_mode=manifest.get("required_common_inputs_by_mode",{k:manifest["required_common_inputs"]for k in ("S","F","WV_ZERO_RO")})
    cross=cross_profile(base["records"],manifest["reference_profile"],manifest["profile_contracts"],by_mode)
    reference_groups={}
    for r in base["records"]:
        if r["accepted"] and r["profile"]==manifest["reference_profile"]:
            key=(r["mode"],m.digest_bytes(m.canonical(r["source_identity"])),m.digest_bytes(m.canonical(r["pair_population"]["observer_env"])))
            reference_groups.setdefault(key,[]).append(r["input_identity_sha256"])
    references=[]
    for key,ids in reference_groups.items():
        required=set(by_mode.get(key[0],[]))
        references.append({"profile":manifest["reference_profile"],"mode":key[0],"source5_digest":key[1],"observer_env_digest":key[2],"full_common_set_GM":1.0,"common_set_complete":bool(required)and len(ids)==len(set(ids))and set(ids)==required,"reference_baseline":True})
    cross["reference_summaries_for_cost_frontier"]=references
    cross["cost_proxy_Pareto"]=proxy_pareto(cross["summaries"]+references,manifest["profile_contracts"])
    base.update(schema="EP_FULL_PERF_OFFLINE_MERGE_RESULT_V2",parent_module_sha256=PARENT_SHA256,same_mode_cross_profile=cross,
                interpretation="Report both same-hardware S/F mechanism ratio and same-mode absolute-cycle improvement. A faster F may coexist with a smaller S/F ratio; neither is a free hardware gain.")
    return base

def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument("--manifest",required=True);a.add_argument("--manifest-sha256",required=True);a.add_argument("--output",required=True);args=a.parse_args()
    m=load_parent();data=Path(args.manifest).read_bytes();m.need(m.digest_bytes(data)==args.manifest_sha256,"manifest SHA drift")
    result=merge(m.load_bytes(data));dest=Path(args.output);m.need(not dest.exists()and not dest.is_symlink(),"fresh output required")
    m.need(not any(p.is_symlink()for p in dest.parents),"linked output parent")
    dest.mkdir(parents=True,exist_ok=False);(dest/"SUMMARY.json").write_bytes(m.canonical(result)+b"\n")
    cols=["input_identity_sha256","profile","reference_profile","mode","candidate_cohort","reference_cohort","candidate_cycles","reference_cycles","same_mode_speedup_reference_over_candidate","candidate_cycle_reduction_fraction","slowdown"]
    with(dest/"SAME_MODE_CROSS_PROFILE.csv").open("x",newline="")as f:
        w=csv.DictWriter(f,fieldnames=cols,extrasaction="ignore");w.writeheader();w.writerows(result["same_mode_cross_profile"]["rows"])
    print(json.dumps({"status":result["status"],"output":str(dest),"science_granted":False}))

if __name__=="__main__":main()
