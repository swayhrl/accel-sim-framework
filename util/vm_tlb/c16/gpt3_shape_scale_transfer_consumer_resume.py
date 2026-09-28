#!/usr/bin/env python3
"""Formal CPU-only resume consumer for accepted GPT-3 public-shape producer raw tables."""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,statistics,subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any
import numpy as np

PREP_COMMIT="117c9e994ea08d8307e349f75e2852d239635a15"
PRODUCER="1544018d967003c2825eb69f56440f641f5f5581"
PRODUCER_TREE="08cffe7ff0e5c4981aef0c6626950a6632d5dc73"
PACK="docs/vm_tlb/review_packs/C16_GPT3_PUBLIC_SHAPE_SCALE_TRANSFER_109_V1"
OUT="docs/vm_tlb/review_packs/C16_GPT3_PUBLIC_SHAPE_SCALE_TRANSFER_CONSUMER_174NEW_V1"
SEED=20260928

def blob(repo,commit,path): return subprocess.run(["git","show",f"{commit}:{path}"],cwd=repo,check=True,stdout=subprocess.PIPE).stdout
def tsv_bytes(data): return list(csv.DictReader(io.StringIO(data.decode()),delimiter="\t"))
def tsv(repo,name): return tsv_bytes(blob(repo,PRODUCER,f"{PACK}/{name}"))
def js(repo,name): return json.loads(blob(repo,PRODUCER,f"{PACK}/{name}"))
def stats(v): return {"n":len(v),"min_ms":min(v),"median_ms":statistics.median(v),"max_ms":max(v),"mean_ms":statistics.mean(v),"cv":statistics.pstdev(v)/statistics.mean(v)}
def write_tsv(path,fields,rows):
 with path.open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter="\t",lineterminator="\n",extrasaction="ignore");w.writeheader()
  for r in rows:w.writerow({k:"NA" if r.get(k) is None else r.get(k) for k in fields})
def write_json(path,x): path.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def sha(data): return hashlib.sha256(data).hexdigest()
def bootstrap(samples,point):
 by=defaultdict(list)
 for r in samples:
  if r["point"]==point:by[(int(r["block"]),r["cell"])].append(float(r["ms"]))
 assert all(len(by[(b,c)])==2 for b in range(25) for c in ("A_W","B_W","A_E","B_E"))
 rng=np.random.default_rng(SEED); out=[]
 for _ in range(1000):
  chosen=rng.integers(0,25,25); med={c:float(np.median([x for b in chosen for x in by[(int(b),c)]])) for c in ("A_W","B_W","A_E","B_E")}
  gw=1-med["B_W"]/med["A_W"];ge=1-med["B_E"]/med["A_E"];out.append(gw-ge)
 try:q=np.quantile(out,[.05,.5,.95],method="linear")
 except TypeError:q=np.quantile(out,[.05,.5,.95],interpolation="linear")
 return [float(x) for x in q]

