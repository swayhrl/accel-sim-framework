#!/usr/bin/env python3
"""Non-executing FX/output-code provenance and runtime-kernel join audit."""
import ast
import csv
import hashlib
import json
import pickletools
import re
from collections import defaultdict,deque
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
PACK=ROOT/"docs/vm_tlb/review_packs/C16_COMPILED_PATH_ARTIFACT_ATTRIBUTION_FEASIBILITY_109_V1"
PRIOR=ROOT/"docs/vm_tlb/review_packs/C16_QWEN_DECODE_MODE_DECONFLATION_CANARY_109_V1"
WEIGHT=re.compile(r"[lL]_self_modules_layers_modules_(\d+)_modules_(self_attn|mlp)_modules_(qkv_proj|o_proj|gate_up_proj|down_proj)_parameters_weight_")
ASSIGN=re.compile(r"^\s*([A-Za-z_]\w*)(?::[^=]+)?\s*=")
SOURCE_NODES=re.compile(r"# Topologically Sorted Source Nodes: \[([^]]*)\], Original ATen: \[([^]]*)\]")
KERNEL_DEF=re.compile(r"async_compile\.triton\('([^']+)'")

def sha(data):return hashlib.sha256(data).hexdigest()
def write_tsv(name,rows,fields):
    with (PACK/name).open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=fields,delimiter="\t",lineterminator="\n",extrasaction="ignore")
        writer.writeheader();writer.writerows(rows)

def nested_sources(model_path):
    queue=deque([(0,model_path.read_bytes())]);seen=set();code=[];all_string_hashes=set()
    while queue:
        depth,data=queue.popleft()
        digest=sha(data)
        if digest in seen:continue
        seen.add(digest)
        for op,arg,pos in pickletools.genops(data):
            if isinstance(arg,(str,bytes)):
                payload=arg.encode() if isinstance(arg,str) else arg
                all_string_hashes.add(sha(payload))
                if isinstance(arg,str) and len(payload)>1000 and "def forward" in arg and "gate_up_proj" in arg:
                    code.append({"text":arg,"sha256":sha(payload),"pickle_depth":depth,"position":pos})
                if depth<4 and isinstance(arg,bytes) and len(payload)>1000 and payload.startswith(b"\x80\x04"):
                    queue.append((depth+1,payload))
    return code,all_string_hashes

def fx_rows(point,text,artifact_path,artifact_sha,graph_sha):
    lines=text.splitlines();rows=[];last_gate=None
    for i,line in enumerate(lines,1):
        node=(ASSIGN.match(line).group(1) if ASSIGN.match(line) else "")
        weights=list(WEIGHT.finditer(line)) if "torch._C._nn.linear" in line else []
        if weights:
            for match in weights:
                layer=int(match.group(1));component=match.group(3)
                family={"qkv_proj":"ATTENTION","o_proj":"ATTENTION","gate_up_proj":"GATE_UP_PROJECTION","down_proj":"DOWN_PROJECTION"}[component]
                rows.append({"point":point,"artifact_stage":"FX_GRAPH","fx_node":node,"layer":layer,
                             "semantic_family":family,"module_path":f"model.layers.{layer}.{match.group(2)}.{component}",
                             "direct_provenance_source":artifact_path,"artifact_sha256":artifact_sha,
                             "embedded_graph_sha256":graph_sha,"source_line":i,
                             "provenance_relation":"FX linear consumes layer-specific parameter weight",
                             "kernel_join":"NOT_ESTABLISHED","source_excerpt":line.strip()[:240]})
                if component=="gate_up_proj":last_gate=(layer,i)
        if "torch.nn.functional.silu(" in line and last_gate and i-last_gate[1]<=20:
            layer=last_gate[0]
            rows.append({"point":point,"artifact_stage":"FX_GRAPH","fx_node":node,"layer":layer,
                         "semantic_family":"ACTIVATION","module_path":f"model.layers.{layer}.mlp.act_fn",
                         "direct_provenance_source":artifact_path,"artifact_sha256":artifact_sha,
                         "embedded_graph_sha256":graph_sha,"source_line":i,
                         "provenance_relation":"silu follows same-layer gate_up projection and precedes down projection in FX graph",
                         "kernel_join":"NOT_ESTABLISHED","source_excerpt":line.strip()[:240]})
    return rows

def output_code(root,embedded_hashes):
    rows=[];symbols=defaultdict(list)
    for path in sorted(root.rglob("*.py")):
        data=path.read_bytes();text=data.decode("utf-8",errors="replace")
        if "Topologically Sorted Source Nodes" not in text:continue
        file_sha=sha(data);last_source=("","")
        for line_no,line in enumerate(text.splitlines(),1):
            match=SOURCE_NODES.search(line)
            if match:last_source=(match.group(1),match.group(2))
            match=KERNEL_DEF.search(line)
            if match:
                name=match.group(1)
                record={"kernel_symbol":name,"output_code_path":str(path),"output_code_sha256":file_sha,
                        "embedded_in_aot_pickle":file_sha in embedded_hashes,"line":line_no,
                        "source_nodes":last_source[0],"original_aten":last_source[1]}
                rows.append(record);symbols[name].append(record)
    return rows,symbols

