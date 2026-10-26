#!/usr/bin/env python3
"""Read-only fresh EP lifetime resource reference aligned to exact pinned R19-to-R20 continuation. Never grants science authority.

Only local metadata/PID/RSS and statvfs are read. No imports of actor engines,
leases, subprocesses, asset scans, controller calls, writes or cleanup.
"""
import argparse
import datetime
import hashlib
import json
import os
import stat
from pathlib import Path

G=1<<30
M=1<<20
N=Path('/root/data/ep_l2_dtc_l1_native_v2')
T=Path('/root/data/dtc_main_v100_sweep_20261025_v1')
F=Path('/root/data/dtc_failure_repair_20261025_v1')
REG=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json'
EPOCH=N/'control/CURRENT_SCIENCE_EPOCH.json'
MAIN='DTC_AE_V100_FULL_SWEEP_20261025_V1'
ROOTS={MAIN:T,
 'DTC_AE_FAILURE_REPAIR_VALIDATION_20261025_V1':F/'validation',
 'DTC_AE_LAVAMEM_REPAIR_20261026_V2':F/'validation_lava_memory_v2',
 'DTC_AE_LATE_FAILURE_REPAIR_20261026_V1':F/'validation_late_failure_v1',
 'DTC_AE_REMAINING_FAILURE_REPAIR_20261026_V1':F/'validation_remaining_failure_v1'}
TERMINAL={'COMPLETE','CLOSED','STOP_UNACCEPTED','COMPAT_PARTIAL_COMPLETE','CANCELLED','SEALED'}
RECOVERY='DTC_AE_STORAGE_RECOVERY12_20261026_V1'
RECOVERY_ROOT=F/'validation_storage_recovery12_v1'
ROOTS[RECOVERY]=RECOVERY_ROOT
BASE_RESOURCE=Path('/root/data/ep_tag_reservation_lifetime_20261026_v1/tools/resource_snapshot.py')
BASE_RESOURCE_SHA='3074ba6467bb192160e199b49fc8448f46d78ae4c2a18c82c63894511961fe80'
R20_CONTROLLER=F/'ops/revision20/sweep_controller.py'
R20_CONTROLLER_SHA='de715b527c6194a65b30d0b921c34a26bc8af4433eddd78c957d98c123723c81'
R20_OVERLAY=F/'ops/revision20/resource_accounting_v1.py'
R20_OVERLAY_SHA='e9c864c109ea4e87521713246e5a1602d95da5413861cc7f34be100180ee866e'
R20_POLICY=F/'control/R20_RESOURCE_ACCOUNTING_POLICY_V1.json'
R20_POLICY_SHA='9fe20c76465e307d1807e57cd97d8029f50db9cd70fa3cb1348b6a89748facb9'
R20_PLAN_SHA='1741bf968d8aa9f5b48897a978c123aba59d1df1ca830831351107c83fa8b834'
R20_ENGINE_SHA='1ecee0c0150c4a015b4b7242b9e6c71f261ef81a05189d51e43030dfcda93864'
R20_BEFORE_MAIN_SHA='a83278a2805fdad663de547fba4813599f5d25d4179154928b1d5f5ba5660b57'
R20_BEFORE_FOUR_SHA='ac28bb5db45e3a72cd46f227fb41a89bf0fd0504439fb55a0eaf8ce0fa152560'
R19_OVERLAY=F/'ops/revision19/resource_accounting_v1.py'
R19_POLICY=F/'control/R19_RESOURCE_ACCOUNTING_POLICY_V1.json'
REMAIN='DTC_AE_REMAINING_FAILURE_REPAIR_20261026_V1'
R19_OVERLAY_SHA='a34eeb5a57229ac2189d17cc7c37b07cc06e86c228168dfdff540d52c396f00f'
R19_POLICY_SHA='295b15531fe06ffc0e6e9420e7ba15f5e4b2135b5d8c3335529dcc1e175fb31d'
R19_PLAN_SHA='3af7771c5b7f0c7e5c859677905a52fa6d7817872c88955b1ad29d3dde7412bc'
R19_CONTROLLER_SHA='c4cc1f48e404f949afb5bfe942044031bfc6650fe6f4032b97757b370f82f532'
GHOST_CERT=F/'ops/revision17/THREE_DEPARTED_ORIGINAL_RAM_CERTIFICATE_V1.json'
GHOST_CERT_SHA='cd86d9cb2609a968310937fcdf6c24764897c23e7dc2516e9be4bb6701b4be42'
GHOST_VERIFIER=F/'ops/revision17/admission_resource_adapter_v1.py'
GHOST_VERIFIER_SHA='decbfc33d5741d48721262aea235c45ef3af22321f78054a20ab400952f29520'
CLOSED_CERT_SHA='6cd77f85067c13b261f06d2414d328a20f515096cfe015ebda17e13dfc0dd4ba'
GHOST_ALLOWED={'E2-AEV100-09f94fcc7494a03b-CM':'df5fda68-3c3d-4b37-844f-d7ea6a1d5293','E2-AEV100-85700545918390d7-DM':'97c43b01-9628-490f-839e-4a2a8126122e','E2-AEV100-e7c791ce2e4b09ee-DM':'f6c79f5f-6b0e-42d7-a5be-c3013fa7aaba'}
V4_ADAPTER_SHA='5456bcf34174d16679d99805556fea621cc6c1d2ae64f059523ace5185937c33'
POSTRUN_STATES={'NATURAL_COMPLETE_PENDING_ACCEPTANCE_ARCHIVE','ACCEPTED_PENDING_ARCHIVE',
                'NATURAL_COMPLETE_ACCEPTED_PENDING_ARCHIVE'}

