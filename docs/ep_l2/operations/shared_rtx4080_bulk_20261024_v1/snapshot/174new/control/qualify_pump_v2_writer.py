#!/usr/bin/env python3
import pathlib,hashlib,json,time,os
R=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1');C=R/'control';N=R/'nas_rtx4080'
ident='pump_v2_'+str(int(time.time()));root=N/'quarantine'/ident;root.mkdir();payload=hashlib.shake_256(b'rtx4080-pump-v2-qualification').digest(8*1024**2);expected=hashlib.sha256(payload).hexdigest();rows=[]
# A real closed interrupted prefix remains uncommitted, and cannot pass full identity.
partial=root/'interrupted.bin'
pid=os.fork()
if pid==0:
 with partial.open('xb') as f:f.write(payload[:1048576]);f.flush();os.fsync(f.fileno())
 os._exit(99)
_,status=os.waitpid(pid,0);assert os.WEXITSTATUS(status)==99
assert hashlib.sha256(partial.read_bytes()).hexdigest()!=expected and partial.stat().st_size!=len(payload)
for rate in [4,8]:
 (C/'SSHFS_RATE_POLICY_V2.json').write_text(json.dumps({'requested_mib_s':rate,'epoch':ident+'_'+str(rate),'changed_unix':time.time()}))
 time.sleep(11);p=root/('full_%dM.bin'%rate);start=time.monotonic()
 with p.open('xb') as f:
  for off in range(0,len(payload),65536):f.write(payload[off:off+65536])
  f.flush();os.fsync(f.fileno())
 write=time.monotonic()-start;start=time.monotonic();actual=hashlib.sha256(p.read_bytes()).hexdigest();read=time.monotonic()-start;assert actual==expected
 rows.append({'requested_mib_s':rate,'write_fsync_seconds':write,'reopen_sha_seconds':read,'observed_write_MiB_s':8/write,'sha256':actual,'bytes':len(payload),'path':str(p.relative_to(N)),'pump_state':json.loads((C/'SSHFS_RATE_STATE_V2.json').read_text())})
result={'schema':'PUMP_V2_AB_SOURCE_QUALIFICATION','kind':'TRANSPORT_ONLY_NOT_WORKLOAD','identity':ident,'pump_sha256':hashlib.sha256((C/'ssh_rate_bridge_v2.py').read_bytes()).hexdigest(),'interrupted_exit':99,'interrupted_prefix_rejected':True,'no_partial_COMMIT':True,'rows':rows,'source_keep':True}
(C/'PUMP_V2_AB_SOURCE_QUALIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
