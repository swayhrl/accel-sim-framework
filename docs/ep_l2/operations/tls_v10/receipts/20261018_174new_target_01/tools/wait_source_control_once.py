"""Finite foreground metadata wait: Git AND exact independent bridge publication."""
import sys,time,json,pathlib,subprocess,hashlib
import tls_target as t
wid,suffix,cap=sys.argv[1:];cap=int(cap);assert 0<cap<=900 and suffix in ['SOURCE_KEEP_ACK.json','SOURCE_READY_COPY16.json']
G=['git','--git-dir=D:/repo/storage-ops-174new-164-exec-v1/.git/source-evidence.git'];branch='hrl/ops-174-tls-v10-source-exec-v1'
name=wid+'_'+suffix;path='docs/ep_l2/operations/tls_v10_174_to_164_source/'+name
end=time.monotonic()+cap;last=None;errors=0;candidate=None

def bridge_ready(item):
 code="import pathlib,json,hashlib,os,stat\nB=pathlib.Path(%r);name=%r;pin=%r;commit=%r;wid=%r;suffix=%r\n"%(t.BRIDGE,name,item['raw_sha256'],item['commit'],wid,suffix)
 code+="assert os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]' and B.stat().st_dev==2431\np=B/name;ready=False\n"
 code+="if p.exists():\n assert not p.is_symlink() and stat.S_ISREG(p.lstat().st_mode) and p.stat().st_size<=8*1024**2\n assert hashlib.sha256(p.read_bytes()).hexdigest()==pin,'SOURCE_GIT_BRIDGE_CONTROL_SHA_MISMATCH'\n ready=True\n"
 code+=" if suffix=='SOURCE_KEEP_ACK.json':\n  pub=B/(wid+'_SOURCE_KEEP_ACK_PUBLICATION.json')\n  if not pub.exists():ready=False\n  else:\n   info=json.loads(pub.read_bytes());assert info['source_git_commit']==commit and info['source_keep_ack_sha256']==pin,'SOURCE_ACK_PUBLICATION_BINDING_MISMATCH'\n"
 code+="print(json.dumps({'ready':ready}))\n"
 r=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=15','hrl-174-new','timeout 20s python3 -B -'],input=code.encode(),capture_output=True,timeout=30)
 if r.returncode:raise RuntimeError(r.stderr.decode(errors='replace')[-1200:])
 return json.loads(r.stdout)['ready']

while True:
 try:
  ref=subprocess.check_output(G+['ls-remote','origin','refs/heads/'+branch],timeout=35).decode().split()[0]
  if ref!=last:
   f=subprocess.run(G+['fetch','origin',branch],capture_output=True,timeout=70)
   if f.returncode:raise RuntimeError(f.stderr.decode(errors='replace')[-1000:])
   last=ref;obj=subprocess.run(G+['show',ref+':'+path],capture_output=True,timeout=60)
   if obj.returncode==0:
    commit=subprocess.check_output(G+['log','-1','--format=%H',ref,'--',path],timeout=30).decode().strip()
    prefix='SOURCE_'+commit[:7]+'_';(t.BASE/(prefix+name)).write_bytes(obj.stdout)
    candidate=dict(status='SOURCE_CONTROL_FOUND',utc=t.now(),window_id=wid,suffix=suffix,commit=commit,latest_source_head=ref,raw_sha256=hashlib.sha256(obj.stdout).hexdigest(),cached_prefix=prefix)
   elif b'does not exist' not in obj.stderr:raise RuntimeError(obj.stderr.decode(errors='replace')[-1000:])
  if candidate and bridge_ready(candidate):
   candidate.update(utc=t.now(),exact_source_Git_bridge_controls_and_publication_match=True)
   (t.META/'last_source_control_wait.json').write_bytes((json.dumps(candidate,indent=2)+chr(10)).encode());print(json.dumps(candidate),flush=True);break
  errors=0
 except Exception as e:
  errors+=1;print('BOUNDED_CONTROL_NETWORK_RETRY',errors,str(e),flush=True)
  if errors>=3:raise
 if time.monotonic()>=end:
  record=dict(status='BOUNDED_SOURCE_CONTROL_WAIT_EXPIRED',utc=t.now(),window_id=wid,suffix=suffix,last_source_head=last,cap_seconds=cap,Git_candidate_waiting_for_bridge=bool(candidate))
  (t.META/'last_source_control_wait.json').write_bytes((json.dumps(record,indent=2)+chr(10)).encode());print(json.dumps(record),flush=True);break
 print('WAIT_SOURCE_GIT_AND_BRIDGE',wid,suffix,'head',last[:12] if last else None,flush=True)
 time.sleep(min(15,max(0,end-time.monotonic())))
