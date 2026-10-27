"""New Native174 own-scope supervisor. Default requires exact external Root approval; no auto-arm."""
import pathlib,os,sys,json,time,math,fcntl,signal,subprocess,resource,importlib.util,socket,argparse,shutil,stat
from owned_runtime_v1 import *
D=pathlib.Path(__file__).resolve().parent
AUTHOR=D.parent/'streamcluster_cpu_resume_execute_prepare_20261027_v2'
PROD_SRC=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/inflight/ORD_Rodinia_streamcluster_1be5fda1aa60_A001')
AUTH=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control/ROOT_STREAMCLUSTER_CPU_RESUME_EXEC_APPROVAL_V2.json')
POST5D='5d3ffcd3cf000e1f72e2adf97b4185217a51e1fe0c147c5c39500130e418e66d'
BOOT="import os,sys;fd=int(sys.argv[1]);t=os.read(fd,1);os.close(fd);sys.exit(125)if t!=b'G'else None;os.execv(sys.argv[2],sys.argv[2:])"
def readref(r):
 p=pathlib.Path(r['path']);need(type(r['bytes'])is int and 0<r['bytes']<=8*2**20,'bounded metadata8MiB')
 fd=os.open(p,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW)
 try:
  before=os.fstat(fd);need(stat.S_ISREG(before.st_mode)and before.st_size==r['bytes'],'regular exact metadata size')
  raw=b''
  while len(raw)<=8*2**20:
   chunk=os.read(fd,min(65536,8*2**20+1-len(raw)))
   if not chunk:break
   raw+=chunk
  after=os.fstat(fd);now=p.stat(follow_symlinks=False)
  identity=lambda x:(x.st_dev,x.st_ino,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
  need(identity(before)==identity(after)==identity(now)and len(raw)==r['bytes']and hashlib.sha256(raw).hexdigest()==r['sha256'],'stable metadata FD raw hash')
 finally:os.close(fd)
 return json.loads(raw)
def ref(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
def load(path):
 sp=importlib.util.spec_from_file_location('selected_exact',path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def release_code(pin):
 need(sha(D/'launch/CODE_MANIFEST.json')==pin,'external launch code pin')
 for r in json.loads((D/'launch/CODE_MANIFEST.json').read_text())['files']:need(sha(D/r['relative'])==r['sha256'],'launch source changed')
def resource_gate(a):
 import dynamic_resources_v1 as R
 return R.check(a)
def fresh_terminal(a,M,runtime):
 probe=load(D/'fresh_terminal_probe_v1.py');actual=probe.observe();need(actual['closed']is True,'old exact workload/owned/leases not terminal')
 write(runtime/'FRESH_OLD_TERMINAL_RAW.json',actual)
 e=readref(a['terminal_base_ref']);e['terminal']['audit_age_seconds']=0;e['terminal']['observed_unix']=actual['unix'];e['terminal']['root_terminal_receipt_raw_sha256']=sha(runtime/'FRESH_OLD_TERMINAL_RAW.json');e['terminal']['root_terminal_receipt_ref']=ref(runtime/'FRESH_OLD_TERMINAL_RAW.json');e['terminal']['root_did_not_reap_original']=True
 write(runtime/'EXACT_TERMINAL_EVIDENCE.json',e);return ref(runtime/'EXACT_TERMINAL_EVIDENCE.json')
