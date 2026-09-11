#!/usr/bin/env python3
"""Build measured-only FAST64.5 feature tables after FAST64.4 PASS.

This future-only tool intentionally has no causal-classification logic.
"""
from __future__ import annotations
import argparse, csv, json, math, os, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROSTER = ("ATAX", "BICG", "GESUMMV", "GEMM", "2DConvolution", "Btree", "DWT2D", "Gaussian", "Hotspot1", "LUD", "NN", "MRI-Q")
MODES = ("BASE", "IO", "OO")
def read(path):
    with path.open(encoding="utf-8", newline="") as f:
        lines=f.readlines()
    if path.suffix==".tsv":
        header=next((n for n,line in enumerate(lines) if line.startswith("stage\tcurrent_state")),None)
        if header is not None: lines=lines[header:]
    return list(csv.DictReader(lines, delimiter="\t" if path.suffix==".tsv" else ","))
def write(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
def value(m, key): return m.get(key, "UNSUPPORTED")
def lower(m, mode, kind):
    key = "DTC_L1_lower_requests_" + ("acquired" if kind=="create" else "released") if mode=="BASE" else "DTC_L1_lower_credit_" + ("acquired" if kind=="create" else "released")
    return value(m,key)
def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--stage-ledger",type=Path,required=True); p.add_argument("--stage4-dir",type=Path,required=True); p.add_argument("--stage3-dir",type=Path,required=True); p.add_argument("--output-dir",type=Path,required=True); a=p.parse_args()
    ledger=read(a.stage_ledger)
    if not any(r.get("stage")=="FAST64.4" and r.get("current_state", r.get("status"))=="PASS" for r in ledger): raise RuntimeError("FAST64_4_PASS_REQUIRED")
    matrix=read(a.stage4_dir/"fast64_4_primary_matrix.tsv")
    if len(matrix)!=36 or {(r.get("workload"),r.get("mode")) for r in matrix}!={(w,m) for w in ROSTER for m in MODES}: raise RuntimeError("FAST64_4_EXACT_MATRIX_REQUIRED")
    structural={r["workload"]:r for r in read(a.stage3_dir/"fast64_3_structural_pressure.tsv")}
    if set(structural)!=set(ROSTER): raise RuntimeError("FAST64_3_EXACT_STRUCTURAL_REQUIRED")
    records={}
    for r in matrix:
        path=Path(r["evidence_path"]); path=path if path.is_absolute() else ROOT/"docs/dtc_l1/fast64/generated"/path
        data=json.loads(path.read_text(encoding="utf-8")); records[(r["workload"],r["mode"])]=data["metrics"]
    summary=[]; stalls=[]; live=[]; traffic=[]; io_oo=[]
    for w in ROSTER:
        b,i,o=(records[(w,m)] for m in MODES); bc,ic,oc=(x["gpu_tot_sim_cycle"] for x in (b,i,o))
        summary.append(dict(workload=w,base_cycles=bc,io_cycles=ic,oo_cycles=oc,speedup_io=f"{bc/ic:.9f}",speedup_oo=f"{bc/oc:.9f}",instructions=b["gpu_tot_sim_insn"]))
        stalls.append(dict(**structural[w],base_lower_cap_full=value(b,"DTC_L1_lower_cap_full_events")))
        for mode,m in zip(MODES,(b,i,o)): live.append(dict(workload=w,mode=mode,create_or_acquire=lower(m,mode,"create"),complete_or_release=lower(m,mode,"complete"),peak=value(m,"DTC_L1_lower_outstanding_peak"),average_per_sm="MISSING_SOURCE_DEFINED_AVERAGE",terminal_lower=value(m,"DTC_L1_lower_outstanding")))
        for mode,m in zip(MODES,(b,i,o)): traffic.append(dict(workload=w,mode=mode,l1_accesses=value(m,"L1D_total_cache_accesses"),l1_misses=value(m,"L1D_total_cache_misses"),l2_accesses=value(m,"L2_total_cache_accesses"),l2_misses=value(m,"L2_total_cache_misses"),l2_reservation_fails=value(m,"L2_total_cache_reservation_fails"),global_reads=value(m,"gpgpu_n_mem_read_global"),global_writes=value(m,"gpgpu_n_mem_write_global")))
        for mode,m in (("IO",i),("OO",o)): io_oo.append(dict(workload=w,mode=mode,head_not_ready=value(m,"DTC_L1_io_head_not_ready_cycles"),head_ready=value(m,"DTC_L1_io_pib_head_ready_cycles"),hol_cycles=value(m,"DTC_L1_io_hol_ready_younger_cycles"),hol_count=value(m,"DTC_L1_io_hol_ready_younger_count_sum"),retire=value(m,"DTC_L1_oo_retire_count" if mode=="OO" else "DTC_L1_io_retire_count"),ooo_retire=value(m,"DTC_L1_oo_out_of_order_retires"),immediate_reclaim=value(m,"DTC_L1_oo_immediate_reclaims"),deferred_reclaim=value(m,"DTC_L1_oo_deferred_reclaims"),final_ref_reclaim=value(m,"DTC_L1_oo_final_ref_reclaims"),active_refs=value(m,"DTC_L1_oo_active_refs"),wakeups=value(m,"DTC_L1_oo_wakeups")))
    gm=lambda k: math.prod(float(r[k]) for r in summary)**(1/12)
    summary.append(dict(workload="GM-FAST12",base_cycles="n/a",io_cycles="n/a",oo_cycles="n/a",speedup_io=f"{gm('speedup_io'):.9f}",speedup_oo=f"{gm('speedup_oo'):.9f}",instructions="exact_12_members"))
    if a.output_dir.exists(): raise RuntimeError("OUTPUT_ALREADY_EXISTS")
    tmp=Path(tempfile.mkdtemp(prefix=".fast64_5.",dir=a.output_dir.parent))
    try:
        for name,rows in (("fast12_summary.csv",summary),("fast12_stalls.csv",stalls),("fast12_live_misses.csv",live),("fast12_traffic.csv",traffic),("fast12_io_oo.csv",io_oo)):
            write(tmp/name,list(rows[0]),rows)
        os.replace(tmp,a.output_dir)
    except Exception:
        import shutil; shutil.rmtree(tmp,ignore_errors=True); raise
    print("FAST64_5_FEATURE_TABLES_V1_CANDIDATE_PASS output="+str(a.output_dir))
if __name__=="__main__": main()
