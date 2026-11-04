import pathlib,json,hashlib,copy,ast,types,tempfile,threading,os,fcntl,sys,importlib.util
sys.dont_write_bytecode=True
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');D=A/'agents/B/owner_claim_snapshot_sync_main_review_v1';D.mkdir(exist_ok=True)
S=types.SimpleNamespace
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def rd(p):return json.loads(P(p).read_bytes())
def js(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
native=R/'control/operational_amendments/owner_claim_snapshot_sync_v1';source=native/'main_install.py';cfgpath=native/'actual_install_v1/CONFIGURATION.json'
assert sha(source)=='f7d1ab503e88d1b17ac088fc208f6fd4c1c773043872abbf6cebf62b39e82fae'
assert sha(cfgpath)=='b5e8aa23d984d66470c09f11567b7039e5dc7325e0f0279144a71237728e3e3b'
m=load('B_readonly_claim_main_source',source);cfg=rd(cfgpath)
for p,h in cfg['source_pins'].items():assert sha(p)==h
template=rd(cfg['helper_configuration_template_path']);qa=rd(template['QA_path']);rb=rd(template['readback_path'])
assert sha(template['QA_path'])==template['QA_sha256']and sha(template['readback_path'])==template['readback_sha256']
assert qa['status']=='PASS'and rb['verified']is True and rb['QA_sha256']==template['QA_sha256']
assert qa['source_sha256']==rb['source_sha256']==template['source_sha256']==cfg['helper_source_sha256']
assert qa['dependency_pins']==rb['dependency_pins']==template['dependency_pins']
assert template['scheduler_thread_ident']=='MAIN_MUST_CAPTURE_ACTUAL_ADDON_THREAD_IDENT'
am=rd(A/'agents/A/owner_claim_snapshot_sync_v1/MANIFEST.json')
for v in am['members']:assert sha(v['path'])==v['sha256']
tree=ast.parse(source.read_text());callback=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='append_locked')
calls=[ast.unparse(n.func)for n in ast.walk(callback)if isinstance(n,ast.Call)]
assert set(calls)<=set(['len','copy.deepcopy']),'NONPURE_CALLBACK_CALL '+repr(calls)
checks=[dict(case='actual_source_config_all_pins_A_manifest_QA_readback_template_join',status='PASS'),dict(case='actual_append_callback_AST_only_len_deepcopy_no_authority_file_reads',status='PASS')]
def fakeq():return dict(request='REQ',budget=3,remaining=2,consumed={'old':{'uuid':'retained'}},admitted_specs={'old':'KEEP'},additional_operational_overlays={'existing':{'keep':True}},peers='KEEP')
q=fakeq();before=dict(budget=3,remaining=2,consumed=copy.deepcopy(q['consumed']),records=copy.deepcopy(q['additional_operational_overlays']));reg={'registered_future_requests':{'REQ':q,'PEER':{'untouched':True}}};orig=copy.deepcopy(reg)
lockpath=D/'CPU_EX.lock'
with lockpath.open('a+b')as one:
 fcntl.flock(one,fcntl.LOCK_EX)
 with lockpath.open('a+b')as two:
  try:fcntl.flock(two,fcntl.LOCK_EX|fcntl.LOCK_NB);raise AssertionError('EX_NOT_HELD')
  except BlockingIOError:pass
 m.append_locked(reg,'REQ',before,{'source':'CPU-fixture'})