class Metadata:
 def __init__(self):
  self.before={};self.after={};self.stat_files=0;self.device=T.stat().st_dev;self.read_drift=False
 def raw(self,path,optional=False):
  p=Path(path)
  try:s=p.lstat()
  except FileNotFoundError:
   if optional:
    if str(p) in self.before and self.before[str(p)] is not None:self.read_drift=True
    self.before[str(p)]=None;return None
   raise
  if not stat.S_ISREG(s.st_mode) or s.st_dev!=self.device:
   raise ValueError('metadata must be a local regular file: '+str(p))
  if s.st_size>16*M:raise ValueError('metadata exceeds16MiB bound: '+str(p))
  b=p.read_bytes();digest=hashlib.sha256(b).hexdigest()
  if str(p) in self.before and self.before[str(p)]!=digest:self.read_drift=True
  self.before[str(p)]=digest;return b
 def read(self,path,optional=False):
  b=self.raw(path,optional);return None if b is None else json.loads(b)
 def tree_bytes(self,root):
  p=Path(root)
  if not p.exists():return 0
  if p.is_symlink() or p.stat().st_dev!=self.device:
   raise ValueError('result root must remain local and unaliased: '+str(p))
  total=0
  for parent,dirs,files in os.walk(p,followlinks=False):
   for name in dirs:
    d=Path(parent)/name
    if d.is_symlink() or d.stat().st_dev!=self.device:
     raise ValueError('unexpected result directory alias: '+str(d))
   for name in files:
    self.stat_files+=1
    if self.stat_files>20000:raise ValueError('bounded result metadata walk exceeded20000 files')
    f=Path(parent)/name
    try:s=f.lstat()
    except FileNotFoundError:continue
    if stat.S_ISLNK(s.st_mode):
     # Existing DTC producers use exactly this internal perf alias. Do not
     # follow it or count the target bytes twice; no remote/body access.
     target=os.readlink(f)
     if (name!='perf_counter.csv.gz' or '/' in target or '\\' in target or
         not target.startswith('perf_counter_') or not target.endswith('.csv.gz')):
      raise ValueError('result file alias requires explicit profile: '+str(f))
     ts=(f.parent/target).lstat()
     if not stat.S_ISREG(ts.st_mode) or ts.st_dev!=self.device:
      raise ValueError('perf alias target must be local regular sibling: '+str(f))
     self.before[str(f)]='LINK:'+target
     continue
    if not stat.S_ISREG(s.st_mode):raise ValueError('nonregular result file: '+str(f))
    total+=s.st_size
  return total
 def stable(self):
  for name,old in self.before.items():
   p=Path(name)
   try:
    s=p.lstat()
    if isinstance(old,str) and old.startswith('LINK:'):
     self.after[name]='LINK:'+os.readlink(p) if stat.S_ISLNK(s.st_mode) and s.st_dev==self.device else 'INVALID_ALIAS'
     continue
    if not stat.S_ISREG(s.st_mode) or s.st_dev!=self.device or s.st_size>16*M:
     self.after[name]='INVALID_METADATA_TYPE';continue
    self.after[name]=hashlib.sha256(p.read_bytes()).hexdigest()
   except FileNotFoundError:self.after[name]=None
  return self.before==self.after and not self.read_drift

def positive(value,label,allow_zero=False):
 if type(value) is not int or value<(0 if allow_zero else 1):
  raise ValueError('unknown/noninteger resource field '+label)
 return value

def rss_for(out,meta):
 pid=meta.read(Path(out)/'NATIVE_SIMULATOR_PID_AND_MAPS.json',True)
 if pid is None:return 0,False,'PID_RECEIPT_ABSENT'
 p=Path('/proc')/str(pid['pid'])
 try:
  fields=(p/'stat').read_text().rsplit(')',1)[1].split()
  if int(fields[19])!=pid['start_ticks'] or fields[0] in {'Z','X'}:
   return 0,False,'EXACT_PID_GENERATION_NOT_LIVE'
  current_boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
  if pid.get('boot_id',current_boot)!=current_boot:return 0,False,'BOOT_CHANGED'
  rss=int(next(x.split()[1] for x in (p/'status').read_text().splitlines() if x.startswith('VmRSS:')))*1024
  return rss,True,'EXACT_PID_START_TICKS_MATCH'
 except (FileNotFoundError,ProcessLookupError,StopIteration):return 0,False,'PROCESS_GONE'

def exact_spec(request,q,case,root,meta):
 path=root/'control'/((case+'_SPEC.json') if request==MAIN else ('specs/'+case+'.json'))
 spec=meta.read(path);expected=q['admitted_specs'][case]
 if not isinstance(expected,str) or meta.before[str(path)]!=expected:
  raise ValueError('admitted spec SHA mismatch: '+case)
 limits=spec['limits'];upper=positive(limits['max_result_directory_bytes'],case+'.result_cap')
 hard=positive(limits['max_process_tree_rss_bytes'],case+'.RAM_hard_cap')
 planpath=root/'control'/('OPERATIONAL_OUTPUT_CAP_'+case+'.json')
 op=meta.read(planpath,True);cap=upper
 if op is not None:
  cap=positive(op['effective_result_cap_bytes'],case+'.effective_result_cap')
  if op['cohort']!=case or cap>upper:raise ValueError('invalid tightened output cap: '+case)
  declared=spec.get('operational_output_cap_sha256')
  if declared is not None and declared!=meta.before[str(planpath)]:
   raise ValueError('effective output cap SHA drift: '+case)
 if request==RECOVERY:
  require(op is not None and spec['request']==RECOVERY and spec['cohort']==case and cap==256*M,'RECOVER12 effective cap receipt must be exact256MiB')
 return spec,cap,hard

def require(value,message):
 if not value:raise ValueError(message)

def pinned(meta,path,expected):
 data=meta.raw(path)
 require(hashlib.sha256(data).hexdigest()==expected,'qualified resource pin changed: '+str(path))
 return data

