"""CPU-only aggregation of every actual native sample, no sample selection."""
import os
os.sched_setaffinity(0,{22,23})
import json,statistics,hashlib,csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(os.environ.get("Q1_EXECUTION_OUT",ROOT/"docs/ai_workload_research/runs/AI_ARCH_Q1_COMPLETION_109_V1"))
def load(p):
    return json.loads(p.read_text()) if p.exists() else None
def dump(n,x):(OUT/n).write_text(json.dumps(x,indent=2)+"\n")
def union(intervals):
    ends=sorted((float(a),float(b)) for a,b in intervals if b>=a)
    total=0.;left=right=None
    for a,b in ends:
        if left is None:left,right=a,b
        elif a<=right:right=max(right,b)
        else:total+=right-left;left,right=a,b
    return total+(0 if left is None else right-left)
def stats(v):
    if not v:return dict(n=0,median=None,MAD=None)
    m=statistics.median(v)
    return dict(n=len(v),median=m,MAD=statistics.median(abs(x-m) for x in v),min=min(v),max=max(v),all_samples=v)
def main():
    receipt=load(OUT/"RESOURCE_RECEIPT.json")
    rows=[];groups={};identities=[];diagnostics=[];invalid=[];camera_sequences={}
    for record in receipt["jobs"]:
        job=record["job"];d=OUT/".private/JOBS"/job["id"]
        result=load(d/"RESULT.json")
        if not result:continue
        good=record.get("returncode")==0 and result.get("status")=="COMPLETE"
        pool=job.get("sample_pool","UNKNOWN")
        rawrows=result.get("rows",[])
        clock=result.get("closed_window_wall_seconds")
        if pool=="FORMAL":
            window=[x for x in rawrows if job["window_start"]<=x["step"]<job["stop_next"]]
            cameras=[x["camera_ids"] for x in window]
            signature=hashlib.sha256(json.dumps(cameras).encode()).hexdigest()
            camera_sequences.setdefault(job["phase"],{}).setdefault(signature,cameras)
            row=dict(job=job["id"],phase=job["phase"],policy=job["OMP_cap"],round=job["round"],
                valid=good,closed_window_wall_seconds=clock,camera_SHA256=signature,
                actual_steps=len(window),N_total_min=min(x["N_total"] for x in window),
                N_total_max=max(x["N_total"] for x in window),
                N_visible_mean=statistics.mean(x["N_visible"] for x in window),
                N_visible_min=min(x["N_visible"] for x in window),N_visible_max=max(x["N_visible"] for x in window),
                U_over_N_mean=statistics.mean(x["U_over_N"] for x in window) if all(x["U_over_N"] is not None for x in window) else None,
                N_updated_mean=statistics.mean(x["N_updated"] for x in window) if all(x["N_updated"] is not None for x in window) else None,
                final_semantic_fingerprint=result.get("final_semantic_fingerprint"),
                numeric_scope=result.get("numerical_equivalence_to_other_policies"))
            rows.append(row)
            if not good or clock is None or clock<=0 or len(window)!=51:
                invalid.append(dict(job=job["id"],reason="Invalid/incomplete fixed-window sample"))
            if good and clock is not None:
                groups.setdefault(job["phase"],{}).setdefault(str(job["OMP_cap"]),[]).append(clock)
        if pool=="DIAGNOSTIC_NOT_FORMAL":
            regions=load(d/"REGIONS.json") or [];events=load(d/"GPU_EVENT_SPANS.json") or [];transfers=load(d/"TRANSFERS.json") or []
            mainpid=record["pid"]
            mainregions=[x for x in regions if x["TID"]==mainpid and job["window_start"]<=x["step"]<job["stop_next"]]
            labels={}
            for x in mainregions:labels.setdefault(x["tag"],[]).append((x["begin_host_monotonic"],x["end_host_monotonic"]))
            waits=[x for x in mainregions if x["tag"].startswith(("join@","synchronize@"))]
            traffic={}
            for x in transfers:
                if not job["window_start"]<=x["step"]<job["stop_next"]:continue
                direction=x["src"].get("device","UNKNOWN").split(":")[0]+"->"+x["dst"].get("device","UNKNOWN").split(":")[0]
                group=traffic.setdefault(direction,dict(calls=0,known_logical_call_operand_bytes=0,unknown_logical_payload_calls=0,src_operand_bytes=0,dst_operand_bytes=0,original_host_call_seconds=0.,noop_calls=0))
                group["calls"]+=1
                group["noop_calls"]+=int(x.get("noop_label")!="NO_NOOP_CLAIM")
                amount=x.get("logical_payload_bytes")
                if amount is None:group["unknown_logical_payload_calls"]+=1
                else:group["known_logical_call_operand_bytes"]+=amount
                group["src_operand_bytes"]+=x.get("src_operand_payload_bytes",0)
                group["dst_operand_bytes"]+=x.get("dst_operand_payload_bytes",0)
                group["original_host_call_seconds"]+=x.get("host_call_elapsed_ns",0)/1e9
            diagnostics.append(dict(job=job["id"],phase=job.get("phase"),policy=job["OMP_cap"],valid=good,closed_window_wall_seconds=clock,
                main_host_regions_union_seconds=union([(x["begin_host_monotonic"],x["end_host_monotonic"]) for x in mainregions]),
                host_wait_join_sync_union_seconds=union([(x["begin_host_monotonic"],x["end_host_monotonic"]) for x in waits]),
                host_region_by_tag_seconds={k:union(v) for k,v in labels.items()},
                host_region_accumulated_by_tag_seconds={k:sum(b-a for a,b in v) for k,v in labels.items()},
                GPU_event_span_ms=stats([x["gpu_span_ms"] for x in events if job["window_start"]<=x["step"]<job["stop_next"]]),
                transfer_operand_summary=traffic,transfer_scope="Actual instrumented Tensor call operands only, not DMA/PCIe/DRAM counters; unknown payloads retained separately",
                transfer_row_count=len(transfers),transfer_metadata_schema=list(transfers[0]) if transfers else [],
                no_cross_clock_subtraction=True,scope="ON diagnostic only; GPU event span includes launch gaps; host join/sync wait is not exclusively GPU-resource delay"))
        if good:identities.append(dict(job=job["id"],pool=pool,restore=(load(d/"RESTORE_INITIAL.json") or {}).get("status"),
            semantic=result.get("final_semantic_fingerprint"),frontier=result.get("frontier"),
            actual_thread_intra=result.get("actual_torch_intra_threads"),OMP_cap=result.get("actual_OMP_cap"),
            affinity=result.get("train_affinity")))
    aggregated={p:{k:stats(v) for k,v in g.items()} for p,g in groups.items()}
    ratios={}
    for p,g in aggregated.items():
        if "8" in g and "16" in g and g["8"]["median"] and g["16"]["median"]:
            ratios[p]=dict(T16_over_T8_median=g["16"]["median"]/g["8"]["median"],scope="Descriptive fixed-work window, no full-200000step or strict-quality-equivalence claim")
    camera_scopes={p:sorted(set(r["camera_SHA256"] for r in rows if r["phase"]==p)) for p in ["DISCOVERY","VALIDATION"]}
    input_windows=dict(camera_sequences=camera_sequences,within_phase_same_sequence=all(len(v)<=1 for v in camera_sequences.values()),
        discovery_validation_same_scene=True,second_scene=False)
    if all(p in camera_sequences for p in ["DISCOVERY","VALIDATION"]):
        sets={p:set(i for sequence in camera_sequences[p].values() for camera in sequence for i in camera) for p in camera_sequences}
        input_windows["camera_ID_intersection"]=sorted(sets["DISCOVERY"]&sets["VALIDATION"])
    dump("NATIVE_INPUT_WINDOW_IDENTITY.json",input_windows)
    result=dict(formal_samples=len(rows),all_samples=rows,stats=aggregated,thread_ratios=ratios,
        invalid=invalid,camera_identity_by_phase=camera_scopes,
        all_same_camera_sequence_within_each_phase=all(len(v)<=1 for v in camera_scopes.values()),
        complete_expected_20_samples=(len(rows)==20 and not invalid and all(x["n"]==5 for g in aggregated.values() for x in g.values())),
        final_semantic_fingerprints_all_equal=len(set(x["final_semantic_fingerprint"] for x in rows))<=1,
        numerical_trajectory_scope="Actual fingerprints retained. No new tolerance; identical starting state/cameras does not assert final trajectory quality equivalence.",
        measurements_scope="Complete closed natural50step target work plus1closure step, restore/checkpoint outside sample",
        stats_not_physical_hardware_attribution=True)
    dump("FORMAL_ANALYSIS.json",result);dump("DIAGNOSTIC_ANALYSIS.json",dict(jobs=diagnostics));dump("NATIVE_EXECUTION_IDENTITY.json",dict(jobs=identities))
    if rows:
        with (OUT/"FORMAL_SAMPLES.tsv").open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
    print(json.dumps(dict(formal_samples=len(rows),stats=aggregated,invalid=invalid)))
if __name__=="__main__":main()
