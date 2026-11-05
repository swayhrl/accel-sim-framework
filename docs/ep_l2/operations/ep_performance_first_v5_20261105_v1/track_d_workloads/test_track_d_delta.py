from pathlib import Path
import sys,json,copy,os,importlib.util
D=Path(__file__).resolve().parent
def load(n,f):
 s=importlib.util.spec_from_file_location(n,D/f);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
p=load('postrun','check_postrun_identity.py');r=load('resources','resources_a2_v5.py')
results=[]
def case(name,fn,reject=False):
 try:v=fn()
 except Exception as e:
  if not reject:raise
  results.append(dict(name=name,status='PASS_REJECT',reason=str(e)));return
 if reject:raise AssertionError('negative accepted '+name)
 if v is False:raise AssertionError('positive returned false '+name)
 results.append(dict(name=name,status='PASS',result=v))
c=json.loads((D/'POSTRUN_ACTUAL_CLOSED_STENCIL_OFFLINE_CONTRACT.json').read_text())
case('actual_closed_stencil_frozen_Main_snapshot_metadata_replay',lambda:p.validate(c))
for key,value in [('cohort','WRONG'),('uuid','WRONG'),('request','WRONG'),('required_production_terminal_validation_ref',{})]:
 v=copy.deepcopy(c);v[key]=value;case('postrun_reject_'+key,lambda v=v:p.validate(v),True)
for key in ['spec_ref','done_ref']:
 v=copy.deepcopy(c);v[key]['sha256']='0'*64;case('postrun_reject_'+key+'_SHA',lambda v=v:p.validate(v),True)
policy=p.exact(c['Main_shared_route_review_ref']);native=Path(policy['reviewed_current_snapshot_ref']['path']).read_bytes()
case('route_exact_existing_Main_review',lambda:p.route_check(policy,native))
case('route_unreviewed_append',lambda:p.route_check(policy,native+b'\n#foreign\n'),True)
case('route_unreviewed_delete',lambda:p.route_check(policy,native[:-1]),True)
case('route_unreviewed_interior_mutation',lambda:p.route_check(policy,native[:10]+b'X'+native[11:]),True)
for key,value in [('scope','NEW_START'),('new_model_authority',True)]:
 v=copy.deepcopy(policy);v[key]=value;case('route_reject_'+key,lambda v=v:p.route_check(v,native),True)
proc=Path('/proc')/str(os.getpid());st=(proc/'stat').read_text();ticks=int(st[st.rfind(')')+2:].split()[19])
case('current_generation_live_rejected',lambda:False if p.nonlive(os.getpid(),ticks)else True)
assert not p.nonlive(os.getpid(),ticks)
case('recycled_PID_generation_is_not_same_model',lambda:p.nonlive(os.getpid(),ticks+1))
b=r.shared()
for name,argv,expected in [('cmake_literal_build_target',['/usr/bin/cmake','--build','/tmp/private','--target','accel-sim.out','-j','2'],'NOT_MODEL'),('ninja_literal_build_target',['/usr/bin/ninja','-j','2','accel-sim.out'],'NOT_MODEL'),('gmake_literal_build_target',['/usr/bin/gmake','-f','Makefile','-j2','ep_l2_quota_handshake_v5','accel-sim.out'],'NOT_MODEL'),('direct_model',['/tmp/accel-sim.out','-trace','/x'],'MODEL'),('unknown_wrapper_with_ELF_path',['bash','/tmp/accel-sim.out'],'UNKNOWN_MODEL_WRAPPER'),('build_tool_with_ELF_path_not_ignored',['/usr/bin/ninja','/tmp/accel-sim.out'],'UNKNOWN_MODEL_WRAPPER')]:
 case('loader_classification_'+name,lambda argv=argv,expected=expected:b.classify(argv)==expected);assert b.classify(argv)==expected
snap=r.snapshot();case('actual_dynamic_owner_mapping_has_no_errors',lambda:not snap['foreign_metadata_errors']);assert not snap['foreign_metadata_errors']
case('unregistered_A2_admit',lambda:r.admit(snap,5*(1<<30),64*(1<<20),dict(max_global_EP_models=10)),True)
pins=r.read(r.PIN);req=sorted(pins)[0];d=pins[req];reg=r.read('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json');q=reg['registered_future_requests'][req]
v=copy.deepcopy(q);v['budget']+=1;case('foreign_budget_mismatch',lambda:r.map_owner(req,v,d,None,[]),True)
v=copy.deepcopy(q);v['schema']='WRONG';case('foreign_schema_mismatch',lambda:r.map_owner(req,v,d,None,[]),True)
v=copy.deepcopy(d);v['policy_ref']['sha256']='0'*64;case('foreign_policy_drift',lambda:r.map_owner(req,q,v,None,[]),True)
v=copy.deepcopy(snap);v['current_request']='OTHER';case('cross_scope_admit',lambda:r.admit(v,1,1),True)
sys.path.insert(0,str(D/'three_mm/runtime'));import ep_perf_native_wv_modes_draft as e
for f in sorted((D/'three_mm/execution/cases').glob('*/control/FROZEN_SPEC.json')):
 s=e.read(f);case('new_exact_graph_'+s['cohort'],lambda s=s:e.engineering_spec_for(s['cohort'])['cohort'])
 case('science_HOLD_'+s['cohort'],lambda s=s:e.fresh_science_authorization(s),True)
out=dict(schema='EP_V5_TRACK_D_FINITE_WIRING_METADATA_DELTA_TESTS_V1',status='PASS',cases=results,count=len(results),old_124_or_geometry_or_mode_CPU_suites_rerun=0,new_model_or_science_budget=0,shared_Native_or_foreign_metadata_writes=False,actual_resource_foreign_metadata_errors=snap['foreign_metadata_errors'],foreign_remaining_write_bytes=snap['foreign_remaining_write_bytes'])
(D/'TRACK_D_NEW_DELTA_TEST_RESULTS.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(dict(status='PASS',count=len(results),actual_resource_errors=snap['foreign_metadata_errors'])))
