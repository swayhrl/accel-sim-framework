#!/usr/bin/env python3
"""Bounded, read-only CPU consumer of nine preselected accepted original runs.

No subprocess may execute a simulator, launch script or GPU tool. Output is
exclusive-create in this branch and a separate CPU evidence directory.
"""
import csv
from datetime import datetime,timezone
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys

REPO=Path(__file__).resolve().parents[2]
A=Path('/workspace/worktrees/accel-sim-iscas2027-dtc-service-closure-174-v1')
BASE=A/'docs/dtc_l1/iscas2027/service_closure_174_v1'
CHECK=BASE/'review_pack/checkpoint_20261016T2133Z'
PACK=REPO/'docs/dtc_l1/review_packs/DTC_MECHANISM_CPU_CONSUMER_V1'
OUT=Path('/workspace/dtc-mechanism-consumer-174-v1')
RAW=Path('/workspace/dtc-service-closure-174-v1')
CORE=Path('/workspace/worktrees/gpgpu-sim-iscas2027-dtc-service-closure-174-v1')
TRAD=Path('/workspace/worktrees/gpgpu-sim-iscas2027-sg1-canonical')
FW=Path('/workspace/worktrees/accel-sim-decoupled-l1-fast64')
TARGETS=[('GEMM','C+','ba4b73f1-33bc-49ab-9945-f7df3d1a3955',1511333),
 ('GEMM','IO256','b106a859-3c31-4a7b-949a-bf83cdf17e51',1457468),
 ('GEMM','OO128','c76bcd36-f912-4854-8d1c-481fbf8f488a',1377919),
 ('BICG','C+','f91d33da-730a-4047-998c-566c4fc416c0',25353488),
 ('BICG','IO128','87c9040b-1ce7-4166-b68e-38da9bceb1d6',93312525),
 ('BICG','OO128','8a5da6ac-ef65-4ca0-b1de-15a69d6ba613',47533116),
 ('BICG','WAIT128','88ed4a02-4ead-47f5-8e92-cc57fe67c0cf',84049733)]
SOURCES={}
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(4*1024**2),b''):h.update(b)
 return h.hexdigest()
def track(p,role):
 p=Path(p);v=dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p),role=role);SOURCES[str(p)]=v;return v
def need(v,s):
 if not v:raise ValueError(s)
def save(p,v):
 with Path(p).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def read(p,role='accepted receipt'):
 track(p,role);return json.loads(Path(p).read_text())
def table(p):
 track(p,'frozen accepted index')
 with Path(p).open() as f:return list(csv.DictReader(f,delimiter='\t'))
def git(p,*args):return subprocess.check_output(['git','-C',str(p),*args],text=True).strip()
def options(paths):
 o={}
 for p in paths:
  key=None
  for t in shlex.split(Path(p).read_text(),comments=True):
   if re.match(r'^-[A-Za-z_]',t):key=t;o[key]=[]
   else:need(key is not None,'config parse');o[key].append(t)
 return o
def scalar(text):return {k:int(v) for k,v in re.findall(r'^[\t ]*([^\s=]+)[\t ]*=[\t ]*(\d+)[\t ]*$',text,re.M)}
def snapshots(text):
 # Each gpu_print_stat starts with kernel_name; all scalar counters here are
 # lifetime/stream cumulative except explicitly gpu_sim_* per kernel.
 starts=[s.start() for s in re.finditer(r'^kernel_name\s*=',text,re.M)]
 return [text[s:(starts[i+1] if i+1<len(starts) else len(text))] for i,s in enumerate(starts)]