def qualified_r19_lineage(meta,reg):
 """Verify current registered linkage; read source bytes, never import actor code."""
 q=reg['registered_future_requests'];main=q[MAIN];new=q[REMAIN]
 profile=main['live_resource_accounting_correction_profile_R19']
 require(profile['profile_id']=='R19_EXACT_FIVE_SCOPE_RUNTIME_RESOURCE_ACCOUNTING_V1' and
         profile['policy_sha256']==R19_POLICY_SHA,'unqualified current R19 registry profile')
 require(new['execution_plan_sha256']==R19_PLAN_SHA,'REMAIN4 registered execution plan changed')
 plan_path=ROOTS[REMAIN]/'control/EXECUTION_PLAN_V1.json'
 plan=json.loads(pinned(meta,plan_path,R19_PLAN_SHA))
 require(plan['resource_accounting_overlay']=={'path':str(R19_OVERLAY),'sha256':R19_OVERLAY_SHA},'R19 overlay binding changed')
 require(plan['parent_controller_sha256']==new['orchestrator_sha256']==R19_CONTROLLER_SHA,'preserved REMAIN4 R19 parent identity changed')
 pinned(meta,plan['parent_controller_path'],R19_CONTROLLER_SHA)
 pinned(meta,R19_OVERLAY,R19_OVERLAY_SHA)
 policy=json.loads(pinned(meta,R19_POLICY,R19_POLICY_SHA))
 require(policy['schema']=='R19_FIVE_SCOPE_RESOURCE_ACCOUNTING_POLICY_V1' and
         policy['source_path']==str(R19_OVERLAY),'R19 policy identity changed')
 require(policy['host_runtime_floor_bytes']==64*G and policy['cgroup_runtime_floor_bytes']==48*G,'qualified RAM floors changed')
 require(policy['ghost_certificate_path']==str(GHOST_CERT) and policy['ghost_certificate_sha256']==GHOST_CERT_SHA and
         policy['ghost_verifier_path']==str(GHOST_VERIFIER) and policy['ghost_verifier_sha256']==GHOST_VERIFIER_SHA,'R19 departed binding changed')
 pinned(meta,GHOST_VERIFIER,GHOST_VERIFIER_SHA)
 cert=json.loads(pinned(meta,GHOST_CERT,GHOST_CERT_SHA))
 require(cert['schema']=='R17_THREE_DEPARTED_ORIGINAL_RAM_EVIDENCE_V1' and cert['request']==MAIN,'departed certificate schema changed')
 require({x['cohort']:x['uuid'] for x in cert['targets']}==GHOST_ALLOWED and len(cert['targets'])==3,'departed allowlist changed')
 for ref in cert['forensic_pins']:pinned(meta,ref['path'],ref['sha256'])
 require(policy['closed_scope_certificate_sha256']==CLOSED_CERT_SHA,'R19 closed certificate pin changed')
 closed_certificate=json.loads(pinned(meta,policy['closed_scope_certificate_path'],CLOSED_CERT_SHA))
 require(plan['per_cohort_memory']==new['per_cohort_memory'],'registered mixed memory profile differs from exact plan')
 return {'plan':plan,'certificate':cert,'closed_certificate':closed_certificate,'policy_sha256':R19_POLICY_SHA,'overlay_sha256':R19_OVERLAY_SHA,
         'plan_sha256':R19_PLAN_SHA,'ghost_certificate_sha256':GHOST_CERT_SHA,
         'ghost_verifier_sha256':GHOST_VERIFIER_SHA,'pure_independent_implementation':True,
         'actor_or_controller_imports':0}

