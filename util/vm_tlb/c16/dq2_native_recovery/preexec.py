#!/usr/bin/env python3
"""CPU-only PREEXEC authority freeze and recheck for DQ2 native recovery."""
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from cache_check import check as cache_check

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
PACK=ROOT/"docs/vm_tlb/review_packs/C16_DQ2_NATIVE_RECOVERY_109_V1"
ASSET=ROOT/"docs/vm_tlb/review_packs/C16_MEASUREMENT_CAMPAIGN_STAGEA_ASSET_INPUT_CLOSURE_174NEW_V1"
PRIOR=ROOT/"docs/vm_tlb/review_packs/C16_QWEN_DECODE_MODE_DECONFLATION_CANARY_109_V1"
MODEL=Path("/data/c16/stagea_runtime_qualification_v1/assets/qwen2.5-3b-instruct/aa8e72537993ba99e69dfaafa59ed015b17504d1")
VLLM=Path("/data/c16/envs/c16-vllm-v0.30.0-sm89-v1/lib/python3.12/site-packages/vllm")
BASE="ab3df70e3a18eea6292af71334f9a2727066c5b3"
AUTH={"artifact_feasibility":BASE,"compiler_native_design":"ecd9978a719836268d1eb6625b534c8e66db1774",
      "mode_ab_correctness":"9122fac5c50dbf19706636fc03978a356ffd800f",
      "observer_v2_failure":"c48331a9ea5a3f381741aad4bae91dfb0eefc2c2",
      "stagea_v1_contract":"fad9da8116c8ad794f99a93f153b0866162158a4",
      "stagea_v1_producer":"82788c2d587e86f94791d65aaa2bde28929f9303",
      "stagea_v1_consumer":"9d82ff41132e7b1a1fdd18a287c13627fe62e5b7"}
SOURCE_SHA={"compilation.py":"c9cec5c7200e8e559810ec8c30113ad61dab6780f9f7fb3c116bd0d9b5a43065",
            "qwen2.py":"eb2f0eeb13c57a28bbc06bc64afff18cd8865f89fbe9ff2a3cf3a896f037cfe9"}
EXPECTED_UUID="GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59"

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()
def sha_ids(ids):return hashlib.sha256(json.dumps(ids,sort_keys=True,separators=(",", ":")).encode()).hexdigest()
def git(*args):return subprocess.check_output(["git","-C",str(ROOT),*args],text=True).strip()
def git_bytes(commit,path):return subprocess.check_output(["git","-C",str(ROOT),"show",f"{commit}:{path}"])
def save(path,value):path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")

def verify_current_authority(contract=None):
    if git("rev-parse",BASE)!=BASE or git("rev-parse",BASE+"^{tree}")!="d68af347fe33addef143c634fab850e9a2580fd0":
        raise RuntimeError("artifact feasibility authority commit/tree mismatch")
    for name,commit in AUTH.items():
        if git("cat-file","-t",commit)!="commit":raise RuntimeError(f"authority unavailable {name}")
    original=json.loads(git_bytes(AUTH["mode_ab_correctness"],"docs/vm_tlb/review_packs/C16_QWEN_DECODE_MODE_DECONFLATION_CANARY_109_V1/FINAL_DECISION.json"))
    observer=json.loads(git_bytes(AUTH["observer_v2_failure"],"docs/vm_tlb/review_packs/C16_QWEN_COMPILED_NO_CUDAGRAPH_OBSERVER_V2_CANARY_109_V1/FINAL_DECISION.json"))
    artifact=json.loads(git_bytes(BASE,"docs/vm_tlb/review_packs/C16_COMPILED_PATH_ARTIFACT_ATTRIBUTION_FEASIBILITY_109_V1/FINAL_DECISION.json"))
    if original["decision"]!="MODE_DECONFLATION_CORRECTNESS_PASS_FOR_OBSERVER_REVIEW_ONLY" or not(original["mp02_pass"] and original["mp03_pass"]):raise RuntimeError("Mode A/B correctness authority mismatch")
    if observer["decision"]!="COMPILED_NO_CUDAGRAPH_OBSERVER_V2_IDENTITY_FAIL" or artifact["decision"]!="COMPILED_ATTRIBUTION_LEVEL_0_UNRESOLVED":raise RuntimeError("frozen observer/artifact decisions mismatch")
    source={"compilation.py":sha(VLLM/"config/compilation.py"),"qwen2.py":sha(VLLM/"model_executor/models/qwen2.py")}
    if source!=SOURCE_SHA:raise RuntimeError("vLLM installed source identity mismatch")
    if contract is not None:
        if contract["base_commit"]!=BASE or contract["authorities"]!=AUTH or contract["vllm_installed_source_sha256"]!=SOURCE_SHA:
            raise RuntimeError("PREEXEC contract authority mismatch")
    return source