def perf(p,text,last):
 track(p,'original sampled performance statistics')
 with gzip.open(p,'rt') as f:
  r=csv.DictReader(f);h=r.fieldnames;rows=list(r)
 need(rows,'perf rows');end=rows[-1]
 sampled_cycle=int(end['gpu_tot_sim_cycle'])+int(end['gpu_sim_cycle'])
 sampled_insn=int(end['gpu_tot_sim_insn'])+int(end['gpu_sim_insn'])
 need(sampled_cycle<=last['gpu_tot_sim_cycle'] and sampled_insn<=last['gpu_tot_sim_insn'],'perf scope cannot exceed terminal')
 final=sampled_cycle==last['gpu_tot_sim_cycle'] and sampled_insn==last['gpu_tot_sim_insn']
 selected={k:int(end[k]) for k in h if k and re.fullmatch(r'(dram_(reads|writes)_per_mc_\d+|gpgpu_n_mem_(read|write)_global)',k)}
 if final:
  for k in ['gpgpu_n_mem_read_global','gpgpu_n_mem_write_global']:need(selected[k]==last[k],'CSV/stdout same terminal counters')
 return dict(path=str(p),sha256=sha(p),rows=len(rows),header_fields=len(h),DTC_fields=sum('dtc' in k.lower() for k in h),sampled_cycle=sampled_cycle,sampled_instructions=sampled_insn,coverage='TERMINAL_COMPLETE' if final else 'PARTIAL_NOT_TERMINAL',last_selected=selected)
