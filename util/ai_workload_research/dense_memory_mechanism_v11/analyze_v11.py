"""Independent CPU-only V11 synthesis; lawful private completions needed."""
from pathlib import Path
import json,hashlib,statistics,csv,gzip
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'docs/ai_workload_research/runs/QWEN_DENSE_MEMORY_MECHANISM_CONVERGENCE_109_V11'
def H(b):return hashlib.sha256(b).hexdigest()
def D(v):return H(json.dumps(v,sort_keys=True,separators=(',',':')).encode())
def load(p):
 return json.loads(p.read_text()) if p.exists() else json.loads(gzip.decompress(p.with_suffix(p.suffix+'.gz').read_bytes()))
def lines(p):
 b=p.read_text() if p.exists() else gzip.decompress(p.with_suffix(p.suffix+'.gz').read_bytes()).decode()
 return b.splitlines(keepends=True)
def write(name,v):(OUT/name).write_text(json.dumps(v,indent=2)+'\n')
def val(n,k):return float(n['metrics'][k]['value'].replace(',',''))
def stats(v):
 m=statistics.median(v);return dict(n=len(v),median=m,MAD=statistics.median(abs(x-m) for x in v),minimum=min(v),maximum=max(v),all_values=v)
def receipt(folder):
 a=load(folder/'RESOURCE_RECEIPT.json')
 return load(folder/'raw/RESOURCE_RECEIPT.json') if 'full_executed_receipt_archive' in a else a
