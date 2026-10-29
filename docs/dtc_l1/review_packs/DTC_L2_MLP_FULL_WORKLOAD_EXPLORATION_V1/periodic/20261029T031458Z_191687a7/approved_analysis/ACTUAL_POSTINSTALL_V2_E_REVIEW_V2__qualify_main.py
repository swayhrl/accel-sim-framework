"""Actual Main v2 apply control-flow fault injection, private frame/helper only."""
import pathlib,json,hashlib,importlib.util,types,threading,tempfile,copy,os,sys
P=pathlib.Path;D=P(__file__).parent;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');M=R/'control/operational_amendments/pending_resource_forecast_refresh_v1'
sys.dont_write_bytecode=True
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
source=M/'main_apply_v2.py';pin='f48fb251f0ec30593611d70c11a08c4292bd8b39e1b2e9677be785b5fee98351';assert sha(source)==pin
testroot=P(tempfile.mkdtemp(prefix='CPU_MAIN_RESOURCE_V2_',dir=D))
def audit(event,args):
 if event=='subprocess.Popen'or event.startswith('os.exec')or event in('os.system','os.kill','os.killpg'):raise AssertionError('No model/process/signal')
sys.addaudithook(audit)
cases=[]
for kind in ['success','ACK_put_failure','apply_BaseException','unknown_chooser_protection']:
 root=testroot/kind;root.mkdir();module=load('actual_Main_v2_private_'+kind,source);module.R=root
 stat=P('/proc/self/stat').read_text();head,tail=stat.rsplit(')',1);fields=tail.split();fields[19]='977758783';fake_stat=head+') '+' '.join(fields)
 class ProcWitness:
  def read_text(self):return fake_stat
 module.P=lambda p:ProcWitness()if str(p)=='/proc/self/stat'else P(p)
 module.os=types.SimpleNamespace(getpid=lambda:1498278,fsync=os.fsync)
 previous=lambda *a,**k:'PREVIOUS';foreign=lambda *a,**k:'FOREIGN'
 aging=types.SimpleNamespace(lock=threading.RLock(),state=types.SimpleNamespace(protected=123,pending_releases={'token':456}),calls=7)
 res=types.SimpleNamespace(choose_dispatch=previous,DTC_LARGE_JOB_AGING_INSTALLED=aging)
 items=[dict(cohort='CPU_SYRK_'+str(i),new_spec_sha256='CPU_NEW_'+str(i),DB_present=i==0)for i in range(10)]
 q=dict(budget=360,remaining=358,consumed={'oldA':{'uuid':'UNCHANGED_A'},'oldB':{'uuid':'UNCHANGED_B'}},admitted_specs={x['cohort']:'CPU_OLD_'+str(i)for i,x in enumerate(items)})
 engine=types.SimpleNamespace(registered=lambda:(None,None,q,None),assert_parent_lease=lambda:None)
 frame=types.SimpleNamespace(f_locals={'engine':engine,'res':res,'claims':{}});main=types.SimpleNamespace(DTC_MAIN_BROAD_SHARED_CPU_INSTALL_V1={'frame':frame})
 module.sys=types.SimpleNamespace(modules={'__main__':main})
 proposal=dict(qualification_only=False,items=items,CPU_ONLY_HELPER_STANDIN=True)
 events=[]
 def prepare(*a):
  assert res.choose_dispatch is not previous;events.append('PREPARE_UNDER_HOLD');return copy.deepcopy(proposal)
 def apply(*a):
  assert res.choose_dispatch is not previous;events.append('APPLY_UNDER_HOLD')
  if kind=='apply_BaseException':raise KeyboardInterrupt('CPU interruption inside helper apply')
  if kind=='unknown_chooser_protection':res.choose_dispatch=foreign;raise RuntimeError('CPU foreign newer chooser appeared')
  for item in items:q['admitted_specs'][item['cohort']]=item['new_spec_sha256']
  return dict(status='CPU_COMMITTED_HELPER_STANDIN')
 helper=types.SimpleNamespace(prepare=prepare,apply=apply);module.load=lambda *a:helper
 original_put=module.put
 def monitored_put(path,value):
  if P(path).name=='ACK.json':
   assert res.choose_dispatch is not previous;events.append('ACK_PUBLISHED_UNDER_HOLD')
   if kind=='ACK_put_failure':raise OSError('CPU injected ACK publication failure')
  return original_put(path,value)
 module.put=monitored_put
 directory=root/'actual';helperpath=M/'resource_refresh.py';cfg=dict(schema='DTC_MAIN_PENDING_RESOURCE_REFRESH_CONFIG_V1',installer_path=str(source),installer_sha256=pin,source_pins={str(source):pin,str(helperpath):sha(helperpath)},helper_path=str(helperpath),helper_sha256=sha(helperpath),directory=str(directory),scope_contract_path=str(root/'CPU_SCOPE_STANDIN.json'))
 put(root/'control/HISTORICAL_RSS.json',{});put(root/'control/RESOURCE_POLICY.json',{});cfgpath=root/'CONFIG.json';put(cfgpath,cfg)
 before=copy.deepcopy(q);before_ledger=copy.deepcopy(aging.state.__dict__);result=module.apply(cfgpath);state=getattr(main,module.MARKER)
 assert aging.state.__dict__==before_ledger and aging.calls==7 and q['budget']==before['budget']and q['remaining']==before['remaining']and q['consumed']==before['consumed']
 if kind=='success':
  assert result['status']=='COMMITTED_UNUSED_SYRK_RESOURCE_ONLY_SAME_OWNER'and res.choose_dispatch is previous and (directory/'ACK.json').exists()
 elif kind=='unknown_chooser_protection':
  assert result['admission_held']is False and res.choose_dispatch is foreign and not(directory/'ACK.json').exists()
 else:
  assert result['admission_held']is True and res.choose_dispatch is state['hold']and not(directory/'ACK.json').exists()
 assert(directory/'PROPOSAL.json').exists()
 cases.append(dict(name=kind,status='PASS',events=events,admission_held=result.get('admission_held'),exact_previous_restored=kind=='success',foreign_reference_not_overwritten=kind=='unknown_chooser_protection',original_UUIDs_budget_and_R_tokens_preserved=True))
report=dict(schema='E_RESOURCE_MAIN_V2_ACTUAL_APPLY_PRIVATE_FAULT_QUALIFICATION_V1',status='PASS',count=len(cases),cases=cases,source_path=str(source),source_sha256=pin,driver_sha256=sha(__file__),fixture_root=str(testroot),limitations=['Actual frozen apply function executes in an isolated module with private Main/frame/owner identity and helper/authority stand-ins.','Tests only operator hold/ACK/exception/reference ordering; actual helper transaction and partial forward recovery are covered by separate B8 qualification.','No actual owner entry, resource file/registry writes or model action.'],models_started=0,new_grants=0,production_changes=0)
assert not(D/'CPU_MAIN_V2_QUALIFICATION.json').exists();put(D/'CPU_MAIN_V2_QUALIFICATION.json',report);print(json.dumps(dict(status='PASS',count=len(cases),QA_sha256=sha(D/'CPU_MAIN_V2_QUALIFICATION.json'))))
