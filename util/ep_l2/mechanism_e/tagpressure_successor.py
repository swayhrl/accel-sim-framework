"""Source-bound exact four F-only successor, original central APIs only.

Default unbound. Historical55 is validated before any projection; all new Q,
specs, attempted starts and canonical rows are checked independently. The view
exists only for old scientific guards, never resource admission or persistence.
"""
import copy,hashlib,json
from pathlib import Path
import tagpressure_runtime_identity as runtime_identity
from detach_scope_core import CAMPAIGN,sha,spec_sha,require
SCI_SCOPE="TAGPRESSURE_OBSERVER_DIAGNOSTIC_POINT_V1"
import tagpressure_validation as detach_validation
FIELD='tagpressure_observer_successor_batch'
FINAL_SUCCESSOR_REF={'path': '/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/docs/ep_l2/review_packs/MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1/approved_r5_joint_r1/FINAL_MANIFEST.json', 'sha256': '25d1b8cf8b80d53bfe677f58d5273f35115cf40599660b1c0038a9be7ed58b69'}  # Root only: seal real new r5 release/Q/source after qualification.
_SCOPE=None
CONDITIONS=('V8_TAGPRESSURE_cfd_097k_F','V8_TAGPRESSURE_dwt2d_F','V8_TAGPRESSURE_vectorAdd_4M_F','V8_TAGPRESSURE_convolutionSeparable_F')
SELECTIONS=('D_V2_cfd_097k','D_V1_dwt2d','D_V2_vectorAdd_4M','D_V1_convolutionSeparable')
ACTIVE={'RESERVED','RUNNING','START_INTENT_UNRECONCILED'}
BEFORE={'RESERVED','START_INTENT_UNRECONCILED','FAILED_SPAWN','CANCELLED_BEFORE_START'}
AFTER={'RUNNING','COMPLETE_VALID','FAILED','TIMEOUT','RESOURCE_LIMIT','INCOMPLETE'}
MAPS=('qualifications','accepted_results','accepted_pairs','input_selections','scientific_holds')
HISTORIES=('scientific_hold_history','scientific_hold_resolution_history')
DYNAMIC={'controller','attempts','actual_starts','uncertain_start_intents','remaining_start_capacity',FIELD,*MAPS,*HISTORIES}
CAP=384*2**20

def file_ref(path):
 p=Path(path);require(p.stat().st_size<4*2**20,'bounded metadata only');b=p.read_bytes()
 return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest())
def read(ref):
 require(file_ref(ref['path'])['sha256']==ref['sha256'],'successor metadata changed: '+ref['path'])
 return json.loads(Path(ref['path']).read_text())
def has(item):return FIELD in item
def is_spec(spec):return spec.get('condition_id') in CONDITIONS

def historical55_seal(item,data):
 require(len(item['attempts'])==item['actual_starts']==55,'exact baseline55 required')
 return dict(attempts_sha256=sha(item['attempts']),
  maps={g:{k:sha(v) for k,v in item.get(g,{}).items()} for g in MAPS},
  histories={g:dict(length=len(item.get(g,[])),sha256=sha(item.get(g,[]))) for g in HISTORIES},
  immutable={k:sha(v) for k,v in item.items() if k not in DYNAMIC},
  baseline_keys=sorted(item),
  canonical_runs={k:sha(v) for k,v in data['runs'].items() if v.get('experiment_id')==CAMPAIGN})