def exact_current_parent_generation(meta):
 lease=meta.read(T/'control/BATCH_LEASE.json')
 started=meta.read(RECOVERY_ROOT/'control/CONTROLLER_START_R20.json')
 require(lease==started and lease['request']==MAIN and lease['controller_sha256']==R20_CONTROLLER_SHA,'R20 current parent generation binding changed')
 require(set(lease['additional_requests'])==set(ROOTS)-{MAIN} and len(lease['additional_requests'])==5,'R20 declared scopes changed')
 pid=positive(lease['pid'],'R20 parent pid');ticks=positive(lease['start_ticks'],'R20 parent ticks');fd=positive(lease['fd'],'R20 parent fd',True)
 proc=Path('/proc')/str(pid)
 try:
  fields=(proc/'stat').read_text().rsplit(')',1)[1].split()
  require(int(fields[19])==ticks and fields[0] not in {'Z','X'},'R20 parent generation is not currently live')
  require(str(R20_CONTROLLER).encode() in (proc/'cmdline').read_bytes().split(b'\0'),'R20 parent actual command changed')
  held=(proc/'fd'/str(fd)).stat();lock=(N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock').stat()
  require((held.st_dev,held.st_ino)==(lock.st_dev,lock.st_ino),'R20 parent recorded qualification FD changed')
 except (FileNotFoundError,ProcessLookupError):raise ValueError('R20 parent generation/FD departed; new transition proof required')
 return {'pid':pid,'start_ticks':ticks,'fd':fd,'controller_sha256':R20_CONTROLLER_SHA,'observed_live':True,'lock_acquired_by_observer':False}

def qualified_policy(meta,reg):
 """Only this exact R20 activation extends preserved R19; no actor imports."""
 pinned(meta,BASE_RESOURCE,BASE_RESOURCE_SHA)
 qualified=qualified_r19_lineage(meta,reg);qs=reg['registered_future_requests'];main=qs[MAIN];new=qs[RECOVERY]
 prior=json.loads(pinned(meta,RECOVERY_ROOT/'control/ORIGINAL_REQUEST_BEFORE_R20.json',R20_BEFORE_MAIN_SHA))
 oldfour=json.loads(pinned(meta,RECOVERY_ROOT/'control/OLD_FOUR_REPAIR_REQUESTS_BEFORE_R20.json',R20_BEFORE_FOUR_SHA))
 require(prior['orchestrator_sha256']==R19_CONTROLLER_SHA and main['orchestrator_sha256']==R20_CONTROLLER_SHA,'unqualified MAIN R19-to-R20 transition')
 for field in ['budget','remaining','sealed','sealed_unused','admitted_inputs','admitted_specs','effective_specs']:
  require(prior.get(field)==main.get(field),'R20 changed old MAIN scientific/budget field '+field)
 require(set(prior['consumed'])==set(main['consumed']),'R20 introduced/replaced old MAIN starts')
 for case,row in prior['consumed'].items():
  current=main['consumed'][case]
  require({k:v for k,v in row.items() if k!='execution_receipt'}=={k:v for k,v in current.items() if k!='execution_receipt'},'R20 changed spent generation identity '+case)
 require(set(oldfour)==set(ROOTS)-{MAIN,RECOVERY},'R20 old-four scope set changed')
 for request,old in oldfour.items():require(old==qs[request] and old['state']=='CLOSED' and old['remaining']==0,'R20 changed/unclosed preserved old repair '+request)
 continuations=[x for x in main['operational_continuations'] if x.get('revision')=='R20_FINITE12_STORAGE_RECOVERY_VALIDATION']
 require(len(continuations)==1,'R20 registered continuation absent/duplicate');c=continuations[0]
 require(c['controller_sha256']==R20_CONTROLLER_SHA and c['publication_commit']=='04cc5c543e207cf62eb7a237d3c100445dbb0ce0' and
         c['new_original_starts']==0 and c['old_live_generations_adopted'] is True and c['old_spent_budget_unchanged'] is True,'R20 continuation does not preserve original science')
 plan=json.loads(pinned(meta,RECOVERY_ROOT/'control/EXECUTION_PLAN_V1.json',R20_PLAN_SHA))
 require(new['execution_plan_sha256']==R20_PLAN_SHA and new['authorized_parent_request']==MAIN and new['orchestrator_sha256']==R20_CONTROLLER_SHA and
         new['engine_sha256']==R20_ENGINE_SHA and new['budget']==12 and new['model_automatic_retries']==0 and new['old_failed_attempts_preserved'] is True,'RECOVER12 registered identity/budget changed')
 require(new['correctness_validation_only'] is True and new['reserved_write_bytes']==plan['reserved_write_bytes']==7*G,'RECOVER12 canonical 7GiB guarantee changed')
 require(new['remaining']+len(new['consumed'])+new.get('sealed_unused',0)==12,'RECOVER12 finite request accounting malformed')
 require(plan['request']==RECOVERY and plan['parent_controller_path']==str(R20_CONTROLLER) and plan['parent_controller_sha256']==R20_CONTROLLER_SHA and
         plan['resource_accounting_overlay']=={'path':str(R20_OVERLAY),'sha256':R20_OVERLAY_SHA},'RECOVER12 plan/parent/overlay changed')
 require(plan['per_cohort_memory']==new['per_cohort_memory'] and len(plan['per_cohort_memory'])==12,'RECOVER12 mixed memory bindings changed')
 pinned(meta,R20_CONTROLLER,R20_CONTROLLER_SHA);pinned(meta,R20_OVERLAY,R20_OVERLAY_SHA)
 pinned(meta,RECOVERY_ROOT/'tools/recovery12_native_v1.py',R20_ENGINE_SHA)
 policy=json.loads(pinned(meta,R20_POLICY,R20_POLICY_SHA))
 require(policy['schema']=='R20_SIX_SCOPE_RESOURCE_ACCOUNTING_POLICY_V1' and policy['source_path']==str(R20_OVERLAY) and
         policy['new_request']==RECOVERY and policy['new_root']==str(RECOVERY_ROOT) and policy['new_finite_budget']==12 and policy['new_expected_output_cap_bytes']==256*M,'R20 policy new scope changed')
 require(policy['derived_unchanged_R19_policy_sha256']==R19_POLICY_SHA and policy['derived_unchanged_R19_resource_sha256']==R19_OVERLAY_SHA and
         policy['derived_unchanged_R19_policy_path']==str(R19_POLICY),'R20 policy lost preserved R19 lineage')
 require(policy['host_runtime_floor_bytes']==64*G and policy['cgroup_runtime_floor_bytes']==48*G and
         policy['ghost_certificate_sha256']==GHOST_CERT_SHA and policy['ghost_verifier_sha256']==GHOST_VERIFIER_SHA and
         policy['closed_scope_certificate_sha256']==CLOSED_CERT_SHA,'R20 RAM floors/closure proofs changed')
 refs=plan['source_pins']+plan['additional_source_pins'];require(len(refs)==240,'RECOVER12 exact source-pin entry count changed')
 for ref in refs:pinned(meta,ref['path'],ref['sha256'])
 for key in ['copy_gate_overlay','closed_R1_cpu_reuse_evidence','observer_overlay']:
  ref=plan[key];pinned(meta,ref['path'],ref['sha256'])
 pinned(meta,plan['scope_path'],plan['scope_sha256'])
 require(set(new['admitted_specs'])==set(plan['per_cohort_memory']),'RECOVER12 admitted/memory case sets differ')
 claims=meta.read(RECOVERY_ROOT/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']
 require(isinstance(claims,dict) and set(claims)<=set(new['admitted_specs']) and set(new['consumed'])<=set(new['admitted_specs']) and len(claims)<=12,'RECOVER12 unknown/oversubscribed claim/case')
 cpus=[]
 for case in new['admitted_specs']:
  spec,cap,hard=exact_spec(RECOVERY,new,case,RECOVERY_ROOT,meta)
  binding=plan['per_cohort_memory'][case]
  if case in claims:
   claim=claims[case];require(claim['result_cap_bytes']==cap and claim['RAM_cap_bytes']==hard and claim['host_cpu'] in plan['allowed_model_CPUs'],'RECOVER12 serialized claim cap/CPU changed');cpus.append(claim['host_cpu'])
  if case in new['consumed']:
   row=new['consumed'][case];ip=RECOVERY_ROOT/'control/qualification_ledger'/(case+'.INTENT.json');intent=json.loads(pinned(meta,ip,row['intent_sha256']))
   require(row['charged']==1 and intent['cohort']==case and intent['uuid']==row['uuid'] and intent['output']==str(RECOVERY_ROOT/'DTC/run/results'/row['uuid']),'RECOVER12 consumed/INTENT binding changed')
  require(spec['request']==RECOVERY and spec['cohort']==case and cap==256*M and
          (hard,spec['estimated_peak_model_RAM_bytes']) in {(16*G,4*G),(128*G,96*G)} and
          binding=={'estimated_peak_model_RAM_bytes':spec['estimated_peak_model_RAM_bytes'],'initial_working_set_floor_bytes':4*G,'max_process_tree_rss_bytes':hard},'RECOVER12 exact effective caps/mixed profile changed')
 require(len(cpus)==len(set(cpus)),'RECOVER12 duplicate serialized model CPU')
 parent=exact_current_parent_generation(meta)
 qualified.update(recovery_plan=plan,R20_policy_sha256=R20_POLICY_SHA,R20_overlay_sha256=R20_OVERLAY_SHA,
  R20_plan_sha256=R20_PLAN_SHA,R20_controller_sha256=R20_CONTROLLER_SHA,R20_parent_generation=parent,
  recovery_source_pin_entries_verified=len(refs),base3074_sha256=BASE_RESOURCE_SHA)
 return qualified

def qualified_estimate(request,spec,hard,qualified):
 # This is the exact mixed formula of the pinned R19 overlay memory(), not an
 # assertion that any estimate is a guaranteed upper bound. Hard caps remain.
 estimate=96*G if request=='DTC_AE_LAVAMEM_REPAIR_20261026_V2' else 4*G
 if request in {REMAIN,RECOVERY}:
  bound_plan=qualified['recovery_plan'] if request==RECOVERY else qualified['plan']
  b=bound_plan['per_cohort_memory'][spec['cohort']]
  estimate=positive(spec['estimated_peak_model_RAM_bytes'],'qualified mixed estimate')
  require(b['max_process_tree_rss_bytes']==hard and b['estimated_peak_model_RAM_bytes']==estimate and
          b['initial_working_set_floor_bytes']==4*G,'mixed profile spec binding changed')
 if request==RECOVERY:require((hard,estimate) in {(16*G,4*G),(128*G,96*G)},'RECOVER12 estimate/cap pair not qualified')
 require(4*G<=estimate<=hard,'estimate is outside qualified hard cap')
 return estimate

def certified_departed(request,case,row,root,claims,meta,qualified):
 """Independent implementation of pinned verifier14–34; uncertainty retains RAM."""
 if request!=MAIN or case not in GHOST_ALLOWED:return False,'NOT_ALLOWLISTED'
 targets=[x for x in qualified['certificate']['targets'] if x['cohort']==case]
 require(len(targets)==1,'departed target multiplicity changed');x=targets[0]
 if row.get('uuid')!=x['uuid'] or 'execution_receipt' in row or case in claims:
  return False,'RETAIN_RECEIPT_CLAIM_OR_GENERATION_CHANGED'
 ip=root/'control/qualification_ledger'/(case+'.INTENT.json');out=root/'DTC/run/results'/x['uuid']
 require(str(ip)==x['intent_path'] and str(out)==x['output'],'departed exact roots changed')
 require(row['intent_sha256']==x['intent_sha256'],'departed registered INTENT pin changed')
 intent=json.loads(pinned(meta,ip,x['intent_sha256']))
 pid=json.loads(pinned(meta,out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',x['PID_receipt_sha256']))
 launch=json.loads(pinned(meta,out/'NATIVE_LAUNCH.json',x['launch_receipt_sha256']))
 require(intent['cohort']==case and intent['uuid']==x['uuid'] and intent['output']==str(out),'departed INTENT identity changed')
 require((pid['pid'],pid['start_ticks'],launch['launcher_pid'])==(x['model_pid'],x['model_start_ticks'],x['launcher_pid']),'departed process generation changed')
 if meta.raw(ip.with_name(case+'.DONE.json'),True) is not None or meta.raw(out/'NATIVE_EXIT.json',True) is not None:
  return False,'RETAIN_NEW_CLOSURE_REQUIRES_REVIEW'
 if (Path('/proc')/str(pid['pid'])).exists() or (Path('/proc')/str(launch['launcher_pid'])).exists():
  return False,'RETAIN_PID_PRESENT_OR_REUSED'
 return True,'PINNED_CERTIFIED_EXACT_GENERATIONS_ABSENT_NO_CLAIM'

def archived_verified(root,case,row,meta):
 receipt=meta.read(root/'control'/(case+'_ARCHIVE_RECEIPT.json'),True)
 if receipt is None:return False
 ip=root/'control/qualification_ledger'/(case+'.INTENT.json');out=root/'DTC/run/results'/row['uuid']
 done=meta.read(ip.with_name(case+'.DONE.json'),True);exit_receipt=meta.read(out/'NATIVE_EXIT.json',True)
 if done is None or exit_receipt is None or 'execution_receipt' not in row:return False
 intent=meta.read(ip)
 return (done==exit_receipt==row['execution_receipt'] and done['uuid']==intent['uuid']==row['uuid'] and
         meta.before[str(ip)]==row['intent_sha256'] and receipt['cohort']==case and
         receipt['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET' and receipt['source_disposition']=='SOURCE_KEEP')

def closed_scope_verified(request,q,root,claims,meta,qualified):
 if q.get('state')!='CLOSED':return False
 proof=qualified['closed_certificate']['scopes'].get(request)
 if proof is None:return False  # R20 deliberately retains1GiB otherwise.
 if not(q['budget']==proof['budget'] and q['remaining']==0 and set(q['consumed'])==set(proof['points']) and set(claims)<=set(q['consumed'])):return False
 for case,row in q['consumed'].items():
  ref=proof['points'][case]
  require(row['uuid']==ref['uuid'] and row['intent_sha256']==ref['intent_sha256'],'closed-scope generation changed')
  for pin in ref['pins']:pinned(meta,pin['path'],pin['sha256'])
  if not archived_verified(root,case,row,meta) or rss_for(root/'DTC/run/results'/row['uuid'],meta)[1]:return False
 return True

def request_resources(request,q,root,meta,legacy,qualified):
 consumed=q['consumed']
 if not isinstance(consumed,dict):raise ValueError('unknown consumed schema: '+request)
 claims=meta.read(root/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']
 if not isinstance(claims,dict):raise ValueError('unknown claim schema: '+request)
 terminal=q.get('state') in TERMINAL
 if closed_scope_verified(request,q,root,claims,meta,qualified):
  return {'request':request,'state':q['state'],'root':str(root),'charged_future_write_bytes':0,'additional_RAM_bytes':0,'original_conservative_additional_RAM_bytes':0,'original_conservative_charged_future_write_bytes':0,'rows':[],'archived_rows_skipped':len(consumed),'basis':'PINNED_R20_CLOSED_SCOPE_CERTIFICATE_ALL_DONE_ARCHIVE_PID_PROOF'}
 rows=[];remaining=0;ram=0;archived=0;old_ram=0;old_writes=0
 for case,row in consumed.items():
  if archived_verified(root,case,row,meta):
   archived+=1;continue
  out=root/'DTC/run/results'/row['uuid'];used=meta.tree_bytes(out);done=bool(row.get('execution_receipt'))
  e={'request':request,'case':case,'uuid':row['uuid'],'output':str(out),
     'existing_result_bytes_information_only':used,'execution_receipt_present':done}
  old_extra=0
  if done:
   pending=used+16*M;old_pending=pending;e.update(kind='COMPLETE_PENDING_ARCHIVE_RESTORE',additional_RAM_bytes=0)
  else:
   spec,cap,hard=exact_spec(request,q,case,root,meta)
   observed,live,birth=rss_for(out,meta)
   old_pending=max(0,cap-used)+cap
   old_envelope=(hard if case in legacy else min(hard,max(4*G,observed))) if request==MAIN else hard
   old_extra=max(0,old_envelope-observed)
   departed,departed_basis=certified_departed(request,case,row,root,claims,meta,qualified)
   estimate=qualified_estimate(request,spec,hard,qualified)
   if departed:
    require(not live,'departed certificate conflicts with actual live process')
    pending=used+16*M;envelope=0;extra=0;kind='CERTIFIED_DEPARTED_PENDING_FORENSIC_ARCHIVE_RESTORE'
   else:
    pending=old_pending;envelope=min(hard,max(4*G,estimate,observed));extra=max(0,envelope-observed)
    kind='LIVE_MODEL' if live else 'HISTORICAL_UNRESOLVED_CONSERVATIVE'
   ram+=extra
   e.update(kind=kind,result_cap_bytes=cap,RAM_hard_cap_bytes=hard,observed_model_RSS_bytes=observed,
    model_live=live,PID_evidence=birth,RAM_envelope_bytes=envelope,additional_RAM_bytes=extra,
    RAM_basis='PINNED_R20_CERTIFIED_DEPARTED_NO_FUTURE_MODEL' if departed else 'PINNED_R20_MIXED_ESTIMATE_AND_OBSERVED_RSS_CAPPED_AT_HARD',
    estimated_RAM_information_only=estimate,qualified_peak_estimate_bytes=estimate,
    certified_departed=departed,departed_evidence=departed_basis,
    original_conservative_RAM_envelope_bytes=old_envelope)
  e.update(remaining_result_growth_and_one_restore_bytes=pending,
   original_conservative_additional_RAM_bytes=old_extra,
   original_conservative_remaining_write_bytes=old_pending)
  old_ram+=old_extra;old_writes+=old_pending;remaining+=pending;rows.append(e)
 for case,claim in claims.items():
  if case in consumed:continue
  spec,cap,hard=exact_spec(request,q,case,root,meta)
  if claim.get('result_cap_bytes')!=cap or claim.get('RAM_cap_bytes')!=hard:
   raise ValueError('serialized claim cap differs from exact effective spec: '+case)
  estimate=qualified_estimate(request,spec,hard,qualified);extra=min(hard,max(4*G,estimate))
  old_extra=min(hard,4*G) if request==MAIN else hard
  ram+=extra;old_ram+=old_extra;remaining+=2*cap;old_writes+=2*cap
  rows.append({'request':request,'case':case,'kind':'CLAIM_BEFORE_INTENT',
   'result_cap_bytes':cap,'RAM_hard_cap_bytes':hard,'qualified_peak_estimate_bytes':estimate,'additional_RAM_bytes':extra,
   'remaining_result_growth_and_one_restore_bytes':2*cap,'original_conservative_remaining_write_bytes':2*cap,
   'original_conservative_additional_RAM_bytes':old_extra,'RAM_basis':'PINNED_R20_QUALIFIED_MIXED_CLAIM_ESTIMATE'})
 if terminal and rows:raise ValueError('terminal peer still has unclosed operations: '+request)
 registered=positive(q.get('reserved_write_bytes'),request+'.reserved_write_bytes',True)
 metadata=G;known=remaining+metadata;old_known=old_writes+metadata
 if request==MAIN:charged=known;old_charged=old_known
 else:charged=max(known,registered);old_charged=max(old_known,registered)
 if not terminal and known>registered:raise ValueError('qualified known peer writes exceed registered ceiling: '+request)
 return {'request':request,'state':q.get('state'),'root':str(root),
  'registered_write_bytes_information_only':registered,'pool_ceiling_only':request==MAIN,
  'current_result_bytes_information_only':sum(e.get('existing_result_bytes_information_only',0) for e in rows),
  'remaining_result_growth_and_one_restore_bytes':remaining,'metadata_envelope_bytes':metadata,
  'known_remaining_write_bytes':known,'preserved_foreign_reserve_margin_bytes':max(0,charged-known),
  'charged_future_write_bytes':charged,'additional_RAM_bytes':ram,
  'original_conservative_additional_RAM_bytes':old_ram,'original_conservative_charged_future_write_bytes':old_charged,
  'archived_rows_skipped':archived,'rows':rows}

def generic_foreign_ep(request,q,meta):
 """Narrow explicit-spec EP peer; unknown active schemas HOLD instead of guessing."""
 if q.get('project')!='EP_L2' or not q.get('spec_path') or not q.get('spec_sha256'):
  raise ValueError('unknown active foreign resource profile: '+request)
 p=Path(q['spec_path']);spec=meta.read(p)
 if meta.before[str(p)]!=q['spec_sha256']:raise ValueError('foreign EP spec SHA mismatch: '+request)
 hard=positive(spec.get('memory_cap_bytes'),request+'.memory_cap_bytes')
 reserve=positive(q.get('reserved_write_bytes'),request+'.reserved_write_bytes',True)
 consumed=q.get('consumed');observed=0;live=False
 if consumed==1:
  if not q.get('output'):raise ValueError('consumed foreign EP lacks output: '+request)
  observed,live,_=rss_for(q['output'],meta)
  # A naturally completed foreign request retains disk guarantee but no model RAM.
  natural=q.get('state') in POSTRUN_STATES
  if natural and live:raise ValueError('foreign EP marked postrun but model live: '+request)
  extra=0 if natural else max(0,hard-observed)
 elif consumed==0 and q.get('state')=='AUTHORIZED_UNUSED':extra=hard
 else:raise ValueError('unknown active foreign EP phase: '+request)
 return {'request':request,'state':q.get('state'),'charged_future_write_bytes':reserve,
  'registered_write_bytes_information_only':reserve,'additional_RAM_bytes':extra,
  'RAM_hard_cap_bytes':hard,'observed_model_RSS_bytes':observed,'model_live':live,
  'basis':'EXACT_REGISTERED_FOREIGN_EP_SPEC_AND_PHASE'}

def snapshot(job_root,own_request,phase='admission',own_write_bytes=512*M,own_memory_cap_bytes=9*G):
 """A sampled prerequisite, not a reservation, SourceQ, budget or launch permit.

 phase admission forecasts known commitments; runtime checks actual headroom
 under already-held own reservation; postrun is the same held operation with
 additional256MiB archive-process RAM margin. Caller separately proves natural
 DONE+acceptance+no model and enforces own model/operation caps.
 """
 if phase not in {'admission','runtime','postrun'}:raise ValueError('unknown resource phase')
 own_write_bytes=positive(own_write_bytes,'own_write_bytes')
 own_memory_cap_bytes=positive(own_memory_cap_bytes,'own_memory_cap_bytes')
 meta=Metadata();errors=[];peers=[];pair=False;own_held=False;own={};budget=None
 qualified={};root=Path(job_root);anchor=root if root.exists() else Path('/root/data')
 v0=os.statvfs(anchor)
 try:
  reg=meta.read(REG);epoch=meta.read(EPOCH);pair=meta.before[str(REG)]==epoch['native_registry_sha256']
  if epoch.get('epoch')!=2 or epoch.get('state')!='NATIVE_SCIENCE_ACTIVE' or epoch.get('holder')!=os.uname().nodename:
   raise ValueError('unknown/inactive native epoch identity')
  budget=reg['new_scientific_budget_remaining']  #never used for eligibility
  profile=meta.read(T/'control/HOST_EXECUTION_PLAN_V4.json')
  raw=meta.raw(T/'tools/sweep_host_execution_v4.py')
  if (profile.get('profile_id')!='HOST_ACTUAL4G40_V4' or
      profile.get('adapter_sha256')!=V4_ADAPTER_SHA or hashlib.sha256(raw).hexdigest()!=V4_ADAPTER_SHA):
   raise ValueError('unknown qualified DTC working-set/credit profile')
  if phase=='admission':qualified=qualified_policy(meta,reg)
  else:qualified={'forecast_not_evaluated_in_held_phase':True,'actor_or_controller_imports':0}
  own=reg['registered_future_requests'].get(own_request,{})
  if own:
   advertised=positive(own.get('reserved_write_bytes'),'own.registered_write_bytes',True)
   actual=positive(own.get('actual_write_restore_envelope_bytes',advertised),'own.actual_write_envelope',True)
   own_held=advertised>=own_write_bytes and actual>=own_write_bytes and own.get('state') not in TERMINAL
  if phase!='admission':
   if not own_held or own.get('consumed')!=1:raise ValueError('held-phase requires own consumed1 and intact registered envelope')
   if phase=='postrun' and own.get('state') not in POSTRUN_STATES:
    raise ValueError('postrun phase lacks natural-completion state; caller must prove DONE+accepted')
   # Observe claims for short metadata consistency only; do not forecast their
   # future legal growth/RAM as a new admission or running-model abort test.
   for request,proot in ROOTS.items():
    if request in reg['registered_future_requests']:meta.read(proot/'control/POOL_DISPATCH_RESERVATIONS.json')
  else:
   legacy=set(profile['legacy_V1_cells'])
   for request,q in reg['registered_future_requests'].items():
    if request==own_request:continue
    if not isinstance(q,dict):raise ValueError('unknown request row schema: '+request)
    if request in ROOTS:
     peers.append(request_resources(request,q,ROOTS[request],meta,legacy,qualified));continue
    reserve=q.get('reserved_write_bytes')
    if q.get('state') in TERMINAL:
     if reserve not in [0,None]:
      peers.append({'request':request,'state':q.get('state'),
       'terminal_registered_reserve_information_only':reserve,'charged_future_write_bytes':0,
       'additional_RAM_bytes':0,'basis':'OWNER_TERMINAL_STATE_NO_NEW_WRITES'})
     continue
    positive(reserve,request+'.reserved_write_bytes',True)
    if not reserve:continue
    peers.append(generic_foreign_ep(request,q,meta))
 except (OSError,ValueError,KeyError,TypeError) as e:errors.append(type(e).__name__+': '+str(e))
 mem=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
 cg=Path('/sys/fs/cgroup');current=int((cg/'memory.current').read_text());maximum=(cg/'memory.max').read_text().strip()
 ms={a:int(b) for a,b in (x.split() for x in (cg/'memory.stat').read_text().splitlines())}
 clean=max(0,ms.get('file',0)-ms.get('shmem',0)-ms.get('file_mapped',0)-ms.get('file_dirty',0)-ms.get('file_writeback',0))
 credit=max(0,min(ms.get('inactive_file',0),clean)-8*G)
 effective=None if maximum=='max' else int(maximum)-current+credit
 stable=meta.stable();resample=not stable or not pair
 valid=stable and pair and not errors
 v1=os.statvfs(anchor);free=min(v0.f_bavail*v0.f_frsize,v1.f_bavail*v1.f_frsize)
 writes=sum(x['charged_future_write_bytes'] for x in peers)
 ram=sum(x['additional_RAM_bytes'] for x in peers)
 forecast=phase=='admission';required=8*G+own_write_bytes+(writes if forecast else 0)
 extra=(ram+own_memory_cap_bytes) if forecast else 256*M if phase=='postrun' else 0
 host_required=64*G+extra;cg_required=48*G+extra
 disk_ok=valid and free>required and v1.f_favail>=100000
 ram_ok=valid and mem>=host_required and (effective is None or effective>=cg_required)
 decision='RESAMPLE' if resample else 'HOLD' if errors or not(disk_ok and ram_ok) else 'PASS'
 old_ram=sum(x.get('original_conservative_additional_RAM_bytes',x.get('additional_RAM_bytes',0)) for x in peers)
 old_writes=sum(x.get('original_conservative_charged_future_write_bytes',x.get('charged_future_write_bytes',0)) for x in peers)
 old_host=64*G+old_ram+own_memory_cap_bytes;old_cg=48*G+old_ram+own_memory_cap_bytes
 comparison={'same_metadata_and_actual_resource_sample':True,'comparison_scope':'hard-cap alternative over all recognized scopes; old3074 itself cannot recognize R20','phase_applicable':forecast,
  'original_conservative_peer_additional_RAM_bytes':old_ram if forecast else None,
  'qualified_peer_additional_RAM_bytes':ram if forecast else None,
  'original_conservative_required_host_available_RAM_bytes':old_host if forecast else None,
  'original_conservative_required_cgroup_headroom_bytes':old_cg if forecast else None,
  'original_conservative_required_disk_bytes':8*G+own_write_bytes+old_writes if forecast else None,
  'original_conservative_RAM_pass':bool(valid and mem>=old_host and (effective is None or effective>=old_cg)) if forecast else None,
  'qualified_RAM_requirement_reduction_bytes':old_ram-ram if forecast else None,
  'qualified_disk_requirement_reduction_bytes':old_writes-writes if forecast else None}
 historic=[row for p in peers for row in p.get('rows',[]) if row['kind']=='HISTORICAL_UNRESOLVED_CONSERVATIVE']
 return {'schema':'EP_LIFETIME_QUALIFIED_R20_READONLY_RESOURCE_REFERENCE_V1',
  'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phase':phase,
  'job_root':str(root),'own_request':own_request,'own_reservation_held':own_held,
  'own_write_restore_envelope_bytes':own_write_bytes,'own_model_hard_cap_bytes':own_memory_cap_bytes,
  'local_disk_floor_bytes':7*G,'unknown_incremental_margin_bytes':G,
  'free_bytes':free,'required_bytes':required,'disk_deficit_bytes':max(0,required-free),
  'host_MemAvailable_bytes':mem,'required_host_available_RAM_bytes':host_required,
  'host_RAM_deficit_bytes':max(0,host_required-mem),'cgroup_memory_current_bytes':current,
  'cgroup_memory_max':maximum,'clean_inactive_file_credit_bytes':credit,
  'cgroup_effective_headroom_bytes':effective,'required_cgroup_headroom_bytes':cg_required,
  'cgroup_RAM_deficit_bytes':None if effective is None else max(0,cg_required-effective),
  'peer_forecast_evaluated':forecast,'peer_charged_write_bytes':writes if forecast else None,
  'peer_additional_RAM_bytes':ram if forecast else None,'peer_breakdown':peers,
  'historical_unresolved_conservative_write_bytes':sum(e['remaining_result_growth_and_one_restore_bytes'] for e in historic),
  'historical_unresolved_conservative_RAM_bytes':sum(e['additional_RAM_bytes'] for e in historic),
  'global_budget_information_only':budget,'budget_not_used_for_admission_eligibility':True,
  'stable_metadata_snapshot':stable,'authority_pair_matches':pair,'consistent_snapshot':valid,
  'projected_sums_complete':not errors,
  'incomplete_sums_are_known_lower_bounds_only':bool(errors),
  'resample_required':resample,'errors':errors,'disk_pass':disk_ok,'RAM_pass':ram_ok,
  'resource_pass':disk_ok and ram_ok,'decision':decision,
  'abort_recommended':bool(phase=='runtime' and valid and not(disk_ok and ram_ok)),
  'qualified_policy_binding':{k:v for k,v in qualified.items() if k not in {'plan','certificate','closed_certificate','recovery_plan'}},
  'same_sample_original_conservative_comparison':comparison,
  'metadata_SHA256_before':meta.before,'metadata_SHA256_after':meta.after,
  'result_file_stats_read':meta.stat_files,'locks_acquired':0,'authority_writes':0,
  'qualification_or_budget_granted':False,
  'limits':['current sample is not a held lease or future guarantee',
   'no asset/body reads; existing bytes already reduce df free space',
   'DTC35GiB pool ceiling is information only; historical unresolved rows retained',
   'qualified R19 estimates are admission envelopes, never hard peak guarantees; hard enforcement caps unchanged',
   'certified departed generations retain existing-file closure but no future model RAM; no synthetic DONE',
   'held-phase caller must separately prove own PID/DONE/acceptance and enforce own hard caps',
   'unknown request/resource profile HOLD; unstable authority/claims RESAMPLE']}

if __name__=='__main__':
 a=argparse.ArgumentParser(description=__doc__)
 a.add_argument('--job-root',default='/root/data/ep_tag_reservation_lifetime_20261026_v1')
 a.add_argument('--own-request',default='EP_L2_TAG_RESERVATION_LIFETIME_CAUSAL_V1_REFERENCE_ONLY')
 a.add_argument('--phase',choices=['admission','runtime','postrun'],default='admission')
 a.add_argument('--own-write-bytes',type=int,default=512*M)
 a.add_argument('--own-memory-bytes',type=int,default=9*G)
 args=a.parse_args();print(json.dumps(snapshot(args.job_root,args.own_request,args.phase,args.own_write_bytes,args.own_memory_bytes),indent=2))