def asset_bindings():
    receipt=json.loads((ASSET/"QWEN_BF16_ASSET_RECEIPT.json").read_text())
    if receipt["revision"]!=MODEL.name:raise RuntimeError("model revision mismatch")
    files=[]
    for item in receipt["files"]:
        path=MODEL/item["path"]
        digest=sha(path)
        if path.stat().st_size!=item["size_bytes"] or digest!=item["sha256"]:raise RuntimeError(f"model asset SHA mismatch: {item['path']}")
        files.append({"path":str(path),"size_bytes":item["size_bytes"],"sha256":digest})
    with (ASSET/"TOKENIZATION_RECEIPTS.tsv").open(newline="") as f:
        rows={r["source_text_id"]:r for r in csv.DictReader(f,delimiter="\t") if r["model_key"]=="QWEN_BF16"}
    tokens={}
    for i in range(4):
        source=f"TRAIN_A_DISCOVERY_{i:02d}";r=rows[source]
        path=ASSET/"token_ids/QWEN_BF16"/f"{source}.json";ids=json.loads(path.read_text())
        if len(ids)!=512 or sha(path)!=r["token_id_file_sha256"] or sha_ids(ids)!=r["token_ids_sha256"]:
            raise RuntimeError(f"frozen token binding mismatch {source}")
        if r["model_revision"]!=MODEL.name or r["tokenizer_revision"]!=MODEL.name:raise RuntimeError("tokenizer revision mismatch")
        if sha(MODEL/"tokenizer.json")!=r["tokenizer_json_sha256"]:raise RuntimeError("tokenizer SHA mismatch")
        if sha(MODEL/"tokenizer_config.json")!=r["tokenizer_config_sha256"]:raise RuntimeError("tokenizer config SHA mismatch")
        source_path=ROOT/"docs/vm_tlb/review_packs/C16_PROBLEM_DISCOVERY_MEASUREMENT_CAMPAIGN_EXECUTION_PREFLIGHT_174NEW_V1/input_sources"/f"{source}.txt"
        if sha(source_path)!=r["source_utf8_sha256"]:raise RuntimeError(f"source text SHA mismatch {source}")
        tokens[source]={"path":str(path),"file_sha256":sha(path),"ids_sha256":sha_ids(ids),
                        "source_text_path":str(source_path),"source_utf8_sha256":r["source_utf8_sha256"],"token_count":len(ids)}
    return {"status":"PASS","model_revision":MODEL.name,"model_path":str(MODEL),"model_files":files,
            "tokenizer_json_sha256":sha(MODEL/"tokenizer.json"),"token_bindings":tokens}

