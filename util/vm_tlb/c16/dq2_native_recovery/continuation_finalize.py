#!/usr/bin/env python3
"""CPU-only MP03_B continuation fail-closed result and durable raw closeout."""
import csv
import hashlib
import json
import sys
from pathlib import Path

from analysis import compare_rows
from publish import publish

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
PACK=ROOT/"docs/vm_tlb/review_packs/C16_DQ2_NATIVE_RECOVERY_MP03B_CONTINUATION_109_V1"
OLD=ROOT/"docs/vm_tlb/review_packs/C16_DQ2_NATIVE_RECOVERY_109_V1"
PREEXEC="31af510d85e89344acf6e4c519ae5f0419d50d40"
RESULT="a12bbfa4609ece57fadde107f9fd2e3bc0380cdf"

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()
def load(path):return json.loads(Path(path).read_text())
def save(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")
def tsv(path,rows,fields):
    with path.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=fields,delimiter="\t",lineterminator="\n")
        writer.writeheader();writer.writerows(rows)

def main(raw):
    contract=load(PACK/"CONTINUATION_PREEXEC_CONTRACT.json")
    run=load(raw/"RUN_IDENTITY.json")
    status=load(raw/"EXECUTION_STATUS.json")
    arm=load(raw/"MP03_B.json")
    before=load(raw/"CACHE_BEFORE.json")
    after=load(raw/"CACHE_AFTER.json")
    usage=load(raw/"GPU_USAGE_RECEIPT.json")
    assert run["continuation_preexec_commit"]==PREEXEC
    assert run["continuation_preexec_tree"]=="cab0090fe289758c1213d3b8fd3b099238fcd3f0"
    assert run["old_result_commit"]==RESULT and run["only_new_arm"]=="MP03_B"
    assert status["decision"]=="DQ2_EXECUTION_IDENTITY_FAIL" and status["old_three_arms_rerun"] is False
    assert arm["status"]=="ERROR" and arm["error"]=="MP03_B cache identity did not converge to accepted post-warmup authority"
    assert len(arm["warmups"])==2 and len(arm["formal_samples"])==0
    pre=arm["cache_lifecycle"]["pre_warmup"]
    post=arm["cache_lifecycle"]["after_warmup"]
    assert pre["status"]=="PASS" and post["status"]=="AFTER_WARMUP_FINAL_IDENTITY_FAIL"
    assert pre["actual_path"]==post["actual_path"]==contract["aot_pre_warmup"]["path"]
    assert post["expected_path"]==contract["after_warmup_final"]["path"]
    assert post["accepted_final_content_sha256"]==contract["after_warmup_final"]["content_sha256"]
    assert arm["cache_lifecycle"]["graph_count_after_warmup"]==0
    compiled=arm["compiled_qwen2model_after_warmup"]
    assert any(x["class"]=="Qwen2Model" and not x["do_not_compile"] and (x["compiled"] or x["aot_compiled_fn"]) for x in compiled)
    assert arm["runtime"]["enforce_eager"] is False and arm["runtime"]["compilation_mode"]=="VLLM_COMPILE" and arm["runtime"]["backend"]=="inductor" and arm["runtime"]["cudagraph_mode"]=="NONE"
    assert arm["backend"]["attention_impl"]==["FlashAttentionImpl"] and arm["backend"]["linear_method"]==["UnquantizedLinearMethod"]
    assert before["four_bound_roots"]["status"]==after["four_bound_roots"]["status"]=="PASS"
    assert before["pre_warmup_aot_root"]["content_identity_sha256"]==after["pre_warmup_aot_root"]["content_identity_sha256"]==contract["aot_pre_warmup"]["content_sha256"]
    for b,a in zip(before["four_bound_roots"]["rows"],after["four_bound_roots"]["rows"]):
        assert b["actual_sha256"]==a["actual_sha256"]==b["expected_sha256"]
    old_raw=Path(run["old_raw"])
    old_index=load(OLD/"RAW_INDEX.json")
    for name in ("MP02_A.json","MP02_B.json","MP03_A.json"):
        path=old_raw/name
        assert sha(path)==next(x["sha256"] for x in old_index if x["local_path"]==str(path))
        assert sha(path)==run["old_arm_sha256"][name]
    accepted=load(OLD/"PREEXEC_CONTRACT.json")["accepted_outputs"]
    ids=[f"TRAIN_A_DISCOVERY_{i:02d}" for i in range(4)]
    old_a=load(old_raw/"MP03_A.json")
    ref_a=load(accepted["MP03_A"]["path"])["formal_rows"]
    ref_b=load(accepted["MP03_B"]["path"])["formal_rows"]
    canary=[]
    for i,warmup in enumerate(arm["warmups"]):
        against_old,_=compare_rows(old_a["warmups"][i]["rows"],warmup["rows"],"MP03",ids)
        against_a,_=compare_rows(ref_a,warmup["rows"],"MP03",ids)
        against_b,_=compare_rows(ref_b,warmup["rows"],"MP03",ids)
        canary.append({"warmup_index":i,"old_mp03_a_pass":against_old,"accepted_9122_a_pass":against_a,
                       "accepted_9122_b_pass":against_b,"row_count":len(warmup["rows"]),
                       "duration_role":"WARMUP_CORRECTNESS_ONLY_NOT_SCIENCE"})
    correctness={"warmup_canaries":canary,"warmup_pair_pass":all(x["old_mp03_a_pass"] and x["accepted_9122_a_pass"] and x["accepted_9122_b_pass"] for x in canary),
                 "formal_correctness":"NOT_EVALUATED_ZERO_FORMAL_SAMPLES","point_science_valid":False,
                 "frozen_tolerance":"abs(A-B)<=0.05+0.01*abs(A); four rows and 32 tokens exact"}
    save(raw/"CORRECTNESS_RECEIPT.json",correctness);save(PACK/"CORRECTNESS_RECEIPT.json",correctness)
    cache={"four_accepted_roots_before_after":"CONTENT_SHA_UNCHANGED_PASS",
           "pre_warmup_aot_content_sha256":before["pre_warmup_aot_root"]["content_identity_sha256"],
           "post_run_aot_content_sha256":after["pre_warmup_aot_root"]["content_identity_sha256"],
           "pre_warmup_gate":pre,"after_warmup_gate":post,
           "accepted_final_root_content_sha256":post["accepted_final_content_sha256"]}
    save(raw/"CACHE_IDENTITY_BEFORE_AFTER.json",cache);save(PACK/"CACHE_IDENTITY_BEFORE_AFTER.json",cache)
    identity={"status":"DQ2_EXECUTION_IDENTITY_FAIL","scope":"MP03_B_ONLY",
              "mode_b_config_before_and_after_warmup":"VLLM_COMPILE_INDUCTOR_CUDAGRAPH_NONE",
              "compiled_qwen2model_after_warmup":compiled,"graph_count_after_warmup":0,
              "attention_impl":arm["backend"]["attention_impl"],"linear_method":arm["backend"]["linear_method"],
              "pre_warmup_aot_identity":"PASS","post_warmup_final_cache_identity":"FAIL_NOT_CONVERGED",
              "formal_samples":0,"old_three_arms_unchanged":True}
    save(raw/"EXECUTION_IDENTITY_RECEIPT.json",identity);save(PACK/"EXECUTION_IDENTITY_RECEIPT.json",identity)
    warm_rows=[{"point":"MP03","mode":"B","warmup_index":i,"request_gpu_elapsed_ms":w["request_gpu_elapsed_ms"],
                "row_count":len(w["rows"]),"role":"CORRECTNESS_CANARY_NOT_SCIENCE"} for i,w in enumerate(arm["warmups"])]
    tsv(raw/"WARMUP_CANARIES.tsv",warm_rows,["point","mode","warmup_index","request_gpu_elapsed_ms","row_count","role"])
    tsv(PACK/"WARMUP_CANARIES.tsv",warm_rows,["point","mode","warmup_index","request_gpu_elapsed_ms","row_count","role"])
    tsv(PACK/"FORMAL_SAMPLES.tsv",[{"point":"MP03","mode":"B","sample_index":"NA","request_gpu_elapsed_ms":"NA","status":"NOT_EXECUTED_AFTER_WARMUP_IDENTITY_FAIL"}],
        ["point","mode","sample_index","request_gpu_elapsed_ms","status"])
    old_metrics=load(OLD/"DQ2_METRICS.json")
    combined={"status":"DQ2_NATIVE_RECOVERY_PARTIAL_PRESERVED","new_MP03_B_formal_samples":0,
              "original_result_commit":RESULT,"original_run_id":Path(run["old_raw"]).name,
              "old_MP02_A_median_ms":old_metrics["MP02_B1"]["A"]["median_ms"],
              "old_MP02_B_median_ms":old_metrics["MP02_B1"]["B"]["median_ms"],
              "old_MP03_A_raw_median_diagnostic_only_ms":old_metrics["MP03_B4"]["A_raw_diagnostic_only"]["median_ms"],
              "MP03_B_median":"NOT_AVAILABLE","ThroughputScale_A":"NOT_IDENTIFIABLE_B4_POINT_INCOMPLETE",
              "ThroughputScale_B":"NOT_IDENTIFIABLE_B4_B_MISSING","interaction":"NOT_IDENTIFIABLE",
              "MP03_B_over_A_ratio":"NOT_IDENTIFIABLE","MP03_A_vs_B_time_reduction":"NOT_IDENTIFIABLE",
              "old_results_referenced_by_sha_not_replayed":True}
    save(raw/"COMBINED_DQ2_METRICS.json",combined);save(PACK/"COMBINED_DQ2_METRICS.json",combined)
    save(PACK/"RUN_IDENTITY.json",run);save(PACK/"GPU_USAGE_RECEIPT.json",usage)
    final={"goal":"C16_DQ2_NATIVE_RECOVERY_109_V1_MP03B_CONTINUATION","decision":"DQ2_EXECUTION_IDENTITY_FAIL",
           "reason":"MP03_B local_cache_dir stayed at pinned AOT hash root after two warmups; accepted 9122 final c975 cache path was not reached",
           "pre_warmup_gate":"PASS","after_warmup_gate":"FAIL","warmups_completed":2,"formal_samples_completed":0,
           "old_partial_result_preserved":True,"original_result_commit":RESULT,"old_three_arms_rerun":False,
           "combined_dq2_matrix_closed":False,"automatic_next_goal":False,"stop":True,
           "raw_local":str(raw)}
    save(raw/"FINAL_DECISION.json",final);save(PACK/"FINAL_DECISION.json",final)
    tests={"status":"PASS_CPU_FAIL_CLOSED_RESULT_VALIDATION","root_cause_source_gate":"PASS_PREEXEC",
           "aot_pre_warmup_identity":"PASS","accepted_final_cache_content_unchanged":True,
           "after_warmup_path_not_converged":True,"warmups_two_formals_zero":True,
           "warmup_correctness_canary_pass":correctness["warmup_pair_pass"],
           "old_three_arm_sha_rechecked":True,"new_gpu_repeat_count":1,"cache_clear_or_recompile_attempted":False}
    save(PACK/"TESTS.json",tests)
    publish_receipt=publish(raw,PACK)
    assert publish_receipt["status"]=="PASS_DURABLE_PUBLISH_AND_COPYBACK"
    (PACK/"README.md").write_text(f"""# DQ2 MP03_B surgical continuation on 109

Final decision: `DQ2_EXECUTION_IDENTITY_FAIL`. Original PREEXEC `cfa3ba1f5cb5c236b0000ba0f5656e75e2e05b79` and original PARTIAL RESULT `{RESULT}` are unchanged. Continuation PREEXEC `{PREEXEC}` froze a two-stage cache gate before any new GPU request. `CACHE_PATH_LIFECYCLE_ROOT_CAUSE.md` shows why the old PREEXEC pre-warmup equality was too strict while correctly applied at the time.

Only a fresh MP03_B process ran. The pre-warmup AOT path/content/source gate passed. Two warmups completed and their four-row output receipts were preserved. `Qwen2Model` remained compiled, Mode B stayed `VLLM_COMPILE`/`inductor`/`CUDAGraphMode.NONE`, FlashAttentionImpl and UnquantizedLinearMethod were retained, and graph count was zero. After warmup, `local_cache_dir` still pointed to the AOT hash root `{pre['actual_path']}` instead of the 9122 accepted final cache `{post['expected_path']}`. The runner stopped **before** formal timing (0/5). No cache clear, forced recompile, environment change or second policy was attempted.

The four original 9122 cache roots and the AOT root retained identical content SHA before and after this run. The three old arms were not rerun. `CORRECTNESS_RECEIPT.json` reports the two warmup canaries separately; without any new formal B4 sample the DQ2 matrix remains incomplete, so original B1 medians are referenced by SHA and no throughput-scale/interaction or B4 A↔B metric is newly claimed. `COMBINED_DQ2_METRICS.json` keeps this boundary explicit.

New raw remains at `{raw}` and was published to `{publish_receipt['durable_path']}` with per-file SHA and copy-back verification. `RAW_INDEX.json`, `PUBLISH_RECEIPT.json`, `GPU_USAGE_RECEIPT.json`, and `SHA256SUMS` close the evidence. No other arm, consumer, Stage A V2, Tier1, holdout, NCU, NSYS, NVBit, SASS, Accel-Sim, Observer V3, mechanism or AWMA work ran.\n""")
    (PACK/"OPEN_ISSUES.md").write_text("# Open issues\n\nThe pinned AOT cache hit leaves `local_cache_dir` at the AOT hash root after warmup. The continuation contract requires the 9122 final c975 path. This goal stops; a different cache-authority policy would require a separate project decision.\n")
    files=sorted(p for p in PACK.iterdir() if p.is_file() and p.name!="SHA256SUMS")
    (PACK/"SHA256SUMS").write_text("".join(f"{sha(p)}  {p.name}\n" for p in files))
    print(json.dumps({"decision":final["decision"],"warmup_correctness_pass":correctness["warmup_pair_pass"],
                      "raw_files":publish_receipt["local_verify"]["file_count"],"pack_files":len(files)}))

if __name__=="__main__":main(Path(sys.argv[1]))
