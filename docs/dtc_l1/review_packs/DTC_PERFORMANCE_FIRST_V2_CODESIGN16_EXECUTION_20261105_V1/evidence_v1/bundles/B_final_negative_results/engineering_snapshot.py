#!/usr/bin/env python3
"""Original charged launcher failures: report facts only; no native state writes."""
from pathlib import Path
import argparse,csv,datetime,gzip,hashlib,json,re
D=Path(__file__).resolve().parent
R=Path('/root/data/dtc_perf_first_v2_codesign16_20261105_v1')
REQ='DTC_PERF_FIRST_V2_PHYSICAL_PIB16_20261105_V1'
REG=Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
EPOCH=Path('/root/data/ep_l2_dtc_l1_native_v2/control/CURRENT_SCIENCE_EPOCH.json')
sha=lambda b:hashlib.sha256(b).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def get(p):
 p=Path(p);b=p.read_bytes();return json.loads(b),{'path':str(p),'sha256':sha(b),'bytes':len(b)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,required=True);args=ap.parse_args();out=args.output_dir.resolve();assert out.is_relative_to(D/'snapshots')and not out.exists(),'NEW_OWN_SNAPSHOT_ONLY'
 for _ in range(3):
  reg,rp=get(REG);ep,epp=get(EPOCH)
  if ep['native_registry_sha256']==rp['sha256']:break
 else:raise ValueError('REGISTRY_EPOCH_CAPTURE_RACE')
 q=reg['registered_future_requests'][REQ];m,mp=get(R/'control/MATRIX.fixed.json');points=m['points'];assert len(points)==16 and q['budget']==16 and len(q['consumed'])==16 and q['remaining']==0;assert set(q['admitted_specs'])==set(q['consumed'])=={p['cohort']for p in points};rows=[]
 for p in points:
  c=p['cohort'];cons=q['consumed'][c];ip=R/'control/qualification_ledger'/(c+'.INTENT.json');i,ir=get(ip);d,dr=get(ip.with_name(c+'.DONE.json'));uid=d['uuid'];native=R/'DTC/run/results'/uid;ev,er=get(native/'NATIVE_EXIT.json');assert cons['uuid']==i['uuid']==uid and i['output']==str(native);assert cons['intent_sha256']==ir['sha256']and cons['execution_receipt']==d==ev and d['new_attempt_consumed']==1
  sp=R/'control/specs'/(c+'.json');spec,sr=get(sp);assert sr['sha256']==q['admitted_specs'][c]==p['spec_sha256'];assert spec['input_digest']==p['input_digest']and spec['profile']==p['profile']and spec['expected']==p['expected']
  raw=native/'raw.log.gz';rb=raw.read_bytes();plain=gzip.decompress(rb);assert sha(rb)==d['raw_sha256']and sha(plain)==d['raw_uncompressed_sha256']and len(plain)==d['raw_uncompressed_bytes'];text=plain.decode(errors='replace');pid=native/'NATIVE_SIMULATOR_PID_AND_MAPS.json';trace=native/'actual_file_process_network.log'
  exact=d['launcher_wait_returncode']==127 and d['native_simulator_observed']is False and not pid.exists()and not trace.exists()and len(plain)==236 and str(R/'tools/bin/strace')in text and'error while loading shared libraries:'in text and'No such file or directory'in text and not re.search(r'^\s*(gpu_sim_cycle|gpu_tot_sim_cycle)\s*=',text,re.M)
  assert exact,'UNEXPECTED_FAILURE_CLASS_KEEP_SEPARATE:'+c
  rr=R/'analysis'/(c+'.RESULT.json');formal=None
  if rr.exists():
   res,ref=get(rr);assert res['state']=='FAIL_PERFV2_CODESIGN16_DH_ARCHIVED_NO_RETRY'and res['cycles']is None and res['proof']['performance_accepted']is False and res['uuid']==uid;formal={'source':ref,'state':res['state'],'full_archive_qualification':'NOT_GRANTED_BY_THIS_FACTS_COLLECTOR'}
  row=dict(program=p['program'],suite=p['suite'],input_digest=p['input_digest'],profile=p['profile'],cohort=c,uuid=uid,intent=ir,DONE=dr,NATIVE_EXIT=er,canonical_spec=sr,registered_consumption={'intent_sha256':cons['intent_sha256'],'uuid':cons['uuid'],'new_attempt_consumed':d['new_attempt_consumed']},raw_gzip={'path':str(raw),'bytes':len(rb),'sha256':sha(rb)},raw_plain_bytes=len(plain),raw_plain_sha256=sha(plain),raw_stderr=text,launcher_returncode=d['launcher_wait_returncode'],native_simulator_observed=d['native_simulator_observed'],simulator_PID_metadata_exists=pid.exists(),strace_file_exists=trace.exists(),launcher_elapsed_seconds=d['elapsed_seconds'],peak_observed_process_tree_rss_bytes=d['peak_observed_rss_bytes'],configured_launcher_parent_flag_preserved=d['launcher_is_strace_parent_of_native_simulator'],configured_parent_flag_is_not_observed_simulator_evidence=True,engineering_classification='LauncherMissingStrace',formal_negative_RESULT=formal,cycles=None,S_combo=None,R_combo=None,I=None,J=None,kernel_or_population_or_guard_performance_evidence='UNAVAILABLE_NO_SIMULATOR_OBSERVED')
  rows.append(row)
 summary=dict(schema='DTC_CODESIGN16_LAUNCHER_FAILURE_FACTS_V1',request=REQ,observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),planned_cells=16,program_inputs=8,uniform_profiles=2,native_attempt_identities_consumed=16,remaining_budget=0,observed_simulator_processes=0,valid_performance_points=0,performance_coverage='0/16',engineering_launcher_negatives=16,formal_FAIL_RESULT_files_present=sum(r['formal_negative_RESULT']is not None for r in rows),archived_negative_verification='REQUIRES_SEPARATE_SOURCE_QUALIFIED_NEGATIVE_ARCHIVE_CONSUMER',uniform_statistics={p:{'planned_n':8,'accepted_n':0,'GM_S_combo':None,'GM_R_combo':None,'GM_J':None,'positive_performance_n':None,'negative_performance_n':None,'zero_performance_n':None,'display':'N/A_NO_ACCEPTED_PERFORMANCE','engineering_negative_n':8}for p in sorted({r['profile']for r in rows})},P0_reruns=0,automatic_retries=0,refunds=0,new_models_or_requests_by_collector=0,all_performance_values_null=True,failure_does_not_establish_architecture_ineffectiveness=True)
 receipt=dict(registry=rp,epoch=epp,matrix=mp,request=REQ,registered_budget=q['budget'],consumed=len(q['consumed']),remaining=q['remaining'],registered_state=q['state'],registered_plan_sha256=q['execution_plan_sha256'],registered_outbox_sha256=q['outbox_sha256'],registered_engine_sha256=q['engine_sha256'],old_V1_data_not_replaced=True)
 out.mkdir(parents=True)
 def emit(n,v):(out/n).write_text(json.dumps(v,indent=2)+'\n')
 emit('SUMMARY.json',summary);emit('ORIGINAL16_FAILURE_FACTS.json',rows);emit('SOURCE_CAPTURE.json',receipt)
 with(out/'ORIGINAL16_FAILURE_FACTS.csv').open('w',newline='')as f:
  fs=['program','suite','input_digest','profile','cohort','uuid','launcher_returncode','native_simulator_observed','raw_plain_bytes','raw_plain_sha256','simulator_PID_metadata_exists','strace_file_exists','cycles','S_combo','R_combo','I','J'];w=csv.DictWriter(f,fieldnames=fs,extrasaction='ignore');w.writeheader();w.writerows(rows)
 files=[dict(name=p.name,path=str(p),bytes=p.stat().st_size,sha256=sha(p.read_bytes()))for p in sorted(out.iterdir())if p.is_file()];emit('MANIFEST.json',dict(schema='DTC_CODESIGN16_ORIGINAL_ENGINEERING_FACTS_MANIFEST_V1',files=files,new_models=0,registry_writes=0,native_writes=0));print(json.dumps({'output':str(out),'manifest_sha256':sha((out/'MANIFEST.json').read_bytes()),'summary':summary}))
if __name__=='__main__':main()
