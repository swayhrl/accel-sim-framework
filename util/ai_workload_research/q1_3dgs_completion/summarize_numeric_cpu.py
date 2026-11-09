"""CPU-only prefix numerical observations; no invented tolerance/quality PASS."""
import os
os.sched_setaffinity(0,{22,23})
import json,math,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(os.environ.get("Q1_EXECUTION_OUT",ROOT/"docs/ai_workload_research/runs/AI_ARCH_Q1_COMPLETION_109_V1"))
def main():
    receipt=json.loads((OUT/"RESOURCE_RECEIPT.json").read_text())
    refs={};results=[];initial=[]
    for j in receipt["jobs"]:
        if j["job"].get("sample_pool")!="FORMAL" or j.get("returncode")!=0:continue
        d=OUT/".private/JOBS"/j["job"]["id"];r=json.loads((d/"RESULT.json").read_text())
        restore=json.loads((d/"RESTORE_INITIAL.json").read_text())
        initial.append(dict(job=j["job"]["id"],exact_initial_semantic_state=restore["semantic_fingerprint_equal"],
            finite_parameter_moment_fields=all(r["finite_state_checks"].values()),final_hash=r["final_semantic_fingerprint"]))
        phase=j["job"]["phase"]
        if phase not in refs:refs[phase]=(j,r)
        ref,rr=refs[phase]
        fields={}
        for k,a in rr["numerical_samples"].items():
            b=r["numerical_samples"].get(k)
            if b is None or len(a)!=len(b):fields[k]=dict(identity="SHAPE_OR_FIELD_MISMATCH");continue
            fields[k]=dict(count=len(a),different_bits=sum(struct.pack("!d",x)!=struct.pack("!d",y) for x,y in zip(a,b)),
                max_abs=max((abs(x-y) for x,y in zip(a,b)),default=0),
                finite=all(math.isfinite(x) and math.isfinite(y) for x,y in zip(a,b)))
        results.append(dict(reference_job=ref["job"]["id"],job=j["job"]["id"],phase=phase,policy=j["job"]["OMP_cap"],fields=fields,
            same_full_final_semantic_hash=rr["final_semantic_fingerprint"]==r["final_semantic_fingerprint"]))
    output=dict(scope="First128 parameter/64moment values perfield only, plus full-state hashes; cannot localize first native divergence or assert quality equivalence",
        initial_states=initial,comparisons=results,tolerance_applied=None,numeric_equivalence_PASS_not_claimed=True)
    (OUT/"NUMERICAL_OBSERVATIONS.json").write_text(json.dumps(output,indent=2)+"\n")
    print(json.dumps(dict(formal_jobs=len(initial),all_initial_states_exact=all(x["exact_initial_semantic_state"] for x in initial),
       finite_all_saved_parameter_moment_fields=all(x["finite_parameter_moment_fields"] for x in initial))))
if __name__=="__main__":main()