class Scope:
 def __init__(self,ref,*,fixture_mode=False):self.ref=copy.deepcopy(ref);self.fixture_mode=fixture_mode
 def manifest(self):
  m=read(self.ref);a=read(m['approval_ref']);p=read(m['proposal_ref'])
  require(m['schema']=='E2_R5_EXACT_TAGPRESSURE_FOUR_SUCCESSOR_V1' and m['status']=='E_NEW_R5_SOURCE_BOUND_PRIMARY_FOUR_SEALED','real r5 source seal required')
  require(m.get('synthetic_fixture') is self.fixture_mode and a.get('synthetic_fixture') is self.fixture_mode,'synthetic metadata forbidden in production')
  require(a['schema']=='E2_R5_EXACT_TARGET_SET_JOINT_FOUR_USER_APPROVAL_V1' and a['status']=='USER_APPROVED_R5_ENGINEERING_AND_PRIMARY_FOUR_ONLY','exact r5 userapproval')
  require(self.fixture_mode or m['approval_ref']['sha256']=='b66c91254560b6a1ea3843de2ea5aa31f3a0cd58fcfd1b1c9d3a09e98d15c44b','wrong real approval')
  require(m['campaign_id']==a['campaign_id']==CAMPAIGN and m['baseline_actual_starts']==a['baseline_actual_starts']==55,'original campaign/exact55')
  require(m['maximum_new_actual_starts']==a['maximum_new_actual_starts']==4 and a['maximum_actual_starts_if_all_four_started']==59,'exact four only')
  require(m['condition_order']==a['approved_conditions']==list(CONDITIONS) and set(m['conditions'])==set(CONDITIONS),'exact four identity/order')
  require(m['batch_id']==a['batch_id'] and m['pairs']==[] and a['automatic_retry_authorized'] is False and a['proposal_union_authorized'] is False and a['build_only_alternative_authorized'] is False,'no retry/pair/union')
  require(m['endpoint_result_hardcap_bytes']==a['endpoint_result_hardcap_bytes']==CAP and m['all_four_endpoint_results_hardcap_bytes']==a['all_four_endpoint_results_hardcap_bytes']==4*CAP,'endpoint cap exact')
  require(m['new_observer_output_hardcap_bytes']==a['new_observer_output_hardcap_bytes']==64*2**20 and m['collector_metadata_forecast_bytes']==a['collector_metadata_forecast_bytes']==640*2**20,'observer/metadata exact caps')
  require(a['original_T0']==1792414193 and a['operational_global_count_route_timeout_deadline_restored'] is False,'T0/no restored limits')
  require(a['new_generation_limit_bytes']==10*2**30 and a['total_generation_limit_bytes']==24*2**30 and a['workspace_floor_bytes']==5*2**30 and a['monitor_margin_bytes']==2*2**30,'original output/resource policy')
  require(m['proposal_ref']['sha256']==a['proposal_ref']['sha256'],'exact approved proposal')
  proposed={r['new_condition_id']:r for r in p['conditions']};require(set(proposed)==set(CONDITIONS),'proposal exact4')
  source=m['source_identity'];require(source['core_source_commit']!='9243f769620653f2a9d4df5599e9581e9dae6067' and source['binary_sha256']!='d99ac88d60a596b123765009420a85eea1463c01e88807a8876ae946e380fd13','old r4 producer cannot substitute')
  scope=m['validation_scope'];require(scope['source_identity']==source and scope['scientific_scope']==SCI_SCOPE and scope['pair'] is False and scope['synthetic_fixture'] is self.fixture_mode,'new source validator scope')
  require(scope['fixed_r4_decoder']['sha256']=='647510163053d30773176578cf35c10e0aea0a1256af366feba520820d0e11d4' or self.fixture_mode,'old212 byte grammar compatibility only')
  for key in ('formal_producer_release','independent_native_review','emitter_byte_compatibility_proof','new_source_independent_review'):read(m[key])
  for cid,selection in zip(CONDITIONS,SELECTIONS):
   c=m['conditions'][cid];r=proposed[cid]
   require(c['selection_id']==r['selection_id']==selection and r['maximum_real_starts']==1,'input/one start exact')
   saved=read(c['spec_ref']);require(saved['identity']==c['identity'],'manifest/spec actual identity differs')
   rebind=runtime_identity.frozen_scientific_identity(saved,r,c['runtime_identity_rebind'])
   require(saved['runtime_identity_rebind']==rebind,'manifest/spec engineering runtime rebind differs')
   require(c['resources']==dict(cpu=1,memory_bytes=9*2**30,maximum_result_bytes=CAP) and c['metadata_forecast_bytes']==160*2**20,'exact new resource envelope/metadata')
  return m
 def legacy_view(self,item):
  """Validate immutable old55 and all additional keys before filtering extras."""
  m=self.manifest();h=m['historical55_seal']
  require(item['campaign_id']==CAMPAIGN and item['t0_unix']==1792414193,'original campaign/T0')
  require(55<=len(item['attempts'])<=59 and sha(item['attempts'][:55])==h['attempts_sha256'],'original55 prefix changed')
  require(set(item)<=set(h['baseline_keys'])|{FIELD},'unapproved ledger namespace')
  for k,v in h['immutable'].items():require(k in item and sha(item[k])==v,'old immutable record changed: '+k)
  for group,records in h['maps'].items():
   require(all(k in item.get(group,{}) and sha(item[group][k])==v for k,v in records.items()),'old map record changed: '+group)
  for group,record in h['histories'].items():
   rows=item.get(group,[]);n=record['length'];require(len(rows)>=n and sha(rows[:n])==record['sha256'],'old history prefix changed')
  require(set(item.get(FIELD,{}))<={'manifest_ref','bindings','attempt_ids','start_witnesses','metadata_closures'},'extra r5 batch namespace')
  extra_q=set(item['qualifications'])-set(h['maps']['qualifications']);allowed_q={x['qualification']['sha256'] for x in m['conditions'].values()}
  require(extra_q<=allowed_q,'unapproved new qualification')
  for c in m['conditions'].values():
   qid=c['qualification']['sha256']
   if qid in item['qualifications']:
    row=item['qualifications'][qid]
    require(row['path']==c['qualification']['path'] and row['sha256']==qid and row['qualification']==read(c['qualification']),'new Q row/bytes changed')
  require(set(item['input_selections'])==set(h['maps']['input_selections']) and set(item['accepted_pairs'])==set(h['maps']['accepted_pairs']),'new input/pair forbidden')
  allowed_holds={'qualification:'+q for q in allowed_q};extra_holds=set(item['scientific_holds'])-set(h['maps']['scientific_holds'])
  require(extra_holds<=allowed_holds,'unrelated qualification HOLD')
  for group in HISTORIES:
   for row in item.get(group,[])[h['histories'][group]['length']:]:require(row.get('qualification_id') in allowed_q,'unrelated new history')
  tail=item['attempts'][55:];batch=item.get(FIELD)
  require(batch is not None and batch['manifest_ref']==self.ref,'new scope not adopted/exact bound')
  require(batch['attempt_ids']==[a['attempt_id'] for a in tail] and len(set(batch['attempt_ids']))==len(tail),'tail accounting mismatch')
  require(set(batch['bindings'])<=set(CONDITIONS) and set(batch['start_witnesses'])<=set(CONDITIONS),'extra binding/witness')
  seen=set()
  for a in tail:
   cid=a.get('condition_id');require(cid in CONDITIONS and cid not in seen,'duplicate/extra condition; no retry');seen.add(cid)
   c=m['conditions'][cid];saved=read(c['spec_ref']);b=batch['bindings'].get(cid)
   require(a['profile']=='F' and a['labels']==saved['labels'] and a['comparison_group']==saved['comparison_group'],'tail profile/labels/comparison metadata differs')
   require(b==dict(identity=c['identity'],spec_sha256=c['spec_sha256'],qualification_id=c['qualification']['sha256']),'unbound/changed condition')
   require(a['identity']==c['identity'] and a['run_key']==sha(c['identity']) and a['qualification_id']==c['qualification']['sha256'] and a['diagnostic_spec_sha256']==c['spec_sha256'],'tail source/spec/Q mismatch')
   require(a['selection_id']==c['selection_id'] and a['budget_bucket']==m['batch_id'] and a['scientific_scope']==SCI_SCOPE and a['maximum_result_bytes']==CAP,'tail input/scope/resource changed')
   require(a['state'] in BEFORE|AFTER and a['actual_start'] is (a['state'] in AFTER),'state/start charge mismatch')
   retained=any(k in a for k in ('process','started_unix','started_identity','immutable_started_marker'))
   require(not retained or a['actual_start'] is True,'retained process/start forbids refund')
   witness=batch['start_witnesses'].get(cid)
   if a['actual_start']:
    expected=dict(attempt_id=a['attempt_id'],run_key=a['run_key'],process=a['process'],started_unix=a['started_unix'])
    require(witness==expected and a['started_identity']==a['process'] and a['immutable_started_marker']==sha(expected),'paid start witness mismatch')
   else:require(witness is None,'witness forbids refund')
  require(set(batch['start_witnesses'])=={a['condition_id'] for a in tail if a['actual_start']},'orphan start witness')
  require(item['actual_starts']==sum(a.get('actual_start') is True for a in item['attempts']),'actual-start recount mismatch')
  require(item['uncertain_start_intents']==sum(a['state']=='START_INTENT_UNRECONCILED' for a in item['attempts']),'uncertain intent recount mismatch')
  extra_results=set(item['accepted_results'])-set(h['maps']['accepted_results'])
  require(extra_results<={a['attempt_id'] for a in tail if a['state']=='COMPLETE_VALID'},'unaccepted/extra diagnostic result')
  for a in tail:
   if a['attempt_id'] in extra_results:
    r=item['accepted_results'][a['attempt_id']]
    require(r['identity']==a['identity'] and r['run_key']==a['run_key'] and r['qualification_id']==a['qualification_id'] and r['scientific_scope']==SCI_SCOPE and r['path']==a['receipt_path'] and r['sha256']==a['receipt_sha256'],'accepted endpoint pointer mismatch')
  view=copy.deepcopy(item);view.pop(FIELD,None);view['attempts']=copy.deepcopy(item['attempts'][:55]);view['actual_starts']=55;view['uncertain_start_intents']=0;view['remaining_start_capacity']=None
  for group,records in h['maps'].items():view[group]={k:copy.deepcopy(item[group][k]) for k in records}
  for group,record in h['histories'].items():view[group]=copy.deepcopy(item.get(group,[])[:record['length']])
  return view
 def active(self,item,legacy_active):
  view=self.legacy_view(item);require(legacy_active(view),'old original55 authority failed');return True
 def check_spec(self,spec):
  m=self.manifest();cid=spec.get('condition_id');require(cid in CONDITIONS,'unapproved condition')
  c=m['conditions'][cid];saved=read(c['spec_ref'])
  require(spec_sha(spec)==c['spec_sha256']==spec_sha(saved) and spec['identity']==c['identity'],'exact approved spec/identity changed')
  require(spec['campaign_id']==CAMPAIGN and spec['launch_owner']=='E' and spec['budget_bucket']==m['batch_id'] and spec['scientific_scope']==SCI_SCOPE,'exact campaign/owner/scope/bucket')
  require(spec['selection_id']==c['selection_id'] and spec['profile']=='F' and not spec.get('retry_previous_attempt') and not spec.get('retry_reason') and not spec.get('pair_id') and spec.get('pairs',[])==[],'F only no retry/pair')
  require(all(spec[k]==v for k,v in c['resources'].items()),'exact endpoint resource budget')
  require(spec['timeout_seconds'] is None,'old operational time cap not restored')
  q=read(c['qualification']);require(spec['qualification_id']==c['qualification']['sha256'],'exact per-input Q')
  require(q['status']=='INDEPENDENTLY_QUALIFIED' and q['qualified_by']=='E' and q['synthetic_fixture'] is self.fixture_mode and q['source_identity']==m['source_identity'] and q['scientific_scope']==SCI_SCOPE,'new independent Q/source required')
  require(q['input_selection_id']==c['selection_id'] and spec['profile_semantics']==q['supported_profiles']['F']==q['profile_semantics'] and spec['labels']==spec['profile_semantics']['labels'],'per-input independently qualified F profile')
  require(spec['profile_semantics']['research_switches']==dict.fromkeys(('W','V','T','M'),1),'full finite F')
  contract=q['detach_observer_diagnostic'];require(contract['validation_scope']==m['validation_scope'],'common decoder binding differs')
  require(q.get('runtime_identity_rebind')==spec.get('runtime_identity_rebind')==c.get('runtime_identity_rebind'),'new Q/spec runtime engineering rebind differs')
  require(contract['trace_content_sha256']==spec['identity']['trace_content_sha256'] and contract['runtime_config_sha256']==spec['identity']['runtime_config_sha256'] and contract['input_selection_id']==spec['selection_id'] and contract['termination_contract']==spec['identity']['termination_contract'],'per-input full contract differs')
  proposed={r['new_condition_id']:r for r in read(m['proposal_ref'])['conditions']}
  require(contract['expected_full_instructions']==saved['input_scope_admission']['expected_full_instructions'] and spec['parser']==c['parser']==q['terminal_parser'],'full denominator/actual terminal CLI required')
  require(spec.get('maximum_added_observer_output_bytes')==64*2**20,'observer substream cap exact')
  require(spec['environment'].get('EPL2_DETACH_DIAG')=='1' and spec['environment'].get('EPL2_TAGPRESSURE_DIAG')=='1','observer env required')
  require(all(spec['identity'][k]==m['source_identity'][k] for k in ('core_source_commit','framework_source_commit','binary_sha256')) and spec['vendor_pybind11_commit']==m['source_identity']['vendor_pybind11_commit'],'actual formal source binding')
  for ref in c['content_refs']+[spec['parser']]:file=Path(ref['path']);require(file_ref(file)['sha256']==ref['sha256'],'config/asset/source binding changed')
  return c,q
 def adopt(self,item,data,source_leases,legacy_active):
  m=self.manifest()
  if has(item):self.active(item,legacy_active);return False
  require(item['controller']['state']=='STOPPED' and len(item['attempts'])==item['actual_starts']==55,'completed51 STOPPED adoption only')
  require(not any(a['state'] in ACTIVE for a in item['attempts']) and not any(r['status'] in ACTIVE for r in source_leases),'active source/science work')
  require(historical55_seal(item,data)==m['historical55_seal'],'adoption51 snapshot changed')
  item[FIELD]=dict(manifest_ref=self.ref,bindings={},attempt_ids=[],start_witnesses={},metadata_closures={})
  self.active(item,legacy_active);return True
 def bind(self,item,spec,legacy_active):
  self.active(item,legacy_active);c,q=self.check_spec(spec);cid=spec['condition_id'];b=item[FIELD]
  require(not any(a['condition_id']==cid for a in item['attempts'][55:]),'consumed binding cannot change')
  qrow=item['qualifications'].get(spec['qualification_id']);require(qrow is not None and qrow['path']==c['qualification']['path'] and qrow['sha256']==c['qualification']['sha256'] and qrow['qualification']==q,'Q not registered exactly')
  binding=dict(identity=c['identity'],spec_sha256=c['spec_sha256'],qualification_id=c['qualification']['sha256']);require(cid not in b['bindings'] or b['bindings'][cid]==binding,'binding immutable');b['bindings'][cid]=binding;return binding
 def scope_allowed(self,item,spec,legacy_active):
  self.active(item,legacy_active);c,q=self.check_spec(spec)
  return item[FIELD]['bindings'].get(spec['condition_id'])==dict(identity=c['identity'],spec_sha256=c['spec_sha256'],qualification_id=c['qualification']['sha256'])
 def guard(self,item,spec,legacy_active):
  require(self.scope_allowed(item,spec,legacy_active),'condition not bound')
  require(not any(a['condition_id']==spec['condition_id'] for a in item['attempts'][55:]),'condition consumed/no retry')
  require('qualification:'+spec['qualification_id'] not in item['scientific_holds'],'exact Q HOLD')
 def record_reservation(self,item,spec,attempt,legacy_active):
  self.guard(item,spec,legacy_active);attempt.update(condition_id=spec['condition_id'],diagnostic_spec_sha256=spec_sha(spec),scientific_scope=SCI_SCOPE);item[FIELD]['attempt_ids'].append(attempt['attempt_id'])
 def record_started(self,item,attempt):
  cid=attempt['condition_id'];w=item[FIELD]['start_witnesses'];require(cid not in w,'duplicate start charge')
  witness=dict(attempt_id=attempt['attempt_id'],run_key=attempt['run_key'],process=copy.deepcopy(attempt['process']),started_unix=attempt['started_unix'])
  attempt.update(started_identity=copy.deepcopy(attempt['process']),immutable_started_marker=sha(witness));w[cid]=witness
 def crosscheck(self,data,item,legacy_active,legacy_crosscheck):
  view=self.legacy_view(item);legacy_active(view);m=self.manifest();old=m['historical55_seal']['canonical_runs']
  for key,digest in old.items():require(key in data['runs'] and sha(data['runs'][key])==digest,'original canonical run changed')
  tail=item['attempts'][55:];expected={a['run_key']:a for a in tail}
  rows={k:r for k,r in data['runs'].items() if r.get('experiment_id')==CAMPAIGN and k not in old}
  require(set(rows)==set(expected),'canonical successor tail mismatch')
  for key,a in expected.items():
   r=rows[key];c=m['conditions'][a['condition_id']];policy=item['workspace_disk_policy']
   require(r.get('cpu_units')==c['resources']['cpu'] and r.get('memory_bytes')==c['resources']['memory_bytes'] and r.get('disk_growth_bytes')==c['resources']['maximum_result_bytes'] and r.get('disk_floor_bytes')==5*2**30 and r.get('monitor_reserve_bytes')==2*2**30 and r.get('policy_id')==policy['policy_id'],'canonical resource reservation changed')
   require(r['run_key']==key and r['lease_id']==a['attempt_id'] and r['identity']==a['identity'] and r['qualification_id']==a['qualification_id'] and r['condition_id']==a['condition_id'] and r['diagnostic_spec_sha256']==a['diagnostic_spec_sha256'] and r['scientific_scope']==SCI_SCOPE and r['budget_bucket']==a['budget_bucket'],'canonical exact binding mismatch')
   if a['state'] in ('RESERVED','START_INTENT_UNRECONCILED'):require(r['status']=='RESERVED' and not r.get('process') and not r.get('started_unix'),'canonical process forbids refund')
   elif a['state'] in ('FAILED_SPAWN','CANCELLED_BEFORE_START'):require(r['status']=='FAILED' and not r.get('process') and not r.get('started_unix'),'canonical failure start refund')
   else:require(r['status']==a['state'] and r.get('process')==a['process'] and r.get('started_unix')==a['started_unix'],'canonical lifecycle mismatch')
  import tagpressure_metadata
  tagpressure_metadata.remaining(item,scope=self)
  # Only the pure old science checker sees this projection. Physical resource
  # admission continues to receive the complete original data/leases/runs.
  historical_data=dict(data,runs={k:v for k,v in data['runs'].items() if k not in rows})
  legacy_crosscheck(historical_data,view);return True

