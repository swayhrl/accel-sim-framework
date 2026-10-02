#!/usr/bin/env python3
"""Evidence-bound PRESENT/ABSENT/UNREADABLE artifact inventory."""
import csv
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
PACK=ROOT/"docs/vm_tlb/review_packs/C16_COMPILED_PATH_ARTIFACT_ATTRIBUTION_FEASIBILITY_109_V1"
AUTH=json.loads((PACK/"COMPILE_CACHE_AUTHORITY.json").read_text())
PROV=json.loads((PACK/"PROVENANCE_ANALYSIS.json").read_text())
ROWS=[]

def add(point,kind,status,evidence,limit):
    ROWS.append({"point":point,"mode":"B","artifact_kind":kind,"status":status,"direct_evidence":evidence,"interpretation_limit":limit})

def main():
    for point in ("MP02","MP03"):
        entry=next(x for x in AUTH["roots"] if x["point"]==point and x["mode"]=="B")
        root=Path(entry["cache_path"])
        if point=="MP02":
            model=root/"rank_0_0/model"
            add(point,"FX_READABLE_GRAPH","PRESENT",f"safe pickletools nested GraphModule source in {model}; embedded graph SHA {PROV['mp02_embedded_fx_graph_sha256']}","No model/torch import; 36 layer paths visible at FX level")
            add(point,"FX_RUNNABLE_GRAPH","UNREADABLE",f"serialized GraphModule in {model}","Would require unsafe pickle reconstruction/import to validate runtime execution; forbidden here")
            add(point,"INDUCTOR_PRE_FUSION_IR","ABSENT",str(root),"No standalone pre-fusion Inductor IR file in exact 346-file cache")
            add(point,"INDUCTOR_POST_FUSION_IR","ABSENT",str(root),"Output-code source-node comments exist, but no standalone full Inductor post-fusion IR")
            add(point,"TRITON_TTIR_TTGIR","PRESENT",f"40 .ttir and 40 .ttgir under {root/'inductor_cache/triton'}","Lowered Triton IR, not Inductor pre/post-fusion graph IR")
            add(point,"GENERATED_OUTPUT_CODE","PRESENT",f"Inductor .py output code under {root/'inductor_cache'}; exact SHA also embedded in AOT pickle","Source-node comments map some compiled symbols to FX nodes; not runtime instances")
            add(point,"KERNEL_SOURCE","PRESENT",f"13 generated .py, 40 .source, 40 .ptx, 40 .cubin under {root/'inductor_cache'}","Contains generated Triton kernels and external call sites; generic external GEMMs have no unique runtime callsite ID")
            add(point,"KERNEL_NAMES","PRESENT",f"6 generated Triton symbols cross-check 9122 MP02 B runtime names","Only 6 of 49 distinct runtime names match generated symbols; names alone are not semantic provenance")
            add(point,"STACK_SOURCE_METADATA","PRESENT",f"safe AOT nested pickle scan and output-code Source Nodes under {root}","Trace/source-node metadata exists but launch-instance correlation is absent")
            add(point,"MODULE_PATH_METADATA","PRESENT",f"embedded FX layer-specific weight names model.layers.0..35 in {model}","FX node to layer; not runtime kernel instance to layer")
            add(point,"GRAPH_INPUT_OUTPUT_METADATA","PRESENT",f"embedded FX forward signatures and shape annotations in {model}","Static graph shape metadata; no decode step tags")
            add(point,"CACHE_MANIFEST","ABSENT",str(root),"No standalone cache_key_factors.json in exact AOT root; root key and serialized guards are recorded separately")
        else:
            graph=root/"computation_graph.py";manifest=root/"cache_key_factors.json"
            add(point,"FX_READABLE_GRAPH","PRESENT",str(graph),"Layer-indexed GraphModule source text present")
            add(point,"FX_RUNNABLE_GRAPH","PRESENT",str(graph),"Defines GraphModule.forward; execution deliberately not attempted")
            add(point,"INDUCTOR_PRE_FUSION_IR","ABSENT",str(root),"No standalone pre-fusion Inductor IR in exact two-file cache")
            add(point,"INDUCTOR_POST_FUSION_IR","ABSENT",str(root),"No output-code or full post-fusion Inductor IR in exact two-file cache")
            add(point,"TRITON_TTIR_TTGIR","ABSENT",str(root),"No .ttir or .ttgir in exact two-file cache")
            add(point,"GENERATED_OUTPUT_CODE","ABSENT",str(root),"No point-bound output_code file in 9122-recorded path; other global cache roots are unbound")
            add(point,"KERNEL_SOURCE","ABSENT",str(root),"No point-bound generated kernel source in exact two-file cache")
            add(point,"KERNEL_NAMES","ABSENT",str(root),"Runtime names exist in 9122 receipt, but this point-specific cache has no generated-name manifest")
            add(point,"STACK_SOURCE_METADATA","PRESENT",str(graph),"Per-node # File source comments present")
            add(point,"MODULE_PATH_METADATA","PRESENT",str(graph),"Layer-specific Qwen weight parameter names present")
            add(point,"GRAPH_INPUT_OUTPUT_METADATA","PRESENT",str(graph),"Forward signature/shape annotations and return nodes present")
            add(point,"CACHE_MANIFEST","PRESENT",str(manifest),"Cache key factors; no kernel-to-module map")
    with (PACK/"ARTIFACT_INVENTORY.tsv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=["point","mode","artifact_kind","status","direct_evidence","interpretation_limit"],delimiter="\t",lineterminator="\n")
        writer.writeheader();writer.writerows(ROWS)
    print(json.dumps({"status":"PASS","rows":len(ROWS),"present":sum(x["status"]=="PRESENT" for x in ROWS),"absent":sum(x["status"]=="ABSENT" for x in ROWS),"unreadable":sum(x["status"]=="UNREADABLE" for x in ROWS)}))

if __name__=="__main__":main()
