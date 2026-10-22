"""Exact user-approved E2 r5 build preparation through the original resource API.
No applications/Q/policy projection, new controller, automatic lease or mutation.
"""
import copy,hashlib,json
from pathlib import Path
CAMPAIGN='EPL2_MECHANISM_STUDY_20261019_V1';FIELD='mechanism_study_20261019_v1';GIB=2**30
PREP_AUTHORITY_REF=None  # Root seals realsource/approval before publishedCLIENT activation.
CORE_PATH='/workspace/worktrees/gpgpu-sim-ep-l2-ms20261022-e2-tagpressure-r5-v1'
FRAMEWORK_PATH='/workspace/worktrees/accel-sim-ep-l2-ms20261021-a2-large-capacity-runtime-v1'
BUILD_PATH='/workspace/build/ep-l2-ms20261022-e2-tagpressure-observer-r5'
FRAMEWORK='9dd1ee57a83d83b56b7874bc7c716185ab52c8f7';VENDOR='f90c430c3a1ce8f08c09942a5a1c3a797bb2295b';BASE='9243f769620653f2a9d4df5599e9581e9dae6067'
ACTIVE={'RESERVED','RUNNING','START_INTENT_UNRECONCILED'}
MAPS=('qualifications','accepted_results','accepted_pairs','input_selections','scientific_holds')
HISTORIES=('scientific_hold_history','scientific_hold_resolution_history')
DYNAMIC={'controller','attempts','actual_starts','uncertain_start_intents','remaining_start_capacity',*MAPS,*HISTORIES}

def require(ok,message):
 if not ok:raise ValueError(message)
def sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def read(ref):
 p=Path(ref['path']);require(p.is_file() and p.stat().st_size<=4*2**20,'bounded exact prep metadata absent');b=p.read_bytes();require(hashlib.sha256(b).hexdigest()==ref['sha256'],'prep metadata changed '+str(p));return json.loads(b)
def is_e2_build(role,kind):return role=='E' and kind=='build'
def is_E(row):return row.get('role')=='E' or row.get('executor_role')=='E' or row.get('owner')=='mechanism_E'
def is_target_build(row):return row.get('output_directory')==BUILD_PATH

def seal55(data,item):
 require(len(item['attempts'])==item['actual_starts']==55,'seal only real completed55')
 return dict(attempts_sha256=sha(item['attempts']),baseline_ledger_keys=sorted(item),
  maps={g:{k:sha(v) for k,v in item.get(g,{}).items()} for g in MAPS},
  histories={g:dict(length=len(item.get(g,[])),sha256=sha(item.get(g,[]))) for g in HISTORIES},
  immutable={k:sha(v) for k,v in item.items() if k not in DYNAMIC},
  canonical_runs={k:sha(v) for k,v in data['runs'].items() if v.get('experiment_id')==CAMPAIGN},
  baseline_resource_lease_keys=sorted(data['resource_leases']),
  old_E_resource_leases={k:sha(v) for k,v in data['resource_leases'].items() if v.get('experiment_id')==CAMPAIGN and is_E(v)})

def validate_manifest(m):
 a=read(m['approval_ref']);proposal=read(m['proposal_ref'])
 require(m['schema']=='E2_R5_PREPARATION_BUILD_AUTHORITY_V1' and m['status']=='E2_R5_PREPARATION_SOURCE_SEALED_NO_APP_AUTHORITY','prep seal absent')
 require(a['schema']=='E2_R5_EXACT_TARGET_SET_JOINT_FOUR_USER_APPROVAL_V1' and a['status']=='USER_APPROVED_R5_ENGINEERING_AND_PRIMARY_FOUR_ONLY' and a['synthetic_fixture'] is False,'real exact userapproval required')
 require(m['campaign_id']==a['campaign_id']==CAMPAIGN and a['baseline_actual_starts']==m['baseline_actual_starts']==55 and a['maximum_new_actual_starts']==4 and a['maximum_actual_starts_if_all_four_started']==59,'original55/exact4 approval')
 require(m['approval_ref']['sha256']=='b66c91254560b6a1ea3843de2ea5aa31f3a0cd58fcfd1b1c9d3a09e98d15c44b','wrong actual user approval')
 require(m['proposal_ref']['sha256']==a['proposal_ref']['sha256'] and proposal['maximum_new_actual_starts']==4,'proposal exact scope')
 require(m['core_worktree']==CORE_PATH and m['framework_worktree']==FRAMEWORK_PATH and m['output_directory']==BUILD_PATH,'only isolated named r5 paths')
 b=m['build_identity'];require(set(b)=={'core_source_commit','framework_source_commit','vendor_pybind11_commit','build_spec_sha256'},'prep sourceidentity fields only, no fake main/archive')
 import re
 require(re.fullmatch('[0-9a-f]{40}',b['core_source_commit']) and b['core_source_commit']!=BASE,'new realisolated Core commit required')
 require(b['framework_source_commit']==FRAMEWORK and b['vendor_pybind11_commit']==VENDOR and b['build_spec_sha256']==m['build_spec_ref']['sha256'],'fixed Framework/vendor/buildspec')
 read(m['build_spec_ref'])
 r=m['resource_envelope'];require(r==dict(role='E',kind='build',cpu_max=2,memory_bytes=8*GIB,growth_max_bytes=GIB,result_growth_bytes=0,workspace_floor_bytes=5*GIB,monitor_margin_bytes=2*GIB),'exact bounded E2 build envelope')
 require(m['formal_build_owner']=='E2_R5_FORMAL_PRODUCER' and m['applications_authorized_by_preparation']==0 and m['registration_authorized_by_preparation'] is False,'preparation cannot launch/register')
 require(a['new_generation_limit_bytes']==10*GIB and a['total_generation_limit_bytes']==24*GIB and a['workspace_floor_bytes']==5*GIB and a['monitor_margin_bytes']==2*GIB,'frozen output/disk policy')
 return m

