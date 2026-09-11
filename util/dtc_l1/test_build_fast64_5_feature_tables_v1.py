#!/usr/bin/env python3
"""Positive/negative fixtures for measured-only Stage5 feature building."""
from __future__ import annotations
import csv, json, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; TOOL=ROOT/"util/dtc_l1/build_fast64_5_feature_tables_v1.py"
R=("ATAX","BICG","GESUMMV","GEMM","2DConvolution","Btree","DWT2D","Gaussian","Hotspot1","LUD","NN","MRI-Q")
def tsv(p,fields,rows):
    with p.open("w",encoding="utf-8",newline="") as f: w=csv.DictWriter(f,fieldnames=fields,delimiter="\t");w.writeheader();w.writerows(rows)
with tempfile.TemporaryDirectory() as d:
    d=Path(d); s4=d/"s4";s3=d/"s3";s4.mkdir();s3.mkdir(); rows=[]
    for w in R:
      for mode in ("BASE","IO","OO"):
        p=d/f"{w}-{mode}.json"; m={"gpu_tot_sim_cycle":100 if mode=="BASE" else 80,"gpu_tot_sim_insn":10,"DTC_L1_lower_outstanding":0,"DTC_L1_lower_outstanding_peak":2,"DTC_L1_lower_cap_full_events":0,"L1D_total_cache_accesses":1,"L1D_total_cache_misses":1,"L2_total_cache_accesses":1,"L2_total_cache_misses":1,"L2_total_cache_reservation_fails":0,"gpgpu_n_mem_read_global":1,"gpgpu_n_mem_write_global":1};m.update({"DTC_L1_lower_requests_acquired":1,"DTC_L1_lower_requests_released":1} if mode=="BASE" else {"DTC_L1_lower_credit_acquired":1,"DTC_L1_lower_credit_released":1});p.write_text(json.dumps({"metrics":m}),encoding="utf-8");rows.append({"workload":w,"mode":mode,"evidence_path":str(p)})
    tsv(s4/"fast64_4_primary_matrix.tsv",["workload","mode","evidence_path"],rows)
    tsv(s3/"fast64_3_structural_pressure.tsv",["workload","pib_full_events"],[{"workload":w,"pib_full_events":0} for w in R])
    ledger=d/"ledger.tsv";tsv(ledger,["stage","current_state"],[{"stage":"FAST64.4","current_state":"PASS"}])
    out=d/"out";ok=subprocess.run([str(TOOL),"--stage-ledger",str(ledger),"--stage4-dir",str(s4),"--stage3-dir",str(s3),"--output-dir",str(out)],text=True,capture_output=True);assert ok.returncode==0,ok.stderr
    assert len(list(csv.DictReader((out/"fast12_summary.csv").open())))==13
    tsv(ledger,["stage","current_state"],[{"stage":"FAST64.4","current_state":"ACTIVE"}]);bad=subprocess.run([str(TOOL),"--stage-ledger",str(ledger),"--stage4-dir",str(s4),"--stage3-dir",str(s3),"--output-dir",str(d/"bad")],text=True,capture_output=True);assert bad.returncode!=0 and "PASS_REQUIRED" in bad.stderr
print("FAST64_5_FEATURE_TABLES_V1_REGRESSION_PASS")
