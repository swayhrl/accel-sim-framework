"""CPU-only independent reduction of preserved V5 execution evidence."""
import json,hashlib,math,csv,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/"docs/ai_workload_research/runs/QWEN_BF16_BATCH_PERFORMANCE_NUMERIC_STUDY_109_V8"
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def main():
    raw=json.load(open(OUT/"raw/PROBE.json"));private=json.load(open(OUT/".private/PROBE_private_outputs.json"));resource=json.load(open(OUT/"RESOURCE_RECEIPT.json"));ref=json.load(open(OUT/".private/reference.json"))["formal_rows"][0]
    records=[];historical=[]
    for item in private["samples"]:
        pub=next(x for x in raw["samples"] if x["point"]==item["point"] and x["role"]==item["role"] and x["round"]==item["round"])
        for value in item["outputs"]:
            ids=value["tokens"];probs=[value["logprobs"][i][str(token)] for i,token in enumerate(ids)]
            p=next(v for v in pub["outputs"] if v["source"]==value["source"])
            assert p["token_sha256"]==digest(ids) and p["logprob_sha256"]==digest(value["logprobs"])
            assert all(math.isfinite(x) for step in value["logprobs"] for x in step.values())
            record=dict(point=item["point"],source=value["source"],role=item["role"],round=item["round"],token_sha256=digest(ids),length=len(ids),sampled=probs)
            records.append(record)
            if value["source"]=="TRAIN_A_DISCOVERY_00" and len(ids)==32:
                errors=[abs(a-b) for a,b in zip(probs,ref["sampled_logprobs"])]
                passed=ids==ref["tokens"] and all(abs(a-b)<=0.05+0.01*abs(b) for a,b in zip(probs,ref["sampled_logprobs"]))
                assert passed
                historical.append(dict(point=item["point"],token_exact=True,within_frozen_tolerance=True,max_abs_error=max(errors)))
    b1=next(v for v in records if v["point"]=="P1");b2=next(v for v in records if v["point"]=="P3")
    errors=[dict(step=i,reference=a,actual=b,abs_error=abs(a-b),allowed=0.05+0.01*abs(a),excess=abs(a-b)-(0.05+0.01*abs(a)),pass_gate=abs(a-b)<=0.05+0.01*abs(a)) for i,(a,b) in enumerate(zip(b1["sampled"],b2["sampled"]))]
    assert b1["token_sha256"]==b2["token_sha256"] and any(not e["pass_gate"] for e in errors)
    numeric=dict(status="CONFIRMED_FROZEN_NUMERIC_STOP",failure_point="P3",source="TRAIN_A_DISCOVERY_00",reference_point="P1",token_exact=True,all_preserved_logprobs_finite=True,atol=0.05,rtol=0.01,tolerance_changed=False,failed_comparisons=errors,B1_A00_32_historical=historical,private_completion_records_verified=len(records),capture_limitation="P3returned2responses;workerfailedfirstA00gatebeforepersistingsecondA01response. It is missing,not reconstructed or rerun.",engine_runtime=raw.get("runtime"),graph_observation=[dict(point=s["point"],replays=len(s.get("graph_replays",[])),descriptors=sorted({str(v) for v in s.get("graph_replays",[])}),compiled_model_observed=bool(s.get("active_compiled_Qwen2Model")),snapshot_complete="status" in s) for s in raw["samples"]])
    (OUT/"NUMERIC_AND_IDENTITY.json").write_text(json.dumps(numeric,indent=2)+"\n")
    fields=["point","role","round","batch_size","output_tokens_each","request_gpu_elapsed_ms","host_generate_call_ms","host_synchronized_request_ms","status","output_hashes","graph_descriptors"]
    def table(path,samples):
        with path.open("w",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=fields,delimiter="\t",lineterminator="\n");writer.writeheader()
            for s in samples:
                row={k:s.get(k,"") for k in fields};row.update(status=s.get("status","NUMERIC_GATE_FAILED_BEFORE_FINAL_SNAPSHOT"),output_hashes=json.dumps(s["outputs"],sort_keys=True,separators=(",",":")),graph_descriptors=json.dumps(s.get("graph_replays",[]),separators=(",",":")))
                writer.writerow(row)
    formals=[s for s in raw["samples"] if s["role"]=="FORMAL"];warms=[s for s in raw["samples"] if s["role"]=="WARMUP"]
    table(OUT/"FORMAL_SAMPLES.tsv",formals);table(OUT/"WARMUP_SAMPLES.tsv",warms);assert not formals
    analysis=dict(status="NUMERIC_OR_RUNTIME_NO_GO",scientific_performance_conclusion="INCONCLUSIVE",reason="FrozenB1/B2sampledlogprobthresholdfailedatP3warmup;noformaladmission",formal_samples=0,warmup_requests=len(warms),completed_warmup_requests=sum(s.get("status")=="PASS" for s in warms),runtime_contexts=1,point_statistics={p:dict(n=0,median_ms=None,MAD_ms=None) for p in ["P1","P2","P3","P4","P5","P6"]},delta_A00_ms=None,delta_A01_ms=None,delta_B2_ms=None,R=None,H1="UNTESTED;noqualifiedsixpointtiming",H2="UNTESTED;batch/compute/schedulingalternativesnotseparated",H3="Numericpairqualificationfailureobserved;notassignedtoaspecifickernel,causeorqualityfailure",resource_admission="VERIFIED_GATED_RESIDENT_CONTEXT_ACCEPTED",measurement_condition="VERIFIED_GATED_RESIDENT_CO_RESIDENT_NATIVE_OBSERVATION;initializationandwarmuponly",telemetry_gap=resource.get("performance_comparability_gap"),batch_weight_reuse_novelty="Alreadystrongsoftwarecapability;nogeneralhardwareclaim",hardware_candidate=None,warmup_times_used_for_performance_comparison=False,additional_GPU_runs=0)
    (OUT/"ANALYSIS.json").write_text(json.dumps(analysis,indent=2)+"\n")
    index=dict(path=str(OUT/".private/PROBE_private_outputs.json"),sha256=hashlib.sha256((OUT/".private/PROBE_private_outputs.json").read_bytes()).hexdigest(),bytes=(OUT/".private/PROBE_private_outputs.json").stat().st_size,redistributed=False,capture_gap=numeric["capture_limitation"])
    (OUT/"PRIVATE_RAW_INDEX.json").write_text(json.dumps(index,indent=2)+"\n")
    print(json.dumps(dict(primary_status=analysis["status"],warmup_requests=len(warms),formal_samples=0,failure=errors,historical=historical)))
if __name__=="__main__":main()
