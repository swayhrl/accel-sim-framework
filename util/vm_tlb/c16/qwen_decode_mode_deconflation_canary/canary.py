#!/usr/bin/env python3
"""One authorized Qwen decode execution-mode canary, with fail-closed gates."""
import csv
import fcntl
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PACK = ROOT / "docs/vm_tlb/review_packs/C16_QWEN_DECODE_MODE_DECONFLATION_CANARY_109_V1"
ASSET_PACK = ROOT / "docs/vm_tlb/review_packs/C16_MEASUREMENT_CAMPAIGN_STAGEA_ASSET_INPUT_CLOSURE_174NEW_V1"
SOURCE_PACK = ROOT / "docs/vm_tlb/review_packs/C16_PROBLEM_DISCOVERY_MEASUREMENT_CAMPAIGN_EXECUTION_PREFLIGHT_174NEW_V1"
CONTRACT_REL = "docs/vm_tlb/review_packs/C16_QWEN_DECODE_MODE_DECONFLATION_CANARY_CONTRACT_FINAL_174NEW_V1/C16_QWEN_DECODE_COMPILED_NO_CUDAGRAPH_CANARY_109_V1.json"
CONTRACT_SHA = "bc547a652ed04db9c3e1e1e7020be53ac76052bd76bfdad6d89eee0f69678501"
COMMIT = "c4a61e8f2d4d96587e0006726e21796a360404e7"
TREE = "d0370fa0fba6566161558c6f7b34b3c5eebb14e5"
REV = "aa8e72537993ba99e69dfaafa59ed015b17504d1"
MODEL = Path("/data/c16/stagea_runtime_qualification_v1/assets/qwen2.5-3b-instruct") / REV
ENV = Path("/data/c16/envs/c16-vllm-v0.30.0-sm89-v1")
LOCK = Path("/data/c16/locks/c16_gpu_campaign.lock")
RAW_BASE = Path("/data/c16/qwen_decode_mode_deconflation_canary_v1/raw")
EXPECTED_UUID = "GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59"
SOURCES = [f"TRAIN_A_DISCOVERY_{i:02d}" for i in range(4)]

def now():
    return datetime.now(timezone.utc).isoformat()

def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n")

def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()

def authority():
    actual_commit = git("rev-parse", COMMIT)
    actual_tree = git("rev-parse", f"{COMMIT}^{{tree}}")
    committed = subprocess.check_output(["git", "-C", str(ROOT), "show", f"{COMMIT}:{CONTRACT_REL}"])
    local = (ROOT / CONTRACT_REL).read_bytes()
    contract = json.loads(local)
    final_rel = str(Path(CONTRACT_REL).with_name("FINAL_DECISION.json"))
    final = json.loads(subprocess.check_output(["git", "-C", str(ROOT), "show", f"{COMMIT}:{final_rel}"]))
    checks = {
        "commit": actual_commit == COMMIT,
        "tree": actual_tree == TREE,
        "contract_sha256": hashlib.sha256(committed).hexdigest() == CONTRACT_SHA,
        "working_contract_bytes": local == committed,
        "status": contract.get("status") == "AUTHORIZED_BY_PROJECT_REVIEW",
        "execution_authorized": contract.get("execution_authorized") is True,
        "finalization_decision": final.get("status") == "MODE_DECONFLATION_CANARY_CONTRACT_FINALIZED",
        "finalization_execution_authorized": final.get("execution_authorized") is True,
    }
    result = {"checks": checks, "commit": actual_commit, "tree": actual_tree,
              "sha256": hashlib.sha256(committed).hexdigest(), "status": "PASS" if all(checks.values()) else "CONTRACT_AUTHORITY_FAILURE"}
    write_json(PACK / "CONTRACT_AUTHORITY.json", result)
    if result["status"] != "PASS":
        raise RuntimeError("CONTRACT_AUTHORITY_FAILURE")
    return contract

