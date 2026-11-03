from pathlib import Path
import sys,json,hashlib,importlib.util

def register(group,manifest_path,nativeq_path):
 assert group in ['system','highclock']
 manifest=json.loads(Path(manifest_path).read_text());g=manifest['groups'][group]
 sys.path.insert(0,g['runtime_root'])
 import ep_perf_common_v2 as c
 assert c.GOAL==g['request_id'] and str(c.ROOT)==g['data_root']
 nq=c.read(nativeq_path)
 assert nq['status']=='MAIN_REVIEWED_PFV2_SCOPED_NATIVE_REGISTRATION_QUALIFIED' and nq['approved_by']=='EP-MAIN'
 assert nq['manifest_ref']==c.ref(manifest_path) and nq['entry_ref']==g['native_entry_ref']==c.ref(c.ROOT.parent/'bin/native')
 assert c.sha(c.NATIVE/'bin/native')==manifest['shared_native_ref']['sha256']
 points=[p for p in manifest['points']if p['group']==group];budget={'system':12,'highclock':6}[group]
 assert len(points)==budget==g['budget'] and len({p['cohort']for p in points})==budget
 specs=[c.exact(p['spec_ref'])for p in points]
 for p,s in zip(points,specs):
  assert s['science_request_id']==c.GOAL and s['cohort']==p['cohort']
  assert p['spec_ref']['path']==str(c.ROOT/'cases'/s['cohort']/'control/FROZEN_SPEC.json')
  assert s['source_identity']==specs[0]['source_identity']
  assert s['native_entry_ref']==g['native_entry_ref']
  c.module(s['mode_contract_ref'],'Main_registration_formal_mode').validate_static(s)
  for f,h in s['pinned_files'].items():assert c.sha(f)==h,f
  assert c.sha(s['binary_path'])==s['source_identity']['binary_sha256']
  assert c.sha(s['static_library_path'])==s['source_identity']['archive_sha256']
  e=c.exact(s['eligibility_ref']);assert e['status']=='MAIN_REVIEWED_EP_COMPLETE_INPUT_ELIGIBLE' and s['mode']in e['modes_qualified'] and e['source_identity']==s['source_identity'] and e['input_identity_sha256']==s['input_identity_sha256']
 auth=c.exact(g['authorization_ref']);assert auth['goal']==c.GOAL and auth['budget']==budget and auth['user_request_ref']==c.ref(c.ROOT/'control/USER_REQUEST.txt')
 assert auth['review_commit']=='14b2eead02e70cdf39fa2a6cd5e53a48f1590559' and auth['NI_additional']==0
 q=dict(request=c.GOAL,owner='EP-MAIN',project='EP_L2',state='REGISTERED_EXACT_USER_AUTHORIZED_FAMILY',budget=budget,remaining=budget,consumed={},admitted_specs={p['cohort']:p['spec_ref']['sha256']for p in points},authorization_ref=g['authorization_ref'],Main_manifest_ref=c.ref(manifest_path),native_entry_ref=g['native_entry_ref'],native_qualification_ref=c.ref(nativeq_path),source_identity=specs[0]['source_identity'],source_keep=True,automatic_retry=False,refund=False,reserved_write_bytes=0,resource_group_id=c.GOAL,runtime_versions={s['host_engine_ref']['sha256']:dict(engine_ref=s['host_engine_ref'],common_ref=s['host_common_ref'])for s in specs})
 def add(reg):
  assert c.GOAL not in reg['registered_future_requests'],'Already registered; never duplicate budget'
  reg['registered_future_requests'][c.GOAL]=q
 before=c.ref(c.REG);epochbefore=c.ref(c.EPOCH)
 c.transaction('REGISTER_NEW_APPROVED_PFV2_EXACT_FAMILY_NO_MODEL_START',add)
 reg,ep=c.authority();assert reg['registered_future_requests'][c.GOAL]==q
 receipt=dict(schema='EP_MAIN_PFV2_FRESH_FAMILY_REGISTRATION_V1',status='REGISTERED_EXACT_QUALIFIED_FAMILY_NO_START',utc=c.now(),science_request_id=c.GOAL,budget=budget,scientific_starts=0,foreign_rows_preserved=True,old_source_history_preserved=True,old_HOLD_budget_reused=False,manifest_ref=c.ref(manifest_path),native_qualification_ref=c.ref(nativeq_path),native_entry_ref=g['native_entry_ref'],prior_registry_ref=before,prior_epoch_ref=epochbefore,new_registry_ref=c.ref(c.REG),new_epoch_ref=c.ref(c.EPOCH))
 c.put(Path(manifest['control_root'])/('REGISTRATION_'+group.upper()+'.json'),receipt,True)
 print(json.dumps(receipt))
if __name__=='__main__':
 assert len(sys.argv)==4
 register(*sys.argv[1:])
