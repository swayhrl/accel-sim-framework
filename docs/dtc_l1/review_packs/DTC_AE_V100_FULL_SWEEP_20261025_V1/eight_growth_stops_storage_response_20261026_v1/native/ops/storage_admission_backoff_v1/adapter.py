"""R19 metadata-only storage recovery backoff after actual growth stops.
Preserves all native runtime guard floors and scientific attempts.
"""
import pathlib,json,hashlib,os,sys,threading,datetime,importlib.util
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');D=F/'ops/storage_admission_backoff_v1';T=P('/root/data/dtc_main_v100_sweep_20261025_v1');CONT=F/'ops/revision19/sweep_controller.py';EXPECTED='c4cc1f48e404f949afb5bfe942044031bfc6650fe6f4032b97757b370f82f532';G=1024**3
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def ready(sample):return sample['physical_RAM_pass']and sample['physical_disk_pass']and sample['native_free_bytes']-sample['required_free_bytes']>=5*G
def make_wrapper(original,resource):
 def admit_order(q,root,claims,cooldown,now,blocked=()):
  candidates=original(q,root,claims,cooldown,now,blocked)
  if not candidates:return candidates
  c=candidates[0];p=root/'control'/((c+'_SPEC.json')if root==T else('specs/'+c+'.json'));s=read(p);sample=resource(s,True)
  # Recheck on every controller cycle, admitting at most one point per scope.
  # The native admission/runtime checks are still independently executed.
  return [c]if ready(sample)else[]
 return admit_order
def apply():
 assert threading.current_thread()is threading.main_thread();plan=read(D/'PLAN.json');qual=read(D/'CPU_QUALIFICATION.json');assert qual['status']=='PASS'and qual['adapter_sha256']==sha(__file__)and qual['plan_sha256']==sha(D/'PLAN.json');st=P('/proc/self/stat').read_text().rsplit(')',1)[1].split();assert(os.getpid(),int(st[19]))==(plan['parent_pid'],plan['parent_start_ticks'])and sha(CONT)==EXPECTED;frame=sys._getframe()
 while frame and not(frame.f_code.co_name=='main'and frame.f_globals.get('__file__')==str(CONT)):frame=frame.f_back
 assert frame is not None;g=frame.f_globals;l=frame.f_locals;lease=read(T/'control/BATCH_LEASE.json');assert(lease['pid'],lease['start_ticks'],lease['controller_sha256'])==(os.getpid(),plan['parent_start_ticks'],EXPECTED);assert g['admit_order'].__code__.co_filename==str(CONT)and not(D/'ACTUAL_ACK.json').exists();old=g['admit_order'];new=make_wrapper(old,l['accounting'].resources);ack=dict(status='ACTUAL_STORAGE_RECOVERY_ADMISSION_BACKOFF_INSTALLED',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),pid=os.getpid(),start_ticks=plan['parent_start_ticks'],parent_source_sha256=EXPECTED,adapter_sha256=sha(__file__),plan_sha256=sha(D/'PLAN.json'),admission_only_recovery_margin_bytes=5*G,native_runtime_floors_unchanged=True,scientific_model_signals=0,model_starts_by_callback=0,authority_mutations=0,old_function_source=old.__code__.co_filename,new_function_source=new.__code__.co_filename)
 # Main thread cannot dispatch between the ACK and the immediate dictionary set.
 with(D/'ACTUAL_ACK.json').open('x')as f:json.dump(ack,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 g['admit_order']=new;g['_STORAGE_ADMISSION_BACKOFF_STATE']=ack;return ack
