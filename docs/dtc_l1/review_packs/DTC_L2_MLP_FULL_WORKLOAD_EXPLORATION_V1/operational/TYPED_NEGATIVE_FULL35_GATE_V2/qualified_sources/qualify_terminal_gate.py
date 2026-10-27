"""Small isolated CPU fixture using actual frozen consumer and 350 scope."""
import copy,hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path;HERE=P(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from terminal_gate import recommend,TYPED
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
E=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/E')
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def load(n,p):
 sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
consumer=load('terminal_fixture_actual_consumer',R/'tools/l2_results.py')
base=load('terminal_fixture_original_base',R/'tools/l2_adaptive.py')
v2=load('terminal_fixture_original_v2',E/'boundary_validation_v2/l2_boundary_validation.py')
scope=read(R/'control/MATRIX_CURRENT.json');assert len(scope['points'])==350
history=read(R/'control/SEARCH_HISTORY.json')
paths=dict(base=str(R/'tools/l2_adaptive.py'),supplement=str(E/'boundary_validation_v2/l2_boundary_validation.py'))
pins={k:sha(p)for k,p in paths.items()};checks=[]
gain={'E384':1.02,'E768':1.05,'M8':1.02,'M16':1.05,'Q64':1.02,'Q128':1.05}
records={}
for p in scope['points']:
 cycles=round(10**12/gain.get(p['profile'],1))
 records[p['cohort']]=dict(state=consumer.PASS,uuid='SYNTHETIC_CPU_ONLY',cycles=cycles,
  proof=dict(performance_accepted=True,cycles=cycles),archive={'SYNTHETIC_CPU_ONLY':True})
scan=next(p for p in scope['points']if p['program'].lower()=='scan'and p['profile']=='M16')
c=scan['cohort'];records[c]=dict(state=TYPED,uuid='SYNTHETIC_NEGATIVE_UUID',cycles=None)
summary=consumer.summarize(scope,records);prior=copy.deepcopy(summary)
def verify(row,cert):
 assert cert.get('synthetic_CPU_only')is True
 return dict(verified=True,cohort=row['cohort'],uuid=row['uuid'],performance_accepted=False,cycles=None,
  source_identity_verified=True,archive_verified=True,no_model_retry_verified=True,missing_done_exit_disclosed=True)
kwargs=dict(summary=summary,scope=scope,history=history,source_paths=paths,source_pins=pins,
 certificates={c:{'synthetic_CPU_only':True}},verify_certificate=verify)
out=recommend(**kwargs)
assert any(p['profile']=='M32'and p['evidence']['n']==34 for p in out['original_base_recommendation_retained']['proposals'])
assert any(p['proposal']['profile']=='M32'for p in out['blocked_common_subset_proposals'])
assert not any(p['profile']=='M32'for p in out['proposals'])
checks.append('original_V1_common34_M32_demonstrated_retained_for_audit_but_blocked')
assert all(not('M16'in p.get('evidence',{}).get('parents',[]))for p in out['proposals'])
assert any(n.get('action')=='BOUNDARY_FULL35_EVIDENCE_HOLD'and n.get('factor')=='merge'for n in out['supplementary_decisions'])
checks.append('M16_negative_holds_merge_boundary_and_never_infers_from_missing_input')
assert all(any(p['profile']==n and p['new_cell_count']==35 for p in out['proposals'])for n in ('E1536','Q256','E768_M8'))
checks.append('other_complete35_boundaries_and_M8_combination_continue_without_newtrial')
assert any(p['cells']==['CH']and p['new_cell_count']==35 for p in out['proposals'])
assert summary==prior and not summary['table'][scan['input_digest']]['M16']['DH']['accepted']
assert summary['aggregates']['M16']['ALL']['DH_speedup']['n']==34
assert not out['scientific_stage_complete']and out['requires_engineering_review']
checks.append('original34coverage_preserved_CH35_matches_continue_final_review_not_cleared')
for value in ({}, {c:{'synthetic_CPU_only':False}}):
 try:recommend(**dict(kwargs,certificates=value))
 except (KeyError,AssertionError):pass
 else:raise AssertionError('unverified typed negative admitted')
checks.append('missing_or_invalid_engineering_certificate_fails_closed')
engineering=copy.deepcopy(summary);engineering['table'][scan['input_digest']]['M16']['DH']['state']='ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS'
e=recommend(**dict(kwargs,summary=engineering,certificates={}))
assert not e['proposals']and any(n['action']=='WAIT_INITIAL_ALL35_TERMINAL'for n in e['supplementary_decisions'])
checks.append('ordinary_pending_engineering_event_still_blocks_initial_terminal')
assert TYPED not in base.TERMINAL_NEGATIVE and TYPED not in v2.NEGATIVE
checks.append('existing_module_instances_and_frozen_sources_unchanged')
result=dict(status='PASS',count=len(checks),checks=checks,source_pins=pins,
 source_sha256=sha(HERE/'terminal_gate.py'),original_negative_coverage=34,
 proposal_examples=[dict(profile=p['profile'],phase=p['phase'],n=p['new_cell_count'])for p in out['proposals']],
 source_identity='actual scope / consumer schema, synthetic CPU cycles and certificate only',
 production_installed=False,models_started=0,registry_grants=0,production_mutations=0)
(HERE/'CPU_QUALIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
