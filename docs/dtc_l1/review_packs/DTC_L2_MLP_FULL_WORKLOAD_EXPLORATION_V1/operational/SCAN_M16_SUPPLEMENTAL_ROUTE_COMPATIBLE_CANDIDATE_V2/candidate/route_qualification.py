"""Read-only current-route checks; isolated shell-prefix CPU delegation fixture."""
import hashlib,importlib.util,json,pathlib,shlex,subprocess,tempfile
P=pathlib.Path;HERE=P(__file__).resolve().parent
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
NATIVE=P('/root/data/ep_l2_dtc_l1_native_v2/bin/native')
MEM=R/'control/operational_amendments/future_memory_admission_v1'
IO=R/'control/operational_amendments/shared_json_io_v1/io_frontend.py'
NEW='E2-DTCL2MLP-6df3a84b612086e8-DH-M16-V2'
NEW_ENTRY_SHA='46c69a74154e0690afd82324a348da236baf90189d9a7e474b4b14eb01ab4f0e'
OLD_ENTRY_SHA='039095cc62dd93668f9a17cbb7c5e0df65f44ba6fe56af11a306fe0358395c41'
FRONT_SHA='fa3efd26a779670a5d5df09ce7b7c08d8159195c5d9eb30c889e01c2ce023edb'
IO_SHA='01ba76be6b3f694ae077f21ceda1d108a4616ac54818028469d9afd262c43b7e'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def load(n,p):
 sp=importlib.util.spec_from_file_location(n,p);o=importlib.util.module_from_spec(sp);sp.loader.exec_module(o);return o
def current_route():
 assert sha(NATIVE)==NEW_ENTRY_SHA and sha(MEM/'native.before.sh')==OLD_ENTRY_SHA
 assert sha(MEM/'memory_frontend.py')==FRONT_SHA and sha(IO)==IO_SHA
 cfg=read(MEM/'ACTIVE_MEMORY.json');qa=read(MEM/'CPU_QUALIFICATION.json');back=read(MEM/'PUBLICATION_READBACK.json')
 assert cfg['status']=='ACTIVE_FUTURE_ONLY'and NEW not in cfg['allowed_cohorts']
 assert qa['status']=='PASS'and back['verified']is True and qa['qualified_sources']==back['qualified_sources']
 for role,digest in qa['qualified_sources'].items():assert sha(cfg[role+'_path'])==digest==cfg[role+'_sha256']
 assert sha(MEM/'CPU_QUALIFICATION.json')==cfg['QA_sha256']and sha(MEM/'PUBLICATION_READBACK.json')==cfg['readback_sha256']
 current=NATIVE.read_text();old=(MEM/'native.before.sh').read_text();mp=str(MEM/'memory_frontend.py')
 assert current.count(mp)==2 and current.replace(mp,str(IO))==old,'Unexpected native route change'
 return dict(status='PASS_CURRENT_UNALLOWED_EXACT_OLD_IO_DELEGATION',new_cohort=NEW,native_entry_path=str(NATIVE),native_entry_sha256=NEW_ENTRY_SHA,
  original_IO_qualified_entry_sha256=OLD_ENTRY_SHA,memory_frontend_path=mp,memory_frontend_sha256=FRONT_SHA,
  delegate_IO_path=str(IO),delegate_IO_sha256=IO_SHA,observed_memory_scope_mode=cfg['scope_mode'],observed_allowed_cohorts=cfg['allowed_cohorts'],
  observed_memory_cfg_path=str(MEM/'ACTIVE_MEMORY.json'),observed_memory_cfg_sha256=sha(MEM/'ACTIVE_MEMORY.json'),new_cohort_not_memory_allowed=True,
  only_two_IO_destinations_changed=True,future_memory_policy_applied_to_NEW=False)
def route_lineage_verifier(plan):
 """Mandatory Main registration callback: fresh route branch AND real lineage."""
 route=current_route();expected=plan['new_spec']['supplemental_trial_lineage']['native_entry_evidence']
 assert route['native_entry_sha256']==expected['native_entry_sha256']and route['memory_frontend_sha256']==expected['memory_frontend_sha256']
 from supplemental_trial import verify_lineage
 proof=verify_lineage(plan);return dict(proof,supplemental_current_route_verification=route)
def main():
 before=current_route();entry=NATIVE.read_text();mp=str(MEM/'memory_frontend.py')
 prefix=entry.split('# New exact multiworkload cohorts only.',1)[0];assert prefix.count(mp)==2
 stub='''import importlib.util,json,pathlib,sys,types
P=pathlib.Path
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
front=load('actual_memory_prefix',MEMFRONT)
io=load('actual_IO_parser',IOFRONT)
seen=[]
def delegate(argv):
 parsed,padding=io.parse(argv);seen.append(list(argv));return dict(status='OLD_IO_DELEGATE_CPU_ONLY',argv=argv,parsed=parsed,padding=padding,memory_adapter_called=False,native_prepare_called=False,model_starts=0)
fake=types.SimpleNamespace(main=delegate)
front.load=lambda name,path:fake
front.adapt_io=lambda *a:(_ for _ in()).throw(AssertionError('Unallowed NEW entered memory adapter'))
value=front.main(sys.argv[1:]);assert len(seen)==1;print(json.dumps(value))
'''.replace('MEMFRONT',repr(mp)).replace('IOFRONT',repr(str(IO)))
 rows=[]
 with tempfile.TemporaryDirectory(prefix='CPU_ROUTE_NEWTRIAL_',dir=R/'analysis')as name:
  root=P(name);target=root/'CPU_ONLY_delegate.py';target.write_text(stub)
  shell=root/'native_prefix_CPU_ONLY.sh';shell.write_text(prefix.replace(mp,str(target))+'\nexit 97\n')
  for stage in ('prepare','inspect','run-native'):
   argv=['experiment',stage,NEW,'--project','DTC_L1'];p=subprocess.run(['/bin/sh',str(shell),*argv],capture_output=True,text=True,check=True)
   value=json.loads(p.stdout);assert value['argv']==argv and value['parsed']==argv and value['padding']is False and value['model_starts']==0
   rows.append(value)
  # The real memory-front branch recognizes its actual selected canary.
  front=load('actual_memory_control_branch',MEM/'memory_frontend.py');called=[]
  fake=type('FakeIO',(),{'main':lambda self,argv:dict(CPU_ONLY=True)})()
  front.load=lambda *args:fake
  front.adapt_io=lambda io,cfg:(called.append(cfg)or io)
  allowed=read(MEM/'ACTIVE_MEMORY.json')['allowed_cohorts'][0]
  front.main(['experiment','prepare',allowed,'--project','DTC_L1']);assert len(called)==1
 after=current_route();assert before==after,'Scope/source changed during qualification'
 out=dict(schema='SUPPLEMENTAL_SCAN_NATIVE_ROUTE_CPU_QUALIFICATION_V2',status='PASS',checks=4,
  current_route=before,prefix_cases=rows,allowed_canary_positive_control=True,
  native_entry_bytes_changed=False,native_prepare_calls=0,model_starts=0,signals=0,production_mutations=0,
  publication_commit='b8595e651ab61cf1349bc433a75edaa74b095cdd',
  source_sha256=sha(P(__file__)))
 (HERE/'ROUTE_CPU_QUALIFICATION.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out))
if __name__=='__main__':main()