def main():
 native=[]
 for task in ['NCU_B1_L0','NCU_B2_L0','NCU_B1_L17','NCU_B2_L17']:
  a=load(OUT/'raw'/(task+'_AUDIT.json'));assert a['actual_rows']==3 and a['safe_single_pass']
  for n in a['nodes']:
   assert n['passes']==1 and n['backup_bytes'] is None and n['paired_by_order_contract_grid_weight']
   target=n['target'];read=val(n,'dram__bytes_read.sum');time=val(n,'gpu__time_duration.sum');weight=target['logical_weight_BF16_bytes']
   native.append(dict(task=task,mode='B1' if '_B1_' in task else 'B2',layer=target['decoder_layer_zero_based'],module=target['logical_module'],op=target['logical_op'],M=target['compiled_contract_M'],K=target['compiled_contract_K'],N=target['compiled_contract_N'],weight_bytes=weight,DRAM_read_bytes=read,duration_ns=time,node_read_GB_s=read/time,read_over_weight=read/weight,logical_FLOPs_per_read_byte=2*target['compiled_contract_M']*target['compiled_contract_K']*target['compiled_contract_N']/read,SM_elapsed_cycle_rate_proxy_GHz=val(n,'sm__cycles_elapsed.avg')/time,tensor_pipe_active_percent=val(n,'sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_elapsed'),kernel=n['kernel'],grid=n['grid'],block=n['block'],paired=True,pairing_grade='COMPILED_ORDER_GRAPH_WEIGHT_AND_LAUNCH_CONTRACT;NOTRAWARGUMENTCAPTURE',actual_passes=1,backup_counter=None,grade='OBSERVED_PROFILED_NODE'))
 ratios=[]
 for layer in [0,17]:
  for op in ['self_attn.o_proj','mlp.gate_up_proj','mlp.down_proj']:
   a=next(v for v in native if v['layer']==layer and v['op']==op and v['mode']=='B1');b=next(v for v in native if v['layer']==layer and v['op']==op and v['mode']=='B2')
   ratios.append(dict(layer=layer,op=op,read_ratio_B2_B1=b['DRAM_read_bytes']/a['DRAM_read_bytes'],duration_ratio_B2_B1=b['duration_ns']/a['duration_ns']))
 write('DOMINANT_DENSE_COUNTERS.json',dict(status='12_TARGETS_COMPLETE_PAIRED_BY_CONTRACT',nodes=native,B1_B2_ratios=ratios,sample_size_per_node=1,no_app_DRAM_sum=True,no_layer_multiplication=True,causal_global_bottleneck='INCONCLUSIVE',tensor_metric_deprecated=True))
 with (OUT/'EVIDENCE_MATRIX.tsv').open('w') as f:
  fields=list(native[0]);w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(native)
 local=[]
 for sub,tasks in [('', ['LOCAL_B1','LOCAL_B2']),('readonly_control',['LOCAL_RO_B1','LOCAL_RO_B2'])]:
  for task in tasks:
   folder=OUT/sub;a=load(folder/'raw'/(task+'_AUDIT.json'));raw=load(folder/'raw'/(task+'.json'));assert a['actual_rows']==len(raw['rows'])==10 and a['safe_single_pass']
   rows=[]
   for n,row in zip(a['nodes'],raw['rows']):
    duration=val(n,'gpu__time_duration.sum');assert n['passes']==1
    rows.append(dict(**row,DRAM_read_bytes=val(n,'dram__bytes_read.sum'),DRAM_write_bytes=val(n,'dram__bytes_write.sum') if 'dram__bytes_write.sum' in n['metrics'] else None,duration_ns=duration,SM_elapsed_cycle_rate_proxy_GHz=val(n,'sm__cycles_elapsed.avg')/duration,tensor_pipe_active_percent=val(n,'sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_elapsed'),kernel=n['kernel'],grid=n['grid'],block=n['block']))
   assert len({v['output_bits_sha256'] for v in rows})==1
   summaries={}
   for condition in sorted({v['precondition'] for v in rows}):
    q=[v for v in rows if v['precondition']==condition]
    summaries[condition]={key:stats([v[key] for v in q]) if q[0][key] is not None else None for key in ['DRAM_read_bytes','DRAM_write_bytes','duration_ns','SM_elapsed_cycle_rate_proxy_GHz','tensor_pipe_active_percent']}
   cold=next(k for k in summaries if k!='REUSE');reuse=summaries['REUSE'];evict=summaries[cold];weight=45088768
   contrast=reuse['DRAM_read_bytes']['median']<=.2*weight and evict['DRAM_read_bytes']['median']>=.8*weight and evict['DRAM_read_bytes']['median']/max(1,reuse['DRAM_read_bytes']['median'])>=4
   write_ok=all(v['DRAM_write_bytes'] is not None and v['DRAM_write_bytes']<=.05*weight for v in rows) if sub else None
   local.append(dict(task=task,mode='B2' if task.endswith('B2') else 'B1',method='READ_ONLY_SUM' if sub else 'WRITE_ADD',rows=rows,summaries=summaries,read_state_contrast_valid=contrast,target_write_small_verified=write_ok,same_kernel_name_grid_block=len({(v['kernel'],v['grid'],v['block']) for v in rows})==1,output_bits_identical=True,duration_ratio_cold_reuse=evict['duration_ns']['median']/reuse['duration_ns']['median'],grade='PARTIALLY_ATTRIBUTED_LOCAL_DATA_STATE' if contrast and write_ok else 'INCONCLUSIVE_CONTROL_NOT_ESTABLISHED_OR_WRITE_CONFOUNDED',physical_clocks_uncontrolled=True,no_native_latency_substitution=True,synthetic_values_real_projection_shape=True))
 write('LOCAL_CONTROL_RESULTS.json',dict(experiments=local,all_40_observations_retained=True,write_precondition_not_clean_DRAM_latency_axis=True,B1_failed_reuse_precondition_not_hidden=True,local_not_full_application=True,no_global_CAUSALLY_SUPPORTED=True))
 # Full input-source and token-sequence recheck, with firstDecode consumedtoken identity.
 old=ROOT.parent/'accel-sim-aiarch-decode-cost-and-memory-mechanism-109-v9/docs/ai_workload_research/runs/QWEN_DECODE_COST_MEMORY_MECHANISM_109_V9/.private/CURVE/completions.jsonl'
 refs={}
 for v in map(json.loads,old.read_text().splitlines()):
  for row in v['outputs']:
   ids=row['completions'][0]['tokens']
   if len(ids)==32:refs.setdefault(row['source'],ids)
 verified=[];calls=0;completion_count=0
 for sub,tasks in [('', ['NCU_B1_L0','NCU_B2_L0','NCU_B1_L17','NCU_B2_L17']),('software',['NCU_LT_B1_L0'])]:
  folder=OUT/sub;inputs=load(folder/'.private/inputs.json');sources={D(v):k.removesuffix('_512') for k,v in inputs.items()}
  for task in tasks:
   raw=load(folder/'raw'/(task+'.json'));pub=[json.loads(v) for v in lines(folder/'raw'/(task+'_records.jsonl'))];returns={v['index']:v for v in pub if v['event']=='RETURNED_ALL_REQUESTS'};private=lines(folder/'.private'/task/'completions.jsonl')
   assert len(raw['samples'])==len(returns)==len(private)==3
   for sample,line in zip(raw['samples'],private):
    actual=json.loads(line);record=returns[sample['index']];assert H(line.encode())==sample['private_record_sha256']
    assert H((json.dumps(record,separators=(',',':'),allow_nan=False)+'\n').encode())==sample['public_record_sha256']
    assert record['fullgraph_replay_count']==31 and record['active_compiled_Qwen2Model'];calls+=1
    for row,pubrow in zip(actual['outputs'],record['outputs']):
     assert row['source']==sources[D(row['returned_prompt_token_ids'])]==pubrow['source'];assert D(row['returned_prompt_token_ids'])==pubrow['prompt_sha256']
     assert len(row['completions'])==1;c=row['completions'][0];assert len(c['tokens'])==32 and c['tokens']==refs[row['source']] and not c['logprobs']
     assert D(c['tokens'])==pubrow['token_sha256'][0];completion_count+=1
   verified.append(dict(task=task,runtime=raw['runtime'],all_three_returned_requests_verified=True,exact_V9_reference_tokens=True,first_decode_tokens={k:v[0] for k,v in refs.items()},logprobs='UNOBSERVED',old_numeric_PASS_not_claimed=True))
 write('INPUT_RUNTIME_NUMERIC_RECHECK.json',dict(status='PASS_SOURCE_RUNTIME_TOKEN_IDENTITY',generate_calls=calls,completions=completion_count,tasks=verified,fullgraph_count_each=31,no_new_native_eager_boundary_mapping=True))
 resources=[];total=0
 for sub in ['', 'software','readonly_control']:
  a=receipt(OUT/sub);samples=a['samples'];total+=a['GPU_lock_held_seconds']
  resources.append(dict(window=sub or 'dominant',status=a['status'],reason=a.get('reason'),hold_seconds=a['GPU_lock_held_seconds'],lock_attempts=a['lock_attempt_count'],lock_released=a['lock_released'],contexts_cleared=a.get('own_GPU_contexts_cleared'),reservation_released=a['shared_reservation_cleanup']['released'],model_initializations=a['GPU_model_initializations'],worker_launches=a['worker_launches'],peak_own_NVML_MiB=max(v['own_NVML_MiB'] for v in samples),peak_live_RSS_bytes=max(v['own_tree_RSS_bytes'] for v in samples),peak_session_charged_bytes=max(v['session_memory']['kernel_charged_peak_bytes'] for v in samples),conservative_worktree_disk_peak_bytes=max(v['own_new_disk_bytes'] for v in samples),monitor_gaps=[dict(index=i,gaps=v['monitor_gaps']) for i,v in enumerate(samples) if v['monitor_gaps']]))
 write('RESOURCE_ANALYSIS.json',dict(status='ALL_THREE_WINDOWS_CLOSED',windows=resources,cumulative_GPU_held_seconds=total,nonblocking_acquisitions=3,no_failed_acquire_retry=True,concurrent_owners_max=1,measured_GPUowner_session_caps_met=True,CPU_helper_scope='IndependentreportedHWM/readbounds,notcombinedkernelGoalRSSpeak;unknownshortprocesspeaksremaincensored',no_GPU_after_final_readonly_window=True))
 print(json.dumps(dict(nodes=len(native),ratios=ratios,locals=[{k:v for k,v in a.items() if k not in ['rows','summaries']} for a in local],calls=calls,completions=completion_count,GPU_seconds=total)))
if __name__=='__main__':main()
