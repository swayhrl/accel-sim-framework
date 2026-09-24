#!/usr/bin/env python3
"""Hash-locked immutable runner for predeclared SG3 downstream sensitivities."""
from __future__ import annotations
import argparse, csv, hashlib, json, re, shutil, subprocess, uuid
from datetime import datetime, timezone
from pathlib import Path

TRACE_CONFIG_SHA = "19dd14b3a4b6c1a1cb2833bd091f0dbd485ad79336ef7d4b0c9db1f7c46f504e"
OBSERVER_ON_NAME = "SG3_DOWNSTREAM_OBSERVER_ON.config"
OBSERVER_ON_SHA = "916dd5cf98b57bb99a20ac11871a670b00db293ce7c336f0f88ee8b75469fad2"
GUARD_RETRY_CORE = "9b6bd33f3fb3236fd493db2dd7e11d356d1f272f"
OVERLAYS = {
    ("capacity", "half"): ("SG3_L2_CAPACITY_HALF.config", "c4a714603a0433af5730156122b8742972e65044648b700b5ad9d553bfad7f5b", "S:128:128:8,L:B:m:L:L,A:192:4,32:0,32"),
    ("capacity", "base"): (None, None, "S:128:128:16,L:B:m:L:L,A:192:4,32:0,32"),
    ("capacity", "double"): ("SG3_L2_CAPACITY_DOUBLE.config", "e5cb47a43515ff3c70b88f8d6a3e406e0d404eedaad3d7fd293f00fe9d9e47a7", "S:128:128:32,L:B:m:L:L,A:192:4,32:0,32"),
    ("mshr", "half"): ("SG3_L2_MSHR_HALF.config", "651098a99dcfb14c29ce940805bf14d8c8568a3a102f0a91f7ff2d7db82f1b07", "S:128:128:16,L:B:m:L:L,A:96:4,32:0,32"),
    ("mshr", "base"): (None, None, "S:128:128:16,L:B:m:L:L,A:192:4,32:0,32"),
    ("mshr", "double"): ("SG3_L2_MSHR_DOUBLE.config", "85bf9ed344f5308278294b192034ad21ef19ca63fc162ca28819afa2dab59759", "S:128:128:16,L:B:m:L:L,A:384:4,32:0,32"),
    ("mshr", "quad"): ("SG3_L2_MSHR_QUAD.config", "9f40ad53da8d1d2c76a1f6643127b7553fc2c40fd06b260214d8e90b566bcd9e", "S:128:128:16,L:B:m:L:L,A:768:4,32:0,32"),
    ("queue", "128"): ("SG3_L2_MISS_QUEUE_128.config", "4a52cada89a07a4255629cdb08bb31cc98fd24381b99183bc28cbbb7a81e5119", "S:128:128:16,L:B:m:L:L,A:192:4,128:0,32"),
    ("memservice", "buswidth32"): ("SG3_DRAM_BUSWIDTH_32.config", "9b3ab783a052efd1a0360104852f82607e6a6f507c71e05ba88f1f584d594c28", "S:128:128:16,L:B:m:L:L,A:192:4,32:0,32"),
    ("queue_memservice", "128_buswidth32"): (("SG3_L2_MISS_QUEUE_128.config", "SG3_DRAM_BUSWIDTH_32.config"), ("4a52cada89a07a4255629cdb08bb31cc98fd24381b99183bc28cbbb7a81e5119", "9b3ab783a052efd1a0360104852f82607e6a6f507c71e05ba88f1f584d594c28"), "S:128:128:16,L:B:m:L:L,A:192:4,128:0,32"),
    ("queuechain", "A_l2dram256"): ("SG3_QUEUE_CHAIN_A_L2_TO_DRAM_256.config", "72808731824b738bb5b1b1d0be0f0809839c523719220d3429c5a2bda7cb7998", "S:128:128:16,L:B:m:L:L,A:192:4,32:0,32"),
    ("queuechain", "B_scheduler256"): ("SG3_QUEUE_CHAIN_B_SCHEDULER_256.config", "68abc683238b808d81dd570be05de638c3301c752eed2da1bd64c9bd816355b7", "S:128:128:16,L:B:m:L:L,A:192:4,32:0,32"),
    ("queuechain", "C_return256_768"): ("SG3_QUEUE_CHAIN_C_RETURN_256_768.config", "8bda28f31dc8ef5c4c3f8b770babd6f9bf4b4627c550749a4c519375cb382870", "S:128:128:16,L:B:m:L:L,A:192:4,32:0,32"),
    ("queuechain", "D_full"): (("SG3_L2_MISS_QUEUE_128.config", "SG3_QUEUE_CHAIN_D_FULL_256_768.config"), ("4a52cada89a07a4255629cdb08bb31cc98fd24381b99183bc28cbbb7a81e5119", "1e8e8fb8851de09bcbb081ebcb5875c9bb63a37997f969c6ced8f65b3e4e08f4"), "S:128:128:16,L:B:m:L:L,A:192:4,128:0,32"),
    ("queuechain", "E_dram1700"): ("SG3_QUEUE_CHAIN_E_DRAM_1700.config", "d1016b1fdeebe3feccd95df8d44999d25e496f1d93c1dde203059f7362bb9367", "S:128:128:16,L:B:m:L:L,A:192:4,32:0,32"),
    ("queuechain", "F_full_dram1700"): (("SG3_L2_MISS_QUEUE_128.config", "SG3_QUEUE_CHAIN_F_FULL_DRAM_1700.config"), ("4a52cada89a07a4255629cdb08bb31cc98fd24381b99183bc28cbbb7a81e5119", "973f197c84d624ba68b0a0b004d32e68c4c4a9ef90bef76f135231ef8c195a0e"), "S:128:128:16,L:B:m:L:L,A:192:4,128:0,32"),
    ("cap", "512"): ("SG3_DTC_CAP_512.config", "7c3232b395c5c1b3c3297ed3f540d537a8d824b95f6361ed414687d9d7c18043", "512"),
    ("cap", "1024"): ("SG3_DTC_CAP_1024.config", "22ae581059370debb31098a916c7ad0e50a88652e9f0108546dcc5216c67936b", "1024"),
    ("cap", "2048"): ("SG3_DTC_CAP_2048.config", "b18a857199435851b7815a075552291ab456ef786b23d5f1415d32b457135f66", "2048"),
    ("cap", "4096"): ("SG3_DTC_CAP_4096.config", "48fc87a7dfabbc00451a76d53632932f512be603cc451a33181d1ec5edc4644b", "4096"),
    ("cap", "8192"): ("SG3_DTC_CAP_8192.config", "f8083f9732c406220748bc5c1b9e534e7f02ddfe49d14ffe9792b1cd3d3cc398", "8192"),
}
QUEUE_CHAIN_EXPECTATIONS = {
    "A_l2dram256": (("gpgpu_dram_partition_queues", "64:256:64:64"),),
    "B_scheduler256": (("gpgpu_frfcfs_dram_sched_queue_size", "256"),),
    "C_return256_768": (("gpgpu_dram_partition_queues", "64:64:256:64"), ("gpgpu_dram_return_queue_size", "768")),
    "D_full": (("gpgpu_dram_partition_queues", "64:256:256:64"), ("gpgpu_frfcfs_dram_sched_queue_size", "256"), ("gpgpu_dram_return_queue_size", "768")),
    "E_dram1700": (("gpgpu_clock_domains", "1410.0:1410.0:1410.0:1700.0"),),
    "F_full_dram1700": (("gpgpu_dram_partition_queues", "64:256:256:64"), ("gpgpu_frfcfs_dram_sched_queue_size", "256"), ("gpgpu_dram_return_queue_size", "768"), ("gpgpu_clock_domains", "1410.0:1410.0:1410.0:1700.0")),
}