def asset_recheck():
    receipt = json.loads((ASSET_PACK / "QWEN_BF16_ASSET_RECEIPT.json").read_text())
    checks = {}
    checks["revision"] = receipt["revision"] == REV and MODEL.name == REV
    checks["model_file_sha"] = []
    for row in receipt["files"]:
        p = MODEL / row["path"]
        checks["model_file_sha"].append({"path": row["path"], "pass": p.is_file() and p.stat().st_size == row["size_bytes"] and sha(p) == row["sha256"]})
    token_rows = []
    with (ASSET_PACK / "TOKENIZATION_RECEIPTS.tsv").open(newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            if row["model_key"] == "QWEN_BF16" and row["source_text_id"] in SOURCES:
                token_rows.append(row)
    checks["four_rows"] = len(token_rows) == 4 and [r["source_text_id"] for r in token_rows] == SOURCES
    site = ENV / "lib/python3.12/site-packages/vllm"
    checks["runtime_source"] = {
        "vllm_version": subprocess.check_output([str(ENV / "bin/python"), "-c", "from importlib.metadata import version; print(version('vllm'))"], text=True).strip() == "0.30.0",
        "compilation_py_sha": sha(site / "config/compilation.py") == "c9cec5c7200e8e559810ec8c30113ad61dab6780f9f7fb3c116bd0d9b5a43065",
        "entrypoint_py_sha": sha(site / "entrypoints/llm.py") == "52de4ac99489e004ef6c61d0bedc84aa96020dd58b8bd1ae500814b548b2b83e",
        "source_authority_commit": git("rev-parse", "ced6857afa0ea7b2e3f0846a62e1394e90f15607") == "ced6857afa0ea7b2e3f0846a62e1394e90f15607",
    }
    checks["token_inputs"] = []
    for row in token_rows:
        source_id = row["source_text_id"]
        token_path = ASSET_PACK / row["token_ids_relative_path"]
        source_path = SOURCE_PACK / "input_sources" / f"{source_id}.txt"
        ids = json.loads(token_path.read_text())
        canonical = json.dumps(ids, sort_keys=True, separators=(",", ":")).encode()
        check = {
            "source_id": source_id,
            "token_file_sha": sha(token_path) == row["token_id_file_sha256"],
            "token_ids_sha": hashlib.sha256(canonical).hexdigest() == row["token_ids_sha256"],
            "source_sha": sha(source_path) == row["source_utf8_sha256"],
            "tokenizer_sha": sha(MODEL / "tokenizer.json") == row["tokenizer_json_sha256"] and sha(MODEL / "tokenizer_config.json") == row["tokenizer_config_sha256"],
            "revision": row["model_revision"] == REV and row["tokenizer_revision"] == REV,
            "length": len(ids) == 512 and all(type(i) is int for i in ids),
        }
        checks["token_inputs"].append(check)
    passed = checks["revision"] and checks["four_rows"] and all(x["pass"] for x in checks["model_file_sha"]) and all(all(v for k,v in x.items() if k != "source_id") for x in checks["token_inputs"])
    passed &= all(checks["runtime_source"].values())
    result = {"status": "PASS" if passed else "FAIL", "model_path": str(MODEL), "checks": checks}
    write_json(PACK / "ASSET_INPUT_RECHECK.json", result)
    if not passed:
        raise RuntimeError("ASSET_INPUT_RECHECK_FAILED")

def gpu_query():
    fields = subprocess.check_output(["nvidia-smi", "--query-gpu=uuid,name,memory.used", "--format=csv,noheader,nounits"], text=True).strip()
    processes = subprocess.check_output(["nvidia-smi", "--query-compute-apps=pid,process_name,used_gpu_memory", "--format=csv,noheader,nounits"], text=True).strip()
    parts = [p.strip() for p in fields.split(",")]
    return {"uuid": parts[0], "name": parts[1], "memory_used_mib": int(parts[2]), "compute_processes": processes.splitlines() if processes else []}

def run_child(point, mode, remaining, raw):
    if remaining <= 4:
        raise RuntimeError("GPU_BUDGET_EXHAUSTED_BEFORE_NEXT_MODE")
    name = f"{point}_{mode}"
    output = raw / f"{name}.json"
    stdout = raw / f"{name}.stdout"
    stderr = raw / f"{name}.stderr"
    cmd = [str(ENV / "bin/python"), str(Path(__file__).with_name("runner.py")), "--point", point, "--mode", mode, "--model", str(MODEL), "--output", str(output)]
    env = os.environ.copy()
    env.update({"VLLM_ENABLE_V1_MULTIPROCESSING": "0", "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1", "VLLM_LOGGING_LEVEL": "INFO"})
    with stdout.open("wb") as out, stderr.open("wb") as err:
        process = subprocess.Popen(cmd, stdout=out, stderr=err, env=env, start_new_session=True)
        try:
            code = process.wait(timeout=remaining - 3)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            raise RuntimeError(f"GPU_BUDGET_EXHAUSTED_{name}")
    if code != 0 or not output.exists():
        raise RuntimeError(f"RUNNER_FAILED_{name}_exit_{code}")
    result = json.loads(output.read_text())
    if result.get("status") != "PASS":
        raise RuntimeError(f"RUNNER_FAILED_{name}_{result.get('error_type')}")
    return result

def identity(row):
    c = row["config"]
    r = row["runtime_identity"]
    common = c["enforce_eager"] is False and c["compilation_mode"] == "VLLM_COMPILE" and c["backend"] != "eager" and c["torch_compile_disable"] not in ("1", "true", "True")
    common &= r["compiled_model"] and not r["do_not_compile"] and not r["skip_compiled_seen"]
    common &= r["attention_impl"] == ["FlashAttentionImpl"] and r["linear_method"] == ["UnquantizedLinearMethod"]
    if row["mode"] == "A":
        return common and c["cudagraph_mode"] != "NONE" and r["formal_graph_replay_count"] > 0 and bool(r["formal_graph_shapes"])
    return common and c["cudagraph_mode"] == "NONE" and r["formal_graph_replay_count"] == 0 and r["formal_graph_capture_count"] == 0 and not r["formal_graph_shapes"]

def compare(point, a, b):
    reason = []
    if not identity(a): reason.append("MODE_A_IDENTITY_UNRESOLVED")
    if not identity(b):
        if b["config"]["compilation_mode"] != "VLLM_COMPILE" or b["config"]["backend"] == "eager" or b["runtime_identity"]["do_not_compile"]:
            reason.append("MODE_B_IDENTITY_INVALID")
        else: reason.append("MODE_B_IDENTITY_UNRESOLVED")
    if a["config"]["compilation_mode"] != b["config"]["compilation_mode"]:
        reason.append("MODE_B_IDENTITY_INVALID")
    token_rows, prob_rows, correctness_rows = [], [], []
    rows_a, rows_b = a["formal_rows"], b["formal_rows"]
    expected = SOURCES[:1 if point == "MP02" else 4]
    if len(rows_a) != len(expected) or len(rows_b) != len(expected):
        reason.append("SHAPE_ORDER_FAIL")
    for i, source in enumerate(expected):
        ra = rows_a[i] if i < len(rows_a) else {}
        rb = rows_b[i] if i < len(rows_b) else {}
        mapping = ra.get("source_id") == rb.get("source_id") == source and ra.get("batch_row") == rb.get("batch_row") == i
        ta, tb = ra.get("tokens", []), rb.get("tokens", [])
        pa, pb = ra.get("sampled_logprobs", []), rb.get("sampled_logprobs", [])
        length = len(ta) == len(tb) == len(pa) == len(pb) == 32 and ra.get("prompt_token_count") == rb.get("prompt_token_count") == 512
        row_pass = mapping and length
        for step in range(32):
            aid = ta[step] if step < len(ta) else None
            bid = tb[step] if step < len(tb) else None
            av = pa[step] if step < len(pa) else None
            bv = pb[step] if step < len(pb) else None
            token_pass = aid is not None and aid == bid
            delta = abs(av-bv) if av is not None and bv is not None else None
            tolerance = 0.05 + 0.01 * abs(av) if av is not None else None
            prob_pass = delta is not None and delta <= tolerance
            token_rows.append({"point":point,"row":i,"source_id":source,"step":step,"a_token":aid,"b_token":bid,"pass":token_pass})
            prob_rows.append({"point":point,"row":i,"source_id":source,"step":step,"a_logprob":av,"b_logprob":bv,"abs_delta":delta,"tolerance":tolerance,"pass":prob_pass})
            correctness_rows.append({"point":point,"row":i,"source_id":source,"step":step,"mapping_pass":mapping,"shape_order_pass":length,"token_pass":token_pass,"logprob_pass":prob_pass})
            row_pass &= token_pass and prob_pass
        if not row_pass: reason.append(f"ROW_{i}_CORRECTNESS_FAIL")
    return not reason, sorted(set(reason)), token_rows, prob_rows, correctness_rows

def tsv(path, rows, columns):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

def finish(raw, results, comparisons, decision, reason, gpu_start, lock_receipt, prior_seconds):
    attempt_duration = time.monotonic() - gpu_start if gpu_start else 0.0
    duration = prior_seconds + attempt_duration
    write_json(PACK / "GPU_ACTIVE_BUDGET.json", {"gpu_active_seconds_conservative_wall":duration,"prior_failed_attempt_seconds":prior_seconds,"current_attempt_seconds":attempt_duration,"cap_seconds":120,"within_cap":duration <= 120,"duration_role":"QUALIFICATION_DIAGNOSTIC_ONLY"})
    lock_receipt.update({"released_utc":now(),"released":True})
    write_json(PACK / "GPU_LOCK_RECEIPT.json", lock_receipt)
    mode_rows, backend_rows, tokens, probs, correctness = [], [], [], [], []
    for r in results:
        x = {"point":r["point"],"mode":r["mode"], **r["config"], **r["runtime_identity"]}
        mode_rows.append(x)
        backend_rows.append({"point":r["point"],"mode":r["mode"],"attention_impl":r["runtime_identity"]["attention_impl"],"linear_method":r["runtime_identity"]["linear_method"],"kernel_names":r["kernel_names"]})
    for c in comparisons:
        tokens += c[2]; probs += c[3]; correctness += c[4]
    tsv(PACK / "MODE_RUNTIME_IDENTITY.tsv", mode_rows, ["point","mode","enforce_eager","compilation_mode","cudagraph_mode","optimization_level","backend","torch_compile_disable","breakable_cg_env","compiled_model","do_not_compile","skip_compiled_seen","formal_graph_replay_count","formal_graph_capture_count","formal_graph_shapes","attention_impl","linear_method","compile_cache_path","compile_cache_preexisted"])
    tsv(PACK / "BACKEND_KERNEL_IDENTITY.tsv", backend_rows, ["point","mode","attention_impl","linear_method","kernel_names"])
    tsv(PACK / "TOKEN_COMPARISON.tsv", tokens, ["point","row","source_id","step","a_token","b_token","pass"])
    tsv(PACK / "LOGPROB_DELTA_BY_STEP.tsv", probs, ["point","row","source_id","step","a_logprob","b_logprob","abs_delta","tolerance","pass"])
    tsv(PACK / "FREE_RUNNING_CORRECTNESS_BY_ROW_STEP.tsv", correctness, ["point","row","source_id","step","mapping_pass","shape_order_pass","token_pass","logprob_pass"])
    write_json(PACK / "EFFECTIVE_MODE_CONFIG.json", [{"point":r["point"],"mode":r["mode"],"config":r["config"]} for r in results])
    write_json(PACK / "KERNEL_INVENTORY_SHA256.json", {f"{r['point']}_{r['mode']}":hashlib.sha256("\n".join(r["kernel_names"]).encode()).hexdigest() for r in results})
    index=[]
    for p in sorted(raw.iterdir()):
        if p.is_file() and p.name != "RAW_SHA256SUMS": index.append({"path":str(p),"size_bytes":p.stat().st_size,"sha256":sha(p)})
    tsv(PACK / "RAW_INDEX.tsv", index, ["path","size_bytes","sha256"])
    (raw / "RAW_SHA256SUMS").write_text("".join(f"{x['sha256']}  {Path(x['path']).name}\n" for x in index))
    write_json(PACK / "FINAL_DECISION.json", {"goal":"C16_QWEN_DECODE_EXECUTION_MODE_DECONFLATION_CANARY_109_V1","decision":decision,"reasons":reason,"mp02_pass":bool(comparisons and comparisons[0][0]),"mp03_executed":len(comparisons)>1,"mp03_pass":bool(len(comparisons)>1 and comparisons[1][0]),"automatic_next_goal":False,"forbidden_tools_executed":False,"gpu_active_seconds":duration,"raw_local":str(raw)})

def main():
    PACK.mkdir(parents=True, exist_ok=True)
    authority()
    asset_recheck()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    raw = RAW_BASE / run_id
    raw.mkdir(parents=True, exist_ok=False)
    results, comparisons = [], []
    prior_seconds = float(os.environ.get("C16_PRIOR_GPU_ACTIVE_SECONDS", "0"))
    if prior_seconds < 0 or prior_seconds >= 120:
        raise RuntimeError("INVALID_PRIOR_GPU_BUDGET")
    decision, reason = "CANARY_ENGINEERING_STOP", []
    gpu_start = None
    receipt = {"lock":str(LOCK),"requested_utc":now(),"released":False}
    with LOCK.open("a+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        receipt["acquired_utc"] = now()
        try:
            q = gpu_query()
            deadline = time.monotonic() + 45*60
            while q["compute_processes"] and time.monotonic() < deadline:
                time.sleep(min(30, deadline-time.monotonic()))
                q = gpu_query()
            receipt["gpu_baseline"] = q
            if q["uuid"] != EXPECTED_UUID or q["compute_processes"] or q["memory_used_mib"] > 256:
                raise RuntimeError("GPU_BUSY_OR_AUTHORITY_FAIL_CLOSED")
            gpu_start = time.monotonic()
            for point in ("MP02", "MP03"):
                a = run_child(point, "A", 120-prior_seconds-(time.monotonic()-gpu_start), raw)
                results.append(a)
                b = run_child(point, "B", 120-prior_seconds-(time.monotonic()-gpu_start), raw)
                results.append(b)
                c = compare(point, a, b)
                comparisons.append(c)
                if not c[0]:
                    reason += c[1]
                    if "MODE_B_IDENTITY_INVALID" in reason: decision = "MODE_B_IDENTITY_INVALID"
                    elif "MODE_B_IDENTITY_UNRESOLVED" in reason: decision = "MODE_B_IDENTITY_UNRESOLVED"
                    elif "MODE_A_IDENTITY_UNRESOLVED" in reason: decision = "MODE_A_IDENTITY_UNRESOLVED"
                    else: decision = "MODE_DECONFLATION_CORRECTNESS_FAILED"
                    break
            else:
                decision = "MODE_DECONFLATION_CORRECTNESS_PASS_FOR_OBSERVER_REVIEW_ONLY"
        except Exception as e:
            reason.append(f"{type(e).__name__}: {e}")
            write_json(raw / "ORCHESTRATOR_ERROR.json", {"error":str(e),"traceback":traceback.format_exc()})
        finally:
            finish(raw, results, comparisons, decision, reason, gpu_start, receipt, prior_seconds)
            fcntl.flock(f, fcntl.LOCK_UN)
    print(json.dumps({"decision":decision,"reason":reason,"raw":str(raw)}))

if __name__ == "__main__":
    if sys.argv[1:] == ["--preflight-only"]:
        PACK.mkdir(parents=True, exist_ok=True)
        authority()
        asset_recheck()
        print("CPU_PREFLIGHT_PASS")
    else:
        main()
