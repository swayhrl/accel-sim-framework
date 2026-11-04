#!/usr/bin/env python3
"""Independent read-only exact16 launcher-negative archive witness. Never runs models."""
from pathlib import Path
import argparse,datetime,gzip,hashlib,json,os,sys,types
sys.dont_write_bytecode=True
P=Path
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_codesign16_execution_20261105_v1')
R=P('/root/data/dtc_perf_first_v2_codesign16_20261105_v1')
N=P('/root/data/ep_l2_dtc_l1_native_v2')
D=A/'agents/D_independent_review_v1'
REQ='DTC_PERF_FIRST_V2_PHYSICAL_PIB16_20261105_V1'
def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def put(p,v):
 with P(p).open('xb')as f:f.write((json.dumps(v,indent=2)+'\n').encode());f.flush();os.fsync(f.fileno())
def load(p,name):
 m=types.ModuleType(name);m.__file__=str(p);exec(compile(P(p).read_bytes(),str(p),'exec'),m.__dict__);return m
def retained(aw,m,out):
 for e in m['entries']:
  p=aw.exact_safe(out,e['path']);assert p.lstat().st_dev==2128
  if e['type']=='file':assert p.is_file()and not p.is_symlink()and p.stat().st_size==e['size']and sha(p)==e['sha256']
  elif e['type']=='directory':assert p.is_dir()and not p.is_symlink()
  elif e['type']=='symlink':assert p.is_symlink()and os.readlink(p)==e['target']
  else:raise ValueError('UNSUPPORTED_ENTRY_TYPE')
 return len(m['entries'])