def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1048576),b""): h.update(b)
    return h.hexdigest()
def kv(p, d): Path(p).write_text("".join(f"{k}\t{v}\n" for k,v in d.items()),encoding="utf-8")
def readkv(p): return dict(x.split("\t",1) for x in Path(p).read_text().splitlines() if "\t" in x)
def authority(p,w):
    with Path(p).open(newline="",encoding="utf-8") as f: rows=[r for r in csv.DictReader(f,delimiter="\t") if r["workload"]==w]
    if len(rows)!=1: raise RuntimeError("workload is not one exact FAST12 authority row")
    return rows[0]
def metric(s,n):
    m=re.findall(rf"^{re.escape(n)}\s*=\s*(\d+)\s*$",s,re.M)
    if not m: raise RuntimeError(f"missing {n}")
    return int(m[-1])
def real_metric(s,n):
    m=re.findall(rf"^{re.escape(n)}\s*=\s*(\d+(?:\.\d+)?)\s*$",s,re.M)
    if not m: raise RuntimeError(f"missing {n}")
    return float(m[-1])
def l2_fail_reason(s,reason):
    terminal_block=s.rsplit("L2_total_cache_reservation_fail_breakdown:\n",1)[-1]
    return sum(int(v) for v in re.findall(rf"^\s*L2_cache_stats_fail_breakdown\[[^]]+\]\[{re.escape(reason)}\]\s*=\s*(\d+)\s*$",terminal_block,re.M))
