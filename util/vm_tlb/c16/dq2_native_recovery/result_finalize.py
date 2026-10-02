#!/usr/bin/env python3
"""CPU-only deterministic partial DQ2 result and 164 raw closeout."""
import csv
import hashlib
import json
import statistics
import sys
from pathlib import Path

from analysis import median_and_mad,validate_point
from publish import publish

ROOT=Path(__file__).resolve().parents[4]
PACK=ROOT/"docs/vm_tlb/review_packs/C16_DQ2_NATIVE_RECOVERY_109_V1"

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()
def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+"\n")
def tsv(path,rows,fields):
    with path.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=fields,delimiter="\t",lineterminator="\n")
        writer.writeheader();writer.writerows(rows)

def main(raw):
    contract=json.loads((PACK/"PREEXEC_CONTRACT.json").read_text())
    run=json.loads((raw/"RUN_IDENTITY.json").read_text())
    status=json.loads((raw/"EXECUTION_STATUS.json").read_text())
    usage=json.loads((raw/"GPU_USAGE_RECEIPT.json").read_text())
    before=json.loads((raw/"CACHE_IDENTITY_BEFORE.json").read_text())
    after=json.loads((raw/"CACHE_IDENTITY_AFTER.json").read_text())
    assert run["preexec_commit"]=="cfa3ba1f5cb5c236b0000ba0f5656e75e2e05b79"
    assert run["preexec_tree"]=="40039df3e610c63ba720f072a164b7e8646cdba6"
    assert status["decision"]=="DQ2_NATIVE_RECOVERY_PARTIAL"
    assert before["status"]==after["status"]=="PASS"
    cache_rows=[]
    for b,a in zip(before["rows"],after["rows"]):
        same=b["point"]==a["point"] and b["mode"]==a["mode"] and b["actual_sha256"]==a["actual_sha256"]==b["expected_sha256"]
        cache_rows.append({"point":b["point"],"mode":b["mode"],"path":b["path"],
                           "before_sha256":b["actual_sha256"],"after_sha256":a["actual_sha256"],
                           "content_unchanged":same,"file_count_before":b["actual_file_count"],"file_count_after":a["actual_file_count"]})
    assert all(x["content_unchanged"] for x in cache_rows)
    alternative=json.loads((raw/"MP03_B.json").read_text())
    assert alternative["status"]=="ERROR" and alternative["warmups"]==[] and alternative["formal_samples"]==[]
    alternate_path=alternative["error"].split(": ",1)[1]
    expected_b4_path=contract["cache_authority"]["MP03_B"]["path"]
    assert alternate_path!=expected_b4_path
    assert alternate_path not in {x["path"] for x in contract["cache_authority"].values()}
    cache_receipt={"status":"BOUND_FOUR_CACHE_ROOTS_UNCHANGED","roots":cache_rows,
        "mp03_b_selected_alternate_aot_path":alternate_path,"mp03_b_preexec_bound_path":expected_b4_path,
        "alternate_path_is_accepted_9122_mp03_b_cache":False,
        "disposition":"STOP_MP03_B_BEFORE_WARMUP_NO_CACHE_RESET_OR_RECOMPILE"}
    save(raw/"CACHE_IDENTITY_BEFORE_AFTER.json",cache_receipt)
    save(PACK/"CACHE_IDENTITY_BEFORE_AFTER.json",cache_receipt)
    mp02=validate_point("MP02",raw,contract)
    assert mp02["identity_pass"] and mp02["correctness_pass"]
    identity={"MP02":{"A":"PASS","B":"PASS","point":"PASS"},
              "MP03":{"A":"ARM_PASS_BUT_POINT_INCOMPLETE","B":"FAIL_FROZEN_CACHE_PATH_MISMATCH_BEFORE_WARMUP","point":"NOT_SCIENCE_VALID"},
              "mp03_b_expected_cache_path":expected_b4_path,"mp03_b_actual_cache_path":alternate_path,
              "source_control_flow":"Mode B config was checked before the cache-path error; compiled Qwen2Model path was not verified and no MP03_B request ran",
              "gpu_uuid":usage["lock"]["baseline"]["uuid"],"no_eager_or_backend_substitution_claim_for_unfinished_arm":True}
    save(raw/"EXECUTION_IDENTITY_RECEIPT.json",identity);save(PACK/"EXECUTION_IDENTITY_RECEIPT.json",identity)
    correctness={"MP02":{"status":"PASS","all_two_warmups_and_five_formals_per_mode":True,
                         "exact_tokens_rows_and_frozen_logprob_tolerance":True,
                         "accepted_9122_output_crosscheck":True},
                 "MP03":{"status":"NOT_EVALUATED_MP03_B_STOPPED_BEFORE_WARMUP",
                         "mp03_a_raw_outputs_preserved":True,"mp03_b_output_count":0},
                 "frozen_rule":"abs(A-B)<=0.05+0.01*abs(A); exact 32 tokens and row mapping"}
    save(raw/"CORRECTNESS_RECEIPT.json",correctness);save(PACK/"CORRECTNESS_RECEIPT.json",correctness)
    formal=[];warm=[]
    for point,batch in (("MP02",1),("MP03",4)):
        for mode in ("A","B"):
            arm=json.loads((raw/f"{point}_{mode}.json").read_text())
            science="SCIENCE_VALID_B1_POINT" if point=="MP02" else "NOT_SCIENCE_VALID_POINT_INCOMPLETE"
            for row in arm.get("warmups",[]):
                warm.append({"point":point,"batch":batch,"mode":mode,"index":row["index"],
                             "request_gpu_elapsed_ms":row["request_gpu_elapsed_ms"],"role":"INLINE_CORRECTNESS_CANARY_NOT_SCIENCE"})
            for row in arm.get("formal_samples",[]):
                formal.append({"point":point,"batch":batch,"mode":mode,"index":row["index"],
                               "request_gpu_elapsed_ms":row["request_gpu_elapsed_ms"],"host_wall_ms":row["host_wall_ms"],
                               "graph_replay_count":row["graph_replay_count"],"science_status":science})
            if not arm.get("formal_samples"):
                formal.append({"point":point,"batch":batch,"mode":mode,"index":"NA",
                               "request_gpu_elapsed_ms":"NA","host_wall_ms":"NA","graph_replay_count":"NA",
                               "science_status":"NOT_EXECUTED_CACHE_IDENTITY_STOP"})
    tsv(raw/"FORMAL_SAMPLES.tsv",formal,["point","batch","mode","index","request_gpu_elapsed_ms","host_wall_ms","graph_replay_count","science_status"])
    tsv(PACK/"FORMAL_SAMPLES.tsv",formal,["point","batch","mode","index","request_gpu_elapsed_ms","host_wall_ms","graph_replay_count","science_status"])
    tsv(raw/"WARMUP_CANARIES.tsv",warm,["point","batch","mode","index","request_gpu_elapsed_ms","role"])
    b1={}
    for mode in ("A","B"):
        arm=json.loads((raw/f"MP02_{mode}.json").read_text())
        values=[x["request_gpu_elapsed_ms"] for x in arm["formal_samples"]]
        b1[mode]={**median_and_mad(values),"ms_per_generated_token":statistics.median(values)/32,
                  "science_status":"SCIENCE_VALID_B1_POINT"}
    b4a=json.loads((raw/"MP03_A.json").read_text())
    b4a_values=[x["request_gpu_elapsed_ms"] for x in b4a["formal_samples"]]
    metrics={"status":"DQ2_NATIVE_RECOVERY_PARTIAL","MP02_B1":b1,
             "MP02_B_over_A_ratio":b1["B"]["median_ms"]/b1["A"]["median_ms"],
             "MP02_A_vs_B_time_reduction":1-b1["A"]["median_ms"]/b1["B"]["median_ms"],
             "MP03_B4":{"A_raw_diagnostic_only":median_and_mad(b4a_values),"B":"NOT_EXECUTED",
                        "science_status":"NOT_SCIENCE_VALID_POINT_INCOMPLETE"},
             "ThroughputScale_A":"NOT_IDENTIFIABLE_B4_POINT_INCOMPLETE",
             "ThroughputScale_B":"NOT_IDENTIFIABLE_B4_B_MISSING",
             "scale_interaction":"NOT_IDENTIFIABLE","MP03_B_over_A_ratio":"NOT_IDENTIFIABLE",
             "MP03_A_vs_B_time_reduction":"NOT_IDENTIFIABLE",
             "estimator":"median of exactly five formal request-level CUDA Event values for valid B1 arms; warmups and 9122 durations excluded",
             "dispersion":"MAD; five values are not statistical-significance proof"}
    save(raw/"DQ2_METRICS.json",metrics);save(PACK/"DQ2_METRICS.json",metrics)
    metrics_rows=[]
    for mode,x in b1.items():
        for field in ("median_ms","min_ms","max_ms","mad_ms","ms_per_generated_token"):
            metrics_rows.append({"metric":field,"point":"MP02","mode":mode,"value":x[field],"status":"SCIENCE_VALID_B1_POINT"})
    for metric in ("MP02_B_over_A_ratio","MP02_A_vs_B_time_reduction"):
        metrics_rows.append({"metric":metric,"point":"MP02","mode":"A_VS_B","value":metrics[metric],"status":"SCIENCE_VALID_B1_POINT"})
    metrics_rows.append({"metric":"median_ms","point":"MP03","mode":"A","value":statistics.median(b4a_values),"status":"DIAGNOSTIC_ONLY_POINT_INCOMPLETE"})
    for metric in ("ThroughputScale_A","ThroughputScale_B","scale_interaction","MP03_B_over_A_ratio","MP03_A_vs_B_time_reduction"):
        metrics_rows.append({"metric":metric,"point":"MP03_OR_CROSS_POINT","mode":"NA","value":"NA","status":"NOT_IDENTIFIABLE"})
    tsv(PACK/"DQ2_METRICS.tsv",metrics_rows,["metric","point","mode","value","status"])
    save(PACK/"RUN_IDENTITY.json",run)
    save(PACK/"GPU_USAGE_RECEIPT.json",usage)
    final={"goal":"C16_DQ2_NATIVE_RECOVERY_109_V1","decision":"DQ2_NATIVE_RECOVERY_PARTIAL",
           "failure_class":"DQ2_EXECUTION_IDENTITY_FAIL","failed_arm":"MP03_B",
           "reason":"effective AOT compile cache path changed from PREEXEC-bound 9122 authority before any MP03_B warmup",
           "MP02":{"identity":"PASS","correctness":"PASS","timing":"SCIENCE_VALID_B1_POINT"},
           "MP03":{"A_arm":"PASS_RAW_DIAGNOSTIC","B_arm":"NOT_EXECUTED_CACHE_IDENTITY_STOP",
                   "correctness":"NOT_EVALUATED","timing":"NOT_SCIENCE_VALID"},
           "automatic_next_goal":False,"stop":True,"semantic_attribution_performed":False,
           "forbidden_tools_executed":False,"raw_local":str(raw)}
    save(raw/"FINAL_DECISION.json",final);save(PACK/"FINAL_DECISION.json",final)
    tests={"status":"PASS_CPU_DETERMINISTIC_PARTIAL_CLOSEOUT","mp02_pair_revalidated":True,
           "mp03_b_zero_warmup_and_formal":True,"all_four_accepted_cache_roots_unchanged":True,
           "timing_endpoint_unchanged_from_preexec":True,"result_directed_repeat":False}
    save(PACK/"TESTS.json",tests)
    receipt=publish(raw,PACK)
    assert receipt["status"]=="PASS_DURABLE_PUBLISH_AND_COPYBACK"
    (PACK/"README.md").write_text(f"""# C16 DQ2 native recovery on 109

Final decision: `DQ2_NATIVE_RECOVERY_PARTIAL` (`DQ2_EXECUTION_IDENTITY_FAIL` at MP03_B). PREEXEC commit `cfa3ba1f5cb5c236b0000ba0f5656e75e2e05b79` was pushed/fetched back before GPU execution; `PREEXEC_CONTRACT.md` fixes the endpoint, arm order, formulas and STOP gates.

MP02 B1 Mode A and B each completed two warmups and five formal samples. Their identity and exact A/B/9122 output correctness passed. The formal medians are A `{b1['A']['median_ms']:.6f}` ms and B `{b1['B']['median_ms']:.6f}` ms; `DQ2_METRICS.json` preserves all raw values, MAD and the same-point response. MP03 A completed five raw values but MP03 B selected AOT cache `{alternate_path}` instead of the PREEXEC-bound `{expected_b4_path}`. The runner stopped before B4 warmup, so MP03 has no valid A/B comparison; its A values are diagnostic only. No B1→B4 throughput-scale or interaction metric is reported.

The four 9122-bound cache roots were byte-identical before and after execution. `CACHE_IDENTITY_BEFORE_AFTER.json` records this and the distinct unbound MP03 B selected path. `CORRECTNESS_RECEIPT.json`, `EXECUTION_IDENTITY_RECEIPT.json`, `FORMAL_SAMPLES.tsv` and `GPU_USAGE_RECEIPT.json` keep point-specific evidence. The raw payload remains at `{raw}` and was published to `{receipt['durable_path']}` with per-file SHA and copy-back verification (`PUBLISH_RECEIPT.json`, `RAW_INDEX.json`).

This point-specific partial result supports only the frozen B1 request-level Mode A↔B response. It does not establish B1→B4 scaling, GPU utilization, a pure batch causal effect, semantic-family time fractions, DQ3 memory-service attribution, DQ4a chronology, or a hardware mechanism. No Tier1, holdout, NCU, NSYS, NVBit, SASS, Accel-Sim, Observer V3 or independent consumer was run. `SHA256SUMS` covers the review pack.\n""")
    (PACK/"OPEN_ISSUES.md").write_text("# Open issues\n\nMP03 B selected a different AOT compile artifact path before warmup. The PREEXEC path cannot be rebound after results; no B4 pair or throughput-scale conclusion is available. Any new authority requires separate project review.\n")
    files=sorted(p for p in PACK.iterdir() if p.is_file() and p.name!="SHA256SUMS")
    (PACK/"SHA256SUMS").write_text("".join(f"{sha(p)}  {p.name}\n" for p in files))
    print(json.dumps({"decision":final["decision"],"failure_class":final["failure_class"],"raw_files":receipt["local_verify"]["file_count"],"pack_files":len(files)}))

if __name__=="__main__":main(Path(sys.argv[1]))
