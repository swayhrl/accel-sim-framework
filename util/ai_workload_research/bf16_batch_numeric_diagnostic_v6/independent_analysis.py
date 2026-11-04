"""Post-STOP independent CPU analysis; never imports torch/NVML or launches a worker."""
import json,hashlib,csv,statistics,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/"docs/ai_workload_research/runs/QWEN_BF16_BATCH_NUMERIC_DIAGNOSTIC_109_V6"
def write(name,value):(OUT/name).write_text(json.dumps(value,indent=2)+"\n")
def main():
 v=json.loads((OUT/"V5_CPU_EVIDENCE_REVIEW.json").read_text())
 rr=json.loads((OUT/"RESOURCE_RECEIPT.json").read_text());raw=json.loads((OUT/"raw/PROBE.json").read_text())
 ds=[x["delta"] for x in v["common_logprob_deltas"]];anchor=min(ds);spacing=.125
 lattice=dict(anchor=anchor,spacing=spacing,max_residual=max(abs((d-anchor)-round((d-anchor)/spacing)*spacing) for d in ds),
              interpretation="Observed near-0.125 relative spacing, consistent with quantized score changes plus normalization offset; not proof of BF16 kernel, forward layer or sampler cause. No logits captured.")
 gaps=[dict(index=i,phase=s["phase"],monitor_gaps=s["monitor_gaps"],unknown_gpu_pids=s["unknown_gpu_pids"],unqualified_external_gpu_pids=s.get("unqualified_external_gpu_pids"),own_NVML_MiB=s["own_NVML_MiB"]) for i,s in enumerate(rr["samples"]) if s["monitor_gaps"] or s["unknown_gpu_pids"]]
 formal=[s for s in raw.get("samples",[]) if s.get("role")=="FORMAL"]
 diagnostic=[s for s in raw.get("samples",[]) if s.get("role")=="DIAGNOSTIC"]
 result=dict(execution_status=rr["status"],scientific_status="INCONCLUSIVE",reason="Own process-tree RSS NoSuchProcess during initialization; strict inherited monitor stopped and released the sole lock before any diagnostic generate.",
   GPU_lock_attempts=rr["lock_attempt_count"],GPU_lock_held_seconds=rr["GPU_lock_held_seconds"],model_constructor_attempts=raw["model_initializations"],
   model_constructor_completed_and_strong_runtime_asserted="runtime" in raw,diagnostic_requests=len(diagnostic),diagnostic_groups_completed=0,formal_samples=len(formal),
   V5_numeric_fact=dict(reference=-.9105782508850098,actual=-1.0132758617401123,abs_error=.10269761085510254,allowed=.0591057825088501,selected_token_equal=True,
      returned_top20_common_count=len(ds),delta_min=min(ds),delta_max=max(ds),delta_span=max(ds)-min(ds),uniform_shift=False,relative_spacing=lattice),
   classifications=v["classification"],numeric_reproducibility="UNTESTED_IN_V6; no completion returned; old V5 difference remains valid observed failure, no new positive or negative replication.",
   delta_A00=None,delta_A01=None,delta_B2=None,R=None,point_statistics={},
   H1="Not tested; conditional streamed weight bytes are not measured DRAM.",H2="Not separated from H1; no legal formal samples.",H3="V5 pairing checks support preserved A00 comparison; missing P3 execution snapshot remains unresolved; V6 actual strong runtime qualification not reached.",
   resource_gaps=gaps,external_interference="No unknown external compute observed; no ImageLab completed-scope change while held. Desktop per-process utilization unavailable; cannot claim exclusive or interference-free environment.",
   condition=rr.get("measurement_condition"),next_hardware_candidate=None,performance_ranking=None,
   execution_cleanup=dict(lock_released=rr["lock_released"],own_GPU_contexts_cleared=rr.get("own_GPU_contexts_cleared"),reservation=rr.get("shared_reservation_cleanup")),
   no_retry=True)
 write("ANALYSIS.json",result)
 numeric=dict(V5=v,V6=dict(status="NOT_OBSERVED_RESOURCE_STOP_BEFORE_GENERATE",all_actual_completions=0,no_fabricated_samples=True,raw_status_preserved=raw["status"],raw_status_note="Worker SIGTERM from supervisor prevents its final status update; RESOURCE_RECEIPT is authoritative execution STOP."),atol=.05,rtol=.01,tolerance_changed=False,relative_spacing=lattice)
 write("NUMERIC_AND_IDENTITY.json",numeric)
 for name,role in [("FORMAL_SAMPLES.tsv","FORMAL"),("DIAGNOSTIC_SAMPLES.tsv","DIAGNOSTIC"),("WARMUP_SAMPLES.tsv","WARMUP")]:
  with (OUT/name).open("w",newline="") as f:
   columns=["point","role","round","index","batch_size","output_tokens_each","request_gpu_elapsed_ms","host_generate_call_ms","host_synchronized_request_ms","status"]
   w=csv.DictWriter(f,fieldnames=columns,delimiter="\t",lineterminator="\n");w.writeheader()
   for row in raw.get("samples",[]):
    if row.get("role")==role:w.writerow({k:row.get(k) for k in columns})
 write("RESOURCE_SUMMARY.json",dict(status=rr["status"],sample_count=len(rr["samples"]),held_seconds=rr["GPU_lock_held_seconds"],
  sampled_own_NVML_MiB_peak=max(s["own_NVML_MiB"] for s in rr["samples"]),
  sampled_tree_RSS_bytes_peak=max(s["own_tree_RSS_bytes"] for s in rr["samples"]),
  conservative_root_disk_bytes_peak=max(s["own_new_disk_bytes"] for s in rr["samples"]),
  observation_scope="2-second GPU-phase process-tree samples; not continuous whole-Goal high-water. Root disk counts inherited sparse checkout too. Exited-child RSS sample is missing and triggered STOP.",
  process_tree_gap=gaps,limits_satisfied_in_available_samples=True,downloads=0,installs=0,access164=0,profilers=0,simulators=0,RTL=0,
  scopes_while_held=sorted(set(s["shared_gate"]["completed_scopes"] for s in rr["samples"])),ImageLab_inflight_while_held=sorted(set(s["shared_gate"]["in_flight_scopes"] for s in rr["samples"]))))
 print(json.dumps(dict(status=result["execution_status"],formal=len(formal),diagnostics=len(diagnostic),lattice=lattice)))
if __name__=="__main__":main()
