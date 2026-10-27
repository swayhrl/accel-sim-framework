"""Pure parameter composition; no simulator, controller, registry or model imports."""
import argparse, hashlib, json
from pathlib import Path

def need(ok, message):
    if not ok: raise ValueError(message)

def merge_value(base, current, requested, name):
    if requested == base: return current
    if current == base or current == requested: return requested
    if name in ("-gpgpu_cache:dl1", "-gpgpu_cache:dl2"):
        b, c, r = [v.split(",") for v in (base,current,requested)]
        need(len(b)==len(c)==len(r), "incompatible cache grammar")
        out=[]
        for bi,ci,ri in zip(b,c,r):
            bb,cc,rr=[v.split(":") for v in (bi,ci,ri)]
            need(len(bb)==len(cc)==len(rr), "incompatible cache tuple grammar")
            out.append(":".join(merge_value(x,y,z,"tuplefield") for x,y,z in zip(bb,cc,rr)))
        return ",".join(out)
    raise ValueError("conflicting interventions on "+name)

def compose(catalog, candidate_ids):
    byid={r["candidate_id"]:r for r in catalog["candidates"]}
    need(len(byid)==len(catalog["candidates"]),"duplicate candidate ID")
    need(candidate_ids and len(candidate_ids)==len(set(candidate_ids)),"empty/duplicate combination")
    base=catalog["reference_templates"]["S"]["effective_options"]
    options=dict(base)
    for name in candidate_ids:
        candidate=byid[name]
        need(not candidate.get("mode_specific_option_delta"),"mode-specific P stratum is not a common-hardware composition")
        for key,value in candidate["exact_effective_delta_common_to_S_and_F"].items():
            options[key]=merge_value(base[key],options[key],value,key)
    delta={k:v for k,v in options.items() if v!=base[k]}
    dl2=options["-gpgpu_cache:dl2"].split(",");sets=int(dl2[0].split(":")[1]);ways=int(dl2[0].split(":")[3])
    need(sets in (32,64) and ways in (8,16) and sets*ways<=1024,"unqualified geometry")
    need(dl2[2]=="A:128:1","full F line-MSHR invariant")
    need(options["-gpgpu_ep_l2_descriptor_pool_size"]=="512" and options["-gpgpu_ep_l2_wad_entries"]=="128","full F metadata invariant")
    need(options["-gpgpu_ep_l2_bank_ops"]=="1" and options["-gpgpu_ep_l2_wbuf_entries"]=="16","full F payload invariant")
    sd=int(options["-gpgpu_frfcfs_dram_sched_queue_size"]);ret=int(options["-gpgpu_dram_return_queue_size"])
    need(sd>0 and ret>0 and options["-dram_seperate_write_queue_enable"]=="0","finite common credit contract")
    return {"component_candidate_ids":candidate_ids,"exact_common_effective_delta":delta,
            "old_new_delta":{k:{"old":base[k],"new":v} for k,v in delta.items()},
            "resource_proxies":{"logical_tags_per_slice":sets*ways,"physical_payload_lines_per_slice":1168,
                "L2_MissQ_entries_per_slice":int(dl2[3].split(":")[0]),"lower_FIFO_entries_per_slice":int(options["-gpgpu_dram_partition_queues"].split(":")[1]),
                "FRFCFS_entries_per_channel":sd,"return_entries_per_channel":ret,"shared_general_credits_per_channel":sd+ret-1,
                "private_general_credits_per_channel":2,"WB_progress_credits_per_channel":int(options["-gpgpu_l2_wb_progress_credit"])},
            "status":"CONFIG_COMPOSITION_ONLY_NOT_CPU_NATIVE_OR_APPLICATION_QUALIFIED","source_mutations":0,"model_starts":0}

def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument("--catalog",required=True);a.add_argument("--catalog-sha256",required=True);a.add_argument("--candidate",action="append",required=True);a.add_argument("--output",required=True);args=a.parse_args()
    data=Path(args.catalog).read_bytes();need(hashlib.sha256(data).hexdigest()==args.catalog_sha256,"catalog SHA drift")
    out=compose(json.loads(data),args.candidate);p=Path(args.output)
    need(not p.exists() and not p.is_symlink(),"output must be fresh")
    with p.open("x") as f:json.dump(out,f,sort_keys=True,indent=2);f.write("\n")

if __name__=="__main__":main()
