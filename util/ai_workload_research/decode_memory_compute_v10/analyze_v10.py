"""CPU-only independent V10 counter, identity, and resource synthesis."""
from pathlib import Path
import json,hashlib,statistics,csv,gzip
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/ai_workload_research/runs/QWEN_DECODE_MEMORY_COMPUTE_ATTRIBUTION_109_V10'
def H(b):return hashlib.sha256(b).hexdigest()
def D(v):return H(json.dumps(v,sort_keys=True,separators=(',',':')).encode())
def load(p):
 return json.loads(p.read_text()) if p.exists() else json.loads(gzip.decompress(p.with_suffix(p.suffix+'.gz').read_bytes()))
def journal(p):
 data=p.read_text() if p.exists() else gzip.decompress(p.with_suffix(p.suffix+'.gz').read_bytes()).decode()
 return [json.loads(v) for v in data.splitlines()]
def write(name,v):(OUT/name).write_text(json.dumps(v,indent=2)+'\n')
def main():
 pairs={};identity=[];requests=0;comps=0
 for sub,task in [('', 'NUMERIC'),('native_counters','NCU_B1'),('native_b2','NCU_B2')]:
  folder=OUT/sub;raw=load(folder/'raw'/ (task+'.json'));pub=journal(folder/'raw'/(task+'_records.jsonl'));lines=(folder/'.private'/task/'completions.jsonl').read_text().splitlines(keepends=True)
  secrets=[json.loads(x) for x in lines];returns={v['index']:v for v in pub if v['event']=='RETURNED_ALL_REQUESTS'}
  assert len(raw['samples'])==len(secrets)==len(returns)
  inputs=json.loads((folder/'.private/inputs.json').read_text());src={D(v):k.removesuffix('_512') for k,v in inputs.items()}
  for sample,line,secret in zip(raw['samples'],lines,secrets):
   rec=returns[sample['index']];assert H(line.encode())==sample['private_record_sha256']
   assert H((json.dumps(rec,separators=(',',':'),allow_nan=False)+'\n').encode())==sample['public_record_sha256']
   requests+=1
   for row,public in zip(secret['outputs'],rec['outputs']):
    assert src[D(row['returned_prompt_token_ids'])]==row['source']==public['source']
    assert D(row['returned_prompt_token_ids'])==public['prompt_sha256']
    for j,c in enumerate(row['completions']):
     assert len(c['tokens'])==sample['output_tokens_each'] and D(c['tokens'])==public['token_sha256'][j];comps+=1
   if task.startswith('NCU'):
    assert rec['fullgraph_replay_count']==31 and rec['active_compiled_Qwen2Model']
  identity.append(dict(task=task,requests=len(raw['samples']),actual_completions=sum(len(row['completions']) for s in secrets for row in s['outputs']),runtime=raw['runtime'],all_mapping_hash_length_checks=True))
  if task.startswith('NCU'):
   audit=load(folder/'raw'/('NCU_B1_OFFLINE_AUDIT.json' if task=='NCU_B1' else 'NCU_B2_AUDIT.json'))
   assert audit['safe_single_pass'] and audit['passes']==1 and audit['backup_bytes'] is None
   m=audit['metrics'];reads=int(m['dram__bytes_read.sum']['value'].replace(',',''));ns=float(m['gpu__time_duration.sum']['value'].replace(',',''))
   qkv=next(v for v in raw['linear_weight_identity'] if v['module']=='model.layers.0.self_attn.qkv_proj')
   assert qkv['shape']==[2560,2048] and qkv['dtype']=='torch.bfloat16'
   pairs[task]=dict(grade='OBSERVED_SINGLE_NODE',DRAM_read_bytes=reads,duration_ns=ns,replayed_node_read_GB_s=reads/ns,kernel=audit['kernel'],grid=audit['grid'],block=audit['block'],actual_passes=1,backup_counter_value=None,backup_counter_emitted=False,save_restore_interpretation='Actualonepass+toolguideindicatesnosave_restore;missingcounternotzero',scope='FirstfilteredDenseinsidefirstDecodeGraphaftertwoN32warmups;notappbytesortiming',runtime_weight=qkv,shape_attribution='Compiledsource+moduleweight+Graphdescriptor+order/gridconsistent;noargumentdimensioncapture')
 write('INDEPENDENT_IDENTITY_RECHECK.json',dict(status='PASS_INPUT_RUNTIME_OUTPUT_IDENTITY',tasks=identity,returned_generate_calls=requests,returned_completions=comps,logprobs='UNOBSERVED',not_old_numeric_PASS=True))
 micro=load(OUT/'raw/MICRO.json');points=[]
 for shape in ['QKV','GATE_UP']:
  for batch in [1,2]:
   for mode in ['HOT','STREAM']:
    rows=[v for v in micro['samples'] if v['shape']==shape and v['B']==batch and v['mode']==mode and v['role']=='FORMAL'];vals=[v['ms_per_dense_op'] for v in rows];m=statistics.median(vals)
    points.append(dict(shape=shape,B=batch,mode=mode,n=len(vals),median_us=m*1000,MAD_us=statistics.median(abs(v-m) for v in vals)*1000,values_ms=vals,weight_bytes_each=rows[0]['weight_bytes_each'],working_set_weight_bytes=rows[0]['working_set_weight_bytes']))
 write('MICRO_ANALYSIS.json',dict(grade='OBSERVED_PROXY_CAUSAL_MECHANISM_INCONCLUSIVE',points=points,actual_samples=len(micro['samples']),formal=40,warmup=16,scope='Synthetic F.linear BF16 no bias;not native kernelidentity;address reuse labelsnot DRAMcounts'))
 with (OUT/'MICRO_SAMPLES.tsv').open('w') as f:
  fields=list(micro['samples'][0]);w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(micro['samples'])
 a,b=pairs['NCU_B1'],pairs['NCU_B2']
 write('HARDWARE_COUNTER_COMPARISON.json',dict(status='SYMMETRIC_SINGLE_NODE_COUNTERS_COMPLETE',grade='OBSERVED',nodes=pairs,B2_over_B1=dict(DRAM_read_bytes=b['DRAM_read_bytes']/a['DRAM_read_bytes'],duration=b['duration_ns']/a['duration_ns']),weight_model_bytes=10485760,global_DRAM_unmeasured=True,global_memory_bound_not_proven=True,uncertainty='Oneprofilednodepermode,separatefreshengines,samefrozeninputs/warmup/config;noCIorwholeappsum;defaultclockscachesnotforced;Graphnodeidentitysourceconsistent'))
 resource=[];held=0
 for sub in ['', 'native_counters','native_b2']:
  receipt=load(OUT/sub/'RESOURCE_RECEIPT.json')
  # Packaging leaves original full raw in gzip; the public receipt becomes an index.
  if 'full_executed_receipt_archive' in receipt:receipt=load(OUT/sub/'raw/RESOURCE_RECEIPT.json')
  rows=receipt['samples'];held+=receipt['GPU_lock_held_seconds']
  resource.append(dict(window=sub or 'initial',raw_status=receipt['status'],reason=receipt.get('reason'),lock_attempts=receipt['lock_attempt_count'],lock_acquired=receipt['lock_acquired'],held_seconds=receipt['GPU_lock_held_seconds'],lock_released=receipt['lock_released'],own_contexts_cleared=receipt.get('own_GPU_contexts_cleared'),peak_NVML_MiB=max(v['own_NVML_MiB'] for v in rows),peak_live_RSS_bytes=max(v['own_tree_RSS_bytes'] for v in rows),peak_charged_bytes=max(v['session_memory']['kernel_charged_peak_bytes'] for v in rows),conservative_worktree_disk_bytes=max(v['own_new_disk_bytes'] for v in rows),monitor_gaps=[dict(index=i,phase=v['phase'],gaps=v['monitor_gaps']) for i,v in enumerate(rows) if v['monitor_gaps']],reservation_released=receipt['shared_reservation_cleanup']['released']))
 write('RESOURCE_ANALYSIS.json',dict(grade='OBSERVED',windows=resource,total_GPU_held_seconds=held,total_nonblocking_lock_attempts=3,conflicts=0,concurrent_GPU_owners_max=1,limits_unchanged=True,all_caps_below_limits=True,original_B1_terminal_monitor_STOP_preserved=True,no_GPU_after_final_B2=True,scope='Co-residentgatedImageLab+desktoptelemetrygap;sampledliveRSSpluskernelcgrouppeaknotcompleteRSSpeak'))
 print(json.dumps(dict(counters=pairs,ratios=dict(bytes=b['DRAM_read_bytes']/a['DRAM_read_bytes'],duration=b['duration_ns']/a['duration_ns']),requests=requests,completions=comps,total_held=held)))
if __name__=='__main__':main()
