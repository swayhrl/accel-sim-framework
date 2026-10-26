#!/usr/bin/env python3
"""Explicit E2-only input metadata revalidation adapter; frozen E1 code/proofs unchanged."""
import sys
sys.dont_write_bytecode=True
import os,json,pathlib,hashlib,time,subprocess
import experiment_runtime as v
import native_dispatch
P=pathlib.Path
def fresh_case_assets():
 proof=v.read(v.B/'control/FRESH_INPUT_ASSET_BINDING.json')
 v.need(proof['status']=='FRESH_GENUINE164_INPUT_CLOSED_REOPEN_FULL_SHA_PASS','case input proof absent')
 fs=json.loads(subprocess.check_output(['findmnt','-J','-T',proof['native_mirror_mount_path']],text=True))['filesystems'][0]
 v.need(fs['source']=='admin-wcx@10.208.130.164:/home/shared' and fs['fstype']=='fuse.sshfs','genuine164 changed')
 v.need(P(proof['source_root']).resolve()==P(proof['native_mirror_mount_path']).resolve(),'input alias changed')
 rows=[];start=time.monotonic()
 for expected in proof['members']:
  p=P(expected['path']);a=p.stat();identity=lambda x:[x.st_dev,x.st_ino,x.st_size,x.st_mtime_ns]
  v.need(a.st_size==expected['size'] and os.access(p,os.R_OK),'input size/readability changed')
  row=dict(expected)
  if identity(a)!=expected['identity']:
   sums=[]
   for unused in range(2):
    h=hashlib.sha256()
    with p.open('rb') as f:
     for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    sums.append(h.hexdigest())
   b=p.stat();v.need(sums==[expected['sha256']]*2 and identity(a)==identity(b),'input full SHA or metadata unstable')
   row.update(identity=identity(b),closed_reopen_full_sha256=sums[-1],revalidated_after_metadata_drift=True)
  else:row['revalidated_after_metadata_drift']=False
  rows.append(row)
 return {'EP_VECTORADD_S':dict(proof,members=rows,current_preflight_revalidation_seconds=time.monotonic()-start,new_local_payload_bytes=0)}
def main(args):
 v.need(len(args)>=3 and args[2]==v.E2,'E2-only operational adapter')
 v.bind(v.E2);v.current_assets=fresh_case_assets
 original_put=v.put
 def put(path,obj):
  if P(path).name in ['NATIVE_LAUNCH.json','NATIVE_PRELAUNCH_QUALIFICATION.json']:
   obj=dict(obj,operational_input_binding_adapter_sha256=v.sha(__file__),frozen_shared_engine_sha256=v.sha(v.ROOT/'tools/experiment_runtime.py'),input_binding_scope='E2 case-local genuine164 content revalidation;E1 immutable proof untouched')
  return original_put(path,obj)
 v.put=put
 return native_dispatch.main(args)
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:]),ensure_ascii=False,indent=2))
 except Exception as e:print(json.dumps({'status':'HOLD','reason':str(e),'automatic_retry':False}),file=sys.stderr);sys.exit(2)