def audit(manifest_sha,outname):
 out=(D/outname);assert out.parent==D and not out.exists();out.mkdir();checks=[]
 def ck(n,v):checks.append(dict(check=n,PASS=bool(v)));assert v,n
 put(out/'AUDIT_INVOKED.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope=REQ,read_only=True,new_models=0,archive_or_restore_writes=0,one_shot=True))
 try:
  S=A/'engineering_incidents/launcher_runtime_missing_v1/negative_archive_forward_v1';mp=S/'MANIFEST.json';ck('Frozen independently reviewed negative archiver manifest',sha(mp)==manifest_sha)
  for f in read(mp)['files']:
   rel=f.get('path',f.get('name'));p=S/rel;ck('Negative package source evidence '+rel,sha(p)==f['sha256'])
  adapter=S/'archive_launcher_negatives.py';adsha=sha(adapter);bpack=A/'agents/B_results_v1/forward_v2';witness=bpack/'archive_witness.py';expected=next(x for x in read(bpack/'MANIFEST.json')['files']if x.get('path',x.get('name'))=='archive_witness.py')['sha256'];ck('Reviewed independent archive witness source',sha(witness)==expected);aw=load(witness,'D_NEGATIVE_ARCHIVE_WITNESS')
  diagp=D/'phase2_engineering_negative_review_v1/CLOSED16_RAW_DIAGNOSIS.json';ck('Original all16 closed diagnosis preserved',sha(diagp)=='455b5a73be7f4cee1272561ff04742ea7e5e4bfcec752f0440cd2bc911a3ecb9');diag={r['cohort']:r for r in read(diagp)['rows']}
  reg=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');q=reg['registered_future_requests'][REQ];ck('Exact16 all charged no refunds no remaining',q['budget']==len(q['consumed'])==16 and q['remaining']==0 and set(q['consumed'])==set(q['admitted_specs'])==set(diag));ck('No automatic model retries',q['model_automatic_retries']==0)
  rows=[];proofs=[];uuids=[]
  absent=['NATIVE_SIMULATOR_PID_AND_MAPS.json','SIM_PID','SIM_PID.json','actual_file_process_network.log','L2_STRICT.json']
  for co,c in sorted(q['consumed'].items()):
   old=diag[co];u=c['uuid'];uuids.append(u);ip=R/'control/qualification_ledger'/(co+'.INTENT.json');dp=ip.with_name(co+'.DONE.json');i=read(ip);d=read(dp);src=R/'DTC/run/results'/u;sp=R/'control/specs'/(co+'.json');resultp=R/'analysis'/(co+'.RESULT.json');r=read(resultp)
   ck('Original UUID charge INTENT DONE retained '+co,u==old['uuid']and c['charged']==1 and sha(ip)==old['source_pins']['INTENT']['sha256']==c['intent_sha256']and sha(dp)==old['source_pins']['DONE']['sha256']and d==c['execution_receipt']==read(src/'NATIVE_EXIT.json')and i['uuid']==u)
   ck('Original intended input config source unchanged '+co,sha(sp)==old['source_pins']['canonical_spec']['sha256']and q['admitted_specs'][co]==sha(sp))
   ck('Actual no simulator launcher127 not scientific failure '+co,d['native_simulator_observed']is False and d['launcher_wait_returncode']==127 and all(not(src/x).exists()for x in absent))
   raw=gzip.decompress((src/'raw.log.gz').read_bytes());ck('Original closed raw236 exact retained '+co,sha(src/'raw.log.gz')==old['source_pins']['raw_gzip']['sha256']==d['raw_sha256'] and len(raw)==236 and raw.decode().strip()==old['raw_error_literal'])
   ck('Closed engineering negative result no cycles '+co,r['cohort']==co and r['uuid']==u and r['cycles']is None and r['proof']['performance_accepted']is False and r['proof']['accepted_cycles']is None and r['proof']['native_simulator_observed']is False and r['proof']['returncode']==127 and r['state']=='FAIL_PERFV2_CODESIGN16_DH_ARCHIVED_NO_RETRY')
   scope=r['engineering_source_scope'];ck('Actual independent adapter provenance separate registered outbox '+co,scope['actual_negative_archive_adapter_sha256']==adsha and scope['actual_negative_archive_adapter_path']==str(adapter)and scope['original_registered_outbox_sha256']==q['outbox_sha256']=='2b55983c9b3f974e97d6deaac573a0ef0a27fbced28d75eccdfa96465088df20'and r['archive']['archive_overlay_sha256']==adsha and r['engineering_source_scope_status']=='FORWARD_NEGATIVE_ARCHIVE_ONLY_NOT_ORIGINAL_REGISTERED_OUTBOX')
   refs,proof=aw.verify_for(R,A/'results','UNUSED_POSITIVE_STRICT_STATUS',co,r,src,d,False,adsha,True);target=P(r['archive']['receipt']['target_mount_path']);m=read(target/'SOURCE_MANIFEST.json');restore=P(r['archive']['receipt']['native_restore']);n=retained(aw,m,src)
   ck('Full true164 stream all native restored and retained entries '+co,proof['native_restored_entries_verified']==n==len(m['entries']))
   ck('No fabricated missing PID trace strict archive members '+co,not set(absent)&{e['path']for e in m['entries']}and all(not(restore/x).exists()for x in absent))
   ck('Actual archiver source copied byte exact '+co,sha(target/'negative_archive_adapter.py')==adsha and read(target/'NEGATIVE_ARCHIVE_ENGINEERING_SCOPE.json')==scope and m['engineering_source_scope']==scope)
   launcher=read(src/'NATIVE_LAUNCH.json');ck('No live failed launcher '+co,not P('/proc',str(launcher['launcher_pid'])).exists())
   for f in ['RESOURCE_SAMPLES.jsonl.gz','progress.jsonl.gz']:ck('Actual empty telemetry preserved no fabricated measurements '+co+' '+f,gzip.decompress((src/f).read_bytes())==b'')
   entries={e['path']for e in m['entries']};actual={'.',*(p.relative_to(src).as_posix()for p in src.rglob('*'))};extra=sorted(actual-entries)
   rows.append(dict(cohort=co,uuid=u,program=old['program'],suite=old['suite'],profile=old['profile'],input_digest=old['input_digest'],intended_config_sha256s=[x['sha256']for x in old['intended_configs']],classification='ARCHIVED_ENGINEERING_NEGATIVE_LAUNCHER_LAYOUT_NO_SIMULATOR',charged=1,launcher_returncode=127,actual_simulator_observed=False,performance_accepted=False,cycles=None,S_combo=None,R_combo=None,I=None,J=None,GM_eligible=False,raw_gzip_sha256=d['raw_sha256'],raw_uncompressed_sha256=d['raw_uncompressed_sha256'],result=dict(path=str(resultp),sha256=sha(resultp)),archive_receipt=refs['ARCHIVE_RECEIPT'],full_archive_stream_sha256=proof['archive_stream_sha256'],native_restore=refs['NATIVE_RESTORE'],all_archive_restored_and_SOURCE_KEEP_entries=n,source_extras_not_in_snapshot=extra))
   proofs.append(dict(cohort=co,uuid=u,refs=refs,full_archive_restore_verification=proof))
  ck('16 UUIDs unique no tombstone reuse',len(set(uuids))==16 and not set(uuids)&{'2a6e4b2a-a060-4817-8c44-fa3577e5ef37','aca642eb-5914-4151-bafd-3b64ba18d2c2'})
  profiles={p:dict(n_candidates=8,engineering_negative=8,accepted=0,metric_valid_n=0,missing=8,positive=None,negative=None,zero_response=None,GM_S_combo=None,GM_R_combo=None,GM_I=None,GM_J=None)for p in sorted({r['profile']for r in rows})};ck('Two uniform profiles fixed8 missing not zero',len(profiles)==2 and all(sum(r['profile']==p for r in rows)==8 for p in profiles))
  report=dict(schema='DTC_D_CODESIGN16_FINAL_ENGINEERING_NEGATIVE_REVIEW_V1',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='PASS_ALL16_ARCHIVED_ENGINEERING_NEGATIVES_NOT_PERFORMANCE_ACCEPTED',checks=checks,authority_commit='320b1365902a72502fa61ba114cb4a4a28b934bb',request=REQ,request_terminal_metadata_seen=q.get('state'),budget=16,consumed=16,remaining=0,actual_simulator_observed_count=0,accepted_performance_count=0,archived_engineering_negative_count=16,profiles=profiles,common_accepted_inputs=[],common_J_complete_term_inputs=[],rows=rows,negative_archive_source_manifest=dict(path=str(mp),sha256=sha(mp)),independent_archive_witness=dict(path=str(witness),sha256=sha(witness)),new_scientific_starts_or_retries_or_native_actions_by_D=0,archive_or_restore_writes_by_D=0,causal_inference_from_these16=False,new16_scientific_attempts_require_new_explicit_user_authorization=True,limits=['All16 are legitimate charged launcher attempts; loader failed before simulator observation. They are not physical/PIB correctness or performance failures.','No runtime option echo, actual guard/lifecycle check, cycles, counters or kernel phases exist for these16. Intended frozen configuration is not claimed actual simulator effective configuration.','True164 integrity and native recovery certify retained engineering evidence, not performance acceptance.','Prior CPU qualifications and their missed launcher/real-lock coverage remain preserved; this review does not erase engineering incidents.','Goal and manuscript completion are Root/user decisions; no v0.23 edit or promotion.'])
  put(out/'FINAL_REVIEW.json',report);put(out/'FULL_ARCHIVE_RESTORE_SOURCE_WITNESSES.json',proofs);put(out/'CHECKS.json',checks)
  text='# Independent exact16 engineering-negative closure\n\nAll16 authorized identities were charged exactly once. All16 launchers returned127 before a simulator was observed because the new execution root lacked the tracer path. Accepted performance results:0. Both fixed8 profiles have missing cycles/S/R/I/J for all8; GM is NA. These are engineering negatives, not cache-design regressions.\n\nAll16 true164 archive chunks/full streams, every native restored typed entry and every retained original source entry were independently verified. Missing PID, trace, strict and counter evidence was not fabricated. The new negative-only archive adapter has its own explicit source identity, separate from the original registered outbox.\n\nNo old UUID or consumed credit may be reused. The missing launcher directories were separately repaired and CPU-qualified; any new16 scientific attempts require new explicit authorization. Old evidence and CPU coverage gaps remain preserved.\n'
  with(out/'REPORT.md').open('x')as f:f.write(text)
  members=[dict(path=p.name,bytes=p.stat().st_size,sha256=sha(p))for p in sorted(out.iterdir())if p.is_file()];put(out/'MANIFEST.json',dict(schema='DTC_D_FINAL_ENGINEERING_NEGATIVE_PUBLIC_MANIFEST_V1',files=members))
  print(json.dumps(dict(status=report['status'],checks=len(checks),rows=16,performance_accepted=0,review_sha256=sha(out/'FINAL_REVIEW.json'),manifest_sha256=sha(out/'MANIFEST.json'))))
 except BaseException as e:
  put(out/'HOLD_NO_AUTOMATIC_RETRY.json',dict(error=repr(e),checks=checks,new_models_or_archive_writes=0));raise
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--negative-adapter-manifest-sha256',required=True);p.add_argument('--output-name',required=True);a=p.parse_args();audit(a.negative_adapter_manifest_sha256,a.output_name)
