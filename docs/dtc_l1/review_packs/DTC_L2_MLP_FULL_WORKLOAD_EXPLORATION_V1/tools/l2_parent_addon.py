"""Add a dispatcher to the existing lease owner; retain its original lock handles."""
import pathlib,json,hashlib,importlib.util,threading,os,sys,copy,datetime
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');_KEEPERS=[]
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def exclusive(p,obj):
 with P(p).open('x')as h:json.dump(obj,h,indent=2);h.write('\n');h.flush();os.fsync(h.fileno())
def activate():
 try:
  plan=read(R/'control/EXECUTION_PLAN.json');qual=read(R/'control/CPU_QUALIFICATION.json');assert qual['status']=='PASS'and qual['freeze_manifest_sha256']==sha(R/'control/FREEZE_MANIFEST.json')
  for p in plan['source_pins']:assert sha(p['path'])==p['sha256'],p['path']
  e=load('l2_parent_engine',R/'tools/l2_native.py');candidate=read(R/'control/REGISTRY_REQUEST_CANDIDATE.json');auth=read(R/'control/SCIENCE_AUTHORIZATION.json');assert candidate['budget']==candidate['remaining']==344 and not candidate['consumed']and auth['explicit_user_approval']and auth['approval_request_sha256']==sha(R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')
  leasepath=T/'control/BATCH_LEASE.json';lease=read(leasepath);assert os.getpid()==plan['parent_pid']==lease['pid']and lease['start_ticks']==plan['parent_start_ticks'];assert not(R/'control/PARENT_ADDON_ACK.json').exists()
  entry=N/'bin/native';before=entry.read_bytes();anchor=b'#!/bin/sh\nset -eu\n';assert before.startswith(anchor)and b'E2-DTCL2MLP-'not in before
  block=('''# Exact authorized DTC L2-MLP route; all previous routes retained byte-for-byte.
if [ "$#" -ge 3 ]; then
 case "$1:$3" in
  experiment:E2-DTCL2MLP-*|result:E2-DTCL2MLP-*)
   exec /usr/bin/python3 -B /root/data/dtc_l2_mlp_exploration_20261027_v1/tools/l2_frontend.py "$@"
   ;;
 esac
fi
''').encode();after=anchor+block+before[len(anchor):];assert after.replace(block,b'',1)==before;tmp=entry.with_name('.native.L2MLPwriting');tmp.write_bytes(after);tmp.chmod(entry.stat().st_mode&0o777);assert entry.read_bytes()==before;tmp.replace(entry)
  exclusive(R/'control/NATIVE_ENTRY_TRANSITION.json',dict(prior_sha256=hashlib.sha256(before).hexdigest(),new_sha256=sha(entry),prior_text=before.decode(),new_block=block.decode(),all_prior_routes_byte_preserved=True))
  def register(reg):
   assert e.REQ not in reg['registered_future_requests'];reg['registered_future_requests'][e.REQ]=copy.deepcopy(candidate)
  e.update_authority(register);exclusive(R/'control/LEASE_BEFORE_ADDON.json',lease);new=dict(lease,additional_requests=[*lease.get('additional_requests',[]),e.REQ]);assert read(leasepath)==lease;tmp=leasepath.with_name('.BATCH_LEASE.L2MLPwriting');tmp.write_text(json.dumps(new,indent=2)+'\n');tmp.replace(leasepath)
  exclusive(R/'control/PARENT_ADDON_ACK.json',dict(status='REGISTERED_AUTHORIZED_L2_MLP_READY',parent_pid=os.getpid(),parent_start_ticks=lease['start_ticks'],parent_controller_sha256=lease['controller_sha256'],addon_sha256=sha(__file__),plan_sha256=sha(R/'control/EXECUTION_PLAN.json'),initial_exact_finite_credits=344,no_total_scientific_start_cap=True,old_models_signaled=0,old_controller_source_changed=False,original_lock_handles_retained=True))
  e.registered();e.assert_parent_lease();load('l2_owner_scheduler',R/'tools/l2_ops.py').run_scheduler()
 except BaseException as error:exclusive(R/'analysis/ADDON_ERROR_PRESERVE_ALL_ARTIFACTS.json',dict(error=repr(error),old_scientific_requests_changed=False,new_model_retries=0));raise
def install_parent():
 plan=read(R/'control/EXECUTION_PLAN.json');assert os.getpid()==plan['parent_pid']and int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==plan['parent_start_ticks'];frame=sys._getframe()
 while frame is not None:
  if frame.f_code.co_name=='main'and P(frame.f_code.co_filename)==P(plan['parent_controller_path']):break
  frame=frame.f_back
 assert frame is not None and not hasattr(sys.modules['__main__'],'DTC_L2_MLP_ADDON_THREAD')
 for name in ['held','owner']:
  value=frame.f_locals[name];assert not value.closed;_KEEPERS.append(value)
 lease=read(T/'control/BATCH_LEASE.json');assert _KEEPERS[0].fileno()==lease['fd']and'FLOCK'in(P('/proc/self/fdinfo')/str(lease['fd'])).read_text()
 worker=threading.Thread(target=activate,name='DTC_L2_MLP_ONE_OWNER',daemon=False);sys.modules['__main__'].DTC_L2_MLP_ADDON_THREAD=worker;worker.start()
