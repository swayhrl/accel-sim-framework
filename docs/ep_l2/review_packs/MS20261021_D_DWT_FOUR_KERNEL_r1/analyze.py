"""Bounded D-only projection of four E-accepted DWT endpoints; no execution."""
import csv, datetime, fcntl, hashlib, json, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_study_lane_d'))
import paper_four_pair_details as detail
OUT=Path(__file__).resolve().parent
CACHE=ROOT/'docs/ep_l2/mechanism_study_2026_10_19_v1/lane_d/controls_20261021_r4/accepted_snapshot_04'
E_ROOT=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1')
E_AUDIT=E_ROOT/'docs/ep_l2/review_packs/MS20261020_E2_CONTROLS_QUALIFICATION_r1/APPROVED_DWT_RESOURCE_RETRY/INDEPENDENT_TERMINAL_AUDIT.json'
SHARED=Path('/workspace/ep_l2_ft20261016_shared')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,x):(OUT/name).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def csvout(name,rows):
 with (OUT/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def run():
 with (SHARED/'REGISTRY.lock').open() as lock:
  fcntl.flock(lock,fcntl.LOCK_SH);before=(SHARED/'RUN_REGISTRY.json').read_bytes();ledger=json.loads(before)['mechanism_study_20261019_v1']
 attempts={'S':'E017_2bc62654','S_COPY_FREE':'E031_b7073e01','W_ONLY':'E032_df1d16f2','F':'E018_67a874f4'}
 expected={'S':166519,'S_COPY_FREE':166555,'W_ONLY':166792,'F':167643}
 provenance=[];obs={};receipts={};metrics=[];l2=[]
 em=json.loads(E_AUDIT.read_text()); assert em['status']=='BOTH_CURRENT_ACCEPTED'
 for profile,attempt in attempts.items():
  ref=ledger['accepted_results'][attempt];p=Path(ref['path']);assert sha(p)==ref['sha256']
  r=json.loads(p.read_text());n=p.parent/'NATIVE_EXIT.json';native=json.loads(n.read_text());assert sha(n)==r['native_exit_receipt_sha256']
  assert r['status']=='COMPLETE_VALID' and r['independent_acceptance']=='PASS' and r['complete_input_verified']
  assert native['exit_code']==0 and native['wait_status']==0 and native['exited_normally'] and not native['signaled']
  assert native['binding']['attempt_id']==attempt and native['binding']['identity']==r['identity'] and native['native_process']==r['process']
  assert r['summary']['instructions']==148684429 and r['summary']['cycles']==expected[profile] and r['summary']['hardware_drained']
  assert r['validation']['status']=='PASS' and r['validation']['scope']=='global sum of 64 slices'
  assert r['identity']['binary_sha256']=='61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5'
  if profile in ['S','F']:
   op=CACHE/('OBSERVATIONS_'+attempt+'.json');m=json.loads((CACHE/'FILES_SHA256.json').read_text());assert m[op.name]==sha(op)
   o=json.loads(op.read_text());assert o['sha256']==r['raw_log_sha256'];mode='HASH_BOUND_D_SNAPSHOT_REUSED';cache=dict(path=str(op),sha256=sha(op))
  else:
   o=detail.observe(p.parent/'raw.log',r['raw_log_sha256']);mode='NEW_ACCEPTED_RAW_DECODED_ONCE';cache=None
   er=next(x for x in em['rows'] if x['attempt_id']==attempt);assert er['receipt']['sha256']==ref['sha256'] and er['native_exit']['sha256']==sha(n)
  assert o['frames'][-1]['gpu_tot_sim_cycle']==expected[profile]
  assert len([x for x in o['frames'] if x.get('kernel_name')])==10
  obs[profile]=o;receipts[profile]=r
  save('OBSERVATIONS_'+attempt+'.json',o)
  save(attempt+'_RUN_STATUS.json',r);save(attempt+'_NATIVE_EXIT.json',native)
  provenance.append(dict(profile=profile,attempt_id=attempt,cycles=expected[profile],receipt=ref,native_exit_sha256=sha(n),native_process=native['native_process'],normal_exit_code=0,wait_status=0,full_instructions=148684429,kernels=10,slices=64,observation_mode=mode,cache=cache,raw_sha256=r['raw_log_sha256'],qualification_id=r['qualification_id'],labels=r['labels']))
  for group in ['local_service','bottleneck']:
   for k,v in r['mechanism_metrics'][group].items():
    if isinstance(v,(int,float)):metrics.append(dict(profile=profile,group=group,metric=k,value=v))
    elif group=='bottleneck':
     for sub in ['request_wait_cycle_sum','request_wait_max','distinct_requests_first_block']:
      metrics.append(dict(profile=profile,group=group,metric=k+'.'+sub,value=v[sub]))
  # Only a bounded final raw tail for existing L2/DRAM utilization evidence; no traces.
  raw=p.parent/'raw.log';size=raw.stat().st_size
  with raw.open('rb') as f:f.seek(max(0,size-4*1024*1024));tail_bytes=f.read()
  tail=tail_bytes.decode(errors='replace')
  vals={k:re.findall(r'^'+re.escape(k)+r'\s*=\s*([0-9.]+)',tail,re.M) for k in ['L2_total_cache_accesses','L2_total_cache_misses','L2_total_cache_miss_rate','L2_total_cache_pending_hits']}
  bw=[float(x) for x in re.findall(r'\bbw_util=([0-9.]+)',tail)][-32:]
  assert len(bw)==32 and all(vals.values())
  l2.append(dict(profile=profile,tail_bytes=min(size,4*1024*1024),expected_accepted_raw_sha256=r['raw_log_sha256'],observed_final_tail_sha256=hashlib.sha256(tail_bytes).hexdigest(),raw_path=str(raw),L2={k:float(v[-1]) for k,v in vals.items()},final_dram_channel_bw_util_min=min(bw),final_dram_channel_bw_util_max=max(bw),final_dram_channel_bw_util_mean=sum(bw)/32,scope='Final cumulative reported per-channel utilization; NOT critical path attribution'))
 rows=[];wide=[];comparisons=[('S','S_COPY_FREE'),('S','W_ONLY'),('S','F'),('W_ONLY','F'),('S_COPY_FREE','W_ONLY')]
 for left,right in comparisons:
  rr=detail.paired_timing('dwt2d',{'S':obs[left],'F':obs[right]})
  assert sum(x['F_minus_S_cycles'] for x in rr)==expected[right]-expected[left]
  for x in rr:
   x['left_profile']=left;x['right_profile']=right
   x['right_minus_left_cycles']=x.pop('F_minus_S_cycles')
   for k in list(x):
    if k.startswith('S_'):x['left_'+k[2:]]=x.pop(k)
    elif k.startswith('F_'):x['right_'+k[2:]]=x.pop(k)
   rows.append(x)
 for i in range(11):
  row=dict(kernel_ordinal=i+1 if i<10 else 'FINAL_RESIDUAL')
  for profile in attempts:
   fs=[x for x in obs[profile]['frames'] if x.get('kernel_name')]
   row['kernel_name']=fs[i]['kernel_name'] if i<10 else 'final cycles minus named durations; cause UNKNOWN'
   row[profile]=fs[i]['gpu_sim_cycle'] if i<10 else expected[profile]-sum(x['gpu_sim_cycle'] for x in fs)
  for left,right in comparisons:row[right+'_minus_'+left]=row[right]-row[left]
  wide.append(row)
 csvout('FOUR_PROFILE_KERNEL_CYCLES.csv',wide);csvout('FIVE_CONTRAST_KERNEL_AND_MECHANISM_DELTAS.csv',rows);csvout('TERMINAL_MECHANISM_METRICS.csv',metrics)
 save('ACCEPTED_PROVENANCE.json',provenance);save('L2_DRAM_SENSITIVITY_EVIDENCE.json',dict(rows=l2,recommendation='DO_NOT_SPEND_FIRST_BATCH_STARTS_ON_L2_DRAM_SENSITIVITY',reason='These counters show traffic/miss activity, not a critical L2/DRAM bandwidth bottleneck. Final DRAM channel utilization is well below saturation; nonexclusive request waits cannot identify sensitivity to capacity, service latency or bandwidth. Prioritize direct supported mechanism controls. No grid and no parameter change proposed.',proposed_parameter_changes=0,proposed_SF_pairs=0,application_starts=0))
 save('RECEIPT.json',dict(observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),acceptance_owner='E',analysis_owner='D',E_final_publication='b8a1ddc5995456332ef4ac8e36d028ec8f77e097',D_base_publication='569c12970f81fefac50210c576a357189f9bb1e4',E_final_audit_sha256=sha(E_AUDIT),registry_before_sha256=hashlib.sha256(before).hexdigest(),registry_after_sha256=sha(SHARED/'RUN_REGISTRY.json'),registry_bytes_unchanged=before==(SHARED/'RUN_REGISTRY.json').read_bytes(),application_starts=0,trace_body_reads=0,binary_rebuilds=0,native_tests_repeated=0,raw_new_decodes=2,old_snapshot_reuses=2,raw_final_tail_bytes=4*4*1024*1024,accepted_control_ids=[k for k in ledger['accepted_pairs'] if k.startswith('V2_CONTROL_dwt2d')],W_ONLY_to_F_cycles=851,closure_verified=True,scope='Kernel GPU durations and explicit final residual; counters are cumulative snapshot increments, never additive causal GPU stalls. W_ONLY to F is joint V plus RO/state contrast; COPY_FREE exempts copy services and fixed staging delay, not a physical hardware endpoint.'))
 assert before==(SHARED/'RUN_REGISTRY.json').read_bytes()
 save('FILES_SHA256.json',{p.name:sha(p) for p in OUT.iterdir() if p.is_file() and p.name not in ['FILES_SHA256.json','REMOTE_READBACK.json']})
 print(json.dumps(wide,indent=2))
if __name__=='__main__':run()
