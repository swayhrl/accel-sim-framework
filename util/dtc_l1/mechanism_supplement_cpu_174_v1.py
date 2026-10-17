#!/usr/bin/env python3
"""CPU evidence supplement recipes; exclusive outputs, never run a simulator.

The hypothesis/holdout/derived recipes preserve the commands used in this
delivery. Replays require fresh output roots; never overwrite accepted raw.
"""
import argparse,csv,json
from datetime import datetime,timezone
from pathlib import Path
import sys
import mechanism_consumer_cpu_174_v1 as m

def update_sources():
 p=m.PACK/'SOURCE_SHA256.tsv';old={r['path']:r for r in csv.DictReader(p.open(),delimiter='\t')};old.update(m.SOURCES)
 with p.open('w') as f:
  w=csv.DictWriter(f,fieldnames=['path','bytes','sha256','role'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(old.values())
def hypothesis():
 m.save(m.PACK/'HYPOTHESIS_FREEZE.json',dict(status='FROZEN_BEFORE_DWT2D_RAW_READ',utc=datetime.now(timezone.utc).isoformat(),hypotheses_sha256=m.sha(m.PACK/'HYPOTHESES_PRE_HOLDOUT.md'),primary_raw_evidence_sha256=m.sha(m.PACK/'COUNTER_EVIDENCE.json'),primary_run_table_sha256=m.sha(m.PACK/'EXISTING_RUN_MECHANISM.tsv'),DWT2D_raw_reads_so_far=0,new_candidate_performance_reads=0))
def holdout():
 freeze=json.loads((m.PACK/'HYPOTHESIS_FREEZE.json').read_text());m.need(m.sha(m.PACK/'HYPOTHESES_PRE_HOLDOUT.md')==freeze['hypotheses_sha256'],'sealed hypothesis')
 entries=m.table(m.CHECK/'ALL_ATTEMPTS.tsv');accepted={r['uuid']:r for r in m.read(m.BASE/'review_pack/final_closure_v1/FINAL_INTEGRITY_AUDIT_V1.json')['original41_full_strict_and_ordered_scope']};results=[]
 sys.path.insert(0,str(m.A/'util/dtc_l1'));from collect_service_closure_attempts import collect
 for arm,label,expected in [('C+','R2_COHORT_TRAD96_DWT2D',247588),('OO128','R2_V2_COHORT_OO_DWT2D',237887)]:
  matches=[r for r in entries if r['label']==label];m.need(len(matches)==1,'accepted DWT2D label');row=matches[0];uuid=row['attempt_uuid'];run=Path(row['run_dir']);p=m.RAW/'r2-attempts/strict_reviews_v2'/(uuid+'.json');strict=m.read(p)
  m.need(m.sha(p)==accepted[uuid]['strict_sha256'] and collect(run)==strict['terminal_review'] and row['status']=='PASS_CHECKED_SCOPE','DWT2D old strict identity')
  start=m.read(run/'RUN_START.json');spec=start['spec'];cfg=[]
  for i,c in enumerate(spec['configs']):
   q=run/f'config-{i}.config';m.need(m.sha(q)==c['sha256'],'DWT2D config');m.track(q,'DWT2D old accepted config');cfg.append(q)
  for name in ['RUN_TERMINAL.json','SPEC.json']:m.track(run/name,'DWT2D old accepted identity')
  ident=dict(uuid=uuid,label=label,core=spec['core'],binary_sha256=spec['runtime_sha256'],trace_list_sha256=spec['trace_list_sha256'],members=spec['members'],strict=m.track(p,'old accepted DWT2D strict'))
  out,ev=m.extract(run,'DWT2D',arm,uuid,expected,ident,m.options(cfg));results.append(dict(row=out,evidence=ev))
 m.need(results[0]['evidence']['identity']['trace_list_sha256']==results[1]['evidence']['identity']['trace_list_sha256'] and results[0]['row']['active_thread_instructions']==results[1]['row']['active_thread_instructions'],'DWT2D full same input')
 m.save(m.PACK/'DWT2D_READONLY_CHECK.json',dict(status='PASS_OLD_ACCEPTED_HOLDOUT_ONLY_NOT_SELECTION',utc=datetime.now(timezone.utc).isoformat(),hypothesis_freeze_sha256=m.sha(m.PACK/'HYPOTHESIS_FREEZE.json'),results=results,new_candidate_performance_reads=0,new_runs=0,primary_metric_table_unchanged=m.sha(m.PACK/'EXISTING_RUN_MECHANISM.tsv')==freeze['primary_run_table_sha256']))
 update_sources()
def derived():
 rows=list(csv.DictReader((m.PACK/'EXISTING_RUN_MECHANISM.tsv').open(),delimiter='\t'));by={(r['workload'],r['arm']):r for r in rows};result=[]
 for workload,a,b in [('GEMM','C+','OO128'),('GEMM','IO256','OO128'),('BICG','C+','OO128'),('BICG','IO128','OO128'),('BICG','C16','C80'),('BICG','C16','WAIT128')]:
  x,y=by[workload,a],by[workload,b];metrics={}
  for k in ['cycles','global_read_injected','L2_read_requested_payload_bytes','L2_read_hits','L2_read_reservation_retries','DRAM_read_payload_bytes']:
   old,new=int(x[k]),int(y[k]);metrics[k]=dict(reference=old,comparison=new,delta=new-old,comparison_over_reference=new/old if old else 'UNDEFINED_ZERO_DENOMINATOR')
  result.append(dict(workload=workload,reference_arm=a,comparison_arm=b,reference_uuid=x['attempt_uuid'],comparison_uuid=y['attempt_uuid'],metrics=metrics,scope='DESCRIPTIVE_SAME_ORIGINAL_INPUT_NOT_SINGLE_FACTOR_CAUSAL_CONTRIBUTION'))
 m.save(m.PACK/'DERIVED_COMPARISONS.json',dict(comparisons=result,new_performance_reads=0))
 evidence=json.loads((m.PACK/'COUNTER_EVIDENCE.json').read_text())['runs'];checks=[]
 for e in evidence:
  ident=e['identity'];v=e['raw_scalars'];text=(Path(ident['run_dir'])/'simulator.stdout').read_text();snaps=[m.scalar(s) for s in m.snapshots(text)];monotone=[]
  for key in ['gpgpu_n_mem_read_global','gpgpu_n_mem_write_global','L2_cache_stats_breakdown[GLOBAL_ACC_R][HIT]','L2_cache_stats_breakdown[GLOBAL_ACC_R][TOTAL_ACCESS]','DTC_SERVICE_V1_samples','DTC_SERVICE_V1_retired','DTC_SERVICE_V1_pib_integral']:
   vals=[s[key] for s in snaps if key in s];m.need(all(b>=a for a,b in zip(vals,vals[1:])),'cumulative counter windows');monotone.append(dict(field=key,snapshots=vals))
  m.need(v.get('gpgpu_n_mem_read_local',0)==v.get('DTC_L1_m4_dynamic_atomics',0)==v.get('DTC_L1_m4_bypass_load_admits',0)==0,'read scope classes')
  checks.append(dict(uuid=ident['uuid'],kernel_count=len(snaps),counter_monotonicity=monotone,no_local_read_atomic_or_DTC_bypass_recorded=True))
 m.save(m.PACK/'SCOPE_AND_SAMPLING_AUDIT.json',dict(status='PASS',runs=checks,source_counter_objects='lifetime/stream totals; shader/DRAM objects persist; clear_pw only resets power counters',scope='no sum of cumulative snapshots; independent full per-kernel active instruction check in INPUT_RUN_IDENTITIES'))
def postcheck():
 src=list(csv.DictReader((m.PACK/'SOURCE_SHA256.tsv').open(),delimiter='\t'))
 for r in src:
  p=Path(r['path']);m.need(p.stat().st_size==int(r['bytes']) and m.sha(p)==r['sha256'],'source/raw postcheck identity: '+str(p))
 pre=json.loads((m.PACK/'PRECHECK_RECEIPT.json').read_text())
 for lock in pre['locks']:m.need(Path(lock['path']).stat().st_ino==lock['inode'],'lock inode preserved')
 m.need(m.git(m.A,'rev-parse','HEAD')==pre['accepted_A_HEAD'],'A unchanged')
 freeze=json.loads((m.PACK/'HYPOTHESIS_FREEZE.json').read_text())
 for name,key in [('HYPOTHESES_PRE_HOLDOUT.md','hypotheses_sha256'),('EXISTING_RUN_MECHANISM.tsv','primary_run_table_sha256'),('COUNTER_EVIDENCE.json','primary_raw_evidence_sha256')]:m.need(m.sha(m.PACK/name)==freeze[key],'hypothesis/primary data unchanged after holdout')
 m.save(m.PACK/'POSTCHECK_RECEIPT.json',dict(status='PASS',utc=datetime.now(timezone.utc).isoformat(),source_and_raw_files_rehashed=len(src),A_HEAD=m.git(m.A,'rev-parse','HEAD'),original44_and_HOLD_and_binary_and_Core_and_parser_unchanged=True,hypotheses_and_primary_data_unchanged=True,lock_inodes_unchanged=True,lock_acquisitions=0,process_control_calls=0,simulator_runs=0,GPU_runs=0,new_candidate_performance_reads=0,trace_payload_rescan=0,T_launch_authority='NONE_IN_M'))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['hypothesis','holdout','derived','postcheck']);a=ap.parse_args();globals()[a.phase]();print(a.phase,'PASS')
if __name__=='__main__':main()