assert reg['registered_future_requests']['PEER']==orig['registered_future_requests']['PEER']
expected=copy.deepcopy(orig);expected['registered_future_requests']['REQ']['additional_operational_overlays'][m.ID]={'source':'CPU-fixture'};assert reg==expected
checks.append(dict(case='real_independentFD_EX_callback_zero_grant_full_q_peer_preservation',status='PASS'))
def run(mode):
 root=P(tempfile.mkdtemp(prefix='CPU_MAIN_SYNC_',dir=D));q=fakeq();q['request']='REQ';aging=S(lock=threading.RLock(),original=object(),frame_provider=object(),state=S(advance=object(),protected=123,pending_releases={'x':'KEEP'},previous_C=88),calls=7)
 def prior(*a,**kw):return 'OLD'
 res=S(choose_dispatch=prior,resources=object(),DTC_LARGE_JOB_AGING_INSTALLED=aging);consumer=S(safe_finish=object());frame=S(f_locals=dict(res=res,consumer=consumer),f_globals={'worker':object()})
 main=S(DTC_MAIN_BROAD_SHARED_CPU_INSTALL_V1={'phase':'ARMED_ACKED','armed':True,'frame':frame},DTC_MAIN_PENDING_SYRK_RESOURCE_REFRESH_V1={'phase':'COMMITTED_ACKED'},DTC_MAIN_COUPLED_ROUTE_BRIDGE_INSTALL_V1={'bridge_state':{'wrapper':prior}},DTC_L2_MLP_ADDON_THREAD=S(is_alive=lambda:True,native_id=1723771,ident=threading.get_ident()))
 def update(fn):
  registry={'registered_future_requests':{'REQ':copy.deepcopy(q)}};fn(registry);q.clear();q.update(registry['registered_future_requests']['REQ'])
 engine=S(REQ='REQ',assert_parent_lease=lambda:None,registered=lambda:(None,None,copy.deepcopy(q)),update_authority=update);frame.f_locals['engine']=engine;main.DTC_MAIN_BROAD_SHARED_CPU_INSTALL_V1['engine']=engine
 def wrapper(*args):return 'NEW'
 def install(*args,**kw):
  if mode=='before_wrapper_error':raise RuntimeError('CPU_INJECTED_INSTALL_FAILURE')
  token=dict(wrapper=wrapper,previous=prior,receipt={'CPU_FIXTURE':True});res.choose_dispatch=wrapper;setattr(main,m.ID,token)
  return token
 helper=S(ID=m.ID,record=lambda b:dict(source='CPU_FIXTURE',scheduler_thread_ident=b['scheduler_thread_ident']),validate=lambda b,q:True,install_on_frame=install)
 (root/'control').mkdir();(root/'control/POOL_DISPATCH_RESERVATIONS.json').write_bytes(js({'claims':{}}))
 fakecfg=copy.deepcopy(cfg);fakecfg['source_pins']={};fakecfg['directory']=str(root);fakecfg['helper_configuration_path']=str(root/'ACTIVE_SYNC.json');fakecfg['helper_configuration_template_path']=str(root/'TEMPLATE.json');(root/'TEMPLATE.json').write_bytes(js({'scheduler_thread_ident':'MAIN_MUST_CAPTURE_ACTUAL_ADDON_THREAD_IDENT','root':str(root)}));fp=root/'CONFIG.json';fp.write_bytes(js(fakecfg))
 count={'pins':0}
 def pinned(p):
  if str(p)==str(source):return cfg['installer_sha256']
  return sha(p)
 def put(p,v):
  if mode=='after_wrapper_error'and P(p).name=='ACK.json':raise RuntimeError('CPU_ACK_WRITE_FAILURE')
  m.put(p,v)
 def fakepath(p):
  if str(p)=='/proc/self/stat':return S(read_text=lambda:'0 (cpu) '+' '.join(['S']+['0']*18+['977758783']))
  return P(p)
 namespace=dict(m.__dict__);namespace.update(P=fakepath,os=S(getpid=lambda:1498278),sys=S(modules={'__main__':main}),sha=pinned,load=lambda n,p:helper,put=put)
 fn=types.FunctionType(m.apply.__code__,namespace)
 if mode=='missing_SYRK':main.DTC_MAIN_PENDING_SYRK_RESOURCE_REFRESH_V1['phase']='PREPARED'
 value=fn(fp)
 assert q['budget']==3 and q['remaining']==2 and q['consumed']=={'old':{'uuid':'retained'}}
 assert aging.state.protected==123 and aging.state.pending_releases=={'x':'KEEP'}and aging.calls==7
 if mode=='success':assert value['status'].startswith('INSTALLED')and res.choose_dispatch is wrapper and m.ID in q['additional_operational_overlays']
 elif mode=='missing_SYRK':assert value['status']=='CLAIM_SYNC_INSTALL_HOLD_PRESERVE'and res.choose_dispatch is prior and m.ID not in q['additional_operational_overlays']and not(root/'ACTIVE_SYNC.json').exists()
 elif mode=='before_wrapper_error':assert value['status']=='CLAIM_SYNC_INSTALL_HOLD_PRESERVE'and res.choose_dispatch is prior and m.ID in q['additional_operational_overlays']
 elif mode=='after_wrapper_error':assert value['admission_held']is True and res.choose_dispatch is not prior and res.choose_dispatch()is None
 return dict(case='actual_apply_code_private_globals_'+mode,status='PASS',authority_helper_and_owner='EXPLICIT_CPU_STANDINS',production_calls=0)
