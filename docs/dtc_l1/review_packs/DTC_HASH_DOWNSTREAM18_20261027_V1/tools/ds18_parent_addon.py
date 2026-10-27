"""Additive18-thread dispatcher in the existing qualified sole parent's process.

No old controller code/globals/worker maps are patched. Strong references retain
its existing lock files if its original main returns before this finite addon.
"""
import pathlib,json,hashlib,importlib.util,threading,os,sys,datetime,copy
P=pathlib.Path;R=P('/root/data/dtc_hash_downstream18_20261027_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');_KEEPERS=[]
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def exclusive(p,x):
 with P(p).open('x')as h:json.dump(x,h,indent=2);h.write('\n');h.flush();os.fsync(h.fileno())
def activate_then_schedule():
 try:
  plan=read(R/'control/EXECUTION_PLAN.json');qual=read(R/'control/CPU_QUALIFICATION.json');pub=read(R/'control/PUBLICATION_READBACK.json');assert qual['status']=='PASS'and pub['verified']and qual['plan_sha256']==sha(R/'control/EXECUTION_PLAN.json')and pub['freeze_manifest_sha256']==sha(R/'control/FREEZE_MANIFEST.json')and pub['cpu_qualification_sha256']==sha(R/'control/CPU_QUALIFICATION.json')
  e=load('ds18_parent_native',R/'tools/ds18_native.py');candidate=read(R/'control/REGISTRY_REQUEST_CANDIDATE.json');auth=read(R/'control/SCIENCE_AUTHORIZATION.json');assert candidate['budget']==candidate['remaining']==18 and not candidate['consumed']and auth['explicit_user_approval']and auth['approval_request_sha256']==sha(R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')
  for x in plan['source_pins']:assert sha(x['path'])==x['sha256']
  leasepath=T/'control/BATCH_LEASE.json';lease=read(leasepath);assert lease['pid']==os.getpid()==plan['parent_pid']and lease['start_ticks']==plan['parent_start_ticks']and lease['controller_sha256']==plan['parent_controller_sha256'];assert not(R/'control/PARENT_ADDON_ACK.json').exists()
  entry=N/'bin/native';before=entry.read_bytes();anchor=b'#!/bin/sh\nset -eu\n';assert before.startswith(anchor)and b'E2-DTCHASH18-'not in before
  block=('''# Exact finite DTC HASH18 route; all preexisting native routes retained byte-for-byte.
if [ "$#" -ge 3 ]; then
 case "$1:$3" in
  experiment:E2-DTCHASH18-*|result:E2-DTCHASH18-*)
   exec /usr/bin/python3 -B /root/data/dtc_hash_downstream18_20261027_v1/tools/ds18_frontend.py "$@"
   ;;
 esac
fi
''').encode();after=anchor+block+before[len(anchor):];assert after.replace(block,b'',1)==before;tmp=entry.with_name('.native.DS18writing');tmp.write_bytes(after);tmp.chmod(entry.stat().st_mode&0o777);assert entry.read_bytes()==before;tmp.replace(entry);exclusive(R/'control/NATIVE_ENTRY_TRANSITION.json',dict(prior_text=before.decode(),prior_sha256=hashlib.sha256(before).hexdigest(),new_sha256=sha(entry),block=block.decode(),all_prior_routes_byte_preserved=True))
  def register(reg):
   assert e.REQ not in reg['registered_future_requests'];reg['registered_future_requests'][e.REQ]=copy.deepcopy(candidate)
  e.update_authority(register);exclusive(R/'control/LEASE_BEFORE_ADDON.json',lease);new=dict(lease,additional_requests=[*lease.get('additional_requests',[]),e.REQ]);assert read(leasepath)==lease;tmp=leasepath.with_name('.BATCH_LEASE.DS18writing');tmp.write_text(json.dumps(new,indent=2)+'\n');tmp.replace(leasepath)
  exclusive(R/'control/PARENT_ADDON_ACK.json',dict(status='REGISTERED_ADDON_READY_NO_START',parent_pid=os.getpid(),parent_start_ticks=plan['parent_start_ticks'],parent_controller_sha256=plan['parent_controller_sha256'],addon_sha256=sha(__file__),plan_sha256=sha(R/'control/EXECUTION_PLAN.json'),publication_commit=pub['commit'],original_controller_source_unchanged=True,old_models_signaled=0,additional_finite_budget=18,dispatch_order=plan['dispatch_order'],lock_file_objects_retained=True))
  e.registered();e.assert_parent_lease();load('ds18_finite_workers',R/'tools/ds18_ops.py').run_scheduler()
 except BaseException as x:exclusive(R/'analysis/ADDON_ERROR_PRESERVE_ALL_ARTIFACTS.json',dict(error=repr(x),model_retries=0,old_source_or_spent_ledgers_changed=False));raise
def install_parent():
 plan=read(R/'control/EXECUTION_PLAN.json');assert os.getpid()==plan['parent_pid']and int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==plan['parent_start_ticks'];frame=sys._getframe()
 while frame is not None:
  if frame.f_code.co_name=='main'and P(frame.f_code.co_filename)==P(plan['parent_controller_path']):break
  frame=frame.f_back
 assert frame is not None and not hasattr(sys.modules['__main__'],'DTC_HASH18_ADDON_THREAD')
 for name in ['held','owner']:
  v=frame.f_locals[name];assert not v.closed;_KEEPERS.append(v)
 assert _KEEPERS[0].fileno()==read(T/'control/BATCH_LEASE.json')['fd']and'FLOCK'in(P('/proc/self/fdinfo')/str(_KEEPERS[0].fileno())).read_text()
 worker=threading.Thread(target=activate_then_schedule,name='DTC_HASH18_QUALIFIED_FINITE_ADDON',daemon=False);sys.modules['__main__'].DTC_HASH18_ADDON_THREAD=worker;worker.start()
