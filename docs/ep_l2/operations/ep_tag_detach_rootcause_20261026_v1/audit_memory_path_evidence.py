#!/usr/bin/env python3
"""Read only accepted memory-path evidence; never imports a simulator or launches science."""
import argparse, hashlib, json, math, re
from pathlib import Path
def sha(p):
    if p.stat().st_size > 32*1024*1024: raise ValueError("input above 32MiB cap")
    return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):
    if p.stat().st_size > 16*1024*1024: raise ValueError("JSON above 16MiB cap")
    return json.loads(p.read_text())
def need(v, message):
    if not v: raise ValueError(message)
def convert(v):
    if re.fullmatch(r"[0-9]+",v): return int(v)
    if re.fullmatch(r"-?[0-9]+\.[0-9]+",v): return float(v)
    return v
def kv(line):
    return {k:convert(v) for k,v in (x.split("=",1) for x in line.strip().split("|")[1:] if "=" in x)}
def raw_records(p):
    b0, dram, l1, standard, memcpy, warp = {}, {}, {}, {}, [], {}
    keys = {"gpu_tot_sim_cycle","gpu_tot_sim_insn","gpu_tot_occupancy","gpu_stall_dramfull","gpu_stall_icnt2sh",
            "gpgpu_n_mem_read_global","gpgpu_n_mem_write_global","gpgpu_n_load_insn","gpgpu_n_store_insn",
            "gpgpu_n_tot_w_icount","averagemflatency","maxmflatency","avg_icnt2mem_latency","avg_mrq_latency",
            "avg_icnt2sh_latency","max_icnt2mem_latency","maxmrqlatency","max_icnt2sh_latency",
            "icnt_total_pkts_mem_to_simt","icnt_total_pkts_simt_to_mem","Req_Network_injected_packets_num",
            "Req_Network_cycles","Req_Network_injected_packets_per_cycle","Req_Network_conflicts_per_cycle",
            "Req_Network_in_buffer_full_per_cycle","Req_Network_out_buffer_full_per_cycle",
            "Req_Network_in_buffer_avg_util","Req_Network_out_buffer_avg_util",
            "Rep_Network_injected_packets_num","Rep_Network_cycles","Rep_Network_in_buffer_full_per_cycle",
            "Rep_Network_out_buffer_full_per_cycle","L2_total_cache_accesses","L2_total_cache_misses"}
    with p.open() as f:
        for lineno,line in enumerate(f,1):
            if line.startswith(("EPL2B0V1|scope=application","EPL2DRAMV1|scope=application","EPL2L1V1|scope=application")):
                d=kv(line); d["_raw_line"]=lineno
                if line.startswith("EPL2B0"): b0[str(d["slice"])]=d
                elif line.startswith("EPL2DRAM"): dram[str(d["channel"])]=d
                else: l1=d
            match=re.match(r"\s*([A-Za-z0-9_]+)\s*=\s*([^\s]+)",line)
            if match and match[1] in keys: standard[match[1]]={"value":convert(match[2]),"raw_line":lineno}
            if line.startswith("Stall:"):
                warp={k:int(v) for k,v in re.findall(r"([A-Za-z0-9_]+):([0-9]+)",line)}
                warp["_raw_line"]=lineno
            if line.startswith("launching memcpy command"): memcpy.append({"raw_line":lineno,"text":line.strip()})
    return {"b0_slices":b0,"dram_channels":dram,"l1":l1,"standard":standard,"warp_distribution":warp,"prefill_commands":memcpy}