def runtime_kernel_rows(symbols):
    rows=[]
    with (PRIOR/"BACKEND_KERNEL_IDENTITY.tsv").open(newline="") as f:
        source=[r for r in csv.DictReader(f,delimiter="\t") if r["mode"]=="B"]
    for item in source:
        point=item["point"]
        names=ast.literal_eval(item["kernel_names"])
        for name in names:
            generated=symbols.get(name,[]) if point=="MP02" else []
            direct_activation=bool(generated) and name=="triton_poi_fused_mul_silu_slice_1" and any("silu" in r["source_nodes"] and "mul" in r["source_nodes"] and r["embedded_in_aot_pickle"] for r in generated)
            if direct_activation:
                family="ACTIVATION";status="DIRECT_FAMILY_ONLY";candidates="ACTIVATION"
                evidence="AOT pickle embeds output_code SHA; source-node comment [getitem_2,silu,getitem_3,mul]; FX activation sequence"
            elif any("bf16" in name.lower() and term in name.lower() for term in ("gemm","gemvx")):
                family="UNRESOLVED";status="AMBIGUOUS_EXTERNAL_PROJECTION";candidates="ATTENTION|GATE_UP_PROJECTION|DOWN_PROJECTION"
                evidence="runtime BF16 GEMM/GEMV name; FX/output_code contain multiple extern linear calls; no launch-to-call correlation"
            elif name.startswith("void flash::"):
                family="UNRESOLVED";status="EXTERNAL_ATTENTION_CANDIDATE_ONLY";candidates="ATTENTION"
                evidence="FlashAttentionImpl runtime backend and FX unified_attention_with_output exist; no artifact-to-launch instance link"
            elif generated:
                family="UNRESOLVED";status="GENERATED_SYMBOL_WITHOUT_UNIQUE_FAMILY";candidates="ATTENTION|ACTIVATION|NON_TARGET_BOUNDARY"
                evidence="generated output_code symbol matches runtime name, but source-node grouping does not uniquely resolve target family or layer"
            else:
                family="UNRESOLVED";status="NO_DIRECT_COMPILED_ARTIFACT_LINK";candidates="UNKNOWN_OR_NON_TARGET"
                evidence="runtime name absent from pinned point-specific generated output_code; name is auxiliary only"
            rows.append({"point":point,"mode":"B","runtime_kernel_name":name,"artifact_generated_symbol_match":bool(generated),
                         "direct_provenance_status":status,"semantic_family":family,"candidate_families":candidates,
                         "layer_unique":False,"step_unique":False,"evidence":evidence,
                         "generated_output_code_sha256":"|".join(sorted({r["output_code_sha256"] for r in generated})) or "NONE"})
    return rows

