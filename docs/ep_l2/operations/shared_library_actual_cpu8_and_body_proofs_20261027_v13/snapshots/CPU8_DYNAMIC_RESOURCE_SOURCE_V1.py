"""Fresh mutable registry epochs; fixed dependencies pinned before any import."""
import pathlib,json,hashlib,os,time,importlib.util,shutil,re,subprocess,socket
import boundary_helpers_v1 as H
from owned_runtime_v1 import need,sha,write
D=pathlib.Path(__file__).resolve().parent
R=D.parent/'sm70_r8_owned_descendant_closure_prepare_20261027_v1/production_keeper_v5/tools/versions/100bbf41b45927ec490c63c4e01ffaf64f522321b202e129303bab8cfac6a228'
FIXED={'resources.py':'ce77a7748e8beb0ff4eb71571e4a24858e0e2c905d1bf15a0c642d07b18d84bd','PROFILE.json':'a3d8362d8c06e563cb74d55f92762d2f58d18943f0061fa5a87256335df9f8ce','legacy_foreign_binding.json':'e069be66ddd0e7d9e7000c2edc93d0dcc12436e830c6f685a08e8c0960ce2c34'}
def load(p,name):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def no_secrets(value):
 if isinstance(value,dict):
  for key,item in value.items():
   need(not(re.search(r"token|nonce|secret|challenge",str(key),re.I)and item not in (None,"",[],{},False)),"secret-like mutable registry field: do not freeze raw")
   no_secrets(item)
 elif isinstance(value,list):
  for item in value:no_secrets(item)
def fresh(run):
 for n,h in FIXED.items():need(sha(R/n)==h,'fixed R5 dependency drift before import')
 O=load(D/'current_foreign_observer_v1.py','fixed_current_foreign')
 for attempt in range(3):
  try:
   v=O.observe();r=v['registry_ref'];H.readref(r);p=pathlib.Path(r['path']);raw=p.read_bytes()
   need(len(raw)==r['bytes']and len(raw)<=8*2**20 and hashlib.sha256(raw).hexdigest()==r['sha256'],'mutable epoch changed, retry')
   no_secrets(json.loads(raw))
   target=run/('FOREIGN_REGISTRY_'+r['sha256']+'.raw.json')
   if not target.exists():
    with target.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
   need(sha(target)==r['sha256'],'frozen raw epoch identity')
   v['frozen_registry_ref']=H.ref(target);return v
  except (AssertionError,FileNotFoundError,ProcessLookupError,RuntimeError):
   if attempt==2:raise
 raise RuntimeError('No consistent current foreign epoch')
def check(a):
 x=H.readref(a['resource_ref']);need(x['schema']=='ROOT_COMPLETION_CURRENT_RESOURCE_POLICY_V1'and x['scope_id']==a['scope_id']and x['foreign_future_ceilings_committed_by_this_scope']is False,'Root explicit current resource policy')
 q=json.loads((R/'PROFILE.json').read_bytes());need(socket.gethostname()==q['expected_host']and os.readlink('/proc/self/ns/mnt')==q['expected_mount_namespace']and pathlib.Path('/root/data').stat().st_dev==q['native_device'],'actual Native host/mount/device')
 fs=json.loads(subprocess.check_output(['/usr/bin/findmnt','-J','-T',str(D)],text=True,timeout=3))['filesystems'][0];need(fs['source']==q['nas_endpoint']and fs['fstype']=='fuse.sshfs','actual true164 NAS output mount')
 profile=a['selected_profile'];workers={'CPU2':2,'CPU4':4,'CPU8':8}[profile];need(type(x['own_RAM_bytes'])is int and x['own_RAM_bytes']>=(4+3*workers)*2**30,'outer2+runner2+workers3GiB AS budget')
 run=D/'runs'/a['scope_id'];need(run.is_dir(),'own NAS runtime only')
 v=fresh(run);need(v['unknown_active_cohort_count']==0 and v['registered_history_or_budgets_modified']is False,'unknown foreign profile HOLD')
 r=a['memory_module_ref'];need(sha(pathlib.Path(r['path']))==r['sha256']=='ccde5eb672a38448b834b8339cbbaf1ceeab1b9e8d4ac101253965eab7dd1238','fixed cgroup dependency')
 m=load(pathlib.Path(r['path']),'fixed_cgroup_runtime');snap=m.collect();verdict=m.evaluate(snap,v['additional_active_RAM_commitments_bytes'],x['own_RAM_bytes'],'native174')
 need(snap['host']['namespaces']['cgroup']==x['expected_cgroup_namespace']and snap['MemAvailable_bytes']>=64*2**30 and verdict['status']=='PASS','actual cgroup/host current commitments physical gate')
 need(shutil.disk_usage('/root/data').free>=5*2**30+64*2**20,'Native actual floor+owncontrol; payload0')
 need(shutil.disk_usage(run).free>=20*2**30+a['base_spec']['own_output_limit_bytes'],'NAS actual floor+own pending bound')
 result=dict(schema='COMPLETION_FRESH_CURRENT_RESOURCE_GATE_V1',unix=time.time(),foreign=v,kernel_snapshot=snap,verdict=verdict,foreign_future_ceilings_committed_by_this_scope=False,Native_payload_bytes=0,Native_control_cap_bytes=64*2**20)
 write(run/('RESOURCE_'+str(time.time_ns())+'.json'),result);return result