def authority():
 require(PREP_AUTHORITY_REF is not None,'E2_R5_PREPARATION_AUTHORITY_UNBOUND')
 return validate_manifest(read(PREP_AUTHORITY_REF))

def history_preserved(m,data,item):
 h=m['historical55_seal'];require(item['campaign_id']==CAMPAIGN and item['t0_unix']==1792414193,'original campaign/T0')
 require(len(item['attempts'])>=55 and sha(item['attempts'][:55])==h['attempts_sha256'],'old55 prefix changed')
 for k,digest in h['immutable'].items():require(k in item and sha(item[k])==digest,'old55 immutable changed '+k)
 for group,records in h['maps'].items():require(all(k in item.get(group,{}) and sha(item[group][k])==v for k,v in records.items()),'old55 map record changed '+group)
 for group,record in h['histories'].items():require(len(item.get(group,[]))>=record['length'] and sha(item.get(group,[])[:record['length']])==record['sha256'],'old55 history changed '+group)
 for k,digest in h['canonical_runs'].items():require(k in data['runs'] and sha(data['runs'][k])==digest,'old55 canonical run changed')
 for k,digest in h['old_E_resource_leases'].items():require(k in data['resource_leases'] and sha(data['resource_leases'][k])==digest,'historical E lease changed')
 return True

def quiescent55(m,data,item):
 history_preserved(m,data,item)
 require(len(item['attempts'])==item['actual_starts']==55 and item.get('uncertain_start_intents',0)==0,'prep only before exact55 successor start')
 require(item['controller']['state']=='STOPPED','original controller mustSTOPPED')
 require(set(item)==set(m['historical55_seal']['baseline_ledger_keys']),'prep cannot add scientificnamespace')
 require(all(set(item.get(g,{}))==set(records) for g,records in m['historical55_seal']['maps'].items()),'prep cannot add Q/result/input/scientific records')
 require(not any(r.get('experiment_id')==CAMPAIGN and r.get('status') in ACTIVE for r in data['runs'].values()),'active originalcampaign simulator')
 require(not any(r.get('experiment_id')==CAMPAIGN and is_E(r) and r.get('status') in ACTIVE for r in data['resource_leases'].values()),'active E lease prevents new preparation build')
 return True

def authorize(data,item,role,kind,cpu,memory,growth,directory,result_growth,disk_authorization_id,build_identity):
 m=authority();quiescent55(m,data,item)
 require(is_e2_build(role,kind) and disk_authorization_id is None,'E2 prep cannot use namedA exception')
 require(str(Path(directory).resolve())==m['output_directory'],'wrong E2r5 output path')
 require(type(cpu) is int and 1<=cpu<=2 and type(memory) is int and memory==8*GIB and type(growth) is int and 0<growth<=GIB and result_growth==0,'outside bounded E2r5 build reservation')
 require(build_identity==m['build_identity'],'real isolated source/buildspec identity mismatch')
 require(item['workspace_disk_policy']['disk_floor_bytes']==5*GIB and item['workspace_disk_policy']['monitor_reserve_bytes']==2*GIB,'ordinary5+2 disk policy only')
 return dict(build_owner='E2_R5_FORMAL_PRODUCER',executor_role='E',build_identity=copy.deepcopy(build_identity),r5_preparation_authority_ref=copy.deepcopy(PREP_AUTHORITY_REF),r5_preparation_approval_ref=copy.deepcopy(m['approval_ref']),r5_preparation_scope='BUILD_ONLY_NO_APP_OR_Q_AUTHORITY')

def crosscheck(data,item):
 rows=[(k,r) for k,r in data.get('resource_leases',{}).items() if r.get('experiment_id')==CAMPAIGN and (r.get('r5_preparation_authority_ref') is not None or is_target_build(r) or (is_E(r) and r.get('kind')=='MECHANISM_BUILD'))]
 if PREP_AUTHORITY_REF is None:
  require(not rows,'unbound E2r5 prep rows present');return False
 m=authority();history_preserved(m,data,item);active=0
 for k,r in rows:
  require(r.get('r5_preparation_authority_ref')==PREP_AUTHORITY_REF and r.get('r5_preparation_approval_ref')==m['approval_ref'],'markerless/foreign E2r5 build row')
  require(r.get('role')==r.get('executor_role')=='E' and r.get('owner')=='mechanism_E' and r.get('build_owner')=='E2_R5_FORMAL_PRODUCER' and r.get('kind')=='MECHANISM_BUILD','E2 formalproducer lease attribution')
  require(r.get('output_directory')==BUILD_PATH and r.get('build_identity')==m['build_identity'],'E2 prep source/path changed')
  require(type(r.get('cpu_units')) is int and 1<=r['cpu_units']<=2 and r.get('memory_bytes')==8*GIB and type(r.get('disk_growth_bytes')) is int and 0<r['disk_growth_bytes']<=GIB and r.get('result_growth_bytes')==0,'E2 prep resource row changed')
  require(r.get('disk_floor_bytes')==5*GIB and r.get('monitor_reserve_bytes')>=2*GIB and not r.get('disk_authorization_id'),'E2 prep guard weakened')
  require(r.get('status') in {'RESERVED','RUNNING','RELEASED'},'unknown E2prep lease lifecycle')
  if r['status'] in ACTIVE:active+=1
 require(active<=1,'two active E2r5 build leases')
 return True