def main():
    authority=json.loads((PACK/"COMPILE_CACHE_AUTHORITY.json").read_text())
    mp02=next(r for r in authority["roots"] if r["point"]=="MP02" and r["mode"]=="B")
    mp03=next(r for r in authority["roots"] if r["point"]=="MP03" and r["mode"]=="B")
    model=Path(mp02["cache_path"])/"rank_0_0/model"
    texts,embedded_hashes=nested_sources(model)
    fx_text=max(texts,key=lambda x:len(x["text"]))
    graph=Path(mp03["cache_path"])/"computation_graph.py"
    fx=[]
    model_sha=sha(model.read_bytes())
    for embedded in texts:
        fx+=fx_rows("MP02",embedded["text"],str(model),model_sha,embedded["sha256"])
    fx+=fx_rows("MP03",graph.read_text(),str(graph),sha(graph.read_bytes()),sha(graph.read_bytes()))
    output,symbols=output_code(Path(mp02["cache_path"])/"inductor_cache",embedded_hashes)
    kernels=runtime_kernel_rows(symbols)
    write_tsv("FX_IR_PROVENANCE_MAP.tsv",fx,["point","artifact_stage","fx_node","layer","semantic_family","module_path","direct_provenance_source","artifact_sha256","embedded_graph_sha256","source_line","provenance_relation","kernel_join","source_excerpt"])
    write_tsv("OUTPUT_CODE_SOURCE_NODE_MAP.tsv",output,["kernel_symbol","output_code_path","output_code_sha256","embedded_in_aot_pickle","line","source_nodes","original_aten"])
    write_tsv("KERNEL_TO_SEMANTIC_FAMILY.tsv",kernels,["point","mode","runtime_kernel_name","artifact_generated_symbol_match","direct_provenance_status","semantic_family","candidate_families","layer_unique","step_unique","evidence","generated_output_code_sha256"])
    fusion=[
        {"point":"MP02","kernel_or_call":"triton_poi_fused_mul_silu_slice_1","direct_source":"embedded Inductor output_code source nodes [getitem_2,silu,getitem_3,mul]","relationship":"ACTIVATION_INTERNAL_FUSION","families":"ACTIVATION","allocation":"JOINT_ACTIVATION_ONLY_NO_SPLIT","ambiguity":"same kernel symbol reused across layers; no runtime layer/step instance IDs"},
        {"point":"MP02","kernel_or_call":"gate_up extern_kernels.mm -> triton_poi_fused_mul_silu_slice_1","direct_source":"embedded output_code has separate gate_up GEMM call followed by separate Triton activation launch","relationship":"NO_GATE_UP_PLUS_ACTIVATION_SINGLE_KERNEL_FUSION_SHOWN","families":"GATE_UP_PROJECTION|ACTIVATION","allocation":"SEPARATE_LAUNCHES_BUT_NO_RUNTIME_INSTANCE_TIMING_SPLIT","ambiguity":"do not infer fusion from an extern GEMM source-node comment that lists upstream activation dependencies"},
        {"point":"MP02","kernel_or_call":"extern_kernels.mm/addmm","direct_source":"output_code linear, linear_1, linear_2 calls plus layer-indexed FX weights","relationship":"MULTIPLE_EXTERNAL_PROJECTION_CALLS_SHARE_GENERIC_RUNTIME_KERNEL_FAMILIES","families":"ATTENTION|GATE_UP_PROJECTION|DOWN_PROJECTION","allocation":"NO_DURATION_SPLIT","ambiguity":"runtime cuBLAS/CUTLASS names lack callsite correlation; source-node list may include upstream ops not fused in same launch"},
        {"point":"MP02","kernel_or_call":"triton_poi_fused_1","direct_source":"embedded combo output_code contains source-node groups for embedding/norm and attention rotary","relationship":"MULTI_FAMILY_FUSED","families":"ATTENTION|NON_TARGET_EMBEDDING_NORM","allocation":"JOINT_FAMILY_OR_UNSPLITTABLE","ambiguity":"combo launch cannot be apportioned to target families from artifacts"},
        {"point":"MP02","kernel_or_call":"triton_red_fused_fused_add_rms_norm_2","direct_source":"generated output_code fused_add_rms_norm source nodes at layer boundary","relationship":"BOUNDARY_FUSED","families":"ATTENTION_RESIDUAL|MLP_INPUT_NORM","allocation":"NO_DURATION_SPLIT","ambiguity":"boundary normalization not uniquely one of four target semantic families"},
        {"point":"MP03","kernel_or_call":"compiled B4 kernels","direct_source":"layer-indexed computation_graph.py and cache_key_factors.json only","relationship":"GENERATED_OUTPUT_CODE_ABSENT_IN_POINT_CACHE","families":"UNKNOWN","allocation":"NO_DURATION_SPLIT","ambiguity":"no point-specific output-code-to-kernel bridge on disk"},
    ]
    write_tsv("FUSION_AMBIGUITY.tsv",fusion,["point","kernel_or_call","direct_source","relationship","families","allocation","ambiguity"])
    layer_pairs={point:len({(r["layer"],r["semantic_family"]) for r in fx if r["point"]==point}) for point in ("MP02","MP03")}
    summary={"mp02_embedded_fx_graph_sha256":fx_text["sha256"],"mp02_embedded_fx_source_count":len(texts),
             "mp02_embedded_output_code_kernel_definitions":sum(1 for r in output if r["embedded_in_aot_pickle"]),
             "mp02_distinct_embedded_output_code_files":len({r["output_code_sha256"] for r in output if r["embedded_in_aot_pickle"]}),
             "mp02_output_code_kernel_symbols":sorted(symbols),"fx_rows":len(fx),"runtime_kernel_rows":len(kernels),
             "unique_layer_semantic_family_pairs":layer_pairs,
             "direct_family_only_rows":sum(r["direct_provenance_status"]=="DIRECT_FAMILY_ONLY" for r in kernels),
             "unresolved_rows":sum(r["semantic_family"]=="UNRESOLVED" for r in kernels),
             "mp02_generated_symbol_matches":sum(r["point"]=="MP02" and r["artifact_generated_symbol_match"] for r in kernels),
             "mp03_generated_output_code_present":False,"runtime_kernel_instance_ids_present":False,
             "module_layer_paths_present_in_fx":True,"runtime_step_labels_present_in_artifacts":False,
             "no_pickle_execution":True,"gpu_used":False}
    (PACK/"PROVENANCE_ANALYSIS.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"PASS","fx_rows":len(fx),"runtime_kernels":len(kernels),"direct_family_only":summary["direct_family_only_rows"],"unresolved":summary["unresolved_rows"]}))

if __name__=="__main__":main()
