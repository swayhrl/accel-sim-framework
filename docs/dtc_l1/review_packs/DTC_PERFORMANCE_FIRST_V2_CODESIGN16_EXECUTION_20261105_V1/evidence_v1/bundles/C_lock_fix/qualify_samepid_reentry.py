"""Exact old same-PID distinct-FD flock deadlock and both-profile forward regression.
Every lock, process and mutator is private CPU fixture data; no native authority.
"""
from pathlib import Path
import ast,copy,fcntl,hashlib,json,multiprocessing as mp,os,time
O=Path(__file__).resolve().parent;REQ='DTC_PERF_FIRST_V2_PHYSICAL_PIB16_20261105_V1';R=Path('/root/data/dtc_perf_first_v2_codesign16_20261105_v1');F=O/'cpu_samepid_reentry_fixture';F.mkdir(exist_ok=True);(F/'control/specs').mkdir(parents=True,exist_ok=True);LOCK=F/'LOCK';RESOURCE=R/'tools/perf16_resources.py'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_bytes())
def extracted(path,name,ns):
 n=next(x for x in ast.parse(path.read_bytes()).body if isinstance(x,ast.FunctionDef)and x.name==name);exec(compile(ast.Module(body=[n],type_ignores=[]),str(path)+':SANDBOX_CPU','exec'),ns);return ns[name]

def worker(pipe,physical,old,held):
 cohort='E2-DTCPFV2-d984ea5475a581ad-DH-PHYS'+str(physical)+'-OOPIB192-V1';raw=(R/'control/specs'/(cohort+'.json')).read_bytes();p=F/'control/specs'/(cohort+'.json');p.write_bytes(raw);(F/'control'/(cohort+'_SPEC.json')).write_bytes(raw);spec=read(p);calls=[];second_fd=[]
 pure={'REQ':REQ,'sha':sha,'VARIANT_TOKENS':{'PHYS768_OOPIB192_TAG64x8':'unused','PHYS1024_OOPIB192_TAG64x8':'unused'}};hold=extracted(RESOURCE,'admission_hold',pure)
 def source_read_reentry(c):
  fd=LOCK.open('a+b');second_fd.append(fd);pipe.send({'state':'ABOUT_TO_REENTER_SH_SAME_PID_SECOND_FD','pid':os.getpid(),'second_fd':fd.fileno(),'inode':os.fstat(fd.fileno()).st_ino});fcntl.flock(fd,fcntl.LOCK_SH);return spec
 ns={'R':F,'REQ':REQ,'read':read,'sha':sha,'spec_for':source_read_reentry,'registered':lambda:(_ for _ in()).throw(AssertionError('FORBIDDEN_REGISTERED')),'authority':lambda:(_ for _ in()).throw(AssertionError('FORBIDDEN_AUTHORITY')),'admission_hold':hold}
 guard=extracted(O/('ORIGINAL_perf16_native_635149.py'if old else'perf16_native.py'),'guard_model_mutation',ns)
 own={'request':REQ,'state':'ARMED','consumed':{},'admitted_specs':{cohort:sha(p)},'admission_holds':{}}
 evidence=F/('evidence_'+str(physical)+'.json');evidence.write_text('{"synthetic_CPU_only":true}\n')
 if held:own['admission_holds'][spec['profile']]={'classification':'CONFIGURATION_OR_LIFECYCLE_SAFETY_HOLD','decided_by':'DTC_MAIN','profile':spec['profile'],'reason':'CPU_ONLY','created_utc':'CPU_ONLY','evidence_path':str(evidence),'evidence_sha256':sha(evidence)}
 current={'registered_future_requests':{REQ:own,'FOREIGN':{'opaque':'CPU_SENTINEL'}}};before=copy.deepcopy(current)
 with LOCK.open('a+b')as first:
  fcntl.flock(first,fcntl.LOCK_EX);pipe.send({'state':'EX_LOCKED','pid':os.getpid(),'first_fd':first.fileno(),'inode':os.fstat(first.fileno()).st_ino})
  try:guard(current,cohort,lambda cur:calls.append('CPU_MUTATOR'));state='ALLOWED'
  except AssertionError as e:state='REFUSED';reason=str(e)
 pipe.send({'state':state,'calls':len(calls),'registry_unchanged':before==current,'second_fd_attempts':len(second_fd),'reason':locals().get('reason')})

if __name__=='__main__':
 ctx=mp.get_context('fork');rows=[];checks=[]
 def ck(n,v):assert v,n;checks.append({'check':n,'PASS':True})
 for physical in [768,1024]:
  for old,held in [(True,False),(False,False),(False,True)]:
   par,child=ctx.Pipe();proc=ctx.Process(target=worker,args=(child,physical,old,held),name='PRIVATE_CPU_SAMEPID_FLOCK_ONLY');proc.start();child.close();assert par.poll(3);locked=par.recv();ck(str(physical)+str((old,held))+'_real_exclusive_lock',locked['state']=='EX_LOCKED');assert par.poll(3);msg=par.recv()
   if old:
    ck(str(physical)+'_old_reentry_real_secondFD_samePID_sameinode',msg['state']=='ABOUT_TO_REENTER_SH_SAME_PID_SECOND_FD'and msg['pid']==locked['pid']and msg['inode']==locked['inode']and msg['second_fd']!=locked['first_fd'])
    timed_out=not par.poll(.75);ck(str(physical)+'_old_deadlock_bounded_timeout',timed_out)
    # Terminate only the self-created CPU fixture child, never any native process.
    proc.terminate();proc.join(3);ck(str(physical)+'_private_fixture_child_terminated_and_reaped',not proc.is_alive());rows.append({'physical':physical,'old':True,'state':'EXPECTED_OLD_SAME_PID_FLOCK_SELF_DEADLOCK','timeout_seconds':.75,'samePID_distinctFD_sameinode':True,'signal_scope':'only_own_private_CPU_fixture_child'})
   else:
    proc.join(3);ck(str(physical)+str(held)+'_new_exits_no_lock_reentry',proc.exitcode==0 and msg['second_fd_attempts']==0);ck(str(physical)+str(held)+'_wholemock_registry_unchanged',msg['registry_unchanged']);ck(str(physical)+str(held)+'_correct_mutator_hold_path',msg['calls']==int(not held)and msg['state']==('REFUSED'if held else'ALLOWED'));rows.append({'physical':physical,'old':False,'typed_HOLD':held,'result':msg})
  par.close()
 out={'schema':'DTC_CODESIGN16_SAMEPID_FLOCK_COUNTEREXAMPLE_AND_FIX_CPU_V1','status':'PASS_CPU_ONLY','old_source_sha256':sha(O/'ORIGINAL_perf16_native_635149.py'),'new_source_sha256':sha(O/'perf16_native.py'),'resource_helper_sha256':sha(RESOURCE),'rows':rows,'checks':checks,'count':len(checks),'native_registry_or_owner_or_model_operations':0,'only_signals_sent':'two_bounded_expected_deadlock_private_CPU_fixture_children','old_source_modified':False}
 (O/'CPU_SAME_PID_REENTRY_REGRESSION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':'PASS_CPU_ONLY','checks':len(checks),'cases':len(rows)}))