def l2_terminal_consistency(vals, core_source_head):
    reasons=["LINE_ALLOC_FAIL","MISS_QUEUE_FULL","MSHR_ENRTY_FAIL","MSHR_MERGE_ENRTY_FAIL","MSHR_RW_PENDING"]
    classified=sum(vals[f"L2_fail_{reason}"] for reason in reasons)
    residual=vals["L2_total_cache_reservation_fails"]-classified
    # Core9's source-audited merge-tag identity guard returns a legal retry
    # before it can increment one of the five resource-failure reasons.  The
    # aggregate RESERVATION_FAIL counter still records it.  This field is an
    # inference from the immutable terminal report, never a resource cause.
    vals["L2_fail_merge_tag_identity_guard_retry_inferred"]=residual
    return (vals["L2_total_cache_misses"]<=vals["L2_total_cache_accesses"] and residual>=0 and
            (residual==0 or core_source_head==GUARD_RETRY_CORE))

def run(a):
    key=(a.dimension,a.point)
    if key not in OVERLAYS: raise RuntimeError("unpredeclared SG3 point")
    repo, src=Path(a.repo).resolve(),authority(a.authority,a.workload)
    base=repo/"configs/dtc_l1/fast64"/("FAST64_IO.config" if a.mode=="IO" else "FAST64_OO.config")
    overlay_name, overlay_sha, expected=OVERLAYS[key]
    overlay_names=(overlay_name,) if isinstance(overlay_name,str) else overlay_name
    overlay_shas=(overlay_sha,) if isinstance(overlay_sha,str) else overlay_sha
    overlays=[] if overlay_name is None else [repo/"docs/dtc_l1/iscas2027/granularity/sg3/config"/n for n in overlay_names]
    if any(sha(p)!=h for p,h in zip(overlays,overlay_shas)): raise RuntimeError("overlay hash preflight failed")
    tc=Path(a.trace_config).resolve(); trace=Path(src["trace_list"]); runtime=Path(a.simulator)
    if sha(tc)!=TRACE_CONFIG_SHA or sha(trace)!=src["trace_list_sha256"] or not runtime.is_file(): raise RuntimeError("trace/runtime preflight failed")
    ident=str(uuid.uuid4()); rd=Path(a.runs_root)/f"sg3_{a.dimension}_{a.point}_{a.mode}_{a.workload}_{ident}"
    rd.mkdir(parents=True); frozen=rd/"immutable_sg3_sensitivity_campaign.py"; shutil.copy2(__file__,frozen); frozen.chmod(0o555)
    observer=repo/"docs/dtc_l1/iscas2027/granularity/sg3/config"/OBSERVER_ON_NAME
    if sha(observer)!=OBSERVER_ON_SHA: raise RuntimeError("observer-on overlay hash preflight failed")
    chain=[base]+overlays+[tc,observer]
    stage = "R1" if a.dimension == "queuechain" else "C1" if a.dimension in ("memservice","queue_memservice") else 2 if a.dimension == "capacity" else 4 if a.dimension == "cap" else 3
    default_cap_dimensions=("queue","memservice","queue_memservice","queuechain")
    m={"schema":"SG3_SENSITIVITY_ATTEMPT_V4","attempt_uuid":ident,"lane":"SG3","stage":f"SG3.{stage}","dimension":a.dimension,"point":a.point,"expected_field":expected,"expected_queue_chain":";".join(f"{k}={v}" for k,v in QUEUE_CHAIN_EXPECTATIONS.get(a.point,())) if a.dimension=="queuechain" else "NOT_APPLICABLE","expected_dram_buswidth":"32" if a.dimension in ("memservice","queue_memservice") else "NOT_APPLICABLE","expected_dtc_lower_outstanding_cap":"8192" if a.dimension in default_cap_dimensions else "NOT_APPLICABLE","workload":a.workload,"mode":a.mode,"observer":"1","launch_utc":now(),"immutable_runner":str(frozen),"runner_sha256":sha(frozen),"simulator":str(runtime),"simulator_sha256":sha(runtime),"core_source_head":a.core_source_head,"config_chain":"|".join(map(str,chain)),"config_chain_sha256":"|".join(sha(x) for x in chain),"trace_list":str(trace),"trace_list_sha256":sha(trace),"expected_instructions":src["instructions"]}
    kv(rd/"RUN_MANIFEST.tsv",m); kv(rd/"RUN_START.tsv",m)
    cmd=[str(runtime),"-trace",str(trace)]+sum((["-config",str(x)] for x in chain),[])
    with (rd/"simulator.stdout").open("wb") as o,(rd/"simulator.stderr").open("wb") as e: code=subprocess.run(cmd,cwd=rd,stdout=o,stderr=e).returncode
    end={"attempt_uuid":ident,"terminal_utc":now(),"simulator_exit_status":code,"stdout_sha256":sha(rd/"simulator.stdout"),"stderr_sha256":sha(rd/"simulator.stderr")}; kv(rd/"RUN_TERMINAL.tsv",end)
    with (rd/"RUN_MANIFEST.tsv").open("a") as f: [f.write(f"{k}\t{v}\n") for k,v in end.items()]
    print(rd)