def extract(run,workload,arm,uuid,expected,identity,config):
 p=run/'simulator.stdout';track(p,'accepted raw stdout');text=p.read_text();vals=scalar(text)
 need(vals['gpu_tot_sim_cycle']==expected,'preselected cycles')
 blocks=snapshots(text);need(blocks,'ordered raw kernel blocks')
 per=[]
 for b in blocks:
  v=scalar(b);name=re.search(r'^kernel_name\s*=\s*(\S+)',b,re.M)[1]
  per.append(dict(kernel=name,cycles=v['gpu_sim_cycle'],instructions=v['gpu_sim_insn'],cumulative_cycles=v['gpu_tot_sim_cycle'],cumulative_instructions=v['gpu_tot_sim_insn'],stream=int(re.search(r'^kernel_stream_id\s*=\s*(\d+)',b,re.M)[1])))
 need(sum(v['instructions'] for v in per)==vals['gpu_tot_sim_insn'],'full ordered instruction scope')
 need(len({v['stream'] for v in per})==1,'one fixed stream for cumulative cache buckets')
 # One DRAM counter tuple per controller per kernel print; retain last per
 # controller, do not add Read/Write aliases or repeated kernel snapshots.
 dram={}
 for mc,line in re.findall(r'^DRAM\[(\d+)\]:[^\n]*\n(n_cmd=[^\n]+)',text,re.M):
  d={k:int(v) for k,v in re.findall(r'(n_rd|n_rd_L2_A|n_write|n_wr_bk|n_cmd|n_req)=(\d+)',line)}
  if mc in dram:need(all(d[k]>=dram[mc][k] for k in d),'DRAM lifetime counters monotone')
  dram[mc]=d
 need(len(dram)==int(config['-gpgpu_n_mem'][0]),'all DRAM controllers final tuples')
 ps=perf(run/'perf_counter.csv.gz',text,vals)
 mode='io' if arm.startswith('IO') else 'oo' if arm=='OO128' else 'base'
 out=dict(workload=workload,arm=arm,attempt_uuid=uuid,cycles=expected,active_thread_instructions=vals['gpu_tot_sim_insn'],ordered_kernels=len(per),
  active_PIB=int(config['-gpgpu_dtc_l1_io_pib_entries' if mode=='io' else '-gpgpu_dtc_l1_oo_pib_entries' if mode=='oo' else '-gpgpu_dtc_l1_pib_entries'][0]),
  lower_cap=int(config['-gpgpu_dtc_l1_lower_outstanding_cap'][0]))
 copy={
 'ready_hit_events':f'DTC_L1_{mode}_valid_hits','pending_merge_events':f'DTC_L1_{mode}_pending_hits',
 'cacheable_new_line_requests':f'DTC_L1_{mode}_lower_created',
 'tag_evictions':f'DTC_L1_{mode}_tag_evictions','duplicate_inflight_after_eviction':'DTC_L1_io_duplicate_after_eviction' if mode=='io' else 'UNAVAILABLE',
 'tag_grant_events':'DTC_L1_io_tag_requests' if mode=='io' else 'DTC_L1_tag_requests' if mode=='base' else 'UNAVAILABLE',
 'tag_quota_reject_events':'DTC_L1_io_tag_conflicts' if mode=='io' else 'DTC_L1_tag_conflicts' if mode=='base' else 'UNAVAILABLE',
 'no_free_physical_events':'DTC_L1_io_no_free_physical_events' if mode=='io' else 'UNAVAILABLE',
 'allocation_width_reject_events':'DTC_L1_io_allocation_width_limited_events' if mode=='io' else 'UNAVAILABLE',
 'PIB_full_events':'DTC_L1_pib_full_events' if mode=='base' else 'UNAVAILABLE',
 'MSHR_entry_reject_events':'DTC_L1_baseline_mshr_entry_full_events' if mode=='base' else 'UNAVAILABLE',
 'MSHR_merge_reject_events':'DTC_L1_baseline_mshr_merge_full_events' if mode=='base' else 'UNAVAILABLE',
 'lower_credit_acquired':'DTC_L1_lower_requests_acquired' if mode=='base' else 'DTC_L1_lower_credit_acquired',
 'lower_credit_released':'DTC_L1_lower_requests_released' if mode=='base' else 'DTC_L1_lower_credit_released',
 'cap_full_events':'DTC_L1_lower_cap_full_events','candidate_queue_reject_events':f'DTC_L1_{mode}_lower_create_queue_full_stalls',
 'global_read_injected':'gpgpu_n_mem_read_global','global_write_injected':'gpgpu_n_mem_write_global',
 'L2_read_sectors':'L2_cache_stats_breakdown[GLOBAL_ACC_R][TOTAL_ACCESS]',
 'L2_read_hits':'L2_cache_stats_breakdown[GLOBAL_ACC_R][HIT]',
 'L2_read_pending_hits':'L2_cache_stats_breakdown[GLOBAL_ACC_R][HIT_RESERVED]',
 'L2_read_misses':'L2_cache_stats_breakdown[GLOBAL_ACC_R][MISS]',
 'L2_read_sector_misses':'L2_cache_stats_breakdown[GLOBAL_ACC_R][SECTOR_MISS]',
 'L2_read_reservation_retries':'L2_cache_stats_breakdown[GLOBAL_ACC_R][RESERVATION_FAIL]',
 'L2_all_accesses':'L2_total_cache_accesses','L2_all_reservation_retries':'L2_total_cache_reservation_fails',
 'ordinary_store_warp_admits':'DTC_L1_m4_store_admits','dynamic_load_warps':'DTC_L1_m4_dynamic_loads',
 'dynamic_store_warps':'DTC_L1_m4_dynamic_stores','dynamic_atomic_warps':'DTC_L1_m4_dynamic_atomics',
 'ordinary_retired_warps':'DTC_L1_m4_observation_retires',
 'L1D_path_accesses':'L1D_total_cache_accesses','L1D_path_misses':'L1D_total_cache_misses',
 'L1D_path_pending':'L1D_total_cache_pending_hits','L1D_path_reservation_retries':'L1D_total_cache_reservation_fails'}
 for key,raw in copy.items():out[key]=vals.get(raw,'UNAVAILABLE')
 for key in ['samples','pib_integral','physical_integral','collected_sectors','retired','fully_ready_to_complete_sum','ready_to_collect_sum','collection_cycles','wb_wait','map_loss_to_free_sum','map_loss_to_free_count']:
  out['service_'+key]=vals.get('DTC_SERVICE_V1_'+key,'UNAVAILABLE')
 for metric,numer,denom in [('mean_PIB_all64_SM_cycles','pib_integral','samples'),('mean_physical_all64_SM_cycles','physical_integral','samples'),('mean_ready_to_complete','fully_ready_to_complete_sum','retired'),('mean_ready_to_collect','ready_to_collect_sum','retired'),('mean_collect','collection_cycles','retired'),('mean_post_collect_WB','wb_wait','retired'),('mean_map_loss_to_free','map_loss_to_free_sum','map_loss_to_free_count')]:
  n=out['service_'+numer];d=out['service_'+denom];out[metric]=n/d if isinstance(n,int) and isinstance(d,int) and d else 'UNAVAILABLE'
 if mode!='base':
  need(out['service_samples']==64*expected,'whole64SM cycle denominator')
  need(out['service_fully_ready_to_complete_sum']==sum(out['service_'+k] for k in ['ready_to_collect_sum','collection_cycles','wb_wait']),'residence decomposition')
  need(out['ready_hit_events']+out['pending_merge_events']+out['cacheable_new_line_requests']==vals['DTC_L1_'+mode+'_completion_dependency_count'],'accepted unique128B references sum')
 need(out['global_read_injected']==out['lower_credit_acquired']==out['lower_credit_released'],'cacheable read path aligns with credit, no extra read class')
 need(out['L2_read_sectors']==4*out['global_read_injected'],'actual same128B read -> four32B L2 requests')
 need(out['L2_read_sectors']==sum(out[k] for k in ['L2_read_hits','L2_read_pending_hits','L2_read_misses','L2_read_sector_misses']),'exclude supplemental MSHR_HIT from total')
 out['L2_read_requested_payload_bytes']=32*out['L2_read_sectors']
 for name in ['n_rd','n_rd_L2_A','n_write','n_wr_bk']:out['DRAM_'+name]=sum(d[name] for d in dram.values())
 atom=int(config['-gpgpu_dram_buswidth'][0])*int(config['-gpgpu_dram_burst_length'][0])*int(config['-gpgpu_n_mem_per_ctrlr'][0])
 out['DRAM_atom_bytes']=atom
 out['DRAM_read_payload_bytes']=(out['DRAM_n_rd']+out['DRAM_n_rd_L2_A'])*atom
 out['DRAM_write_payload_bytes']=(out['DRAM_n_write']+out['DRAM_n_wr_bk'])*atom
 if ps['coverage']=='TERMINAL_COMPLETE':
  need(sum(v for k,v in ps['last_selected'].items() if k.startswith('dram_reads_per_mc_'))==out['DRAM_n_rd']+out['DRAM_n_rd_L2_A'],'DRAM actual command CSV/stdout crosscheck')
  need(sum(v for k,v in ps['last_selected'].items() if k.startswith('dram_writes_per_mc_'))==out['DRAM_n_write']+out['DRAM_n_wr_bk'],'DRAM write command CSV/stdout crosscheck')
 identity.update(raw_stdout=track(p,'accepted raw stdout'),ordered_scope=per,effective_options=config,performance_CSV=ps,raw_counter_units='integer events unless explicitly cycle integral; values cumulative final print, never sum snapshots')
 return out,dict(identity=identity,raw_scalars=vals,dram_final_controller_counters=dram,selected_field_raw_names=copy)

