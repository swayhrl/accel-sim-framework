"""Read-only proof of current resource waits; never edits reservations."""
import sys
sys.dont_write_bytecode=True
from local_common import *

CODE=r'''
import pathlib,json,os,time,hashlib,sys
P=pathlib.Path;T=P('/root/data/research_asset_verified_offload_20261024_v1');sys.path.insert(0,str(T/'tools'));import server_resources as rr
p=P('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json');raw=p.read_bytes();r=json.loads(raw);requests=[]
for name,v in r.get('registered_future_requests',{}).items():
 if not v.get('reserved_write_bytes') and v.get('state')!='RUNNING':continue
 consumed=v.get('consumed');cells=list(consumed.values()) if isinstance(consumed,dict) else [];live=[];prefork=0
 for item in cells:
  if not isinstance(item,dict) or item.get('execution_receipt'):continue
  ip=item.get('intent')
  if not ip or not P(ip).exists():prefork+=1;continue
  intent=json.loads(P(ip).read_bytes());output=intent.get('output');proof=P(output)/'NATIVE_SIMULATOR_PID_AND_MAPS.json' if output else None
  if proof is None or not proof.exists():prefork+=1;continue
  q=json.loads(proof.read_bytes());proc=P('/proc',str(q['pid']))
  try:
   ticks=int((proc/'stat').read_text().rsplit(')',1)[1].split()[19])
   if ticks==q['start_ticks']:live.append(dict(pid=q['pid'],start_ticks=ticks))
  except OSError:pass
 requests.append(dict(request_id=name,state=v.get('state'),owner=v.get('owner'),reserved_write_bytes=v.get('reserved_write_bytes',0),budget=v.get('budget'),remaining=v.get('remaining'),consumed_records=len(cells),terminal_receipts=sum(isinstance(z,dict) and bool(z.get('execution_receipt')) for z in cells),verified_live_science=live,prefork_or_unresolved_intents=prefork))
f=os.statvfs('/root/data');free=f.f_bavail*f.f_frsize;reserved=sum(v.get('reserved_write_bytes',0) for v in r.get('registered_future_requests',{}).values());required=7*1024**3+reserved+1024**3+64*1024**2
try:gate=dict(status='PASS',resources=rr.admission('TARGET',include_activity=False,metadata_only=True))
except Exception as e:gate=dict(status='HOLD',reason=str(e))
sup=json.loads((T/'control/CONTINUATION_SUPERVISOR.json').read_bytes());proc=P('/proc',str(sup['pid']));live_sup=False
try:live_sup=int((proc/'stat').read_text().rsplit(')',1)[1].split()[19])==sup['start_ticks'] and str(T/'tools/continuation_supervisor.py').encode() in (proc/'cmdline').read_bytes().split(b'\0')
except OSError:pass
print(json.dumps(dict(schema='LANE_T2_RESOURCE_WAIT_PROOF_V1',unix=time.time(),SSD_available_bytes=free,SSD_required_bytes=required,SSD_deficit_bytes=max(0,required-free),native_registered_reserved_bytes=reserved,request_summaries=requests,registry_sha256=hashlib.sha256(raw).hexdigest(),metadata_only_gate=gate,IO_pressure=rr.pressure(),supervisor=sup,supervisor_identity_verified_live=live_sup,held_global_locks=rr.old_lock_holders(),state=json.loads((T/'control/STATE.json').read_bytes()),resource_contract_modified=rr.active_science_io_authorization() is not None,user_authorized_IO_policy=rr.active_science_io_authorization(),science_processes_stopped=False,Source_files_unlinked=0)))
'''

if __name__=='__main__':
    x=remote('hrl-174-new',CODE,90);save('t2/CURRENT_RESOURCE_WAIT_PROOF.json',x)
    print(json.dumps(dict(free=x['SSD_available_bytes'],required=x['SSD_required_bytes'],deficit=x['SSD_deficit_bytes'],gate=x['metadata_only_gate']['status'],gate_reason=x['metadata_only_gate'].get('reason'),supervisor_live=x['supervisor_identity_verified_live'],rechecks=x['supervisor']['resource_rechecks'],restarts=x['supervisor']['driver_restarts'],requests=x['request_summaries'])))
