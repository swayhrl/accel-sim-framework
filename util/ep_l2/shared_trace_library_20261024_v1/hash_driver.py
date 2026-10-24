from pathlib import Path
import sys,subprocess,shlex,json,time,os,fcntl
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');host=sys.argv[1]
lease=(R/'control'/f'{host}_HASH_DRIVER.lock').open('a');fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
sys.path.insert(0,str(R/'tools'));import library_copy as trace_copy
g=trace_copy.Resources();g(True)
files=json.loads((R/'control'/f'{host}_FROZEN_METADATA.json').read_text())
out=R/'control'/f'{host}_FILE_SHA.jsonl';done={}
if out.exists():
 for l in out.read_text().splitlines():
  d=json.loads(l);done[d['key']]=d
pending=[];seen={}
for r in files['files']:
 if r.get('sha256'):
  done[r['key']]={'key':r['key'],'path':r['path'],'identity':r['identity'],'sha256':r['sha256'],'bytes':r['identity']['size'],'carried_current_commandlist_sha':True};continue
 if r['key'] not in done:pending.append(r)
req={'host':host,'hostname':files['hostname'],'files':pending}
if (R/'control/USER_BULK_4080_AND_IO_AUTHORIZATION_20261024.json').exists():req['parallel_readonly_hash_authorized']=True
if host=='174':
 sys.path.insert(0,'/root/data/ep_l2_dtc_l1_management_20261023_v1/tools');import manage
 cmd=manage.SSH+['python3 -B -c '+shlex.quote((R/'tools/hash_worker.py').read_text())]
else:cmd=['python3','-B',str(R/'tools/hash_worker.py')]
p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
p.stdin.write(json.dumps(req));p.stdin.close();completed=len(done)
try:
 with out.open('a') as log:
  for line in p.stdout:
   d=json.loads(line);g()
   if d['event']=='MISSING_SOURCE':
    with (R/'control'/f'{host}_MISSING_SOURCE.jsonl').open('a') as missing:missing.write(line)
   if d['event']=='FILE_SHA':log.write(line);log.flush();completed+=1
   progress={'host':host,'event':d['event'],'completed_files':completed,'pending_session_files':len(pending),'last':d,'observed_unix':time.time()}
   (R/'control'/f'{host}_HASH_PROGRESS.json').write_text(json.dumps(progress)+'\n')
 rc=p.wait();err=p.stderr.read()
finally:
 if p.poll() is None:
  p.terminate()
  try:p.wait(timeout=15)
  except subprocess.TimeoutExpired:p.kill();p.wait()
if rc:raise RuntimeError((rc,err))
# Rebuild complete map including current commandlist hashes and resumed rows.
for line in out.read_text().splitlines():
 d=json.loads(line);done[d['key']]=d
unresolved=[r for r in files['files'] if r['key'] not in done]
if unresolved:
 (R/'control'/f'{host}_HASH_INCOMPLETE.json').write_text(json.dumps({'status':'SOURCE_RECOVERY_REQUIRED','completed_keys':len(done),'unresolved':unresolved,'no_hash_claimed_for_missing_source':True},indent=2)+'\n')
 raise RuntimeError('RESOURCE_HOLD_SOURCE_RECOVERY_REQUIRED: '+str(len(unresolved)))
(R/'control'/f'{host}_HASH_COMPLETE.json').write_text(json.dumps({'status':'PASS_FULL_SOURCE_SHA','files':done,'source_keep':True,'source_writes':0},indent=2)+'\n')
print(json.dumps({'status':'HASH_COMPLETE','host':host,'files':len(done)}),flush=True)