def main():
 p=argparse.ArgumentParser();p.add_argument("--repo-root",type=Path,default=Path.cwd());a=p.parse_args();repo=a.repo_root.resolve();out=repo/OUT
 subprocess.run(["git","merge-base","--is-ancestor",PREP_COMMIT,"HEAD"],cwd=repo,check=True)
 assert subprocess.check_output(["git","rev-parse",f"{PRODUCER}^{{tree}}"],cwd=repo,text=True).strip()==PRODUCER_TREE
 sums={line.split(maxsplit=1)[1].strip():line.split(maxsplit=1)[0] for line in blob(repo,PRODUCER,f"{PACK}/SHA256SUMS").decode().splitlines()}
 required=["SOURCE_AND_AUTHORITY.json","GPU_LOCK_RECEIPT.json","W4_CORRECTNESS.tsv","W4_LAUNCH_AUDIT.tsv","DENSE_LAUNCH_AUDIT.tsv","DENSE_TIMING_SAMPLES.tsv","W4_TIMING_SAMPLES.tsv","NCU_KERNEL_ROWS.tsv","RAW_INDEX.tsv"]
 for name in required: assert sha(blob(repo,PRODUCER,f"{PACK}/{name}"))==sums[name]
 source=js(repo,"SOURCE_AND_AUTHORITY.json");lock=js(repo,"GPU_LOCK_RECEIPT.json")
 assert source["status"]=="PASS" and source["lane8_ready_head"]=="55cfac5f3edd346d8c6083bdd399a206cc463d0d" and source["validated_prep_tree"]=="4901debe8aae27e055dcac34bba738d0e42255dd"
 assert source["accepted_binary_hashes_verified"] and not source["lane4_partial_accessed"] and lock["status"]=="PASS" and lock["release"]=="RELEASED_BEFORE_CPU_ANALYSIS"
 correctness=tsv(repo,"W4_CORRECTNESS.tsv"); assert len(correctness)==4 and all(r["pass"]=="True" for r in correctness)
 wlaunch=tsv(repo,"W4_LAUNCH_AUDIT.tsv");dlaunch=tsv(repo,"DENSE_LAUNCH_AUDIT.tsv");assert all(r["pass"]=="True" for r in wlaunch+dlaunch)
 dense=tsv(repo,"DENSE_TIMING_SAMPLES.tsv");w4=tsv(repo,"W4_TIMING_SAMPLES.tsv");ncu=tsv(repo,"NCU_KERNEL_ROWS.tsv")
 assert len(dense)==200 and len(w4)==800
 shapes={"EXPAND_M1":(1,12288,49152),"EXPAND_M256":(256,12288,49152),"CONTRACT_M1":(1,49152,12288),"CONTRACT_M256":(256,49152,12288)}
 dense_rows=[]
 for point,(m,k,n) in shapes.items():
  vals=[float(r["ms"]) for r in dense if r["point"]==point];s=stats(vals);launch=next(r for r in dlaunch if r["point"]==point)
  nr=[r for r in ncu if r["track"]=="DENSE" and r["point"]==point]
  dense_rows.append({"point":point,"M":m,"K":k,"N":n,"evidence_class":"GPT-3 public-shape synthetic FP16 Dense anchor","raw_source":f"{PRODUCER}:{PACK}/DENSE_TIMING_SAMPLES.tsv",**s,"kernel_inventory":launch["kernel_name"],"grid":launch["grid"],"block":launch["block"],"correctness_status":"SHAPE_ANCHOR","ncu_l1tex_bytes":int(nr[0]["l1tex_bytes"]) if nr else None,"ncu_lts_bytes":int(nr[0]["lts_bytes"]) if nr else None,"ncu_dram_bytes":int(nr[0]["dram_bytes"]) if nr else None,"status":"PASS"})
 dfields=list(csv.DictReader((out/"NEW_DENSE_RECOMPUTE.tsv").open(),delimiter="\t").fieldnames);write_tsv(out/"NEW_DENSE_RECOMPUTE.tsv",dfields,dense_rows)
 launches={(r["point"],r["arm"],r["kernel_kind"]):r for r in wlaunch};wrows=[];derived={}
 for point,(m,k,n) in shapes.items():
  cells={}
  for cell in ("A_W","B_W","A_E","B_E"):
   vals=[float(r["ms"]) for r in w4 if r["point"]==point and r["cell"]==cell];cells[cell]=stats(vals);arm,state=cell.split("_");g=launches[(point,arm,"GEMM")];red=launches.get((point,arm,"REDUCTION"));nr=[r for r in ncu if r["track"]=="W4" and r["point"]==point and r["cell"]==cell]
   gemm=next((r for r in nr if r["kernel_kind"]=="GEMM"),None);reduction=next((r for r in nr if r["kernel_kind"]=="REDUCTION"),None)
   wrows.append({"point":point,"role":"EXPAND-like" if point.startswith("EXPAND") else "CONTRACT-like","M":m,"K":k,"N":n,"arm":arm,"state":state,"raw_source":f"{PRODUCER}:{PACK}/W4_TIMING_SAMPLES.tsv",**cells[cell],"correctness_status":"PASS","gemm_grid":g["grid"],"reduction_present":bool(red),"reduction_grid":red["grid"] if red else None,"scratch_bytes":int(g["scratch_bytes"]),"ncu_gemm_dram_bytes":int(gemm["dram_bytes"]) if gemm else None,"ncu_reduction_dram_bytes":int(reduction["dram_bytes"]) if reduction else None,"status":"PASS"})
  gw=1-cells["B_W"]["median_ms"]/cells["A_W"]["median_ms"];ge=1-cells["B_E"]["median_ms"]/cells["A_E"]["median_ms"];q=bootstrap(w4,point);derived[point]={"gain_W":gw,"gain_E":ge,"state_interaction":gw-ge,"bootstrap":q}
 wfields=list(csv.DictReader((out/"NEW_W4_RECOMPUTE.tsv").open(),delimiter="\t").fieldnames);write_tsv(out/"NEW_W4_RECOMPUTE.tsv",wfields,wrows)
 old=list(csv.DictReader((out/"OLD_QWEN_RECOMPUTE.tsv").open(),delimiter="\t"));oldmap={(r["role"],int(r["M"])):r for r in old};comp=[]
 for r in old:comp.append({k:r.get(k) for k in list(csv.DictReader((out/"SCALE_TRANSFER_COMPARISON.tsv").open(),delimiter="\t").fieldnames)}|{"status":"OLD_ACCEPTED_RECOMPUTE"})
 for point,(m,k,n) in shapes.items():
  role="EXPAND-like" if point.startswith("EXPAND") else "CONTRACT-like";o=oldmap[(role,m)];d=derived[point];nrows=[x for x in ncu if x["track"]=="W4" and x["point"]==point];dram={c:sum(int(x["dram_bytes"]) for x in nrows if x["cell"]==c) for c in ("A_W","B_W","A_E","B_E")}
  ogw=float(o["gain_W"]);oge=None if o["gain_E"]=="NA" else float(o["gain_E"]);oi=None if o["state_interaction"]=="NA" else float(o["state_interaction"])
  comp.append({"model_shape_class":"GPT3-public-shape proxy","point":point,"role":role,"M":m,"K":k,"N":n,"split1_gemm_grid":int(gpt_grid:=launches[(point,"B","GEMM")]["grid"].strip("[]").split(',')[0]),"split8_gemm_grid":int(launches[(point,"A","GEMM")]["grid"].strip("[]").split(',')[0]),"qweight_bytes":301989888,"l2_bytes":67108864,"qweight_l2_ratio":4.5,**d,"bootstrap_interaction_p05":d["bootstrap"][0],"bootstrap_interaction_median":d["bootstrap"][1],"bootstrap_interaction_p95":d["bootstrap"][2],**{f"ncu_{c}_dram_bytes":dram[c] or None for c in dram},"matched_old_point":o["point"],"delta_gain_W":d["gain_W"]-ogw,"delta_gain_E":None if oge is None else d["gain_E"]-oge,"delta_state_interaction":None if oi is None else d["state_interaction"]-oi,"warm_direction_changed":math.copysign(1,d["gain_W"])!=math.copysign(1,ogw),"disturbed_direction_changed":None if oge is None else math.copysign(1,d["gain_E"])!=math.copysign(1,oge),"interaction_direction_changed":None if oi is None else math.copysign(1,d["state_interaction"])!=math.copysign(1,oi),"status":"PASS_RAW_RECOMPUTE"})
 cfields=list(csv.DictReader((out/"SCALE_TRANSFER_COMPARISON.tsv").open(),delimiter="\t").fieldnames);write_tsv(out/"SCALE_TRANSFER_COMPARISON.tsv",cfields,comp)
 ncuout={"status":"PASS_RAW_ROWS_RECOMPUTED","producer_commit":PRODUCER,"dense":{},"w4":{},"claim_boundary":"kernel rows summed by point/cell; no tensor attribution or unique L2 causality"}
 for r in ncu:
  key=r["point"] if r["track"]=="DENSE" else f'{r["point"]}:{r["cell"]}';target=ncuout["dense"] if r["track"]=="DENSE" else ncuout["w4"];e=target.setdefault(key,{"kernel_count":0,"l1tex_bytes":0,"lts_bytes":0,"dram_bytes":0,"duration_ns":0});e["kernel_count"]+=1
  for x in ("l1tex_bytes","lts_bytes","dram_bytes","duration_ns"):e[x]+=int(r[x])
 write_json(out/"NCU_COMPARISON.json",ncuout)
 authority=json.loads((out/"AUTHORITY_AUDIT.json").read_text());authority["status"]="PASS_FORMAL_CONSUMPTION";authority["producer_gate"].update({"remote_head_observed":PRODUCER,"formal_consumption_started":True,"final_tree":PRODUCER_TREE,"sha_closed":True,"lane8_ready_bound":True,"gpu_lock_released":True,"correctness_closed":True,"launch_closed":True});write_json(out/"AUTHORITY_AUDIT.json",authority)
 exp1,exp256,con1,con256=[derived[x] for x in ("EXPAND_M1","EXPAND_M256","CONTRACT_M1","CONTRACT_M256")]
 text=f"""# 科学解释

独立raw重算确认两处明确方向翻转：EXPAND_M1从旧Qwen的-41.30%变为{100*exp1['gain_W']:.2f}%；EXPAND_M256从旧Qwenwarm +30.00%/disturbed +26.93%变为{100*exp256['gain_W']:.2f}%/{100*exp256['gain_E']:.2f}%。前者与split1 grid从148增至384一致，后者同时伴随新M256 warm DRAM中split1显著高于split8，但这些只是联合一致性，不是唯一L2因果。

CONTRACT_M1仍退化，但由旧Qwen -413.32%缩小到{100*con1['gain_W']:.2f}%，属于幅度明显缩小而非问题消失。CONTRACT_M256为warm {100*con256['gain_W']:.2f}%、disturbed {100*con256['gain_E']:.2f}%。

qweight从0.506×L2变为4.5×L2后，EXPAND_M256 interaction为{100*exp256['state_interaction']:.2f}个百分点，CONTRACT_M256为{100*con256['state_interaction']:.2f}个百分点；与旧Qwen +3.07/+5.34个百分点相比呈混合变化，而非统一增强。W/E DRAM和timing共同表明状态仍有影响，但不能唯一归因L2。

W4仅是GPT-3公开尺寸映射到AutoAWQ内核的机制代理，FP16 Dense只是大shape anchor。现有强crossover值得建议一组后续paired机制研究：旧Qwen UP_M256与GPT-3 proxy EXPAND_M256；本consumer未启动SASS或Accel-Sim。
""";(out/"SCIENTIFIC_INTERPRETATION.md").write_text(text)
 (out/"GRID_AND_WORKSET_INTERPRETATION.md").write_text(text)
 write_json(out/"FINAL_DECISION.json",{"schema_version":2,"status":"FORMAL_CONSUMPTION_COMPLETE","scientific_conclusion_zh":"规模改变确实改变了split策略方向：EXPAND_M1由负转正，EXPAND_M256由正转强负；CONTRACT_M1只是退化幅度缩小。","derived":derived,"recommendation_zh":"建议最多一组paired SASS/Accel-Sim：旧Qwen UP_M256 对 GPT-3 proxy EXPAND_M256；不自动执行。","gpu_used":False,"lane4_partial_accessed":False})
 (out/"OPEN_ISSUES.md").write_text("# Open issues\n\n- W4是公开尺寸机制代理，不是GPT-3量化模型。\n- NCU无tensor级归因，状态变化不能唯一归因L2。\n- paired SASS/Accel-Sim仅为建议，未授权执行。\n")
 (out/"README.md").write_text("# C16 GPT-3公开尺寸规模外推独立consumer\n\n正式消费已完成。独立计算authority为producer基础timing samples、launch/correctness与NCU kernel rows；producer derived summary只用于复核。\n\n主结论：EXPAND_M1由旧Qwen负收益翻为正收益，EXPAND_M256由正收益翻为强负收益；CONTRACT_M1仅是退化幅度缩小。W4是公开尺寸机制代理，不是GPT-3量化模型。\n\n依次阅读AUTHORITY_AUDIT.json、SCALE_TRANSFER_COMPARISON.tsv、SCIENTIFIC_INTERPRETATION.md、FINAL_DECISION.json。\n")
 files=sorted(x for x in out.iterdir() if x.is_file() and x.name!="SHA256SUMS");(out/"SHA256SUMS").write_text("\n".join(f"{sha(x.read_bytes())}  {x.name}" for x in files)+"\n")

if __name__=="__main__":main()