def validate(a):
    rd=Path(a.run_dir); m,t=readkv(rd/"RUN_MANIFEST.tsv"),readkv(rd/"RUN_TERMINAL.tsv"); out=(rd/"simulator.stdout").read_text(errors="replace"); err=(rd/"simulator.stderr").read_text(errors="replace"); src=authority(a.authority,a.workload)
    key=(a.dimension,a.point); expected=OVERLAYS[key][2]; mode_n="2" if a.mode=="IO" else "3"; pre="io" if a.mode=="IO" else "oo"
    checks={"uuid":m.get("attempt_uuid")==t.get("attempt_uuid"),"natural_exit":t.get("simulator_exit_status")=="0","workload":m.get("workload")==a.workload,"mode":m.get("mode")==a.mode,"observer_manifest":m.get("observer")=="1","trace":m.get("trace_list_sha256")==src["trace_list_sha256"],"mode_echo":bool(re.search(rf"^-gpgpu_dtc_l1_mode\s+{mode_n}\s+#",out,re.M)),"observer_echo":bool(re.search(r"^-gpgpu_sg3_downstream_observer\s+1\s+#",out,re.M)),"error_scan":not bool(re.search(r"assertion failed|fatal error|deadlock detected|segmentation fault|core dumped",out+err,re.I))}
    if a.dimension=="cap": checks["sweep_echo"]=bool(re.search(rf"^-gpgpu_dtc_l1_lower_outstanding_cap\s+{expected}\s+#",out,re.M))
    else: checks["sweep_echo"]=bool(re.search(rf"^-gpgpu_cache:dl2\s+{re.escape(expected)}\s+#",out,re.M))
    if a.dimension in ("queue","memservice","queue_memservice","queuechain"): checks["default_dtc_cap_echo"]=bool(re.search(r"^-gpgpu_dtc_l1_lower_outstanding_cap\s+8192\s+#",out,re.M))
    if a.dimension in ("memservice","queue_memservice"): checks["dram_buswidth_echo"]=bool(re.search(r"^-gpgpu_dram_buswidth\s+32\s+#",out,re.M)) and bool(re.search(r"DRAM\[0\]: .*busW=32 BL=2",out))
    if a.dimension=="queuechain":
        for knob,value in QUEUE_CHAIN_EXPECTATIONS[a.point]:
            checks[f"queue_chain_{knob}"]=bool(re.search(rf"^-{re.escape(knob)}\s+{re.escape(value)}\s+#",out,re.M))
    vals={}
    try:
        required=["gpu_tot_sim_cycle","gpu_tot_sim_insn",f"DTC_L1_{pre}_lower_created",f"DTC_L1_{pre}_lower_responses","DTC_L1_lower_credit_acquired","DTC_L1_lower_credit_released","DTC_L1_lower_outstanding","L2_total_cache_accesses","L2_total_cache_misses","L2_total_cache_pending_hits","L2_total_cache_reservation_fails","SG3_dtc_core_tick_samples","SG3_dtc_lower_outstanding_integral","SG3_l2_bank_tick_samples","SG3_l2_mshr_occupancy_integral","SG3_l2_miss_queue_occupancy_integral","SG3_lower_lifetime_completed","SG3_lower_lifetime_sum_cycles","SG3_lower_lifetime_max_cycles","SG3_lower_lifetime_unmatched_completions","SG3_lower_lifetime_live_records"]
        for n in required: vals[n]=metric(out,n)
        for n in ["L2_cache_data_port_util","L2_cache_fill_port_util"]: vals[n]=real_metric(out,n)
        reasons=["LINE_ALLOC_FAIL","MISS_QUEUE_FULL","MSHR_ENRTY_FAIL","MSHR_MERGE_ENRTY_FAIL","MSHR_RW_PENDING"]
        for reason in reasons: vals[f"L2_fail_{reason}"]=l2_fail_reason(out,reason)
        checks["instruction_identity"]=vals["gpu_tot_sim_insn"]==int(src["instructions"]); checks["drain"]=vals[f"DTC_L1_{pre}_lower_created"]==vals[f"DTC_L1_{pre}_lower_responses"] and vals["DTC_L1_lower_credit_acquired"]==vals["DTC_L1_lower_credit_released"] and vals["DTC_L1_lower_outstanding"]==0
        checks["observer_terminal_closure"]=vals["SG3_lower_lifetime_unmatched_completions"]==0 and vals["SG3_lower_lifetime_live_records"]==0
        checks["l2_terminal_consistency"]=l2_terminal_consistency(vals,m.get("core_source_head"))
    except RuntimeError: checks["instruction_identity"]=checks["drain"]=checks["observer_terminal_closure"]=checks["l2_terminal_consistency"]=False
    r={"schema":"SG3_SENSITIVITY_STRICT_VALIDATION_V3","status":"PASS" if all(checks.values()) else "FAIL","workload":a.workload,"mode":a.mode,"dimension":a.dimension,"point":a.point,"run_dir":str(rd),"metrics":vals,"checks":checks,"validation_utc":now()}; target=Path(a.output) if a.output else rd/"VALIDATION.json"; target.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n"); print(json.dumps(r,sort_keys=True));
    if r["status"]!="PASS": raise SystemExit(1)
def main():
    p=argparse.ArgumentParser(); ss=p.add_subparsers(dest="cmd",required=True)
    for c in ("run","validate"):
        x=ss.add_parser(c); x.add_argument("--authority",required=True); x.add_argument("--workload",required=True); x.add_argument("--mode",choices=("IO","OO"),required=True); x.add_argument("--dimension",choices=("capacity","mshr","queue","cap","memservice","queue_memservice","queuechain"),required=True); x.add_argument("--point",required=True)
        if c=="run": x.add_argument("--repo",required=True); x.add_argument("--runs-root",required=True); x.add_argument("--trace-config",required=True); x.add_argument("--simulator",required=True); x.add_argument("--core-source-head",required=True); x.set_defaults(fn=run)
        else: x.add_argument("--run-dir",required=True); x.add_argument("--output"); x.set_defaults(fn=validate)
    a=p.parse_args(); a.fn(a)
if __name__=="__main__": main()
