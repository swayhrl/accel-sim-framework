#!/usr/bin/env python3
"""Independent finite readonly runtime issuer. Root preapproval required.
Only ELF/disk library resolution is attested; never actual loaded GPU modules.
No Root capture grant is created. Request/challenge and all raw evidence stay private.
"""
import pathlib,json,hashlib,time,os,socket,subprocess,shlex,sys
from native_boundary_state_machine_candidate_v1 import SCOPE,DEADLINE
D=pathlib.Path(__file__).resolve().parent
CONTROL=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control')
APP='/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/bin/sdk42_v4_reduction'
BINARY='cdcf7c2abc6cd73afadb2d4e6bce2eb0b06e22d4728b6e6b0df7c04be73cadcf'
ACTION='ISSUE_ONE_REDUCTION_ENTRY_FRESH_READONLY_RUNTIME_ADMISSION_V1'
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def load(p):return json.loads(pathlib.Path(p).read_text())
def need(ok,why):
 if not ok:raise RuntimeError(why)
def save(p,o):
 with pathlib.Path(p).open('x') as f:json.dump(o,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
APPROVED_ENTRY_PYTHON_ALIAS='/usr/bin/python3'
APPROVED_ENTRY_PYTHON_EXE='/usr/bin/python3.10'
APPROVED_ENTRY_PYTHON_FLAGS=('-B',)
def identity(pid):
 try:
  p=pathlib.Path('/proc',str(pid))
  first=(p/'stat').read_text().split(') ',1)[1].split()
  exe=str((p/'exe').resolve(strict=True))
  raw=(p/'cmdline').read_bytes()
  if not raw.endswith(b'\0'):return None
  argv=[os.fsdecode(x) for x in raw[:-1].split(b'\0')]
  last=(p/'stat').read_text().split(') ',1)[1].split()
  if first[19]!=last[19]:return None
  return {'pid':int(pid),'start_ticks':last[19],'boot_id':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'state':last[0],'exe':exe,'argv':argv,'cmdline':' '.join(argv)}
 except (FileNotFoundError,PermissionError,ProcessLookupError,OSError,UnicodeError):return None
def entry_same(request,expected_source):
 """Only the exact approved interpreter/flags/script/entry CLI is accepted.
 A matching path elsewhere in another script's argv is never script identity."""
 try:
  x=identity(request['entry']['pid'])
  if not x or x['state']=='Z' or not all(x[k]==request['entry'][k] for k in ('pid','start_ticks','boot_id')):return False
  if x['exe']!=APPROVED_ENTRY_PYTHON_EXE:return False
  if str(pathlib.Path(APPROVED_ENTRY_PYTHON_ALIAS).resolve(strict=True))!=APPROVED_ENTRY_PYTHON_EXE:return False
  expected_source=str(expected_source)
  if str(pathlib.Path(expected_source).resolve(strict=True))!=expected_source:return False
  pin=request['entry_approval_sha256']
  if not isinstance(pin,str) or len(pin)!=64 or any(c not in '0123456789abcdef' for c in pin):return False
  expected=[APPROVED_ENTRY_PYTHON_ALIAS,*APPROVED_ENTRY_PYTHON_FLAGS,expected_source,
            '--execute','--approval',str(pathlib.Path(expected_source).parent/'ROOT_NATIVE_ENTRY_APPROVAL_V1.json'),
            '--approval-sha',pin]
  return x['argv']==expected
 except (KeyError,TypeError,ValueError,FileNotFoundError,PermissionError,ProcessLookupError,OSError):return False

def namespace(pid):
 return {x:os.readlink('/proc/'+str(pid)+'/ns/'+x) for x in ('mnt','pid','user')}
def pointer(data,parts):
 for p in parts:data=data[p]
 return data
def foreign_snapshot(specs):
 rows=[];total=0
 for spec in specs:
  p=pathlib.Path(spec['path']);need(p.is_file() and not p.is_symlink() and p.stat().st_size<=16*1024**2,'foreign metadata path/size')
  b=p.read_bytes();data=json.loads(b);entries=pointer(data,spec['entries_keys'])
  entries=list(entries.values()) if isinstance(entries,dict) else entries
  need(isinstance(entries,list),'foreign entries schema')
  reservations=[]
  for entry in entries:
   need(spec['reserved_field'] in entry,'unknown foreign reservation schema; do not lower projection')
   value=entry[spec['reserved_field']]
   need(type(value) is int and value>=0,'foreign reserve type')
   total+=value;reservations.append({'identity':entry.get(spec['id_field']),'state':entry.get(spec['state_field']),'reserved_bytes':value,'future_or_remaining':entry.get(spec.get('remaining_field','remaining'))})
  rows.append({'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'reservations':reservations,'all_states_kept':True})
 return rows,total
def local_report(baseline):
 need(socket.gethostname()==baseline['native_hostname'],'Native host drift')
 need(namespace('self')==baseline['native_namespaces'],'Native namespace drift')
 need(str(pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1').resolve())==baseline['native_NAS_canonical_root'],'NAS root drift')
 need(os.stat(baseline['native_NAS_canonical_root']).st_dev!=os.stat('/root/data').st_dev,'NAS unexpectedly Native filesystem')
 import shutil
 native=shutil.disk_usage('/root/data').free;nas=shutil.disk_usage(baseline['native_NAS_canonical_root']).free
 need(native>=5*1024**3 and nas>=6*1024**3,'Native5GiB/NAS5GiB+1GiB own payload reserve')
 foreign,total=foreign_snapshot(baseline['foreign_registry_specs'])
 need(foreign,'all-foreign report absent')
 return {'native_hostname':socket.gethostname(),'namespaces':namespace('self'),'native_free_bytes':native,'NAS_free_bytes':nas,'foreign_snapshots':foreign,'all_registered_reserved_bytes_reported':total,'registered_overcommit_bytes_reported':max(0,total+5*1024**3-native),'resource_mode':'ROOT_PREAPPROVED_NAS_PAYLOAD_ONLY_NATIVE_FLOOR_FULL_FOREIGN_REPORT','no_foreign_reservation_excluded_or_budget_retired':True}
def remote_source(baseline):
 # --list uses the pinned dynamic loader's trace/list mode, not product execution.
 # CPU fixture tests verify constructors are not invoked by this mode.
 return (D/'elf_disk_resolution_v1.py').read_text()+"\n"+"""import pathlib,json,hashlib,os,socket,subprocess,re,shutil
b=EXBASE
os.nice(15);os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[:2])
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for q in iter(lambda:f.read(1048576),b''):h.update(q)
 return h.hexdigest()
assert socket.gethostname()==b['remote_hostname']
ns={x:os.readlink('/proc/self/ns/'+x) for x in ('mnt','pid','user')}
assert ns==b['remote_namespaces']
mounts=pathlib.Path('/proc/mounts').read_text().splitlines()
assert any(x.split()[0]==b['remote_NAS_mount_source'] and x.split()[1]=='/data/c16/rtx4080_suite_fill_20261024_v1/nas_rtx4080' and x.split()[2]=='fuse.sshfs' for x in mounts)
assert shutil.disk_usage('/data/c16').free>=5*1024**3
assert shutil.disk_usage('/data/c16/rtx4080_suite_fill_20261024_v1/nas_rtx4080').free>=6*1024**3
for x in b['remote_code_ELF_library_file_refs']:
 p=pathlib.Path(x['path']);assert str(p.resolve())==x['canonical_path'] and sha(p)==x['sha256']
assert sha('/usr/bin/readelf')==b['readelf_tool_sha256']
assert sha(b['loader_path'])==b['loader_sha256']
assert os.environ.get('LD_LIBRARY_PATH','')==b['LD_LIBRARY_PATH'],'ambient loader environment drift'
assert b['LD_PRELOAD']=='/data/c16/ada_trace_extensions_v8_20261024_v1/frozen/producer_v7_input_c8cfa41fcabc_r2/producer.so:libcuda.so.1'
result=resolve(b['app'],b['loader_path'],b['LD_LIBRARY_PATH'],b['LD_PRELOAD'])
assert result['readelf_stdout_sha256']==b['readelf_stdout_sha256']
resolved=result['library_resolutions']
assert resolved==b['expected_library_resolutions'],'disk library resolution drift'
print(json.dumps({'schema':'READONLY_ELF_DISK_LIBRARY_RESOLUTION_V1','host':socket.gethostname(),'namespaces':ns,'boot_id':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'library_resolutions':resolved,'readelf_stdout_sha256':result['readelf_stdout_sha256'],'loaded_gpu_modules_inspected':False,'CUDA_init_query_launch':False,'loader_list_mode_only':True,'Native_free_bytes':shutil.disk_usage('/data/c16').free,'NAS_free_bytes':shutil.disk_usage('/data/c16/rtx4080_suite_fill_20261024_v1/nas_rtx4080').free}))
""".replace('EXBASE',repr(baseline))
def remote_report(baseline):
 r=subprocess.run(['ssh','-n','-o','BatchMode=yes','-o','ConnectTimeout=12','gpu109','python3 -B -c '+shlex.quote(remote_source(baseline))],capture_output=True,text=True,timeout=45)
 need(r.returncode==0,'readonly remote baseline drift/probe failed '+r.stderr[-1600:])
 return json.loads(r.stdout)
def issue_once(request,entry_approval,baseline,remote,local,issuer_approval_sha,baseline_sha,request_sha):
 need(entry_same(request,entry_approval['controller_path']),'entry identity no longer live')
 need(request['scope']==SCOPE and request['job_id']=='C8_SDK42_REDUCTION_DEFAULT65536_SPECIALIST_A001','request scope')
 need(request['entry_approval_sha256']==entry_approval['sha256'] and request['runtime_baseline_sha256']==baseline_sha,'request approval/baseline')
 need(type(request['challenge']) is str and len(request['challenge'])==64,'one challenge')
 need(baseline['app']==APP and baseline['binary_sha256']==BINARY,'fixed application scope')
 need(remote['loaded_gpu_modules_inspected'] is False and remote['CUDA_init_query_launch'] is False,'issuer cannot claim dynamic GPU module inspection')
 need(remote['library_resolutions']==baseline['expected_library_resolutions'],'resolver drift')
 # Reopen foreign registries after remote work; legitimate updates demand a new request/admission, never stale signing.
 for x in local['foreign_snapshots']:need(sha(x['path'])==x['sha256'],'foreign reservation changed during probe')
 now=time.time()
 return {'schema':'INDEPENDENT_REDUCTION_ENTRY_RUNTIME_ADMISSION_V1','status':'ROOT_FRESH_EXACT_BINARY_ELF_LIBRARY_RUNTIME_ADMITTED','approved':True,'scope':SCOPE,'issuer_authority_id':entry_approval['issuer_authority_id'],'issuer_source_sha256':sha(__file__),'issuer_approval_sha256':issuer_approval_sha,'runtime_baseline_sha256':baseline_sha,'native_entry_Root_approval_sha256':entry_approval['sha256'],'request_sha256':request_sha,'entry_identity':request['entry'],'activation_nonce':entry_approval['activation_nonce'],'challenge':request['challenge'],'unix':now,'expires_unix':min(now+30,request['absolute_deadline_unix']),'worker_sha256':entry_approval['worker_sha256'],'binary_sha256':BINARY,'remote_code_ELF_library_file_refs':baseline['remote_code_ELF_library_file_refs'],'library_resolutions':remote['library_resolutions'],'readelf_tool_sha256':baseline['readelf_tool_sha256'],'fresh_readelf':{'stdout_sha256':baseline['readelf_stdout_sha256'],'LD_LIBRARY_PATH':baseline['LD_LIBRARY_PATH']},'ELF_NEEDED_and_load_paths_closed':True,'full_foreign_reservations_accounted':True,'resource_admitted':True,'foreign_registry_refs':[{'path':x['path'],'sha256':x['sha256']} for x in local['foreign_snapshots']],'native_resource_report':local,'remote_disk_resolution_report':remote,'loaded_gpu_modules_inspected':False,'scope_limit':'ELF/disk resolution only; no actual loaded-GPU-module/native/consumer/timing/science acceptance'}
def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true',required=True);p.add_argument('--approval',required=True);p.add_argument('--approval-sha',required=True);p.add_argument('--entry-approval-sha',required=True);a=p.parse_args()
 need(pathlib.Path(a.approval).resolve()==(D/'ROOT_ISSUER_APPROVAL_V1.json').resolve() and sha(a.approval)==a.approval_sha,'Root issuer approval path/pin')
 cfg=load(a.approval);need(cfg.get('approved') is True and cfg.get('action')==ACTION and cfg.get('fixture_only') is not True,'Root issuer approval absent')
 need(cfg['issuer_source_sha256']==sha(__file__) and cfg['entry_approval_sha256']==a.entry_approval_sha,'issuer/entry pin')
 baseline_path=D/'ROOT_EXPECTED_RUNTIME_BASELINE_V1.json';need(sha(baseline_path)==cfg['runtime_baseline_sha256'],'Root expected immutable baseline')
 baseline=load(baseline_path)
 need(baseline['scope']==SCOPE and baseline['app']==APP and baseline['binary_sha256']==BINARY,'fixed baseline scope')
 need(baseline['resource_mode']=='ROOT_PREAPPROVED_NAS_PAYLOAD_ONLY_NATIVE_FLOOR_FULL_FOREIGN_REPORT','resource mode must be explicitly preapproved')
 entry_path=D/'ROOT_NATIVE_ENTRY_APPROVAL_V1.json';need(sha(entry_path)==a.entry_approval_sha,'entry approval changed')
 entry=load(entry_path);need(entry.get('approved') is True and entry.get('action')==SCOPE and entry['runtime_baseline_sha256']==cfg['runtime_baseline_sha256'] and entry['issuer_authority_id']==cfg['issuer_authority_id'],'entry delegation')
 entry.update(sha256=a.entry_approval_sha,controller_path=str(D/'native_reduction_entry_candidate_v1.py'))
 need(sha(entry['controller_path'])==entry['controller_sha256'],'entry controller source')
 need(entry['issuer_source_sha256']==sha(__file__),'entry expected issuer source')
 need(len(baseline['remote_code_ELF_library_file_refs'])>=8 and baseline['expected_library_resolutions'],'incomplete immutable expected files/libs')
 need(baseline['LD_PRELOAD']=='/data/c16/ada_trace_extensions_v8_20261024_v1/frozen/producer_v7_input_c8cfa41fcabc_r2/producer.so:libcuda.so.1','fixed C8 preload profile')
 need(baseline['loader_path'].startswith('/lib') and baseline['readelf_tool_sha256'] and baseline['loader_sha256'],'loader/tool pins')
 need(baseline['foreign_registry_specs'],'foreign authority inventory absent')

 deadline=cfg['absolute_wait_deadline_unix'];need(time.time()<deadline<=DEADLINE-120 and deadline-time.time()<=72*3600,'finite issuer deadline')
 os.nice(15);os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[:2])
 run=D/'issuer_run';run.mkdir(exist_ok=False);save(run/'IDENTITY.json',identity(os.getpid()))
 request_path=D/'entry_run/RUNTIME_ADMISSION_REQUEST.json';ack_path=D/'entry_run/RUNTIME_ADMISSION_CONSUMED_ACK.json'
 while time.time()<deadline:
  if list((D/'entry_run').glob('*FAILED_RETAINED*.json')):save(run/'TERMINAL.json',{'status':'ENTRY_TERMINAL_NO_ISSUE'});return
  if not request_path.exists():time.sleep(.2);continue
  request=load(request_path);rh=sha(request_path)
  need(entry_same(request,entry['controller_path']),'request entry PID/ticks/boot/cmdline')
  need(namespace(request['entry']['pid'])==baseline['native_namespaces'],'entry namespace drift')
  need(0<request['absolute_deadline_unix']-time.time()<=3600 and request['absolute_deadline_unix']<=deadline,'request finite deadline')
  from resume_gate_v1 import lease_owned_by
  need(all(lease_owned_by(request['entry']['pid'],CONTROL/name) for name in ['RTX4080_DISPATCHER.lock','RTX4080_SOURCE.lock','RTX4080_TARGET.lock','RTX4080_QUEUE.lock']),'entry does not own four Native leases')
  own=request['own_stop_identity'];stop=CONTROL/'STOP_AFTER_CURRENT';st=stop.lstat()
  need(not stop.is_symlink() and (st.st_ino,st.st_dev)==(own['inode'],own['dev']) and stop.read_bytes().hex()==own['raw'],'own STOP identity changed')
  payload=json.loads(stop.read_bytes());need(payload['owner']==SCOPE and payload['Root_approval_sha256']==a.entry_approval_sha,'STOP scope/approval')
  local=local_report(baseline);remote=remote_report(baseline)
  save(run/'LOCAL_READONLY_REPORT.json',local);save(run/'REMOTE_ELF_DISK_REPORT.json',remote)
  runtime=issue_once(request,entry,baseline,remote,local,a.approval_sha,cfg['runtime_baseline_sha256'],rh)
  out=D/'ROOT_ACTIVATION_RUNTIME_ADMISSION_V1.json';save(out,runtime);save(run/'ISSUED_ONCE.json',{'runtime_sha256':sha(out),'request_sha256':rh,'expires_unix':runtime['expires_unix']})
  while time.time()<min(deadline,runtime['expires_unix']):
   if ack_path.exists():
    ack=load(ack_path)
    need(ack['request_sha256']==rh and ack['runtime_sha256']==sha(out) and ack['entry']==request['entry'] and ack['challenge']==request['challenge'],'entry consumption ACK')
    save(run/'TERMINAL.json',{'status':'ONE_ADMISSION_CONSUMED_ACKED_EXIT'});return
   if not entry_same(request,entry['controller_path']):save(run/'TERMINAL.json',{'status':'ENTRY_ENDED_AFTER_ISSUE'});return
   time.sleep(.1)
  save(run/'TERMINAL.json',{'status':'ONE_ADMISSION_EXPIRED_UNCONSUMED_NO_REISSUE'});return
 save(run/'TERMINAL.json',{'status':'ABSOLUTE_FINITE_WAIT_DEADLINE_NO_ISSUE'})
if __name__=='__main__':
 try:main()
 except BaseException as e:
  p=D/'issuer_run/TERMINAL.json'
  if p.parent.exists() and not p.exists():save(p,{'status':'FAILED_READONLY_NO_ISSUE_OR_REISSUE','error_type':type(e).__name__})
  raise
