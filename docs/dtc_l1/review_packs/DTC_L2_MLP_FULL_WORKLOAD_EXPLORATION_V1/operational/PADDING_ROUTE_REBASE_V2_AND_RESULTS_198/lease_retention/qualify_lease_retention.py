import pathlib as pl,importlib.util,hashlib,json,os,sys,tempfile,fcntl,gc,subprocess,threading,time
P=pl.Path;B=P(__file__).parent
sp=importlib.util.spec_from_file_location('retain_candidate',B/'retain_original_lease_io.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
checks=[]
def ck(n,v):
 assert v,n
 checks.append(n)
def denied(fn):
 try:fn()
 except (AssertionError,OSError,ValueError):return True
 return False
# Genuine isolated child process demonstrates destructor behavior after main return.
child="""import importlib.util,pathlib,sys,tempfile,fcntl,os,gc,threading,time
p=pathlib.Path(sys.argv[1]);s=importlib.util.spec_from_file_location('a',p);a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
d=pathlib.Path(tempfile.mkdtemp());targets={};fds=[];result={}
def observer():
 time.sleep(.05);gc.collect()
 result['alive']=[os.path.exists('/proc/self/fd/'+str(x))for x in fds]
def main():
 owner=(d/'owner').open('a+b');held=(d/'held').open('a+b')
 for f in [owner,held]:fcntl.flock(f,fcntl.LOCK_EX);targets[f.fileno()]=pathlib.Path(f.name);fds.append(f.fileno())
 if sys.argv[2]=='retain':a.retain_objects({owner.fileno():owner,held.fileno():held},targets,os.getpid(),a.ticks(os.getpid()))
 t=threading.Thread(target=observer);t.start();return t
t=main();t.join();print(result['alive'])
"""
for mode,expected in [('none','[False, False]'),('retain','[True, True]')]:
 out=subprocess.run([sys.executable,'-c',child,str(B/'retain_original_lease_io.py'),mode],text=True,capture_output=True,check=True)
 ck('main_return_'+mode+'_real_subprocess',out.stdout.strip()==expected)
with tempfile.TemporaryDirectory()as d:
 d=P(d);files=[(d/n).open('a+b')for n in ['owner','held']]
 for f in files:fcntl.flock(f,fcntl.LOCK_EX)
 objects={f.fileno():f for f in files};targets={f.fileno():P(f.name)for f in files};pid=os.getpid();ticks=m.ticks(pid);ns={}
 ck('wrong_pid_rejected',denied(lambda:m.retain_objects(objects,targets,pid+1,ticks,namespace=ns)))
 ck('wrong_generation_rejected',denied(lambda:m.retain_objects(objects,targets,pid,ticks+1,namespace=ns)))
 wrong=dict(targets);wrong[next(iter(wrong))]=d/'wrong';ck('wrong_target_rejected',denied(lambda:m.retain_objects(objects,wrong,pid,ticks,namespace=ns)))
 wrong=dict(objects);ks=list(wrong);wrong[ks[0]]=objects[ks[1]];ck('wrong_fd_rejected',denied(lambda:m.retain_objects(wrong,targets,pid,ticks,namespace=ns)))
 # Any accidental lease reacquisition would fail this qualification.
 original=fcntl.flock
 def forbidden(*a,**k):raise AssertionError('new flock forbidden')
 fcntl.flock=forbidden
 proof=m.retain_objects(objects,targets,pid,ticks,namespace=ns);proof2=m.retain_objects(objects,targets,pid,ticks,namespace=ns)
 ck('idempotent_exact_original_objects_without_flock',proof2['idempotent']and all(ns[m.MARKER]['objects'][fd]is obj for fd,obj in objects.items()))
 fcntl.flock=original
 found,kind=m.discover_original_objects('/absent/controller.py',targets);ck('postmain_gc_recovers_only_original_wrappers',kind=='GC_ORIGINAL_BUFFERED_IO_ONLY'and all(found[fd]is obj for fd,obj in objects.items()))
 files[0].close();ck('closed_object_rejected_no_reacquisition',denied(lambda:m.retain_objects(objects,targets,pid,ticks,namespace={})))
 files[1].close()
res=dict(schema='ORIGINAL_OWNER_LEASE_IO_RETENTION_CPU_QUALIFICATION_V1',status='PASS',checks=checks,total_checks=len(checks),source_sha256=hashlib.sha256((B/'retain_original_lease_io.py').read_bytes()).hexdigest(),driver_sha256=hashlib.sha256(P(__file__).read_bytes()).hexdigest(),production_parent_attached=False,production_mutations=0,model_starts=0,model_signals=0,real_subprocess_main_return_controls=True)
(B/'CPU_QUALIFICATION.json').write_text(json.dumps(res,sort_keys=True,indent=2)+'\n')
print(json.dumps(res))
