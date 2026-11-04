import pathlib,json,hashlib,importlib.util,copy,sys,argparse
P=pathlib.Path(__file__).resolve().parent
def read(p):return json.loads(pathlib.Path(p).read_text())
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def load(p,name):
 sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
p=argparse.ArgumentParser();p.add_argument('group');args=p.parse_args();tag=args.group;g=read(P/'RECOVERY_GROUPS.json')['groups'][tag];r=pathlib.Path(g['new_runtime_root']);sys.path.insert(0,str(r));m=load(r/'ep_perf_native_wv_modes_draft.py','actual_recovery_engine_'+tag);contract=load(r/'mode_contract.py','actual_recovery_contract_'+tag)
idx=read(P/'bound'/tag/'SPEC_INDEX.json');files={z['cohort']:pathlib.Path(z['successor_spec_ref']['path'])for z in idx['rows']};root=pathlib.Path(g['data_ROOT']);canonical=lambda case:root/'cases'/case/'control/FROZEN_SPEC.json';specfile=lambda case:files.get(case,canonical(case));specs={case:read(specfile(case))for case in g['original_admitted_specs']}
rows=[]
def check(name,fn,negative=False):
 try:
  result=fn()
  if negative:raise AssertionError('negative unexpectedly accepted')
 except Exception as e:
  if not negative:raise
  if isinstance(e,AssertionError):raise
  rows.append(dict(name=name,status='PASS_EXPECTED_HOLD',reason=str(e)));return
 rows.append(dict(name=name,status='PASS'))
for case in g['unconsumed']:
 s=specs[case];check('actual_MainQ_static '+case,lambda s=s:contract.validate_static(s));check('actual_mixed_fair_pair '+case,lambda s=s:contract.validate_fair_pair(s,specs[s['same_background_peer_cohort']]))
registry=read('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json');registry=copy.deepcopy(registry);q=registry['registered_future_requests'][g['goal']]
for case,path in files.items():q['admitted_specs'][case]=sha(path)
engine=specs[g['unconsumed'][0]]['host_engine_ref'];common=specs[g['unconsumed'][0]]['host_common_ref'];q['runtime_versions'][engine['sha256']]=dict(engine_ref=engine,common_ref=common)
m.authority=lambda:(registry,None);m.spec_path=specfile
for case in g['unconsumed']:
 if tag=='system':check('full_spec_for_private_registry '+case,lambda case=case:m.spec_for(case,require_release=False))
 elif case.endswith('_850_V1'):check('full_spec_for_fresh850_with_original_accepted_Fpeer '+case,lambda case=case:m.spec_for(case))
 else:check('full_spec_for_futureclock_remains_stage_HOLD '+case,lambda case=case:m.spec_for(case),True)
# Source qualification schema cannot be downgraded or relabeled even in the private registry.
case=g['unconsumed'][0];s=specs[case];original_exact=m.exact
if tag=='highclock':
 def bad_exact(z):
  v=original_exact(z)
  if z==s['source_qualification_ref']:v=copy.deepcopy(v);v['schema']='EP_MAIN_EXACT_ACCEPTED_SOURCE_ALIAS_FORBIDDEN'
  return v
 m.exact=bad_exact;check('reject acceptedSource_schema_alias',lambda:m.spec_for(case),True);m.exact=original_exact
 check('actual_original_closed_F850_stage_compatibility',lambda:m.accepted_cell(g['consumed'][0],specs[g['consumed'][0]],q))
# Check no real registry or old Spec mutation by this module: reads and copied in-memory q only.
result=dict(status='PASS',group=tag,checks=len(rows),rows=rows,registry='in-memory deep copy; no writes',HostQ='actual signed Main qualification; no mock',scientific_starts=0,old_spec_native_source_writes=0)
(P/tag/'ACTUAL_SIGNED_SPEC_CPU.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status='PASS',group=tag,checks=len(rows))))
