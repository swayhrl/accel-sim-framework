#!/usr/bin/env python3
"""CPU-only producer analysis for the GPT-3 public-shape native screen."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import statistics
from pathlib import Path

import numpy as np

from contracts import POINTS, canonical_tables

CELLS=("A_W","B_W","A_E","B_E")
M256=("EXPAND_M256","CONTRACT_M256")


def sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda:stream.read(1<<20),b""): h.update(block)
    return h.hexdigest()


def load(path): return json.loads(Path(path).read_text())
def write_json(path,value): path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")
def write_tsv(path,fields,rows):
    with path.open("w",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=fields,delimiter="\t",extrasaction="ignore",lineterminator="\n"); writer.writeheader()
        for row in rows: writer.writerow({key:("NA" if row.get(key) in (None,"") else row.get(key)) for key in fields})


def stats(values):
    return {"n":len(values),"min_ms":min(values),"median_ms":statistics.median(values),"max_ms":max(values),"mean_ms":statistics.mean(values),"cv":statistics.pstdev(values)/statistics.mean(values)}


def bootstrap(samples,point):
    by={(block,cell):[row["ms"] for row in samples if row["point"]==point and row["block"]==block and row["cell"]==cell] for block in range(25) for cell in CELLS}
    rng=np.random.default_rng(20260928); result=[]
    for _ in range(1000):
        chosen=rng.integers(0,25,size=25); med={cell:float(np.median([v for block in chosen for v in by[(int(block),cell)]])) for cell in CELLS}
        gain_w=1-med["B_W"]/med["A_W"]; gain_e=1-med["B_E"]/med["A_E"]
        result.append((gain_w,gain_e,gain_w-gain_e))
    arr=np.asarray(result)
    return {"seed":20260928,"permutations":1000,"unit":"complete mirror block","gain_W_q05_q50_q95":[float(x) for x in np.quantile(arr[:,0],[.05,.5,.95])],"gain_E_q05_q50_q95":[float(x) for x in np.quantile(arr[:,1],[.05,.5,.95])],"state_interaction_q05_q50_q95":[float(x) for x in np.quantile(arr[:,2],[.05,.5,.95])]}


def parse_ncu(path,track,point,cell="NA"):
    records=list(csv.reader(open(path,newline=""))); header,units=records[0],records[1]; rows=[]
    for values in records[2:]:
        if not values or not values[0] or len(values)!=len(header): continue
        data,unit=dict(zip(header,values)),dict(zip(header,units))
        if not data.get("Kernel Name"): continue
        def number(name):
            value=data[name].replace(",",""); return float(value) if "." in value else int(value)
        kernel=data["Kernel Name"]; kind="GEMM" if "gemm_forward" in kernel else "REDUCTION" if "reduce_kernel" in kernel else "VENDOR_DENSE"
        arm=cell[0] if cell!="NA" else "NA"; state="WARM_SAME_ARM" if cell.endswith("_W") else "EVICT_CONDITIONED" if cell.endswith("_E") else "WARM_ONLY"
        rows.append({"track":track,"point":point,"cell":cell,"arm":arm,"state":state,"kernel_order":len(rows),"kernel_kind":kind,"kernel_name":kernel,"block_size":data["Block Size"],"grid_size":data["Grid Size"],"l1tex_bytes":int(number("l1tex__t_bytes.sum")),"lts_bytes":int(number("lts__t_bytes.sum")),"dram_bytes":int(number("dram__bytes.sum")),"duration_ns":int(number("gpu__time_duration.sum")),"registers_per_thread":int(number("launch__registers_per_thread")),"static_shared_bytes":int(number("launch__shared_mem_per_block_static")),"dynamic_shared_bytes":int(number("launch__shared_mem_per_block_dynamic")),"l1tex_unit":unit["l1tex__t_bytes.sum"],"lts_unit":unit["lts__t_bytes.sum"],"dram_unit":unit["dram__bytes.sum"],"duration_unit":unit["gpu__time_duration.sum"]})
    return rows


def profile_receipt(path):
    found=[]
    for line in Path(path).read_text(errors="replace").splitlines():
        line=line.strip()
        if line.startswith("{"):
            try:
                value=json.loads(line)
                if value.get("status")=="PASS_PROFILE": found.append(value)
            except json.JSONDecodeError: pass
    if not found: raise RuntimeError(f"profile receipt absent: {path}")
    return found[-1]


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--raw",type=Path,required=True); parser.add_argument("--out",type=Path,required=True); args=parser.parse_args()
    raw,out=args.raw,args.out; out.mkdir(parents=True,exist_ok=True)
    qualification=load(raw/"qualification.json"); launch=load(raw/"launch_audit.json"); timing=load(raw/"timing_samples.json")
    if qualification["status"]!="PASS" or launch["status"]!="PASS" or timing["status"]!="PASS": raise RuntimeError("producer qualification failed")
    samples=timing["samples"]
    dense_samples=[row for row in samples if row["track"]=="DENSE"]; w4_samples=[row for row in samples if row["track"]=="W4"]
    if len(dense_samples)!=200 or len(w4_samples)!=800: raise RuntimeError(f"sample totals {len(dense_samples)}/{len(w4_samples)}")

    dense_summary=[]; w4_summary=[]; interactions=[]
    for point in [row["point"] for row in POINTS]:
        values=[row["ms"] for row in dense_samples if row["point"]==point]
        if len(values)!=50: raise RuntimeError(f"dense sample count {point}")
        dense_summary.append({"point":point,"cell":"WARM_ONLY",**stats(values)})
        cells={}
        for cell in CELLS:
            values=[row["ms"] for row in w4_samples if row["point"]==point and row["cell"]==cell]
            if len(values)!=50: raise RuntimeError(f"W4 sample count {point}/{cell}")
            cell_stats=stats(values); cells[cell]=cell_stats["median_ms"]
            w4_summary.append({"record_type":"CELL","point":point,"cell":cell,"arm":cell[0],"state":"WARM_SAME_ARM" if cell.endswith("_W") else "EVICT_CONDITIONED",**cell_stats})
        gain_w=1-cells["B_W"]/cells["A_W"]; gain_e=1-cells["B_E"]/cells["A_E"]; interaction=gain_w-gain_e; boot=bootstrap(w4_samples,point)
        interactions.append({"point":point,"gain_W":gain_w,"gain_E":gain_e,"state_interaction":interaction,"gain_W_q05":boot["gain_W_q05_q50_q95"][0],"gain_W_q50":boot["gain_W_q05_q50_q95"][1],"gain_W_q95":boot["gain_W_q05_q50_q95"][2],"gain_E_q05":boot["gain_E_q05_q50_q95"][0],"gain_E_q50":boot["gain_E_q05_q50_q95"][1],"gain_E_q95":boot["gain_E_q05_q50_q95"][2],"interaction_q05":boot["state_interaction_q05_q50_q95"][0],"interaction_q50":boot["state_interaction_q05_q50_q95"][1],"interaction_q95":boot["state_interaction_q05_q50_q95"][2],"seed":20260928,"permutations":1000})
        w4_summary.append({"record_type":"DERIVED","point":point,"cell":"GAINS","gain_W":gain_w,"gain_E":gain_e,"state_interaction":interaction})

    dense_launch=[row for row in launch["rows"] if row["track"]=="DENSE"]
    w4_launch=[row for row in launch["rows"] if row["track"]=="W4"]
    if len({row["point"] for row in dense_launch})!=4 or len(w4_launch)!=12 or not all(row["pass"] for row in w4_launch): raise RuntimeError("launch audit coverage")
    correctness=[row for row in qualification["rows"] if row["track"]=="W4_CORRECTNESS"]
    if len(correctness)!=4 or not all(row["pass"] for row in correctness): raise RuntimeError("W4 correctness")

    ncu=[]; profile_receipts=[]
    for point in M256:
        ncu+=parse_ncu(raw/f"ncu_dense_{point}.csv","DENSE",point)
        profile_receipts.append(profile_receipt(raw/f"ncu_dense_{point}.log"))
        for cell in CELLS:
            ncu+=parse_ncu(raw/f"ncu_w4_{point}_{cell}.csv","W4",point,cell)
            receipt=profile_receipt(raw/f"ncu_w4_{point}_{cell}.log"); expected=1 if cell.endswith("_E") else 0
            if receipt["conditioner_calls"]!=expected or receipt["conditioner_first_value"]!=expected or receipt["conditioner_last_value"]!=expected: raise RuntimeError(f"conditioner profile receipt {point}/{cell}")
            profile_receipts.append(receipt)
    expected_launch={(row["point"],row["arm"]):row for row in canonical_tables()[1]}
    for point in M256:
        for cell in CELLS:
            rows=[row for row in ncu if row["track"]=="W4" and row["point"]==point and row["cell"]==cell]; arm=cell[0]
            if len(rows)!=(2 if arm=="A" else 1) or rows[0]["kernel_kind"]!="GEMM": raise RuntimeError(f"NCU kernel count {point}/{cell}")
            grid=int(rows[0]["grid_size"].strip("()").split(",")[0].replace(",",""))
            if grid!=expected_launch[(point,arm)]["gemm_grid"]: raise RuntimeError(f"NCU grid {point}/{cell}")
            if arm=="A" and rows[1]["kernel_kind"]!="REDUCTION": raise RuntimeError(f"NCU reduction {point}/{cell}")

    ncu_summary={}
    for track,point,cell in sorted({(row["track"],row["point"],row["cell"]) for row in ncu}):
        rows=[row for row in ncu if (row["track"],row["point"],row["cell"])==(track,point,cell)]
        ncu_summary[f"{track}:{point}:{cell}"]={"kernel_count":len(rows),"l1tex_bytes_total":sum(r["l1tex_bytes"] for r in rows),"lts_bytes_total":sum(r["lts_bytes"] for r in rows),"dram_bytes_total":sum(r["dram_bytes"] for r in rows),"duration_ns_total":sum(r["duration_ns"] for r in rows),"reduction_present":any(r["kernel_kind"]=="REDUCTION" for r in rows)}

    source_commit=(raw/"PRODUCER_SOURCE_COMMIT.txt").read_text().strip(); bootstrap=load(raw/"CPU_BOOTSTRAP_MANIFEST.json")
    prep_pack=Path(__file__).resolve().parents[4]/"docs/vm_tlb/review_packs/C16_GPT3_PUBLIC_SHAPE_PREP_174NEW_V1"
    source={"status":"PASS","run_id":raw.parent.name,"producer_source_commit":source_commit,"producer_branch":"hrl/c16-gpt3-public-shape-scale-transfer-109-v1","lane8_ready_head":"55cfac5f3edd346d8c6083bdd399a206cc463d0d","validated_prep_head":bootstrap["validated_prep_head"],"validated_prep_tree":bootstrap["validated_prep_tree"],"ready_file_sha256":bootstrap["ready_file_sha256"],"synthetic_contract_sha256":sha(prep_pack/"SYNTHETIC_TENSOR_CONTRACT.json"),"launch_table_sha256":sha(prep_pack/"EXPECTED_LAUNCH_AND_SCRATCH.tsv"),"memory_budget_sha256":sha(prep_pack/"SHAPE_AND_MEMORY_BUDGET.tsv"),"accepted_binary_hashes_verified":bootstrap["binary_hashes_verified"],"evidence_boundary":{"dense":"GPT-3 public-dimension FP16 synthetic shape anchor","w4":"AutoAWQ W4 mechanism proxy; not a GPT-3 quantized checkpoint","original_weights_or_natural_activations":False},"lane4_partial_accessed":False}
    write_json(out/"SOURCE_AND_AUTHORITY.json",source)
    write_tsv(out/"SYNTHETIC_TENSOR_RECEIPTS.tsv",["track","point","tensor","shape","dtype","bytes","sha256","formula"],qualification["synthetic_tensor_receipts"])
    memory={"ready_budget":load(prep_pack/"PRE_GPU_READY.json")["memory_budget"],"qualification_lifecycle":qualification["memory_lifecycle"],"timing_lifecycle":timing["memory_lifecycle"],"conditioner":timing["conditioner"],"gpu":qualification["gpu"],"lifetime_rule":"one operator at a time; Dense and W4 live assets not co-resident; one conditioner retained through W4 timing"}
    write_json(out/"MEMORY_LIFECYCLE.json",memory)
    write_tsv(out/"DENSE_TIMING_SAMPLES.tsv",["track","point","sample","ms"],dense_samples)
    write_tsv(out/"DENSE_TIMING_SUMMARY.tsv",["point","cell","n","min_ms","median_ms","max_ms","mean_ms","cv"],dense_summary)
    write_tsv(out/"DENSE_LAUNCH_AUDIT.tsv",["track","point","arm","order","kernel_kind","kernel_name","grid","block","registers_per_thread","static_shared_bytes","dynamic_shared_bytes","pass"],dense_launch)
    write_tsv(out/"W4_CORRECTNESS.tsv",["point","a_sha256","b_sha256","shape","dtype","all_finite","max_abs","mean_abs","relative_l2","changed_element_count","element_count","rtol","atol","pass"],correctness)
    write_tsv(out/"W4_LAUNCH_AUDIT.tsv",["track","point","arm","order","kernel_kind","kernel_name","grid","block","registers_per_thread","static_shared_bytes","dynamic_shared_bytes","scratch_shape","scratch_bytes","reduction_expected","pass"],w4_launch)
    write_tsv(out/"W4_TIMING_SAMPLES.tsv",["track","point","cell","arm","state","block","position","sample_in_cell","ms"],w4_samples)
    write_tsv(out/"W4_TIMING_SUMMARY.tsv",["record_type","point","cell","arm","state","n","min_ms","median_ms","max_ms","mean_ms","cv","gain_W","gain_E","state_interaction"],w4_summary)
    write_tsv(out/"W4_STATE_INTERACTION.tsv",["point","gain_W","gain_E","state_interaction","gain_W_q05","gain_W_q50","gain_W_q95","gain_E_q05","gain_E_q50","gain_E_q95","interaction_q05","interaction_q50","interaction_q95","seed","permutations"],interactions)
    write_tsv(out/"NCU_KERNEL_ROWS.tsv",["track","point","cell","arm","state","kernel_order","kernel_kind","kernel_name","block_size","grid_size","l1tex_bytes","lts_bytes","dram_bytes","duration_ns","registers_per_thread","static_shared_bytes","dynamic_shared_bytes","l1tex_unit","lts_unit","dram_unit","duration_unit"],ncu)
    write_json(out/"NCU_SUMMARY.json",{"status":"PASS","contract":{"profiles":10,"replay_mode":"application","cache_control":"none","metrics":["l1tex__t_bytes.sum","lts__t_bytes.sum","dram__bytes.sum","gpu__time_duration.sum"],"tensor_level_attribution":"FORBIDDEN"},"profiles":ncu_summary,"profile_receipts":profile_receipts})

    interaction_map={row["point"]:row for row in interactions}; dense_map={row["point"]:row for row in dense_summary}
    lines=["# 科学解释（producer侧描述性）","","本结果只使用GPT-3公开FFN尺寸；Dense是合成FP16 shape anchor，W4是既有AutoAWQ内核的机制代理。它们都不是GPT-3原始权重、自然激活或完整模型性能。",""]
    for point in [row["point"] for row in POINTS]:
        row=interaction_map[point]; lines.append(f"- `{point}`：gain_W={100*row['gain_W']:.3f}%，gain_E={100*row['gain_E']:.3f}%，state interaction={100*row['state_interaction']:.3f}个百分点；Dense median={dense_map[point]['median_ms']:.6f} ms。")
    lines += ["","M1是否因更大N而减少对split8额外CTA的依赖、M256方向是否延续旧7B结果、以及>4×L2 qweight下W/E交互如何变化，以上仅作为producer观察列示；最终scale-transfer判断留给Lane6独立consumer。EXPAND与CONTRACT的grid、workspace和reduction差异共同变化，producer不建立通用预测器。NCU计数按kernel保留，不归因到具体tensor，也不证明唯一L2/cache/TLB机制。",""]
    (out/"SCIENTIFIC_INTERPRETATION.md").write_text("\n".join(lines))
    decision={"decision":"PRODUCER_NATIVE_SCREEN_PASS_PENDING_LANE6_INDEPENDENT_CONSUMER","run_id":raw.parent.name,"dense_points":4,"w4_cells":16,"timing_samples":{"dense":len(dense_samples),"w4":len(w4_samples)},"ncu_profiles":10,"correctness":"PASS_ALL_FOUR_W4_POINTS","launch_identity":"PASS","state_interactions":interaction_map,"automatic_sass_or_simulation":False,"claim_boundary":source["evidence_boundary"]}
    write_json(out/"FINAL_DECISION.json",decision)
    (out/"NEXT_174_CONSUMER_CONTRACT.md").write_text(f"""# Lane6 independent consumer contract\n\n- RUN_ID: `{raw.parent.name}`\n- producer source commit: `{source_commit}`\n- producer final commit: `TO_BE_BOUND_BY_PUBLICATION_HEAD`\n- Dense timing rows: 200; W4 timing rows: 800; W4 cells: 16; NCU profiles: 10\n- recompute all summaries, W4 correctness, launch gates, state interactions and public-shape/old-Qwen comparison from raw/pack tables\n- use Lane8 frozen formulas and `OLD_QWEN_COMPARISON_CONTRACT.json`; do not use producer interpretation as calculation authority\n- preserve Dense/W4 evidence-class separation and all claim boundaries\n- do not automatically start SASS capture or simulation\n""")
    (out/"README.md").write_text(f"# C16 GPT-3 public-shape scale-transfer native producer\n\nRUN_ID: `{raw.parent.name}`\n\nStatus: `PRODUCER_NATIVE_SCREEN_PASS_PENDING_LANE6_INDEPENDENT_CONSUMER`. Four Dense shape anchors, sixteen W4 arm/state cells, 1000 CUDA-event samples total and ten bounded NCU profiles completed on node109 RTX4080 under one outer lock.\n")
    lock={"status":"PASS","lock_path":"/data/c16/locks/c16_gpu_campaign.lock","acquisition":"ONE_OUTER_GPU_CAMPAIGN","release":"RELEASED_BEFORE_CPU_ANALYSIS","start_utc":(raw/"GPU_LOCK_START_UTC.txt").read_text().strip(),"end_utc":(raw/"GPU_LOCK_END_UTC.txt").read_text().strip(),"gpu_identity":(raw/"GPU_IDENTITY.txt").read_text().strip(),"producer_source_commit":source_commit,"nvidia_smi_pre":{"path":str(raw/"NVIDIA_SMI_PRE.txt"),"sha256":sha(raw/"NVIDIA_SMI_PRE.txt")},"nvidia_smi_post":{"path":str(raw/"NVIDIA_SMI_POST.txt"),"sha256":sha(raw/"NVIDIA_SMI_POST.txt")},"clocks_power_persistence_driver_modified":False}
    write_json(out/"GPU_LOCK_RECEIPT.json",lock)

    for path in sorted(raw.glob("ncu_*.csv")): shutil.copy2(path,out/f"RAW_{path.name}")
    raw_index=[]
    for path in sorted(raw.rglob("*")):
        if path.is_file(): raw_index.append({"artifact":path.relative_to(raw).as_posix(),"path":str(path),"bytes":path.stat().st_size,"sha256":sha(path),"committed_copy":f"RAW_{path.name}" if path.name.startswith("ncu_") and path.suffix==".csv" else "INDEX_ONLY"})
    write_tsv(out/"RAW_INDEX.tsv",["artifact","path","bytes","sha256","committed_copy"],raw_index)
    print(json.dumps({"status":"PASS_ANALYSIS","run_id":raw.parent.name,"dense_samples":len(dense_samples),"w4_samples":len(w4_samples),"ncu_profiles":10,"source_commit":source_commit},sort_keys=True))


if __name__=="__main__": main()
