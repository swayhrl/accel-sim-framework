"""Default inert. Main-only administrative one-field CAS, never model dispatch."""
from pathlib import Path
import argparse,copy,hashlib,json,os,types
ROOT=Path('/root/data/dtc_oracle_clean_successor_20261107_v1/remaining24')
REQUEST='DTC_ORACLE_REMAINING24_20261106_V1';OLD='DTC_ORACLE_INITIAL8_20261106_V1'
OWNER=525725;START=1077052887
LEASE_SHA='567265d733ffa72a442508202c69c343f417d2a94f9d7f96051d3e8ebbe2d54e'
FROM='CPU_RESOURCE_ONLY_NOT_A_SCIENTIFIC_CANDIDATE'
def need(v,why):
 if not v:raise RuntimeError(why)
def encoded(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def digest(v):return hashlib.sha256(encoded(v)).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):
 m=types.ModuleType('MAIN_METADATA_ONLY_'+Path(p).stem);m.__file__=str(p);exec(compile(Path(p).read_bytes(),str(p),'exec'),m.__dict__);return m
def put(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb')as h:h.write(encoded(v));h.flush();os.fsync(h.fileno())
def cas_arm(current,expected,old32):
 """Pure passed-registry callback: zero IO, nested lock/read or model API."""
 q=current['registered_future_requests'][REQUEST]
 need(q==expected,'OWN96_CHANGED_CAS_HOLD')
 need(current['registered_future_requests'][OLD]==old32,'OLD32_CHANGED_CAS_HOLD')
 need(q['state']==FROM and q['budget']==q['remaining']==96 and q['consumed']=={},'EXACT_UNUSED96_STATE_ONLY')
 need(q['owner_pid']==OWNER and q['owner_start_ticks']==START and q['ready_for_registration']is True,'SAME_ACTUAL_OWNER_SCOPE')
 before=copy.deepcopy(current);q['state']='ARMED'
 projected=copy.deepcopy(current);projected['registered_future_requests'][REQUEST]['state']=FROM
 need(projected==before,'ANY_FIELD_OTHER_THAN_OWN_STATE_CHANGED')
 return 1
def observe_owner(plan):
 lease_path=ROOT/'control/CLEAN_MAIN_PRIVATE_LEASE.fixed.json';need(sha(lease_path)==LEASE_SHA,'ACTUAL_PRIVATE_LEASE_PIN')
 lease=read(lease_path);need(lease['pid']==plan['parent_pid']==OWNER and lease['start_ticks']==plan['parent_start_ticks']==START,'ACTUAL_OWNER_LEASE_PLAN')
 guardref=plan['clean_owner_guard'];need(sha(guardref['path'])==guardref['sha256']==lease['guard_sha256'],'ACTUAL_OWNER_GUARD_SOURCE')
 guard=load(guardref['path']);actual=guard.process(OWNER)
 need(actual is not None and actual['start_ticks']==START and actual['state']!='Z'and actual['tracer_pid']==0,'ACTUAL_NORMAL_OWNER_MISSING')
 need(sha(lease['controller']['path'])==lease['controller']['sha256']==plan['parent_controller_sha256']
      and plan['parent_controller_path']==lease['controller']['path']
      and lease['controller']['path'].encode()in actual['cmdline'],'ACTUAL_OWNER_SOURCE_COMMAND')
 need({x['role']:x['path']for x in lease['locks']}==guard.FIXED_LOCK_PATHS,'ACTUAL_GLOBAL_LOCK_PATHS')
 guard.require_fixed_lock_identities(lease['locks'])
 records=[guard.verify_lock(x,OWNER)for x in lease['locks']]
 # This is an external administrative observer, never a model descendant. Do
 # not override caller_pid or invoke a parent guard pretending to be a child.
 return dict(pid=OWNER,start_ticks=START,private_lease_sha256=LEASE_SHA,actual_lock_records=records,external_admin_not_model_descendant=True)
def run(release):
 need(release['actual_metadata_amendment_authorized']is True and release['subject_source_sha256']==sha(__file__),'MAIN_EXPLICIT_METADATA_RELEASE_REQUIRED')
 need(release['request']==REQUEST and release['models_allowed']==0 and release['registrations_allowed']==0,'NO_MODEL_OR_REGISTRATION_SCOPE')
 root=Path(release['audit_directory']);need(root.is_relative_to(ROOT/'control/METADATA_AMENDMENTS'),'NARROW_NEW_AUDIT_DIRECTORY_ONLY')
 root.mkdir(parents=True,exist_ok=False);put(root/'INTENT.fixed.json',dict(release=release,actor_pid=os.getpid(),source_sha256=sha(__file__),one_attempt_only=True))
 plan=read(ROOT/'control/EXECUTION_PLAN.json');owner=observe_owner(plan)
 e=load(ROOT/'tools/oracle_native.py');reg,epoch,q,actual_plan=e.registered()
 need(actual_plan==plan and q['state']==FROM and q['remaining']==q['budget']==96 and not q['consumed'],'REGISTERED_UNUSED96_SOURCE_PLAN')
 need(not list((ROOT/'control/qualification_ledger').glob('*.INTENT.json')),'NO_SCIENTIFIC_INTENT_ALLOWED')
 auth=read(ROOT/'control/SCIENCE_AUTHORIZATION.json');need(auth['explicit_user_approval']and auth['owner_bindings_ratified']and auth['target_resource_policy_ratified']and len(auth['budgets'])==96,'EXISTING_REAL96_AUTHORIZATION')
 resources=e.resource_module();gates=resources.verify_registration_release(plan,q)
 pause=ROOT.parent/'control/ENGINEERING_PAUSE_NEW.json';need(sha(pause)==release['zero_start_pause_sha256'],'EXACT_ZERO_START_PAUSE_BYTES')
 v=read(pause);need(v['request']==REQUEST and v['result']['state']=='ZERO_START_HOLD'and 'AssertionError()'in v['result']['error']and v['model_retries']==0,'ONLY_OBSERVED_ZERO_START_PREPARE_PAUSE')
 old32=copy.deepcopy(reg['registered_future_requests'][OLD]);put(root/'BEFORE.fixed.json',dict(owner=owner,own96=q,own96_sha256=digest(q),old32=old32,old32_sha256=digest(old32),plan_sha256=sha(ROOT/'control/EXECUTION_PLAN.json'),authorization_sha256=sha(ROOT/'control/SCIENCE_AUTHORIZATION.json'),pause=v,pause_sha256=sha(pause),live_resource_and_Gates=gates))
 e.update_authority(lambda current:cas_arm(current,q,old32))
 after=e.authority()[0];now=after['registered_future_requests'][REQUEST];expected=copy.deepcopy(q);expected['state']='ARMED'
 need(now==expected and after['registered_future_requests'][OLD]==old32,'POST_AMENDMENT_EXACT_STATE_ONLY')
 observe_owner(plan);need(sha(pause)==release['zero_start_pause_sha256'],'PAUSE_CHANGED_AFTER_CAS_RETAIN_HOLD')
 # Existing scheduler file-control semantics: preserve this exact evidence,
 # never delete/reset an unrelated pause or touch its in-memory state.
 archived=root/'ORIGINAL_ZERO_START_ENGINEERING_PAUSE.json';os.rename(pause,archived)
 need(sha(archived)==release['zero_start_pause_sha256'],'ARCHIVED_PAUSE_PIN')
 put(root/'AFTER.fixed.json',dict(status='EXACT_OWN96_STATE_ARMED_AND_ZERO_START_PAUSE_PRESERVED',owner=owner,
    changed_fields=['registered_future_requests.'+REQUEST+'.state'],before_state=FROM,after_state=now['state'],budget=96,remaining=96,
    consumed=0,old32_sha256=digest(old32),own96_before_sha256=digest(q),own96_after_sha256=digest(now),pause_archive=str(archived),
    pause_archive_sha256=sha(archived),model_start_calls=0,registration_calls=0,controller_restart=False))
 return dict(status='METADATA_AMENDMENT_COMPLETE_SAME_OWNER_MAY_NATURALLY_CONTINUE',audit_directory=str(root))
def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument('--release',type=Path);a=p.parse_args(argv)
 if a.release is None:return dict(status='INERT_CPU_PREPARATION_ONLY',models=0,registrations=0,registry_writes=0)
 return run(read(a.release))
if __name__=='__main__':print(json.dumps(main(),sort_keys=True))
