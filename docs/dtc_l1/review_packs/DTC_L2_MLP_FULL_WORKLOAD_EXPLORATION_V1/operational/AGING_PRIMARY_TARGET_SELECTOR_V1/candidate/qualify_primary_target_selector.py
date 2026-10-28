import sys
sys.dont_write_bytecode=True
import pathlib,json,hashlib,importlib.util,copy,types,threading,tempfile,difflib
P=pathlib.Path;D=P(__file__).parent;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');G=1024**3
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=load('B_candidate_primary_targets',D/'primary_target_selector.py');old=load('B_existing_b4e_aging',m.SOURCE);guardlib=load('B_exact_installed_frame_guard',R/'control/operational_amendments/frame_read_guard_v1/frame_read_guard.py')
C='E2-DTCL2MLP-ddb6806316876a85-CH-P0-V1';DH='E2-DTCL2MLP-ddb6806316876a85-DH-P0-V1';V=[C.replace('CH-P0','DH-'+p)for p in ['E384','E768','M8','M16','Q64','Q128','F128','F256']]
specs={c:read(R/'control/specs'/(c+'.json'))for c in[C]+V+[DH]};matrix={p['cohort']:p for p in read(R/'control/MATRIX_CURRENT.json')['points']};registry=read('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests'][m.REQ];active=read(R/'control/operational_amendments/future_memory_admission_v1/ACTIVE_MEMORY.json');sync=read(R/'control/operational_amendments/future_memory_scope_sync_v1/INSTALL.json');scope=read(R/'control/SCOPE.json')
ctx=dict(registry=registry,active_memory=active,matrix_points=matrix,specs=specs,spec_sha256={c:sha(R/'control/specs'/(c+'.json'))for c in specs},preserved_nonprimary=set(sync['preserved_nonprimary_cohorts']),initial_references=set(scope['initial_references']),INTENT_exists=set())
def row(c):
 s=specs[c];return dict(cohort=c,input_digest=s['input_digest'],program=s['program'],cell=s['cell'],profile=s['profile'],cost_bytes=s['estimated_peak_model_RAM_bytes'],first_eligible_monotonic=0)
def frame(points):return dict(now=10000,budget_bytes=100*G,effective_total_growth_bytes=90*G,memory_utilization_fraction=.95,own_live=[],consumed={DH:dict(uuid='ACTUAL_PREVIOUS_DH_P0',terminal=True)},claim_cohorts=[],pending=[row(c)for c in points],active_input_digests=[],started_programs=['lavamd'],accounted_growth_by_cohort={},closures=[],total_padding_discount_bytes=0,padding_discount_by_cohort={},pressure_reasons=[])
def state():
 s=old.AgingState();fn,code=m.build_advance(s.advance,lambda f:ctx);return s,fn,code
checks=[]
def ck(n,b):assert b,n;checks.append(n)
s,fn,code=state();d=fn(s,frame(V+[C]));ck('actual DH-P0 consumed; pending CH-P0 selected ahead of same-age eight variants',d['target']['cohort']==C and len(d['backfill_cohorts'])==9)
s,fn,_=state();d=fn(s,frame(V));ck('after both P0 identities absent/consumed a remaining variant can be protected',d['target']['cohort']in V)
for kind in ['consumed','reference','typednegative','supplemental','unknown','unqualified','intent','claim','activeinput']:
 context=copy.deepcopy(ctx);f=frame([C]);rr=f['pending'][0]
 if kind=='consumed':context['registry']['consumed'][C]={};f['consumed'][C]={}
 elif kind=='reference':context['initial_references'].add(C)
 elif kind=='typednegative':context['specs'][C]['correctness_validation_only']=True
 elif kind=='supplemental':context['preserved_nonprimary'].add(C)
 elif kind=='unknown':context['matrix_points'].pop(C)
 elif kind=='unqualified':context['specs'][C]['source_kind']='UNQUALIFIED_OR_UNKNOWN'
 elif kind=='intent':context['INTENT_exists'].add(C)
 elif kind=='claim':f['claim_cohorts']=[C]
 elif kind=='activeinput':f['active_input_digests']=[rr['input_digest']]
 s=old.AgingState();fn,_=m.build_advance(s.advance,lambda f:context);d=fn(s,f);ck('reject_'+kind,d['target']is None)
