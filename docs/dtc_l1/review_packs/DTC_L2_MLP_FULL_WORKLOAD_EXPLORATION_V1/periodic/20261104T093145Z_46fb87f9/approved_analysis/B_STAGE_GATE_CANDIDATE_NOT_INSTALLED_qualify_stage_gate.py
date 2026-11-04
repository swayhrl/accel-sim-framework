import pathlib,json,hashlib,copy,sys,threading,types,tempfile,importlib.util,fcntl,ast
sys.dont_write_bytecode=True
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');D=A/'agents/B/adaptive_stage_transition_gate_v1';S=types.SimpleNamespace
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=load('B_stage_gate_actual_candidate',D/'stage_gate.py');scope=m.read(R/'control/SCOPE.json');ids=sorted({p['input_digest']for p in scope['points']});source=R/'tools/l2_adaptive.py'
def fixture(unknown=False,raises=False):
 root=P(tempfile.mkdtemp(prefix='CPU_STAGE_GATE_',dir=D));priorlib=load('private_actual_frozen_adaptive_'+root.name,source)
 if raises:
  path=root/'prior_error.py';path.write_text('def recommend(*args):\n raise SystemExit("CPU_ORIGINAL_FAILURE")\n');priorlib=load('CPU_prior_error',path)
 orig=priorlib.recommend;original_source=P(orig.__code__.co_filename);dependency=root/'dependency.txt';dependency.write_text('CPU_SOURCE')
 pins={str(p):m.sha(p)for p in[D/'stage_gate.py',original_source,dependency]};qa=root/'qa.json';rb=root/'rb.json'
 qa.write_bytes(m.js(dict(status='PASS',legacy_proposals_suppressed_qualified=True,no_false_full35_or_IR_union_qualified=True,source_sha256=m.sha(D/'stage_gate.py'),dependency_pins=pins,qualification_only=True)))
 rb.write_bytes(m.js(dict(verified=True,QA_sha256=m.sha(qa),source_sha256=m.sha(D/'stage_gate.py'),dependency_pins=pins,qualification_only=True)))
 cfg=dict(schema=m.ID,overlay_id=m.ID,request=m.REQ,root=str(root),qualification_only=True,mode='HOLD_FOR_SEPARATELY_QUALIFIED_TRANSACTIONAL_STAGE',source_path=str(D/'stage_gate.py'),source_sha256=m.sha(D/'stage_gate.py'),prior_recommend_source_path=str(original_source),prior_recommend_source_sha256=m.sha(original_source),dependency_pins=pins,QA_path=str(qa),QA_sha256=m.sha(qa),readback_path=str(rb),readback_sha256=m.sha(rb))
 if unknown:cfg['next_batch_contract']={'UNSIGNED_CPU_TEST':True}
 q=dict(request=m.REQ,qualification_only=True,budget=360,remaining=18,consumed={'oldnegative':{'uuid':'KEEP','performance_accepted':False}},admitted_specs={'KEEP':'KEEP'},additional_operational_overlays={});q['additional_operational_overlays'][m.ID]=m.record(cfg)
 aging=S(lock=threading.RLock(),original=object(),frame_provider=object(),state=S(advance=object(),protected=123,pending_releases={'retained':'KEEP'}));res=S(DTC_LARGE_JOB_AGING_INSTALLED=aging,choose_dispatch=object(),resources=object())
 def forbidden_extend(*args):raise AssertionError('LEGACY_EXTEND_MUST_NEVER_RUN')
 registry=S(extend=forbidden_extend);claims={'OLD':'KEEP'};frame=S(f_locals=dict(engine=S(registered=lambda:(None,None,q)),res=res,adaptive=priorlib,registry=registry,consumer=S(safe_finish=object()),claims=claims),f_globals={'worker':object()});main=S()
 summary={'programs':{d:{'program':d,'suite':'CPU_ONLY'}for d in ids},'profiles':list(priorlib.INITIAL)if not raises else [],'table':{}}
 if not raises:
  for d in ids:
   summary['table'][d]={}
   for profile in priorlib.INITIAL:
    n=100000 if profile=='F128' else 90000 if profile=='F256' else 130000
    summary['table'][d][profile]={'DH':dict(accepted=True,cycles=n,state='PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE')}
    if profile=='P0':summary['table'][d][profile]['CH']=dict(accepted=True,cycles=130000,state='PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE')
  summary['table'][ids[0]]['M16']['DH']=dict(accepted=False,cycles=None,state='FAIL_L2MLP_ARCHIVED_NO_RETRY')
 state=m.install_on_frame(frame,cfg,lambda:None,main)
 return root,priorlib,orig,summary,scope,cfg,q,aging,frame,main,state,dependency