def build():
    PACK.mkdir(parents=True,exist_ok=True)
    source=verify_current_authority()
    asset=asset_bindings();save(PACK/"ASSET_INPUT_PRECHECK.json",asset)
    cache=cache_check("PREEXEC")
    save(PACK/"CACHE_PREEXEC.json",cache)
    if cache["status"]!="PASS":raise RuntimeError("accepted cache identity mismatch before PREEXEC")
    static=subprocess.run(["python3",str(HERE/"static_gate.py")],capture_output=True,text=True,check=True)
    synthetic=subprocess.run(["python3",str(HERE/"test_synthetic.py")],capture_output=True,text=True,check=True)
    checks={"asset":"PASS","cache":"PASS","timing_source":static.stdout.strip(),"synthetic_formulas":synthetic.stdout.strip()}
    with (PRIOR/"RAW_INDEX.tsv").open(newline="") as f:
        index={r["local_path"]:r for r in csv.DictReader(f,delimiter="\t")}
    original_root=Path(json.loads((PRIOR/"FINAL_DECISION.json").read_text())["raw_local"])
    accepted={}
    for point in ("MP02","MP03"):
        for mode in ("A","B"):
            path=original_root/f"{point}_{mode}.json"
            digest=sha(path)
            if digest!=index[str(path)]["sha256"]:raise RuntimeError("accepted output raw SHA mismatch")
            accepted[f"{point}_{mode}"]={"path":str(path),"sha256":digest,"role":"CORRECTNESS_CROSSCHECK_ONLY_DURATION_EXCLUDED"}
    cache_map={f"{r['point']}_{r['mode']}":{"path":r["path"],"content_identity_sha256":r["content_identity_sha256"]} for r in json.loads((PRIOR/"COMPILE_CACHE_IDENTITY.json").read_text())}
    code_files=("runner.py","analysis.py","cache_check.py","execute.py","publish.py","verify_raw.py","static_gate.py","preexec.py","test_synthetic.py")
    code_hash={name:sha(HERE/name) for name in code_files}
    contract={
      "schema":"C16_DQ2_NATIVE_RECOVERY_PREEXEC_CONTRACT_V1","goal":"C16_DQ2_NATIVE_RECOVERY_109_V1",
      "status":"FROZEN_PREEXEC_AUTHORIZED_BY_USER","base_commit":BASE,"base_tree":"d68af347fe33addef143c634fab850e9a2580fd0",
      "authorities":AUTH,"vllm_source_commit":"ced6857afa0ea7b2e3f0846a62e1394e90f15607",
      "vllm_installed_source_sha256":source,
      "runtime_environment":"/data/c16/envs/c16-vllm-v0.30.0-sm89-v1",
      "gpu":{"node":"109","name":"RTX4080_SM89","uuid":EXPECTED_UUID},
      "model":{"repository":"Qwen/Qwen2.5-3B-Instruct","revision":MODEL.name,"path":str(MODEL),
               "dtype":"bfloat16","tensor_parallel_size":1,"model_impl":"vllm","quantization":None},
      "points":{"MP02":{"batch":1,"source_ids":["TRAIN_A_DISCOVERY_00"],"prompt_tokens_per_row":512,"decode_steps_per_row":32},
                "MP03":{"batch":4,"source_ids":[f"TRAIN_A_DISCOVERY_{i:02d}" for i in range(4)],"prompt_tokens_per_row":512,"decode_steps_per_row":32,"real_single_batch":True}},
      "token_bindings":asset["token_bindings"],
      "sampling":{"seed":0,"temperature":0.0,"top_p":1.0,"max_tokens":32,"ignore_eos":True,"detokenize":False,"logprobs":20},
      "vllm_settings":{"skip_tokenizer_init":True,"max_model_len":544,"max_num_seqs":"batch_size",
                       "max_num_batched_tokens":"batch_size*544","gpu_memory_utilization":0.92,"cpu_offload_gb":0,"enable_prefix_caching":False},
      "modes":{"A":{"enforce_eager":False,"compilation_mode":"VLLM_COMPILE","backend":"inductor","cudagraph_mode":"FULL_AND_PIECEWISE"},
               "B":{"enforce_eager":False,"compilation_mode":"VLLM_COMPILE","backend":"inductor","cudagraph_mode":"NONE","capture_replay_count":0}},
      "formal_arm_order":["MP02_A","MP02_B","MP03_A","MP03_B"],
      "per_arm":{"fresh_process":True,"warmups":2,"second_warmup":"INLINE_CORRECTNESS_CANARY_NOT_SCIENCE",
                 "formal_requests":5,"result_directed_extra_requests":False,"all_raw_values_preserved":True},
      "timing":{"primary_field":"request_gpu_elapsed_ms","source":"Stage A V1 producer observer-OFF native request",
                "source_commit":AUTH["stagea_v1_producer"],"source_runner_sha256":"e5d0c14d008b80d54e3606c98946778fd3954f2c6c07ba8da558b01ba5a17379",
                "boundary":"cuda.synchronize; CUDA Event start; one llm.generate; Event stop; cuda.synchronize; start.elapsed_time(stop)",
                "formal_estimator":"median of exactly five samples","dispersion":"MAD","host_wall_role":"DIAGNOSTIC_ONLY"},
      "correctness":{"tokens":"exact 32 per row","row_mapping":"exact","sampled_logprob":"abs(A-B)<=0.05+0.01*abs(A)",
                     "atol":0.05,"rtol":0.01,"all_warmups_and_formals_required":True,"9122_crosscheck":True},
      "accepted_outputs":accepted,"cache_authority":cache_map,
      "gpu_budget":{"total_seconds_cap":240,"per_arm_seconds_cap":60,"lock_wait_seconds_cap":600,"no_other_campaign_interruption":True},
      "metrics":{"T":"median(request_gpu_elapsed_ms) for five formal requests",
                 "ms_per_generated_token":"T/(batch_size*32)",
                 "ThroughputScale_A":"4*T[MP02,A]/T[MP03,A]","ThroughputScale_B":"4*T[MP02,B]/T[MP03,B]",
                 "B_over_A_ratio":"T[point,B]/T[point,A]",
                 "A_vs_B_time_reduction":"1-T[point,A]/T[point,B]",
                 "interaction_abs_difference":"abs(ThroughputScale_A-ThroughputScale_B)",
                 "interaction_ratio":"ThroughputScale_A/ThroughputScale_B"},
      "shape_boundary":"request-level batch, prompt-token and graph descriptor only; no guessed internal kernel M",
      "semantic_attribution":False,"dq1_dq3_dq4a_unchanged":True,
      "forbidden":["Mode A/B eager fallback","module hooks","NVTX semantic observer","graph break","custom op or marker",
                   "Qwen forward edit","cache clear","Tier1","holdout","NCU","NSYS","NVBit","SASS","Accel-Sim","new mechanism","AWMA"],
      "code_sha256":code_hash,"automatic_next_goal":False}
    save(PACK/"PREEXEC_CONTRACT.json",contract)
    (PACK/"PREEXEC_CONTRACT.md").write_text("""# DQ2 native recovery PREEXEC freeze

This contract is frozen before any GPU execution. It binds the seven accepted commits, the exact Qwen BF16 model and four 512-token input files, the qualified vLLM 0.30.0 environment and four original 9122 cache identities. `ASSET_INPUT_PRECHECK.json`, `CACHE_PREEXEC.json`, and `TIMING_AUTHORITY.json` are CPU-only admission evidence.

The four fresh-process arms are `MP02_A → MP02_B → MP03_A → MP03_B`. Each has two warmups (second saved as an inline correctness canary) and exactly five measured requests. The Stage A V1 observer-OFF request-level CUDA Event endpoint is unchanged: synchronize, record start Event, run one `llm.generate`, record stop Event, synchronize, read elapsed. No semantic hooks, NVTX observer, profiler, custom op, or compiled-graph edit is installed. A thin graph-manager dispatch counter verifies Mode A's actual graph path; compilation/capture counters and graph entries must remain stable during every formal request.

The primary estimator is the median of the five formal CUDA-event request values, with min/max/MAD and every raw value retained. Host wall is diagnostic. Correctness uses the 9122 exact-token/row rule and `abs(A-B) <= 0.05 + 0.01*abs(A)` for every sampled token; each new warmup/formal is also crossed against accepted 9122 output, never its timing. Any point's correctness/identity failure invalidates its timing for science. Frozen formulas for batch/shape throughput response and A↔B response are in `PREEXEC_CONTRACT.json`. No utilization, pure batch-causal, semantic-family, memory-service, producer-consumer or architectural claim follows from them.

New Goal GPU caps are 60 seconds per fresh-process arm, 240 seconds total, and at most 600 seconds of bounded lock/resource retry; these do not borrow Stage A reservations. The cache is read-only to the preparation workflow and checked before/after execution. Raw bytes go to 164 with per-file SHA and copy-back. After RESULT closure the Goal stops; no independent consumer or Stage A V2 starts automatically.\n""")
    save(PACK/"PREEXEC_TESTS.json",{"status":"PASS_CPU_ONLY","checks":checks,"gpu_used":False,"gpu_lock_acquired":False})
    (PACK/"README.md").write_text("# DQ2 native recovery, PREEXEC stage\n\nStart with `PREEXEC_CONTRACT.md` and `PREEXEC_CONTRACT.json`. The contract, runner, validator and formulas are frozen before GPU work. `TIMING_AUTHORITY.json`, `ASSET_INPUT_PRECHECK.json`, `CACHE_PREEXEC.json`, and `PREEXEC_TESTS.json` are CPU-only admission receipts. No GPU was used during PREEXEC.\n")
    files=sorted(p for p in PACK.iterdir() if p.is_file() and p.name!="SHA256SUMS")
    (PACK/"SHA256SUMS").write_text("".join(f"{sha(p)}  {p.name}\n" for p in files))
    print(json.dumps({"status":"PREEXEC_FROZEN","files":len(files),"gpu_used":False}))

if __name__=="__main__":build()
