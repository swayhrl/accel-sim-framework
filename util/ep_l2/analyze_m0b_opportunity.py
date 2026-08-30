#!/usr/bin/env python3
"""Fail-closed M0b timing-neutrality and opportunity aggregation."""
import argparse, csv, json
from pathlib import Path

CONTROLS = ("convolutionSeparable", "dwt2d", "sad")
OFF, ON = "M0A_ON_M0B_OFF_M1_STATIC", "M0A_ON_M0B_ON_M1_STATIC"

def read(path):
    with path.open(newline="") as f: return list(csv.DictReader(f))
def write(path, rows):
    fields=sorted({k for row in rows for k in row})
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
def canonical(rows): return sorted(tuple(sorted(row.items())) for row in rows)

def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument("--results",required=True,type=Path); ap.add_argument("--out",required=True,type=Path); ap.add_argument("--controls",nargs="+",choices=CONTROLS,default=CONTROLS); args=ap.parse_args(); args.out.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((args.results/"campaign_manifest.json").read_text()); timing=[]
    for name in args.controls:
        a,b=args.results/OFF/name,args.results/ON/name
        sa,sb=(json.loads((d/"run_status.json").read_text()) for d in (a,b))
        if sa["status"]!="COMPLETE_VALID" or sb["status"]!="COMPLETE_VALID": raise ValueError("invalid control: "+name)
        equal=sa["terminal_gpu_tot_sim_cycle"]==sb["terminal_gpu_tot_sim_cycle"] and sa["terminal_gpu_tot_sim_insn"]==sb["terminal_gpu_tot_sim_insn"]
        for artifact in ("target_summary.csv","target_slice.csv","target_l1.csv","target_dram.csv"):
            equal &= canonical(read(a/artifact))==canonical(read(b/artifact))
        if not equal: raise ValueError("M0b timing-neutrality mismatch: "+name)
        timing.append({"workload":name,"off_cycles":sa["terminal_gpu_tot_sim_cycle"],"on_cycles":sb["terminal_gpu_tot_sim_cycle"],"off_instructions":sa["terminal_gpu_tot_sim_insn"],"on_instructions":sb["terminal_gpu_tot_sim_insn"],"all_required_parsed_fields_equal":1,"config_delta":"only -gpgpu_ep_l2_m0b_stats: 0 -> 1","framework_sha":manifest["framework_sha"],"core_sha":manifest["core_sha"]})
    write(args.out/"TIMING_NEUTRALITY.csv",timing)
    opportunities=[]
    for d in sorted((args.results/ON).iterdir()):
        if not d.is_dir(): continue
        status=json.loads((d/"run_status.json").read_text())
        if status["status"]!="COMPLETE_VALID": raise ValueError("invalid ON cell: "+d.name)
        summary=read(d/"m0b_summary.csv")[0]
        row={"workload":d.name,"maturity":"SPECULATIVE_PENDING_GATE","ro_interpretation":"candidate_transferable_pending_state_lifetime_not_proven_avoidable_mshr_lifetime","tvd_interpretation":"premise_requires_old_handle_live_until_set_done","shared_payload_interpretation":"NO_REAL_CONSUMER_YET","framework_sha":manifest["framework_sha"],"core_sha":manifest["core_sha"],**summary}
        opportunities.append(row)
    write(args.out/"M0B_OPPORTUNITY_SUMMARY.csv",opportunities)
    (args.out/"ANALYSIS_MANIFEST.json").write_text(json.dumps({"maturity":"SPECULATIVE_PENDING_GATE","controls":args.controls,"framework_sha":manifest["framework_sha"],"core_sha":manifest["core_sha"]},indent=2,sort_keys=True)+"\n")
if __name__=="__main__":
    try: main()
    except (OSError,ValueError,KeyError) as error: raise SystemExit("M0b analyzer error: %s"%error)
