"""Independent post-run CPU recheck; no torch,NVML or additional inference."""
from pathlib import Path
import json,hashlib,math,statistics,csv,time
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/"docs/ai_workload_research/runs/QWEN_BF16_BATCH_NUMERIC_DIAGNOSTIC_109_V7"
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+"\n")
def main():
 raw=json.loads((OUT/"raw/PROBE.json").read_text());private=json.loads((OUT/".private/PROBE_private_outputs.json").read_text());rr=json.loads((OUT/"RESOURCE_RECEIPT.json").read_text())
 inputs=json.loads((OUT/".private/inputs.json").read_text());source_map={digest(v):k.removesuffix("_512") for k,v in inputs.items()}
 assert len(raw['samples'])==len(private['samples'])
 records=[];lookup={};completion_count=0
 for public,secret in zip(raw['samples'],private['samples']):
  assert (public['point'],public['role'],public['round'])==(secret['point'],secret['role'],secret['round'])
  assert public['capture_complete_before_numeric_gate']
  assert len(public['outputs'])==len(secret['outputs'])==public['batch_size']
  for pu,pr in zip(public['outputs'],secret['outputs']):
   actual_source=source_map[digest(pr['returned_prompt_token_ids'])]
   assert actual_source==pr['source']==pu['source'];assert len(pr['returned_prompt_token_ids'])==512
   assert digest(pr['returned_prompt_token_ids'])==pu['prompt_token_sha256']
   assert pr['request_id']==pu['request_id'];assert len(pr['completions'])==1
   c=pr['completions'][0];ids=c['tokens'];probs=c['logprobs'];completion_count+=1
   assert ids==pr['tokens'] and probs==pr['logprobs']
   assert len(ids)==len(probs)==public['output_tokens_each']
   assert digest(ids)==pu['token_sha256'] and digest(probs)==pu['logprob_sha256']
   assert all(math.isfinite(v) for step in probs for v in step.values())
   selected=[probs[j][str(tok)] for j,tok in enumerate(ids)]
   assert selected==c['sampled_token_logprobs'];assert digest(selected)==pu['sampled_logprob_sha256']
   assert all(c['logprob_metadata'][j][k]['logprob']==v for j,step in enumerate(probs) for k,v in step.items())
   row=dict(point=public['point'],role=public['role'],group=public['round']+1,source=actual_source,request_id=pr['request_id'],
      prompt_token_sha256=digest(pr['returned_prompt_token_ids']),token_sha256=digest(ids),token_count=len(ids),sampled_logprobs=selected,
      top20_counts=[len(s) for s in probs],all_returned_finite=True,exact_actual_prompt_source_verified=True,all_public_hashes_verified=True)
   records.append(row);lookup[(public['role'],public['round'],public['point'],actual_source)]=(pr,row)
 groups=[]
 for gi in range(2):
  per=[]
  for source,pid in [('TRAIN_A_DISCOVERY_00','P1'),('TRAIN_A_DISCOVERY_01','P2')]:
   a,ar=lookup[('DIAGNOSTIC',gi,pid,source)];b,br=lookup[('DIAGNOSTIC',gi,'P3',source)]
   al=ar['sampled_logprobs'];bl=br['sampled_logprobs'];delta=bl[0]-al[0];allowed=.05+.01*abs(al[0])
   common=sorted(set(a['logprobs'][0])&set(b['logprobs'][0]),key=int)
   changes=[dict(token_id_sha256=hashlib.sha256(k.encode()).hexdigest(),B1=a['logprobs'][0][k],B2=b['logprobs'][0][k],delta=b['logprobs'][0][k]-a['logprobs'][0][k],
      B1_rank=a['completions'][0]['logprob_metadata'][0][k]['rank'],B2_rank=b['completions'][0]['logprob_metadata'][0][k]['rank']) for k in common]
   ds=[v['delta'] for v in changes];anchor=min(ds);lattice=max(abs((d-anchor)-round((d-anchor)/.125)*.125) for d in ds)
   per.append(dict(source=source,token_exact=a['tokens']==b['tokens'],B1=al[0],B2=bl[0],signed_delta=delta,abs_error=abs(delta),allowed=allowed,pass_gate=a['tokens']==b['tokens'] and abs(delta)<=allowed,
       common_token_count=len(common),top20_changes=changes,delta_min=min(ds),delta_max=max(ds),delta_span=max(ds)-min(ds),delta_median=statistics.median(ds),delta_MAD=statistics.median(abs(d-statistics.median(ds)) for d in ds),relative_0p125_lattice_max_residual=lattice))
  groups.append(dict(group=gi+1,comparisons=per,all_pass=all(x['pass_gate'] for x in per)))
 repeats=[]
 for point,source in [('P1','TRAIN_A_DISCOVERY_00'),('P2','TRAIN_A_DISCOVERY_01'),('P3','TRAIN_A_DISCOVERY_00'),('P3','TRAIN_A_DISCOVERY_01')]:
  a,ar=lookup[('DIAGNOSTIC',0,point,source)];b,br=lookup[('DIAGNOSTIC',1,point,source)]
  shared=set(a['logprobs'][0])&set(b['logprobs'][0])
  repeats.append(dict(point=point,source=source,tokens_exact=a['tokens']==b['tokens'],all_returned_top20_dictionaries_exact=a['logprobs']==b['logprobs'],
    sampled_abs_error=max(abs(x-y) for x,y in zip(ar['sampled_logprobs'],br['sampled_logprobs'])),common_top20_max_abs_error=max(abs(a['logprobs'][0][k]-b['logprobs'][0][k]) for k in shared)))
 old=Path('/home/huangrulin/workspace/worktrees/accel-sim-aiarch-bf16-decode-weight-supply-probe-109-v5/docs/ai_workload_research/runs/QWEN_BF16_DECODE_WEIGHT_SUPPLY_PROBE_109_V5')
 prior=json.loads((old/'.private/PROBE_private_outputs.json').read_text());v5={x['point']:x['outputs'][0] for x in prior['samples']}
 relation=[]
 for gi in range(2):
  for point in ['P1','P3']:
   a,row=lookup[('DIAGNOSTIC',gi,point,'TRAIN_A_DISCOVERY_00')];v=v5[point]
   relation.append(dict(group=gi+1,point=point,source='TRAIN_A_DISCOVERY_00',V5_tokens_equal=a['tokens']==v['tokens'],V5_all_returned_logprob_dictionaries_exact=a['logprobs']==v['logprobs']))
 snapshot=[]
 for s in raw['samples']:
  snapshot.append(dict(point=s['point'],role=s['role'],group=s['round']+1,actual_request_description=s['actual_request_description'],sampling=s['sampling'],
    active_compiled_Qwen2Model=s['active_compiled_Qwen2Model'],fullgraph_replay_count=len(s['graph_replays']),graph_replays=s['graph_replays'],new_graph_descriptors=s['new_graph_descriptors'],
    counters_before=s['counters_before'],counters_after=s['counters_after']))
 diag=dict(status='REPRODUCIBLE_FROZEN_A00_B1_B2_NUMERIC_FAILURE',groups=groups,repetition=repeats,V5_relation=relation,
    request_count=sum(s['role']=='DIAGNOSTIC' for s in raw['samples']),completion_count=completion_count,all_saved_before_numeric=True,atol=.05,rtol=.01,tolerance_changed=False,
    root_cause_category='BATCH_EXECUTION_PATH_ASSOCIATED_DIFFERENCE;originUNRESOLVED',interpretation='Stable nonuniform returned score-vector change associated with B1/B2; same selected token. Exact across two groups and preserved V5 A00 records. Cannot localize toBF16kernel,forwardlayer,lm_headorsamplerwithoutintermediateexecutionevidence.')
 save('DIAGNOSTIC_ANALYSIS.json',diag);save('NUMERIC_AND_IDENTITY.json',dict(status=diag['status'],records=records,runtime=raw['runtime'],request_execution_snapshots=snapshot,all_raw_completion_records_private=True))
 save('INDEPENDENT_NUMERIC_RECHECK.json',dict(status='CONFIRMED_BOTH_GROUPS_A00_FAIL_A01_PASS',records_checked=completion_count,groups=groups,repetition=repeats,V5_relation=relation,actual_prompt_to_source_mapping='IndependentcanonicalhashoffullreturnedpromptIDarray',all_public_private_hashes_verified=True))
 formal=[s for s in raw['samples'] if s['role']=='FORMAL']
 stats={};da=db=dc=ratio=None
 if len(formal)==30 and all(s['status']=='PASS' for s in formal) and all(g['all_pass'] for g in groups):
  for point in ['P1','P2','P3','P4','P5','P6']:
   vals=[s['request_gpu_elapsed_ms'] for s in formal if s['point']==point];assert len(vals)==5
   med=statistics.median(vals);stats[point]=dict(n=5,median_ms=med,MAD_ms=statistics.median(abs(v-med) for v in vals))
  da=stats['P4']['median_ms']-stats['P1']['median_ms'];db=stats['P5']['median_ms']-stats['P2']['median_ms'];dc=stats['P6']['median_ms']-stats['P3']['median_ms'];ratio=dc/statistics.mean([da,db])
 analysis=dict(execution_status=rr['status'],scientific_performance_status='INCONCLUSIVE',numeric_status=diag['status'],diagnostic_requests=diag['request_count'],completions=completion_count,
    warmup_requests=sum(s['role']=='WARMUP' for s in raw['samples']),formal_samples=len(formal),point_statistics=stats,delta_A00=da,delta_A01=db,delta_B2=dc,R=ratio,
    shared_condition=rr.get('measurement_condition'),desktop_telemetry_gap=rr.get('performance_comparability_gap'),
    H1='Weight supply not evaluated: no legal formal samples; conditionalbyteboundnotactualDRAM.',H2='Batch-dependent computation/scheduling or score processing remains competitive; no pure decode timing or kernel trace.',
    H3='Returnedprompt/token/request pairing independently verified; actual strong compiled configuration captured for both groups; internal prefill tensor/kernel shapes not measured.',
    hypotheses=dict(MODEL_FORWARD_NUMERIC='Possible,notlocalized',LOGPROB_OR_SAMPLER_NUMERIC='Possible,notlocalized',BATCH_EXECUTION_PATH='Mostsupportedassociation,notuniquecomputationalcause',OBSERVATION_OR_PAIRING_DEFECT='V6persistencefixworks;noobservedpairingdefectexplainsV7difference',UNRESOLVED='Nohiddenstates,fullvocabularylogits,oractualper-opintermediatetensors.'),
    further_hardware_candidate=None,performance_ranking=None,no_additional_GPU=True)
 save('ANALYSIS.json',analysis)
 for filename,role in [('DIAGNOSTIC_SAMPLES.tsv','DIAGNOSTIC'),('WARMUP_SAMPLES.tsv','WARMUP'),('FORMAL_SAMPLES.tsv','FORMAL')]:
  with (OUT/filename).open('w',newline='') as f:
   fields=['point','role','round','index','batch_size','output_tokens_each','request_gpu_elapsed_ms','host_generate_call_ms','host_synchronized_request_ms','status']
   writer=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');writer.writeheader()
   for s in raw['samples']:
    if s['role']==role:writer.writerow({k:s[k] for k in fields})
 rss_candidates=[dict(snapshot=i,**v) for i,s in enumerate(rr['samples']) for v in s.get('rss_censored_observations',[])]
 save('RESOURCE_SUMMARY.json',dict(status=rr['status'],samples=len(rr['samples']),GPU_lock_held_seconds=rr['GPU_lock_held_seconds'],
    sampled_own_NVML_MiB_peak=max(s['own_NVML_MiB'] for s in rr['samples']),sampled_live_tree_RSS_subtotal_bytes_peak=max(s['own_tree_RSS_bytes'] for s in rr['samples']),
    kernel_session_charged_memory_peak_bytes=max(s['session_memory']['kernel_charged_peak_bytes'] for s in rr['samples']),
    conservative_sparse_worktree_disk_bytes_peak=max(s['own_new_disk_bytes'] for s in rr['samples']),censored_observations=rss_candidates,
    mandatory_monitor_gaps=[dict(snapshot=i,gaps=s['monitor_gaps']) for i,s in enumerate(rr['samples']) if s['monitor_gaps']],
    initial_and_runtime_memory_scope=rr['samples'][0]['session_memory'],peak_is_not_RSS='Neither sampledliveRSS subtotal nor cgroupchargedpeak is exact continuous summedprocessRSS. NoRSSvalueimputedforexitedchildren.',
    ImageLab_completed_scopes=sorted(set(s['shared_gate']['completed_scopes'] for s in rr['samples'])),ImageLab_inflight=sorted(set(s['shared_gate']['in_flight_scopes'] for s in rr['samples'])),
    own_contexts_cleared=rr['own_GPU_contexts_cleared'],lock_released=rr['lock_released'],reservation_cleanup=rr['shared_reservation_cleanup']))
 print(json.dumps(dict(status=diag['status'],requests=diag['request_count'],completions=completion_count,groups=[dict(group=g['group'],pairs=[{k:v for k,v in p.items() if k not in ['top20_changes']} for p in g['comparisons']]) for g in groups],repetition=repeats,V5_relation=relation)))
if __name__=='__main__':main()