def scope():
 global _SCOPE
 if _SCOPE is None:
  require(FINAL_SUCCESSOR_REF is not None,'EXACT_PRIMARY_FOUR_SUCCESSOR_UNBOUND');_SCOPE=Scope(FINAL_SUCCESSOR_REF)
 return _SCOPE

def is_q(q):return q.get('scientific_scope')==SCI_SCOPE and q.get('input_selection_id') in SELECTIONS

def qualification(q,digest):
 s=scope();m=s.manifest();matches=[c for c in m['conditions'].values() if read(c['qualification'])==q]
 require(len(matches)==1,'Q not exact approved per-input qualification')
 c=matches[0];spec=read(c['spec_ref']);s.check_spec(spec)
 require(s.fixture_mode or detach_validation.INDEPENDENT_SCHEMA_VALIDATION_READY,'new exact decoder not initialized')
 return True

def prepare_validator(qrow,spec,digest):
 s=scope();c,q=s.check_spec(spec);expected=c['qualification'];binding=s.manifest()['validation_scope']
 require(qrow['sha256']==spec['qualification_id']==expected['sha256'] and Path(qrow['path']).resolve()==Path(expected['path']).resolve() and qrow['qualification']==q,'exact new registered Q/spec binding')
 if detach_validation.INDEPENDENT_SCHEMA_VALIDATION_READY:
  require(detach_validation._ADAPTER is not None and detach_validation._BINDING==binding,'different existing adapter binding')
 else:
  require(detach_validation._ADAPTER is None and detach_validation._BINDING is None,'partial adapter cannot change')
  detach_validation.configure_binding(binding)
 detach_validation._ADAPTER.check(spec,qrow)
 return dict(status='SYNTHETIC_BINDING_CHECK_ONLY' if s.fixture_mode else 'ADAPTER_BINDING_READY')

def queue_guard(item,queue,digest,legacy_active):
 s=scope();s.active(item,legacy_active);require(queue.get('pairs',[])==[],'F diagnostic cannot pair')
 specs=[]
 for ref in queue.get('specs',[]):
  spec=read(ref);require(is_spec(spec),'queue union/unapproved condition');s.check_spec(spec);specs.append(spec)
 ids=[x['condition_id'] for x in specs]
 require(0<len(ids)<=4 and len(ids)==len(set(ids)),'bounded unique qualified subset queue')
 require(ids==[c for c in CONDITIONS if c in ids],'CFD-first priority order')
 for spec in specs:require(s.scope_allowed(item,spec,legacy_active),'unbound qualified queue spec')
 return True