# This synthetic memory change is not an actual completion or production credit.
s,fn,_=state();f=frame([C]);fn(s,f);f['now']+=1;f['budget_bytes']+=20*G;d=fn(s,f);ck('external/free budget increase without true closure earns no protected credit',d['protected_bytes']==0 and not any(v['kind']=='STRICT_NATURAL_COMPLETION_CREDIT'for v in d['new_credit_events']))
# Healthy witnessed natural strict release earns exactly75%; errors retain original semantics.
s,fn,_=state();f=frame([C]);f['budget_bytes']=90*G;f['effective_total_growth_bytes']=60*G;live=dict(cohort='PURE',uuid='PURE_ONLY',RSS_bytes=80*G,effective_future_bytes=20*G,anon_PSS_bytes=80*G,PSS_sample_monotonic=10000);f['own_live']=[live];fn(s,f)
f2=copy.deepcopy(f);f2.update(now=10001,budget_bytes=110*G,effective_total_growth_bytes=40*G,own_live=[dict(live,cohort='STILL_LIVE',uuid='STILL_LIVE')],closures=[dict(cohort='PURE',uuid='PURE_ONLY',natural_done=True,accepted_strict_archive_restore=True)])
d=fn(s,f2);credits=[e for e in d['new_credit_events']if e['kind']=='STRICT_NATURAL_COMPLETION_CREDIT'];ck('synthetic natural strict realized40GiB release protects exactly30GiB',len(credits)==1 and credits[0]['protected_credit_bytes']==30*G)
# Actual FrameReadGuard second-fresh rollback, same state, private chooser and provider.
calls=[];f=frame([C]);f['budget_bytes']=200*G;f['effective_total_growth_bytes']=10*G
provider_calls=[0]
def provider(*args):
 provider_calls[0]+=1
 if provider_calls[0]in[2,3,4]:raise json.JSONDecodeError('CPU controlled second-frame failure','x',0)
 return copy.deepcopy(f)
def private(*args):calls.append(args[0]);return dict(cohort=args[0][0]['cohort'])
aging=old.AgingChooser(private,provider);gate=guardlib.FrameReadGuard(aging,sleeper=lambda x:None);main=types.SimpleNamespace();before=copy.deepcopy(aging.state.__dict__);refs=(aging.original,aging.frame_provider,aging.lock,aging.wrapper)
m.install_on_existing(aging,lambda f:ctx,lambda:None,guardlib.FrameUnavailable,main)
wrapper=aging.state.advance;assert gate.wrapper([{'cohort':C}],{}, {},{},None,{},0)is None
ck('actual second-fresh JSON failure rolls back without cloning state-bound advance',aging.state.advance is wrapper and aging.state.target==before['target']and aging.calls==0 and gate.last_issue['state_restored'])
gate.wrapper([{'cohort':C}],{}, {},{},None,{},1);ck('after rollback same original state advances and original private chooser is still invoked',aging.state.advance is wrapper and aging.state.target['cohort']==C and calls and refs==(aging.original,aging.frame_provider,aging.lock,aging.wrapper))
m.restore_in_owner(lambda:None,main);ck('exact class advance restored without replacing chooser/state/provider/CPU2 leaf', 'advance'not in aging.state.__dict__ and refs==(aging.original,aging.frame_provider,aging.lock,aging.wrapper))
# New identity-source failure is converted into the exact existing guard sentinel.
aging=old.AgingChooser(private,lambda*args:copy.deepcopy(f));gate=guardlib.FrameReadGuard(aging,sleeper=lambda x:None);main=types.SimpleNamespace()
def failctx(f):raise OSError('CPU private authority read failure')
m.install_on_existing(aging,failctx,lambda:None,guardlib.FrameUnavailable,main);assert gate.wrapper([],{}, {},{},None,{},0)is None
ck('identity read error uses true installed FrameUnavailable and rollback; never escapes scheduler',gate.last_issue['state_restored']and aging.state.target is None and aging.calls==0)
m.restore_in_owner(lambda:None,main)
(D/'EXACT_ADVANCE_SELECTION_DIFF.patch').write_text(''.join(difflib.unified_diff(code['original_advance_utf8'].splitlines(True),code['modified_advance_utf8'].splitlines(True),fromfile='original_b4e_advance',tofile='candidate_selection_only')))
out=dict(schema='B_PRIMARY_TARGET_SELECTOR_CPU_QUALIFICATION_V1',status='PASS',count=len(checks),checks=checks,source_sha256=sha(m.__file__),old_aging_source_sha256=sha(m.SOURCE),frame_guard_source_sha256=sha(R/'control/operational_amendments/frame_read_guard_v1/frame_read_guard.py'),only_target_selection_and_key_transformed=True,real_current_Lavamd_identity_source=True,synthetic_RAM_release_NOT_ACTUAL=True,production_changes=0,models_started=0,new_grants=0,scope_mutated=False)
p=D/'CPU_QUALIFICATION.json';p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),status='PASS',count=len(checks))))