def main():
 PACK.mkdir(parents=True,exist_ok=False)
 need(subprocess.check_output(['hostname'],text=True).strip()=='huangrulin-174','original174')
 need(git(A,'rev-parse','HEAD')=='f5c37d6edcce832a72cb0830021bffa78df6cc13','accepted A head')
 sys.path.insert(0,str(A/'util/dtc_l1'))
 from collect_service_closure_attempts import collect
 need(sha(A/'util/dtc_l1/collect_service_closure_attempts.py')=='a5a1f4018fbfa90b91ad2d3eab4df64f351f905ce74385dbb3a73ec7ca837819','unchanged strong collector')
 for directory,head in [(CORE,'6fba0136f8465b59fe5858a950fa39efb265f654'),(TRAD,'6582b9d171330d88b17e8d5294c97704229e3823'),(FW,'18a68dcccd795f1b6cda75504e9450d00c9cee02')]:need(git(directory,'rev-parse','HEAD')==head,'frozen source HEAD')
 for core in [CORE,TRAD]:
  for name in ['src/gpgpu-sim/gpu-sim.cc','src/gpgpu-sim/shader.cc','src/gpgpu-sim/shader.h','src/gpgpu-sim/dtc-l1-common.h','src/gpgpu-sim/gpu-cache.cc','src/gpgpu-sim/gpu-cache.h','src/gpgpu-sim/dram.cc','src/gpgpu-sim/l2cache.cc','src/gpgpu-sim/mem_latency_stat.cc','src/statistics.h']:
   p=core/name;need(git(core,'hash-object',name)==git(core,'rev-parse','HEAD:'+name),'source bytes frozen');track(p,'frozen statistic implementation')
 for name in ['gpu-simulator/trace-parser/trace_parser.cc','gpu-simulator/trace-parser/trace_parser.h']:track(FW/name,'frozen production parser identity')
 docs=REPO/'docs/dtc_l1/iscas2027/experiment_registry/2026-10-17_mechanism_tuning_v1'
 for name in ['GOAL_M_CPU_ONLY_174.md','SCIENTIFIC_CHARTER_AND_PREREG.md']:track(docs/name,'read authorization')
 plan=table(BASE/'review_pack/r2/REGISTERED_ROWS_V2.tsv');need(len(plan)==44 and sha(BASE/'review_pack/r2/REGISTERED_ROWS_V2.tsv')=='281b2d22ace3bbf105711473516f075fc11c495a1d6c214d9f4a3e42414892e1','original44 immutable')
 holds=read(RAW/'r2-attempts/ROW_ADMISSION_HOLDS.json');need(len(holds['held_labels'])==3,'three holds retained')
 track(RAW/'r2-attempts/HOLD_LAUNCHES','preserved authority-disable token')
 for name in ['README.md','FINAL_INTEGRITY_AUDIT_V1.json','ORIGINAL_INPUT_REVALIDATION.json','CONTRACT_COVERAGE.md','OPEN_SCIENTIFIC_REVIEW_ITEMS.md']:track(BASE/'review_pack/final_closure_v1'/name,'accepted final closure')
 final=read(BASE/'review_pack/final_closure_v1/FINAL_INTEGRITY_AUDIT_V1.json')
 accepted={r['uuid']:r for r in final['original41_full_strict_and_ordered_scope']}
 entries=table(CHECK/'ALL_ATTEMPTS.tsv');bodies=table(BASE/'review_pack/trace_body_v1/KERNEL_BODY_AUDIT.tsv');body={r['path']:r for r in bodies}
 rows=[];evidence=[]
 for workload,arm,uuid,expected in TARGETS:
  matches=[r for r in entries if r['attempt_uuid']==uuid];need(len(matches)==1,'exact UUID index');index=matches[0];run=Path(index['run_dir'])
  start=read(run/'RUN_START.json');spec=read(run/'SPEC.json');need(start['spec']==spec and start['attempt_uuid']==uuid,'raw start/spec identity')
  frozen_path=RAW/'r2-attempts/strict_reviews_v2'/(uuid+'.json');frozen=read(frozen_path)
  need(sha(frozen_path)==accepted[uuid]['strict_sha256'],'final closure strict identity')
  current=collect(run);need(current==frozen['terminal_review'] and current['status']=='PASS_CHECKED_SCOPE','strong read-only recollection')
  need(current['stdout_sha256']==index['stdout_sha256'] and int(current['cycles'])==expected,'accepted UUID/raw identity')
  configs=[]
  for i,c in enumerate(spec['configs']):
   p=run/f'config-{i}.config';need(sha(p)==c['sha256'],'config snapshot');track(p,'accepted effective config');configs.append(p)
  for name in ['RUN_TERMINAL.json','simulator.stderr','resource.time','immutable_runner.py']:track(run/name,'accepted raw identity chain')
  track(run.parent/'binaries'/spec['runtime_sha256']/'accel-sim.out','frozen running binary copy')
  need(sha(Path(spec['runtime']))==spec['runtime_sha256'],'frozen source binary');track(Path(spec['runtime']),'frozen binary')
  track(A/'util/dtc_l1/collect_service_closure_attempts.py','unchanged strong collector')
  need(sha(Path(spec['trace_list']))==spec['trace_list_sha256'],'original list identity');track(Path(spec['trace_list']),'original ordered trace list only; no payload scan')
  identity=dict(uuid=uuid,label=index['label'],run_dir=str(run),kind='FINAL_ACCEPTED_ORIGINAL_R2',strict=track(frozen_path,'final accepted strict'),core=spec['core'],build_framework=spec['build_framework'],binary_sha256=spec['runtime_sha256'],spec_identity=start['identity'],members=spec['members'],trace_list=spec['trace_list'],trace_list_sha256=spec['trace_list_sha256'],trace_payload_SHA_validation='REUSED_A_FINAL_CURRENT_BYTES_PROOF_NO_RESCAN')
  row,ev=extract(run,workload,arm,uuid,expected,identity,options(configs))
  need(ev['identity']['ordered_scope'] and [p['kernel'] for p in ev['identity']['ordered_scope']]==[body[v['path']]['kernel'] for v in spec['members']],'full ordered kernels vs accepted body')
  need([p['instructions'] for p in ev['identity']['ordered_scope']]==[int(body[v['path']]['active_thread_instructions']) for v in spec['members']],'per-kernel complete active instructions')
  rows.append(row);evidence.append(ev)
 baselines=table(BASE/'review_pack/r2/CANONICAL_BASELINE_REUSE.tsv')
 for b in baselines:
  if b['workload']!='BICG':continue
  run=Path(b['run_dir']);strict=read(b['strict_receipt_path']);need(sha(Path(b['strict_receipt_path']))==b['strict_receipt_sha256'] and strict['status']=='PASS' and all(strict['checks'].values()),'accepted baseline strict')
  need(sha(run/'simulator.stdout')==b['stdout_sha256'],'accepted baseline raw SHA')
  start=dict(csv.reader((run/'RUN_START.tsv').open(),delimiter='\t'));end=dict(csv.reader((run/'RUN_TERMINAL.tsv').open(),delimiter='\t'))
  need(start['attempt_uuid']==end['attempt_uuid']==b['attempt_uuid'] and end['stdout_sha256']==b['stdout_sha256'] and end['simulator_exit_status']=='0','baseline identity')
  configs=[]
  for name in ['base_config','overlay_config','trace_config']:
   p=Path(start[name]);need(sha(p)==start[name+'_sha256'],'baseline exact config');configs.append(p);track(p,'accepted baseline config')
  for name in ['RUN_START.tsv','RUN_TERMINAL.tsv','RUN_MANIFEST.tsv','immutable_sg1_campaign.py','simulator.stderr']:track(run/name,'baseline raw wrapper')
  need(sha(run/'immutable_sg1_campaign.py')==start['runner_sha256'] and sha(Path(start['simulator']))==start['simulator_sha256'],'baseline frozen runner/binary')
  arm='C16' if b['variant']=='B16-N' else 'C80';identity=dict(uuid=b['attempt_uuid'],run_dir=str(run),kind='FINAL_EXACT_CANONICAL_REUSE',strict=track(Path(b['strict_receipt_path']),'accepted canonical strict'),core=b['core'],binary_sha256=b['binary_sha256'],trace_list=start['trace_list'],trace_list_sha256=b['trace_list_sha256'],input_members='same original BICG list/member manifest SHA '+start['trace_member_manifest_sha256'])
  row,ev=extract(run,'BICG',arm,b['attempt_uuid'],int(b['cycles']),identity,options(configs));rows.append(row);evidence.append(ev)
 need(len(rows)==9,'fixed nine runs')
 for w in ['GEMM','BICG']:
  group=[(r,e) for r,e in zip(rows,evidence) if r['workload']==w]
  need(len({e['identity']['trace_list_sha256'] for r,e in group})==1,'same original input group')
  need(len({tuple((x['kernel'],x['instructions']) for x in e['identity']['ordered_scope']) for r,e in group})==1,'same full ordered ROI')
 need(rows[4]['active_PIB']==rows[5]['active_PIB']==128,'BICG matched128')
 need(rows[1]['active_PIB']==256 and rows[2]['active_PIB']==128,'GEMM unequal depth explicitly retained')
 authority=read(CHECK/'AUTHORITY_NATURAL_TERMINATION_V2.json');processes=[]
 for pid in [520970,433763,469026]:
  d=Path(f'/proc/{pid}')
  processes.append(dict(pid=pid,present=d.exists(),stat=(d/'stat').read_text() if d.exists() else None))
 locks=[];live_locks=Path('/proc/locks').read_text()
 for name in ['SCOPED_DISPATCH.lock','DISPATCH.lock','STRICT_REVIEW.lock','CRITICAL_LAUNCH.lock']:
  p=RAW/'r2-attempts'/name
  if p.exists():locks.append(dict(path=str(p),inode=p.stat().st_ino,owners=[s for s in live_locks.splitlines() if ':'+str(p.stat().st_ino)+' ' in s],access='stat only; no flock acquisition'))
 save(PACK/'PRECHECK_RECEIPT.json',dict(status='PASS',utc=datetime.now(timezone.utc).isoformat(),host='huangrulin-174',authorization_HEAD=git(REPO,'rev-parse','origin/hrl/iscas2027-dtc-mechanism-tuning-plan-v1'),accepted_A_HEAD=git(A,'rev-parse','HEAD'),execution_branch=git(REPO,'branch','--show-current'),new_isolated_worktree=str(REPO),new_output=str(OUT),duplicate_task_check='no same-name branch/worktree/output/process before creation',authority_history=authority,current_processes=processes,locks=locks,simulator_launches=0,GPU_launches=0,signals=0))
 with (PACK/'EXISTING_RUN_MECHANISM.tsv').open('x') as f:
  wr=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');wr.writeheader();wr.writerows(rows)
 save(PACK/'INPUT_RUN_IDENTITIES.json',dict(status='PASS_ALL_NINE_ACCEPTED_RAW_IDENTITIES_CLOSED',authorization='103c12ca28e0b5fb66f45b905a04108b501f8ec7',accepted_A_HEAD=git(A,'rev-parse','HEAD'),runs=[e['identity'] for e in evidence],DWT2D='NOT_READ_UNTIL_HYPOTHESES_SEALED',candidate_performance_reads=0,trace_payload_reads=0))
 save(PACK/'COUNTER_EVIDENCE.json',dict(status='PASS',runs=evidence,extraction_source=track(Path(__file__),'CPU extraction/proof source')))
 with (PACK/'SOURCE_SHA256.tsv').open('x') as f:
  wr=csv.DictWriter(f,fieldnames=['path','bytes','sha256','role'],delimiter='\t',lineterminator='\n');wr.writeheader();wr.writerows(SOURCES.values())
 print(json.dumps(dict(status='PASS',runs=len(rows),source_files=len(SOURCES),rows=rows)),flush=True)
if __name__=='__main__':
 try:main()
 except Exception as exc:
  p=OUT/'FAIL_STOP.json'
  if not p.exists():save(p,dict(status='FAIL_STOP',error=repr(exc),scientific_data_not_replaced=True))
  raise