for mode in ['success','missing_SYRK','before_wrapper_error','after_wrapper_error']:checks.append(run(mode))
qaout=dict(status='PASS',schema='B_CLAIM_SYNC_MAIN_INDEPENDENT_CPU_V1',source_sha256=sha(source),configuration_sha256=sha(cfgpath),count=len(checks),checks=checks,production_actions=0,model_starts=0,qualification_only=True)
(D/'CPU_QUALIFICATION.json').write_bytes(js(qaout))
review=dict(status='PASS',scope='LIMITED_INDEPENDENT_MAIN_INSTALL_REVIEW_NOT_PRODUCTION_APPLY',installer=dict(path=str(source),sha256=sha(source)),configuration=dict(path=str(cfgpath),sha256=sha(cfgpath)),helper=dict(path=cfg['helper_source_path'],sha256=cfg['helper_source_sha256']),QA=dict(path=str(D/'CPU_QUALIFICATION.json'),sha256=sha(D/'CPU_QUALIFICATION.json')),findings=['No blocking defect found in the reviewed installer scope. The mandatory SYRK COMMITTED_ACKED check precedes ACTIVE_SYNC publication and registry mutation.','Main captures Python addon.ident separately from validated native TID1723771. Helper verifies unchanged saveclaims bytecode, claims closure identity and root; disk/live differences must be bool observed_model only.','append_locked is passed-object-only; independent-FD EX verified. It appends one zero-grant row and preserves all other q and peer contents.','Post-wrapper failure installs a HOLD reference preserving routes/state. Failure before helper assignment retains the old coupled route; pending operational row/config remain visible, no blind reapply.','Initial cfg/source/parent preflight assertions occur outside apply try. Caller pending-callback boundary must contain BaseException; this review does not claim apply alone contains malformed pre-entry input.'],limitations=['Seven focused new checks only, no duplicate A three-case helper suite. apply exercised actual function code with explicit private owner/authority/helper/path standins; not the live Main.','No model, signals, production registration, hooks, source edits or Git. Healthy models untouched.','The actual Main dispatch/CPU/strict/archive outcome remains a production observation task for Root.'])
(D/'REVIEW.json').write_bytes(js(review));manifest=dict(schema='B_CLAIM_SYNC_MAIN_REVIEW_MANIFEST_V1',status='PASS',members=[dict(path=str(D/n),sha256=sha(D/n))for n in ['CPU_QUALIFICATION.json','REVIEW.json']]);(D/'MANIFEST.json').write_bytes(js(manifest));print(json.dumps(dict(QA_sha256=sha(D/'CPU_QUALIFICATION.json'),REVIEW_sha256=sha(D/'REVIEW.json'),MANIFEST_sha256=sha(D/'MANIFEST.json'),count=len(checks)),indent=2))
