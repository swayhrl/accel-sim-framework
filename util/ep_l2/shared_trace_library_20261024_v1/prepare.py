from pathlib import Path
import json,gzip,hashlib,os,subprocess,shlex,sys,datetime
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');R.mkdir(exist_ok=True)
for n in ['tools','control','reports','manifests','logs','recovery']:(R/n).mkdir(exist_ok=True)
A=Path('/root/data/ep_l2_main_20261023_v1/worktree/docs/ep_l2/operations/ep_main_account_workload_audit_20261024_v2')
def put(n,d):(R/n).write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
def canon(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
rows=json.loads(gzip.decompress((A/'EXACT_INPUT_INDEX.json.gz').read_bytes()))
objs=json.loads(gzip.decompress((A/'TRACE_MEMBER_OBJECT_METADATA.json.gz').read_bytes()))
req={h:[] for h in ['174','174-new']};aliases=[]
for x in rows:
 if not x['complete_by_metadata']:continue
 aliases.append({k:v for k,v in x.items() if k not in ['capture_scripts']})
 for k in x['member_object_keys']:
  o=objs[k]
  if not any(r['key']==k for r in req[x['host']]):req[x['host']].append(dict(key=k,path=o['example_path'],prior=o['stat']))
 # The commandlist is an independent necessary member.
 req[x['host']].append(dict(key='ENTRY:'+hashlib.sha256(x['path'].encode()).hexdigest(),path=x['path'],prior=None))
put('control/INPUT_ALIASES_FROM_AUDIT.json',aliases)
put('control/INCOMPLETE_INPUTS_RETAINED.json',[x for x in rows if not x['complete_by_metadata']])
put('control/USER_AUTHORIZATION.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'user_instruction':'Approved complete shared SM70 trace asset library Goal; all necessary permissions authorized','source_keep':True,'source_release_bytes':0,'scientific_starts_authorized':False,'109_capture_authorized':False,'cross_project_public_access':True,'regular_and_fraction_inputs':True})
protected=[Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json'),Path('/root/data/ep_l2_dtc_l1_native_v2/control/CURRENT_SCIENCE_EPOCH.json'),Path('/root/data/ep_l2_dtc_l1_native_v2/bin/native'),Path('/root/data/ep_l2_dtc_l1_native_v2/tools/native_v2.py')]
put('control/PROTECTED_PREIMAGE.json',{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected})
code=r'''
from pathlib import Path
import os,json,sys,stat,hashlib
req=json.load(sys.stdin);out=[]
for r in req:
 p=Path(r['path']);s=p.stat();ident={'dev':s.st_dev,'inode':s.st_ino,'size':s.st_size,'mtime_ns':s.st_mtime_ns,'ctime_ns':s.st_ctime_ns,'uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode),'nlink':s.st_nlink,'type':'file' if stat.S_ISREG(s.st_mode) else 'other'}
 assert ident['type']=='file' and ident['size']>0
 if r['prior']:
  assert [s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns]==[r['prior'][k] for k in ['dev','inode','bytes','mtime_ns']]
 row={'key':r['key'],'path':str(p),'realpath':str(p.resolve()),'identity':ident}
 if p.name=='kernelslist.g':
  fd=os.open(p,os.O_RDONLY|getattr(os,'O_NOATIME',0))
  with os.fdopen(fd,'rb') as f:b=f.read(1048577)
  assert len(b)<=1048576;row.update(sha256=hashlib.sha256(b).hexdigest(),commandlist_hex=b.hex())
 out.append(row)
print(json.dumps({'hostname':os.uname().nodename,'namespace':os.readlink('/proc/self/ns/mnt'),'files':out}))
'''
sys.path.insert(0,'/root/data/ep_l2_dtc_l1_management_20261023_v1/tools');import manage
for h in req:
 cmd=['python3','-B','-c',code] if h=='174-new' else manage.SSH+['python3 -B -c '+shlex.quote(code)]
 cp=subprocess.run(cmd,input=json.dumps(req[h]),capture_output=True,text=True,timeout=120)
 if cp.returncode:raise RuntimeError(cp.stderr)
 d=json.loads(cp.stdout);put('control/'+h+'_FROZEN_METADATA.json',d)
 print(h,len(d['files']),flush=True)
put('control/SOURCE_ARCHIVES.json',[{'host':'174','path':p} for p in [
'/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/cudasdk.tgz',
'/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/parboil.tgz',
'/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/polybench.tgz',
'/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-extract/parboil.mri.closeout.stage.tar.zst']])
print('PREPARED',str(R),flush=True)
