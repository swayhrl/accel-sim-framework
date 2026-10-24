"""Independent parent source/decode/issue/mapping join; no SIM/GPU execution."""
from pathlib import Path
from collections import Counter
import hashlib,json,re,lzma,time
R=Path('/root/data/shared_sm70_trace_library_20261024_v1')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
cases=[('jit','3ca5327ee4124d99a6725644c1bf8b7c','030fd1fd7639878945bebbf8f3f10458dc7a2f31ed92f5ce8fbf98ebe0098489','6e5a2e6ca6895f3b3ada250689f4f07d1f1536a56739b7a836988452b92e8688',45,834,15,287,352,18,11,7),('warpsync','6de4f2ae916c4d9181c14d55d19f43ba','43d967e3502952cf56e8f5a163e541ac35ded18d8fddcd0c1dcb83ec20832b0a','f5300d3f91e63c0323895f3a4292330b3748397dc313f1395bcd4887cbc38fd8',264,5266,16,296,518,28,12,16)]
results=[];reg=json.loads(Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json').read_text())
for kind,uid,specsha,rawsha,nsource,source_lanes,naux,aux_lanes,const_lanes,l1c,miss,hit in cases:
 B=Path('/root/data/ep_l2_main_ada_'+kind+'_maps_r3_compat_20261024_v1');O=B/'run'/uid;assert sha(B/'control/FROZEN_SPEC.json')==specsha
 s=json.loads((B/'control/FROZEN_SPEC.json').read_text());c=next(iter(s['cases'].values()));exit=json.loads((O/'EXIT.json').read_text());row=reg['registered_future_requests'][s['request']]
 assert row['consumed']==row['budget']==1 and row['spec_sha256']==specsha and exit['exit_code']==0 and exit['stop_reason'] is None and exit['application_attempt_consumed']==1
 assert sha(O/'raw.log')==exit['raw_sha256']==rawsha and exit['native_observed'] and exit['maps_observation_proof']['checkpoint_labels']==['FIRST_ISSUE','TERMINAL']
 for name,want in s['pinned_files'].items():assert sha(name)==want,name
 raw=(O/'raw.log').read_text();decoded=[dict(x.split('=',1)for x in line.split()[1:])for line in raw.splitlines()if line.startswith('ADA8_DECODE ')]
 source=[x for x in decoded if x['aux']=='0'];aux=[x for x in decoded if x['aux']=='1']
 assert len(source)==nsource and len(aux)==naux and sum(int(x['mask'],16).bit_count()for x in source)==source_lanes and sum(int(x['mask'],16).bit_count()for x in aux)==aux_lanes
 assert sum(int(x['mask'],16).bit_count()for x in decoded if x['space']=='8')==const_lanes
 def count(pattern):
  vals=re.findall(pattern,raw,re.M);assert vals,pattern;return int(vals[-1])
 total=source_lanes+aux_lanes
 assert count(r'^gpu_tot_sim_insn\s*=\s*(\d+)')==total and count(r'^gpu_tot_issued_cta\s*=\s*(\d+)')==2 and count(r'^ctas_completed\s+(\d+)')==2
 assert count(r'^\s*L1C_total_cache_accesses\s*=\s*(\d+)')==l1c and count(r'^\s*L1C_total_cache_misses\s*=\s*(\d+)')==miss
 assert count(r'^\s*Total_core_cache_stats_breakdown\[CONST_ACC_R\]\[HIT\]\s*=\s*(\d+)')==hit
 assert count(r'^gpgpu_n_mem_const\s*=\s*(\d+)')==6 and count(r'^\s*L2_cache_stats_breakdown\[CONST_ACC_R\]\[TOTAL_ACCESS\]\s*=\s*(\d+)')==12
 assert count(r'^gpgpu_n_mem_write_global\s*=\s*(\d+)')==10
 assert sum(int(x['mask'],16).bit_count()for x in source if x['op'].startswith('STG'))==65 and sum(int(x['mask'],16).bit_count()for x in source if x['op']=='EXIT')==74
 assert re.search(r'^-gpgpu_perfect_inst_const_cache\s+0\s*$',Path(c['config']).read_text(),re.M)
 tr=Path(c['trace_entry']).parent;grouped=list(tr.glob('*.traceg.xz'));assert len(grouped)==1;warps=[];w=None;ctas=0
 with lzma.open(grouped[0],'rt')as f:
  for line in f:
   if line.startswith('thread block ='):ctas+=1
   elif line.startswith('warp ='):w=[];warps.append(w)
   elif re.match(r'^[0-9a-fA-F]{16}\s',line):
    t=line.split();n=int(t[2]);op=t[3+n];ext=t[t.index('ADA8')+1:];w.append((int(t[0],16),int(t[1],16),op,ext))
 assert ctas==2 and len(warps)==4 and sum(len(w)for w in warps)==nsource
 original=Counter((pc,mask,op)for w in warps for pc,mask,op,_ in w);actual=Counter((int(x['pc'],16),int(x['mask'],16),x['op'])for x in source);assert original==actual
 assert sum(mask==0 for w in warps for _,mask,_,_ in w)==2 and min(pc for w in warps for pc,_,_,_ in w)>2**32
 calls=returns=named=0;sync_masks=[];base=min(pc for w in warps for pc,_,_,_ in w)
 for w in warps:
  stacks={lane:[]for lane in range(32)}
  for i,(pc,mask,op,ext)in enumerate(w):
   if op=='WARPSYNC':
    values=list(map(int,ext[8:]));assert int(ext[7])==3 and len(values)==mask.bit_count() and all(x==mask for x in values);named+=len(values);sync_masks.append(mask)
   if not(op.startswith('CALL.')or op.startswith('RET.')):continue
   assert ext[2:4]==['-1','0']and ext[5:7]==['0','0'];kindnum=int(ext[7]);values=list(map(int,ext[8:]));lanes=[lane for lane in range(32)if mask>>lane&1];assert len(values)==len(lanes) and kindnum==(1 if op.startswith('CALL.')else 2)
   for lane,value in zip(lanes,values):
    successor=next(nextpc for nextpc,nextmask,_,_ in w[i+1:]if nextmask>>lane&1);assert successor==base+value
    if kindnum==1:stacks[lane].append(pc+16);calls+=1
    else:assert stacks[lane]and stacks[lane].pop()==base+value;returns+=1
  assert not any(stacks.values())
 drains=re.findall(r'^ada_warp_sync_drain sid=(\d+) warp=(\d+) pc=0x([0-9a-f]+) older_issued=(\d+) pending_stores=(\d+) active=(\d+)',raw,re.M)
 if kind=='warpsync':
  assert calls==returns==named==65 and len(drains)==3 and sorted(int(x[5])for x in drains)==[5,28,32] and all(x[3]==x[4]=='0'for x in drains)
  assert Counter(int(x[5])for x in drains)==Counter(x.bit_count()for x in sync_masks)
  assert sum(int(x['mask'],16).bit_count()for x in source if x['op'].startswith('LDS'))==65 and sum(int(x['mask'],16).bit_count()for x in source if x['op'].startswith('STS'))==65
 else:
  assert not drains and calls==returns==named==0
  want=c['actual_loaded_cubin_sha256'];assert want=='41425beaa2ecbd5a0bdc3e3f992bcb8be328c17dce22c9a335d2a280ac399bf1' and want in s['pinned_files'].values()
 M=O/'MAP_OBSERVATIONS';union=json.loads((M/'UNION.json').read_text());samples=[json.loads(x)for x in(M/'SAMPLES.jsonl').read_text().splitlines()]
 snapshots={};observed=set();valid_samples=0
 for x in samples:
  if x.get('status')=='EXIT_RACE':continue
  valid_samples+=1;key=(x['pid'],x['start_ticks']);assert x['monotonic']>0
  if 'saved_maps'in x:
   p=M/x['saved_maps'];assert sha(p)==x['maps_sha256'];snapshots[key]=x['maps_sha256'];text=p.read_text()
   for line in text.splitlines():
    cells=line.split(None,5)
    if len(cells)<6 or not cells[5].startswith('/'):continue
    name=cells[5].replace('\\040',' ');assert not name.endswith(' (deleted)') and name in s['pinned_files'];assert sha(name)==s['pinned_files'][name];observed.add(name)
  else:assert snapshots[key]==x['maps_sha256']
 assert valid_samples==union['sample_count']==exit['maps_observation_proof']['sample_count'] and observed==set(union['mapped_dependency_union']) and len(observed)==11
 checkpoints=union['checkpoints'];assert [x['label']for x in checkpoints]==['FIRST_ISSUE','TERMINAL']
 primary=union['primary_identity'];assert primary==exit['maps_observation_proof']['primary_identity']
 for x in checkpoints:
  assert x['primary'] and x['state']in('T','t') and (x['pid'],x['start_ticks'])==(primary['pid'],primary['start_ticks']) and s['binary']in x['paths']
  assert any(p.endswith('/libcudart.so')and'ada_native_extensions_stage4' in p for p in x['paths'])
 assert checkpoints[0]['monotonic']<checkpoints[1]['monotonic']
 result={'status':'PARENT_INDEPENDENT_SCOPED_NATIVE_TERMINAL_JOIN_PASS','case':kind,'request':s['request'],'run':str(O),'raw_sha256':rawsha,'spec_sha256':specsha,'pins_current_full_SHA_checked':95,'source_records':nsource,'source_active_lane_instances':source_lanes,'aux_uops':naux,'aux_active_lane_instances':aux_lanes,'actual_issued_active_lane_uops':total,'constant_lane_instances':const_lanes,'L1C_access_miss_hit':[l1c,miss,hit],'constant_requests':6,'L2_const_accesses':12,'global_store_lanes':65,'core_global_writes':10,'physical_EXIT_lanes':74,'completed_ctas':2,'physical_warps':4,'source_and_decoded_original_PC_mask_opcode_multisets_equal':True,'full64_PC_retained':True,'per_lane_call_target_and_return_stack_joins':[calls,returns],'WARPSYNC_uniform_dynamic_named_lanes':named,'actual_drain_records':drains,'maps_samples':valid_samples,'all_saved_maps_and_eleven_current_paths_full_SHA':True,'checkpoints':checkpoints,'mapping_scope':'Sampled primary and main-thread-list descendants, plus two explicit stopped primary checkpoints; no all-transient-TID/orphan/DSO claim','hardware_timing_calibration':False,'EP_science_acceptance':False,'consumer_value_recomputation':False,'archive_and_reservation_retirement_still_pending':True,'application_attempts_consumed':1,'automatic_retry':False,'observed_unix':time.time()}
 out=O/'PARENT_INDEPENDENT_TERMINAL_JOIN.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');results.append(result)
summary={'status':'PASS_PARENT_BOTH_SCOPED_NATIVE_JIT_AND_WARPSYNC_TERMINAL_JOINS','cases':results,'campaign_consumed':6,'campaign_ceiling':8,'old_failed_case_not_refunded':True,'GPU_or_simulator_executed_by_this_verifier':False}
(R/'control/ADA_STAGE4_R3_PARENT_TERMINAL_JOINS.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items()if k!='cases'}))