def format_output(output):
    """Keep machine evidence compact while retaining one line per slice/channel."""
    items=[]
    for key,value in output.items():
        if key=="vector_per_slice":
            body="[\n"+",\n".join("    "+json.dumps(v,separators=(",",":")) for v in value)+"\n  ]"
        elif key=="vector_dram_channels":
            body="{\n"+",\n".join("    "+json.dumps(k)+":"+json.dumps(v,separators=(",",":")) for k,v in value.items())+"\n  }"
        else: body=json.dumps(value,separators=(",",":"))
        items.append("  "+json.dumps(key)+":"+body)
    return "{\n"+",\n".join(items)+"\n}"
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--vector-result",type=Path,required=True)
    ap.add_argument("--q2-result",type=Path)
    a=ap.parse_args(); p=a.vector_result
    point=load(p/"CURRENT_ACCEPTED_DIAGNOSTIC_POINT.json")
    need(point["source_identity"]["core_source_commit"]=="1093d2629e3d6a9130ba25b9dd119b6f3e16c092","wrong Core")
    need(point["source_identity"]["binary_sha256"]=="e511cce7d8bcd5a3ebbe6255f42ebe153547484a69c6857ab55f7a8835a2dc33","wrong binary")
    bindings={"raw.log":"raw_sha256","terminal_summary.json":"model_summary_sha256","R5_TAGPRESSURE_TERMINAL.json":"r5_summary_sha256","R4_212_TERMINAL.json":"old212_summary_sha256"}
    hashes={name:sha(p/name) for name in bindings}
    for name,key in bindings.items(): need(hashes[name]==point[key],"accepted SHA mismatch "+name)
    m=load(p/"terminal_summary.json"); r5=load(p/"R5_TAGPRESSURE_TERMINAL.json")
    r4=load(p/"R4_212_TERMINAL.json")["global_counters"]
    raw=raw_records(p/"raw.log"); cycles=point["cycles"]
    need(set(raw["b0_slices"])==set(map(str,range(64))),"missing B0 slice")
    need(set(raw["dram_channels"])==set(map(str,range(32))),"missing DRAM channel")
    need(all(x["samples"]==cycles and x["completion_cycle"]==cycles for x in raw["b0_slices"].values()),"not final B0 snapshot")
    per_slice=[]
    selected_keys=["samples","descriptor_avg","descriptor_max","line_mshr_avg","line_mshr_max","missq_avg","missq_max","lowerq_avg","lowerq_max",
                   "c7d_reserved_avg","c7d_reserved_max","c7d_reserved_set_max","c7d_resident_valid_avg","c7d_resident_dirty_avg",
                   "c7d_missq_full_block","c7d_tag_set_all_reserved_block","c7d_line_mshr_full_block","c7d_descriptor_pool_full_block",
                   "c7e_dram_scheduler_causal_block","c7d_dram_returnq_block","bank_requests","bank_grants","bank_wait_cycles"]
    for sid in range(64):
        key=str(sid); b=raw["b0_slices"][key]; h=r5["slice_records"][key]["histograms"]
        heads=h["heads_raw_reserved"]; eligible=h["heads_raw_reserved_eligible"]
        hist=[sum(n for rr,res,n in heads if res==j) for j in range(17)]
        nhist=[sum(n for rr,res,n in heads if rr in (2,3) and res==j) for j in range(17)]
        need(sum(hist)==r5["slice_records"][key]["counters"]["covered"],"slice coverage mismatch")
        need(sum(n for rr,res,c,n in h["ways_raw_reserved_class"])==16*sum(hist),"way closure")
        ro=m["mechanism_metrics"]["full_mechanism_records"]["readonly"][key]
        peak=b["c7d_reserved_set_max"]; total=b["c7d_reserved_max"]
        need(0<=peak<=16 and total<=64*peak,"invalid occupancy bounds")
        per_slice.append({"slice":sid,"set_id":"NOT_RECORDED","b0_raw_line":b["_raw_line"],
            "b0_tick_samples":{k:b[k] for k in selected_keys},
            "occupied_sets_lower_bound_at_total_reserved_peak":math.ceil(total/peak) if peak else 0,
            "r5_covered_target_set_hist_reserved_0_to_16":hist,"r5_newtag_target_set_hist_reserved_0_to_16":nhist,
            "r5_newtag_and_eligible_head_cycles":sum(n for rr,res,e,n in eligible if rr in (2,3) and e>0),
            "ro_resource":ro["resource"],"ro_lower_concurrency":ro["lower_concurrency"]})
    dr=list(raw["dram_channels"].values())
    num=sum(x["bandwidth_util_numerator_bytes"] for x in dr)
    den=sum(x["bandwidth_util_denominator_bytes"] for x in dr)
    clocks={x["dram_cycles"] for x in dr}; need(len(clocks)==1,"DRAM windows differ")
    totals={"dram_bytes":num,"dram_capacity_bytes":den,"dram_byte_utilization":num/den,
        "dram_scheduler_full_channel_cycles":sum(x["scheduler_full_cycles"] for x in dr),
        "dram_scheduler_full_channel_cycle_fraction":sum(x["scheduler_full_cycles"] for x in dr)/sum(x["dram_cycles"] for x in dr),
        "dram_read_packets":sum(x["successful_read_issues"] for x in dr),"dram_write_packets":sum(x["successful_write_issues"] for x in dr),
        "dram_read_bytes":sum(x["successful_read_bytes"] for x in dr),"dram_write_bytes":sum(x["successful_write_bytes"] for x in dr),
        "dram_returnq_full_channel_cycles":sum(x["returnq_full_cycles"] for x in dr)}
    ro=m["mechanism_metrics"]["full_mechanism_records"]["readonly"]
    totals["ro_transactions"]=sum(x["summary"]["transactions"] for x in ro.values())
    totals["ro_merges"]=sum(x["summary"]["merges"] for x in ro.values())
    totals["ro_requests"]=sum(x["summary"]["accepted_ro"] for x in ro.values())
    totals["ro_requests_per_transaction"]=totals["ro_requests"]/totals["ro_transactions"]
    totals["ro_merge_fraction"]=totals["ro_merges"]/totals["ro_requests"]
    sums=["c7d_missq_full_block","c7e_dram_scheduler_causal_block","c7d_tag_set_all_reserved_block","c7d_line_mshr_full_block",
          "c7d_descriptor_pool_full_block","c7d_dram_returnq_block","bank_requests","bank_grants","bank_wait_cycles"]
    totals["b0_slice_event_sums"]={k:sum(x[k] for x in raw["b0_slices"].values()) for k in sums}
    totals["l2_ingress_full_slice_tick_fraction"]=raw["standard"]["gpu_stall_dramfull"]["value"]/(64*cycles)
    totals["range_over_slice_highwaters"]={}
    for name,values in {
       "descriptor":[x["ro_resource"]["peak_shared_descriptors"] for x in per_slice],
       "ro_live_transaction":[x["ro_resource"]["peak_transactions"] for x in per_slice],
       "ro_issued_not_ready_unique_lines":[x["ro_lower_concurrency"]["peak_independent_lower_lines"] for x in per_slice],
       "allset_reserved":[x["b0_tick_samples"]["c7d_reserved_max"] for x in per_slice],
       "per_set_reserved":[x["b0_tick_samples"]["c7d_reserved_set_max"] for x in per_slice],
       "occupied_sets_lower_bound":[x["occupied_sets_lower_bound_at_total_reserved_peak"] for x in per_slice]
    }.items(): totals["range_over_slice_highwaters"][name]=[min(values),max(values)]
    q2=None
    if a.q2_result:
        qp=a.q2_result; qhash=sha(qp/"raw.log")
        need(qhash=="a7d18107f4640784465480b8ffeaf0a2c1d70b4d9c8a99b37ece862ac310716a","wrong Q2 raw")
        q=raw_records(qp/"raw.log")
        qdr=list(q["dram_channels"].values())
        need(len(qdr)==32,"Q2 missing DRAM channels")
        q2={"scope":"ACCEPTED_NATIVE_MIGRATION_Q2_INDEPENDENT_BACKGROUND_NOT_ORIGINAL_E013_RAW_NOT_R5_PAIR",
            "core":"d010911e3174a3764791183cd108fe4664ba8731","binary":"61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5",
            "raw_sha256":qhash,"standard":q["standard"],"warp_distribution":q["warp_distribution"],
            "dram_bytes":sum(x["bandwidth_util_numerator_bytes"] for x in qdr),
            "dram_capacity_bytes":sum(x["bandwidth_util_denominator_bytes"] for x in qdr),
            "l1":q["l1"]}
    output={"schema":"EP_L2_MEMORY_PATH_MLP_OFFLINE_AUDIT_V1","status":"PASS",
        "vector_source_identity":point["source_identity"],"vector_cycles":cycles,
        "input_sha256":{**hashes,**{f"config-{i}.config":sha(p/f"config-{i}.config") for i in range(4)}},
        "snapshot_rule":"last application-cumulative row per slice/channel; no summing repeated snapshots",
        "vector_totals":totals,"vector_standard":raw["standard"],"vector_l1":raw["l1"],"vector_warp_distribution":raw["warp_distribution"],
        "vector_prefill_commands":raw["prefill_commands"],"vector_dram_channels":raw["dram_channels"],"vector_per_slice":per_slice,
        "vector_mechanism_waits":m["mechanism_metrics"]["bottleneck"],
        "vector_production_commit":{k:v for k,v in r4.items() if k.startswith("denied_") or k in ["ft_access_attempts","commit_accepted","commit_denied","commit_raw_probe_reached","raw_tag_fail_commit","detach_success"]},
        "q2_independent_background":q2,
        "limits":["No new simulation, source mutation, trace capture, restore, migration or scientific acceptance.",
           "CFD/DWT full local raw not available in audited approved roots; earlier accepted projections retained.",
           "No individual set ID, Tag lifetime, per-set arrival event stream or per-set Little Law closure.",
           "Tick-end allset maximum differs from requester-conditioned r5 hist; skipped requester dimensions stay NA.",
           "Do not sum per-slice highwater marks into simultaneous GPU MLP or overlapping stall reasons into cycles.",
           "Bank_Level_Parallism_Col rejected as invalid; LOCAL_XBAR not real byte-link bandwidth; TLB/PTW not modeled."]}
    print(format_output(output))
if __name__=="__main__":main()