checks=[]
def test(name,fn):fn();checks.append(dict(case=name,status='PASS'))
def positive():
 root,lib,orig,summary,sc,cfg,q,aging,frame,main,state,dep=fixture();raw=orig(summary,sc,{});assert raw['proposals'],'ACTUAL_ORIGINAL_FIXTURE_MUST_OFFER_NEXT_POINTS'
 before=copy.deepcopy(q);s0=copy.deepcopy(summary);p0=copy.deepcopy(sc);value=lib.recommend(summary,sc,{})
 assert value['proposals']==[]and value['adoption_ready']is False and value['scientific_stage_complete']is False
 assert state['original_calls']==1 and state['calls']==1 and state['last_original']['proposal_count']==len(raw['proposals'])and value['legacy_recommendation_evidence']['original_sha256']==m.objsha(raw)
 assert q==before and summary==s0 and sc==p0 and aging.state.protected==123 and aging.state.pending_releases=={'retained':'KEEP'}and frame.f_locals['claims']=={'OLD':'KEEP'}
 assert frame.f_locals['registry'].extend.__name__=='forbidden_extend'
 m.restore_in_owner(lambda:None,main);assert lib.recommend is orig
test('actual_frozen_recommend_with_terminal_negative_positive_proposals_suppressed_exact_once_no_false_full35_or_IR_union_exact_restore',positive)
def unknown():
 root,lib,orig,summary,sc,cfg,q,aging,frame,main,state,dep=fixture(unknown=True);value=lib.recommend(summary,sc,{})
 assert not value['proposals']and state['original_calls']==0 and state['last_issue']['stage']=='UNKNOWN_BATCH_NOT_AUTHORIZED_BY_THIS_GATE'
test('unknown_unsigned_nextbatch_no_old_recommend_or_extend_delegate',unknown)
def drift():
 root,lib,orig,summary,sc,cfg,q,aging,frame,main,state,dep=fixture();dep.write_text('SOURCE_DRIFT');value=lib.recommend(summary,sc,{})
 assert not value['proposals']and state['original_calls']==0 and state['last_issue']['stage']=='ADAPTIVE_STAGE_GATE_FAIL_CLOSED'
test('source_pin_drift_HOLD_before_old_recommend',drift)
def error():
 root,lib,orig,summary,sc,cfg,q,aging,frame,main,state,dep=fixture(raises=True);value=lib.recommend(summary,sc,{})
 assert not value['proposals']and state['original_calls']==1 and 'SystemExit'in state['last_issue']['error']
test('original_BaseException_contained_no_nextbatch_or_false_completion',error)
def badref():
 root,lib,orig,summary,sc,cfg,q,aging,frame,main,state,dep=fixture();frame.f_globals['worker']=object();value=lib.recommend(summary,sc,{})
 assert not value['proposals']and state['original_calls']==0
 lib.recommend=lambda *args:None
 try:m.restore_in_owner(lambda:None,main);raise AssertionError('RESTORE_MUST_REJECT_NEWER')
 except AssertionError as error:assert 'REFUSE_NEWER_STAGE_GATE'in str(error)
test('owner_reference_drift_HOLD_and_restore_refuses_clobber_newer_wrapper',badref)
def pureex():
 tree=ast.parse((D/'stage_gate.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='append_locked');assert {ast.unparse(n.func)for n in ast.walk(fn)if isinstance(n,ast.Call)}<= {'copy.deepcopy'}
 q=dict(budget=360,remaining=18,consumed={'uuid':'KEEP'},admitted_specs={'old':'KEEP'},additional_operational_overlays={});before=copy.deepcopy(q);reg={'registered_future_requests':{m.REQ:q,'FOREIGN':{'KEEP':True}}};p=D/'CPU_ONLY_EX.lock'
 with p.open('a+b')as one:
  fcntl.flock(one,fcntl.LOCK_EX)
  with p.open('a+b')as two:
   try:fcntl.flock(two,fcntl.LOCK_EX|fcntl.LOCK_NB);raise AssertionError('EX_NOT_HELD')
   except BlockingIOError:pass
  m.append_locked(reg,m.REQ,before,{'CPU_ONLY':True})
 expected=copy.deepcopy(before);expected['additional_operational_overlays'][m.ID]={'CPU_ONLY':True};assert q==expected and reg['registered_future_requests']['FOREIGN']=={'KEEP':True}
test('pure_callback_real_independentFD_EX_preserves_budget_consumed_specs_peers_no_grants',pureex)
result=dict(status='PASS',schema='B_STAGE_TRANSITION_GATE_FOCUSED_CPU_V1',source_path=str(D/'stage_gate.py'),source_sha256=m.sha(D/'stage_gate.py'),driver_sha256=m.sha(__file__),prior_recommend_source_path=str(source),prior_recommend_source_sha256=m.sha(source),checks=checks,count=len(checks),production_actions=0,models_started=0,qualification_only=True,limitations=['Cycle/identity/authority/owner inputs are explicit isolated CPU standins; real original adaptive code and actual frozen35 scope are used.','No live owner install or registry update. This gate has no next-stage activation branch.'])
(D/'CPU_QUALIFICATION.json').write_bytes(m.js(result));print(json.dumps(dict(status=result['status'],source_sha256=result['source_sha256'],QA_sha256=m.sha(D/'CPU_QUALIFICATION.json'),count=len(checks)),indent=2))
