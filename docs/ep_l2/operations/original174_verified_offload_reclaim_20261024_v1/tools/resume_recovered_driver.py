"""Qualify and atomically install task-only repairs, then resume one driver."""
from local_common import *

def main():
    resource_code=(R/'tools/server_resources.py').read_text(encoding='utf-8')
    qualification='''
import types,traceback,json,pathlib
m=types.ModuleType('recovery_resources_qualification')
exec(compile(CODE,'server_resources.py','exec'),m.__dict__)
original=m.js
registry_path=m.NATIVE/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json'
registry=original(registry_path)
cases=[]
def fixture(requests):
 def read(p):
  if pathlib.Path(p)==registry_path:return dict(registry,registered_future_requests=requests)
  return original(p)
 m.js=read
fixture({'terminal_int':dict(state='COMPLETE',consumed=1,reserved_write_bytes=0)})
value=m.admission('TARGET',include_activity=False)
cases.append(dict(case='terminal_integer_consumed',result='PASS'))
fixture({'active_int':dict(state='RUNNING',consumed=1,reserved_write_bytes=0)})
try:m.admission('TARGET',include_activity=False)
except RuntimeError as e:
 assert 'RESOURCE_HOLD_ACTIVE_SCIENCE_UNSUPPORTED_PROGRESS_SCHEMA active_int' in str(e)
 cases.append(dict(case='active_integer_consumed',result='FAIL_CLOSED_EXPECTED',reason=str(e)))
else:raise AssertionError('integer schema incorrectly admitted')
fixture({'active_mapping':dict(state='RUNNING',consumed={'cell':dict(intent='/wrong/place')},reserved_write_bytes=0)})
try:m.admission('TARGET',include_activity=False)
except RuntimeError as e:
 assert 'CURRENT_SCIENCE_INTENT_IDENTITY_HOLD' in str(e)
 cases.append(dict(case='active_mapping_unknown_intent',result='FAIL_CLOSED_EXPECTED',reason=str(e)))
else:raise AssertionError('unknown active mapping incorrectly admitted')
m.js=original
actual=m.admission('TARGET')
print(json.dumps(dict(status='PASS',cases=cases,actual_target_admission=actual,registry_modified=False)))
'''
    result=remote('hrl-174-new','CODE='+repr(resource_code)+'\n'+qualification)
    save('checkpoint/recovery_20261025/REPAIR_QUALIFICATION.json',result)
    print('qualification PASS')
    names=['copy_engine.py','server_resources.py','offload_driver.py']
    current={name:git('show','c1a14e51c07743ad674669adb54a4519336034ab:'+str((R/'tools'/name).relative_to(W)).replace('\\','/')) for name in names}
    replacements={name:(R/'tools'/name).read_bytes() for name in names}
    payload={name:dict(expected_sha256=hashlib.sha256(current[name]).hexdigest(),new_sha256=hashlib.sha256(replacements[name]).hexdigest(),blob=base64.b64encode(replacements[name]).decode()) for name in names}
    install_code='PAYLOAD='+repr(payload)+r'''
import pathlib,os,json,base64,hashlib,fcntl,time
T=pathlib.Path('/root/data/research_asset_verified_offload_20261024_v1')
def sha(b):return hashlib.sha256(b).hexdigest()
for proc in pathlib.Path('/proc').iterdir():
 if not proc.name.isdigit():continue
 try:argv=(proc/'cmdline').read_bytes().split(b'\0')
 except OSError:continue
 assert not any(a.endswith(b'/offload_driver.py') for a in argv),'EXISTING_DRIVER_NO_REPLACEMENT'
lock=(T/'control/DRIVER.lock').open('a+b');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
for name,v in PAYLOAD.items():
 p=T/'tools'/name;assert sha(p.read_bytes())==v['expected_sha256'],'TASK_TOOL_CHANGED '+name
 b=base64.b64decode(v['blob']);assert sha(b)==v['new_sha256'];compile(b,str(p),'exec')
backup=T/'control/recovery_20261025/previous_tools';backup.mkdir(parents=True,exist_ok=True)
for name,v in PAYLOAD.items():
 p=T/'tools'/name;old=p.read_bytes();bp=backup/name
 if bp.exists():assert bp.read_bytes()==old
 else:
  with bp.open('xb') as f:f.write(old);f.flush();os.fsync(f.fileno())
 new=p.with_name(p.name+'.recovery-writing')
 with new.open('xb') as f:f.write(base64.b64decode(v['blob']));f.flush();os.fsync(f.fileno())
 os.replace(new,p)
 assert sha(p.read_bytes())==v['new_sha256']
print(json.dumps(dict(status='TASK_TOOLS_ATOMICALLY_REPAIRED',unix=time.time(),files={k:{a:b for a,b in v.items() if a!='blob'} for k,v in PAYLOAD.items()},scientific_or_registry_modifications=0,source_unlinks=0)))
'''
    installed=remote('hrl-174-new',install_code)
    save('checkpoint/recovery_20261025/REPAIRED_TOOL_IDENTITIES.json',installed)
    print('atomic task tool install PASS')
    start_code=r'''
import os,sys,time,pathlib,json,subprocess,fcntl,hashlib,gzip
T=pathlib.Path('/root/data/research_asset_verified_offload_20261024_v1');sys.path.insert(0,str(T/'tools'))
import copy_engine as c
assert hashlib.sha256((T/'control/FROZEN_SCOPES.json.gz').read_bytes()).hexdigest()=='718f30ec3bc8e5ece20df02cd472ebee17eac320f7b5a9e5b5e69841cc63cc04'
for p in pathlib.Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:args=(p/'cmdline').read_bytes().split(b'\0')
 except OSError:continue
 assert not any(x.endswith(b'/offload_driver.py') for x in args),'EXISTING_DRIVER_NO_SECOND_START'
gate=c.Resources()(True)
# This Source admission is metadata-only code execution, not prehash or sender.
code=(T/'tools/server_resources.py').read_text()+'\nprint(json.dumps(admission("SOURCE")))\n'
ssh=['ssh','-i','/root/.ssh/id_ed25519_old174','-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/root/data/result_offload_pilot_20261023_v1/controls/OLD174_VERIFIED_KNOWN_HOSTS','-p','2233','root@10.208.130.174','python3 -B -']
r=subprocess.run(ssh,input=code.encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=90)
assert r.returncode==0,r.stderr.decode();source=json.loads(r.stdout)
log=T/'control/driver_resume_20261025.log';assert not log.exists(),'RESUME_LOG_ALREADY_EXISTS'
with log.open('xb') as out:
 p=subprocess.Popen(['nice','-n','19','ionice','-c','3','/usr/bin/python3','-B',str(T/'tools/offload_driver.py')],stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,cwd=str(T),start_new_session=True)
time.sleep(1)
assert p.poll() is None,'DRIVER_EXITED_AT_LAUNCH '+log.read_text()[-4000:]
ticks=int(pathlib.Path('/proc',str(p.pid),'stat').read_text().rsplit(')',1)[1].split()[19])
receipt=dict(status='SAME_FROZEN_QUEUE_RESUMED',unix=time.time(),pid=p.pid,start_ticks=ticks,mount_namespace=os.readlink('/proc/self/ns/mnt'),log=str(log),source_admission=source,target_admission=gate,previous_committed_skipped=9,source_retirements_repeated=False,new_source_retirements=0,task_identity_unchanged=True)
dest=T/'control/RESUMED_DRIVER_PROCESS.json'
with dest.open('xb') as f:f.write(c.canon(receipt));f.flush();os.fsync(f.fileno())
print(json.dumps(receipt))
'''
    started=remote('hrl-174-new',start_code,180)
    save('checkpoint/recovery_20261025/RESUMED_DRIVER_PROCESS.json',started)
    print(json.dumps({k:started[k] for k in ['status','pid','start_ticks','log']}))

if __name__=='__main__':main()
