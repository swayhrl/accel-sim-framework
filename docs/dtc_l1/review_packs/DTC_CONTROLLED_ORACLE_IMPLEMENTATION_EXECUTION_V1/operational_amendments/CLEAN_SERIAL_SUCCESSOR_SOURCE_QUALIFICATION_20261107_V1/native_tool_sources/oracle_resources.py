"""Oracle-only dynamic admission; runtime sampling is local and nonblocking."""
from pathlib import Path
import hashlib,json,os,re,time,types,subprocess
P=Path;R=P(__file__).resolve().parents[1];G=1024**3;M=1024**2
REQ=json.loads((R/'control/EXECUTION_PLAN.json').read_bytes())['request']if(R/'control/EXECUTION_PLAN.json').exists()else None
AUTHORITY_COMMIT='18b1ee9d339902e555fc2e04ef51c84f77dfe1b1'
class WaitInitialRuntimeGate(RuntimeError):pass
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):
 m=types.ModuleType(n);m.__file__=str(p);exec(compile(P(p).read_bytes(),str(p),'exec'),m.__dict__);return m
def plan():return read(R/'control/EXECUTION_PLAN.json')
def pinned(ref):
 assert sha(ref['path'])==ref['sha256'],'PIN_DRIFT:'+ref['path'];return read(ref['path'])
def policy(value=None):
 p=dict(memory_utilization_fraction=.88,min_host_headroom_bytes=8*G,min_cgroup_headroom_bytes=8*G,native_safety_floor_bytes=5*G,metadata_reserve_bytes=256*M,min_free_inodes=100000)
 p.update(value or {});assert .85<=p['memory_utilization_fraction']<=.90 and p['native_safety_floor_bytes']>=5*G;return p
def verify_frozen_release(container,q=None):
 assert container.get('authority_commit',container.get('approved_contract_commit'))==AUTHORITY_COMMIT and container['request']==REQ
 assert container['archive_workers']==1,'SINGLE_RESTORE_WINDOW_REQUIRES_ONE_ARCHIVE_WORKER'
 modes=set(container['qualified_modes']);assert modes and modes<={'M_DATAREAD','L2_DATAREAD','L1_DATAREADY'}
 gate=pinned(container['gate0_release']);assert gate['status']=='PASS' and set(gate['qualified_modes'])==modes
 build=read(R/'control/BUILD_PROFILE.json');assert gate['binary_sha256']==build['binary_sha256'] and gate['core_commit']==build['core_commit']
 assert gate['source_lifecycle_independent_review']=='PASS' and gate['CPU_lifecycle_qualification']=='PASS'
 for x in container['source_pins']:assert sha(x['path'])==x['sha256']
 n=8 if container['stage']=='initial8'else 24
 assert container['stage']in['initial8','remaining24']
 assert container['expected_new_starts']==n*(1+len(modes))
 if q is not None:assert q['budget']==container['expected_new_starts']
 if n==24:
  gate2=pinned(container['gate2_release']);assert gate2['status']=='PASS' and set(gate2['released_modes'])and set(gate2['released_modes'])<=modes
  assert gate2['fixed8_matched_OFF_and_mode_strict_archive_restore_independently_reviewed']is True
 return dict(authority_commit=AUTHORITY_COMMIT,exact_candidate_count=container['expected_new_starts'],stage=container['stage'],qualified_modes=sorted(modes),Gate0_CPU_source_strict_independent_review='PASS',**({'Gate2_any_mode_fixed8_and_shared_OFF_accepted_independently_reviewed':'PASS','Gate2_released_modes':sorted(gate2['released_modes'])}if n==24 else{}))
def verify_registration_release(container,candidate):
 evidence=verify_frozen_release(container,candidate)
 assert candidate['request']==REQ and candidate['remaining']==candidate['budget']==container['expected_new_starts'] and candidate['consumed']=={}
 points=read(R/'control/MATRIX.fixed.json')['points'];assert set(candidate['admitted_specs'])=={x['cohort']for x in points} and len(points)==candidate['budget']
 assert set(container['authorized_cohorts'])==set(candidate['admitted_specs'])
 for c,d in candidate['admitted_specs'].items():assert sha(R/'control/specs'/(c+'.json'))==d
 # Explicit bounded peer/archive reservation check belongs outside EX only.
 first=read(R/'control/specs'/(points[0]['cohort']+'.json'));sample=resources(first,True)
 assert sample['physical_RAM_pass']and sample['physical_disk_pass']and sample['admission_disk_pass']and sample['admission_pressure_pass'],'INITIAL_LIVE_RESOURCE_HOLD'
 return dict(evidence,resource_sample=sample)
def admission_hold(q,spec):
 mode=spec.get('oracle_mode',spec.get('mode',spec.get('profile')))
 if mode in q.get('admission_holds',{}):return q['admission_holds'][mode]
 return None
def _qualifier_review(container,cohort,q):
 p=R/'control/actual_qualification_reviews'/(cohort+'.json')
 if not p.exists():raise WaitInitialRuntimeGate('WAIT_INDEPENDENT_ACTUAL_QUALIFIER_REVIEW:'+cohort)
 v=read(p);ref=container['actual_qualification_reviewer'];assert sha(ref['path'])==ref['sha256']
 assert v['reviewer_source_sha256']==ref['sha256'] and v['status']=='PASS','ACTUAL_QUALIFIER_INDEPENDENT_REVIEW_FAILED'
 row=q['consumed'].get(cohort);assert row is not None and v['input_uuid']==row['uuid'] and v['cohort']==cohort
 result=R/'analysis'/(cohort+'.RESULT.json');assert sha(result)==v['result_sha256']
 value=read(result);assert value['state']=='PASS_CONTROLLED_ORACLE_DH_STRICT_ARCHIVE_NATIVE_RESTORE'
 spec=read(R/'control/specs'/(cohort+'.json'));assert value['plan_id']==spec['plan_id']==v['plan_id'] and value['input_digest']==spec['input_digest']==v['input_digest']
 assert v['source_plan_sha256']==sha(R/'control/EXECUTION_PLAN.json')==q['execution_plan_sha256'] and v['effective_options_count']==271
 assert v['binary_sha256']==spec['binary_sha256'] and v['core_commit']==spec['core_commit'] and v['framework_commit']==spec['framework_commit']
 strict=R/'DTC/run/results'/row['uuid']/'L2_STRICT.json';assert sha(strict)==v['strict_sha256']
 ar=v['archive_native_review'];assert ar['SOURCE_KEEP']is True and ar['typed_source_entries']==ar['typed_native_restore_entries']>0 and ar['true164_source']=='admin-wcx@10.208.130.164:/home/shared'
 if spec['oracle_mode']!='OFF_MATCHED':assert v['actual_mechanism_exposure']>0
 return dict(path=str(p),sha256=sha(p),cohort=cohort,uuid=row['uuid'],mode=spec['oracle_mode'])
def verify_initial_runtime_gate(container,cohort,q=None):
 # MUST be usable while REGISTRY EX is held. q is required; no authority reader.
 assert q is not None,'PASSED_LOCK_SNAPSHOT_REQUIRED'
 points=read(R/'control/MATRIX.fixed.json')['points'];row=next(x for x in points if x['cohort']==cohort)
 if container['stage']=='remaining24':
  modes=container['qualified_modes']if row['mode']=='OFF_MATCHED'else[row['mode']]
  passed=[]
  for mode in modes:
   try:passed.append(verify_mode_extension_receipt(container,mode))
   except WaitInitialRuntimeGate:pass
  if not passed:raise WaitInitialRuntimeGate('WAIT_MODE_GATE2:'+row['mode'])
  return dict(state='EXTENSION_MODE_GATE2_RELEASED',mode=row['mode'],evidence=passed)
 qual=container['initial_qualifiers'];off=qual['OFF_MATCHED']
 if cohort==off:return dict(state='DECLARED_OFF_QUALIFIER_ONLY',cohort=cohort)
 baseline=_qualifier_review(container,off,q)
 mode=row['mode']
 if mode=='OFF_MATCHED':return dict(state='OFF_QUALIFIED',baseline=baseline)
 if cohort==qual[mode]:return dict(state='DECLARED_MODE_QUALIFIER_ONLY',baseline=baseline,cohort=cohort)
 return dict(state='MODE_ACTUAL_QUALIFIED',baseline=baseline,mode=_qualifier_review(container,qual[mode],q))
def verify_mode_extension_receipt(container,mode):
 path=P(container['mode_gate2_reviews'][mode])
 if not path.exists():raise WaitInitialRuntimeGate('WAIT_MODE_GATE2_REVIEW:'+mode)
 v=read(path);ref=container['actual_qualification_reviewer'];assert sha(ref['path'])==ref['sha256']
 assert v['status']=='PASS'and v['mode']==mode and v['reviewer_source_sha256']==ref['sha256']
 initial=P('/root/data/dtc_controlled_oracle_20261106_v1/initial8');ip=read(initial/'control/EXECUTION_PLAN.json');build=read(R/'control/BUILD_PROFILE.json')
 assert v['initial_request']==ip['request']and v['initial_plan_sha256']==sha(initial/'control/EXECUTION_PLAN.json')
 assert v['binary_sha256']==build['binary_sha256']and v['core_commit']==build['core_commit']and v['framework_commit']==build['framework_commit']
 assert v['input_count']==8 and v['accepted_result_count']==16 and v['all_fixed8_and_samebuild_OFF_accepted']is True and v['strict_archive_native_reviewed']is True and v['performance_selection_used']is False
 refs=v['result_refs'];assert len(refs)==16 and len({r['uuid']for r in refs})==16
 for r in refs:assert sha(initial/'analysis'/(r['cohort']+'.RESULT.json'))==r['result_sha256']
 return dict(path=str(path),sha256=sha(path),mode=mode,initial_request=v['initial_request'])
def inspect_first_closed(container,q):return _qualifier_review(container,container['initial_qualifiers']['OFF_MATCHED'],q)
def sample_system():
 h=load('oracle_local_sample',R/'tools/oracle_runtime_contract.py');s=h.local_safety_sample(R)
 cpus=sorted(os.sched_getaffinity(0));observed=[]
 for p in P('/proc').iterdir():
  if not p.name.isdigit():continue
  try:
   args=(p/'cmdline').read_bytes()
   # Read actual model affinity only. This is not request identity evidence.
   if b'accel-sim.out'in args and b'--library-path'in args and b'-trace'in args:
    status=(p/'status').read_text();rss=re.search(r'^VmRSS:\s+(\d+)\s+kB',status,re.M)
    observed.append(dict(pid=int(p.name),cpus=sorted(os.sched_getaffinity(int(p.name))),RSS_bytes=int(rss[1])*1024 if rss else None))
  except(OSError,ValueError):continue
 s.update(cpu_allowed=cpus,observed_affinity_claims=observed,host_MemAvailable_bytes=s['host_mem_available_bytes'],cgroup_effective_headroom_bytes=s['cgroup_headroom_bytes'],free_inodes=s['native_free_inodes'])
 cpu_node={};nodes={}
 for node in P('/sys/devices/system/node').glob('node[0-9]*'):
  members=[]
  for part in (node/'cpulist').read_text().strip().split(','):
   if '-'in part:a,b=map(int,part.split('-'));members.extend(range(a,b+1))
   elif part:members.append(int(part))
  number=int(node.name[4:]);cpu_node.update({str(c):number for c in members})
  fields={k:int(v)*1024 for k,v in re.findall(r'Node\s+\d+\s+(\w+):\s+(\d+)\s+kB',(node/'meminfo').read_text())}
  nodes[str(number)]=dict(cpus=members,MemFree_bytes=fields.get('MemFree'),FilePages_bytes=fields.get('FilePages'),rough_free_plus_file_bytes=fields.get('MemFree',0)+fields.get('FilePages',0),scope='ROUGH_NUMA_PLACEMENT_CONTEXT_NOT_ADMISSION_HEADROOM_OR_PHYSICAL_AREA')
 s.update(cpu_NUMA_node=cpu_node,NUMA_nodes=nodes,NUMA_placement_policy='Balance new projected RAM and job count by first-touch CPU node; no mbind or healthy-task changes')
 return s
def forecast(spec,history=None,policy=None):
 estimate=spec['estimated_peak_model_RAM_bytes'];assert estimate>0
 peaks=[]
 for row in (history or []):
  if row.get('input_digest')==spec['input_digest']and type(row.get('peak_RSS_bytes'))is int:peaks.append(row['peak_RSS_bytes'])
 return max(estimate,int(max(peaks)*1.20))if peaks else estimate
def choose_dispatch(pending,sample,claims,history=None,previous=None,policy=None,dispatch_index=0):
 p=globals()['policy'](policy);helper=load('oracle_admit_policy',R/'tools/oracle_runtime_contract.py')
 used={x['host_cpu']for x in claims.values()}|{c for x in sample['observed_affinity_claims']for c in x['cpus']}
 available=[x for x in sample['cpu_allowed']if x not in used]
 if not available:return None
 reserved=0;node_ram={};node_count={};cpu_node=sample.get('cpu_NUMA_node',{})
 for claim in claims.values():
  observed=sum(x.get('RSS_bytes')or 0 for x in sample['observed_affinity_claims']if claim['host_cpu']in x['cpus'])
  reserved+=max(0,claim.get('predicted_peak_RAM_bytes',0)-observed)
  node=cpu_node.get(str(claim['host_cpu']),-1);node_ram[node]=node_ram.get(node,0)+claim.get('predicted_peak_RAM_bytes',0);node_count[node]=node_count.get(node,0)+1
 available.sort(key=lambda c:(node_ram.get(cpu_node.get(str(c),-1),0),node_count.get(cpu_node.get(str(c),-1),0),c))
 # Long work starts early; short jobs fill unused RAM/CPU gaps. This only affects
 # execution order, never inclusion in the frozen population/statistics.
 ordered=sorted(pending,key=lambda s:(-s.get('estimated_wall_seconds',0),-s['expected']['instructions'],s['cohort']))
 if dispatch_index%3==2:ordered=sorted(ordered,key=lambda s:(s['expected']['instructions'],s['cohort']))
 for spec in ordered:
  decision=helper.admit_resource(sample,forecast(spec,history),reserved,fraction=p['memory_utilization_fraction'])
  if decision['admit']:return dict(cohort=spec['cohort'],host_cpu=available[0],predicted_peak_RAM_bytes=forecast(spec,history))
 return None
def runtime_resources(spec):
 helper=load('oracle_local_runtime',R/'tools/oracle_runtime_contract.py');s=helper.local_safety_sample(R)
 safe=s['native_free_bytes']>5*G and s['native_free_inodes']>=100000
 return dict(s,scope='RUNTIME_LOCAL_SAFETY_ONLY',physical_RAM_pass=True,physical_disk_pass=safe,admission_disk_pass=False,admission_pressure_pass=False,registry_or_peer_reads=0,true164_reads=0,required_free_bytes=5*G,pressure_only_controls_new_admission=True)
def resources(spec,fresh_source=False):
 if not fresh_source:return runtime_resources(spec)
 container=plan();helper=load('oracle_admit_full',R/'tools/oracle_runtime_contract.py');s=sample_system()
 # Main pins a bounded read-only peer accounting adapter. It must reconcile old
 # sealed/closed scopes using published evidence, never charge old nominal
 # reservations blindly or free them merely because a PID disappeared.
 ref=container['peer_disk_adapter'];assert sha(ref['path'])==ref['sha256']
 peer=load('oracle_qualified_peer_disk_adapter',ref['path']);v=getattr(peer,ref['function'])(spec,container)
 if v.get('status')=='HOLD':raise RuntimeError('RESOURCE_HOLD_PEER_RESERVATION:'+json.dumps(v,sort_keys=True))
 assert v['status']=='PASS','PEER_RESERVATION_UNEXPECTED_SCHEMA_STATUS'
 assert v['fresh_local_native_peer_reservations']is True,'PEER_RESERVATION_FRESHNESS_SCHEMA_DRIFT'
 assert v['native_device']==2128 and v['bounded_runtime_seconds']<=container.get('admission_peer_timeout_seconds',5)
 predicted=forecast(spec);d=helper.admit_resource(s,predicted,write_reservation=v['own_future_write_bytes'],restore_reservation=v['native_restore_bytes'],peer_reservation=v['peer_future_write_bytes'])
 archive_path=P('/root/share/mnt164');assert P(container['archive_target_root']).is_relative_to(archive_path),'ARCHIVE_NAMESPACE_OUTSIDE_TRUE164'
 try:
  mount=json.loads(subprocess.check_output(['findmnt','-J','-T',str(archive_path)],text=True,timeout=5))['filesystems'][0]
 except subprocess.TimeoutExpired as error:raise RuntimeError('RESOURCE_HOLD_TRUE164_BOUNDED_QUERY_TIMEOUT')from error
 assert mount['fstype']=='fuse.sshfs'and mount['source']=='admin-wcx@10.208.130.164:/home/shared','RESOURCE_HOLD_NOT_TRUE164'
 # Bounded independent CPU helper: an unresponsive FUSE stat cannot hang the
 # 10-second local model safety sampler or hold the science registry lock.
 code='import os,json,sys;v=os.statvfs(sys.argv[1]);print(json.dumps({"free_bytes":v.f_bavail*v.f_frsize}))'
 try:
  archive=json.loads(subprocess.check_output(['/usr/bin/python3','-c',code,str(archive_path)],text=True,timeout=5))
 except subprocess.TimeoutExpired as error:raise RuntimeError('RESOURCE_HOLD_TRUE164_BOUNDED_QUERY_TIMEOUT')from error
 assert archive['free_bytes']>G+v['own_future_write_bytes']+v['native_restore_bytes'],'RESOURCE_HOLD_TRUE164_CAPACITY'
 ram='DYNAMIC_MEMORY_ADMISSION_HOLD'not in d['reasons']
 pressure='MEMORY_PRESSURE_ADMISSION_HOLD'not in d['reasons']
 disk=not any('NATIVE_'in x for x in d['reasons'])
 return dict(s,physical_RAM_pass=ram,physical_disk_pass=disk,admission_disk_pass=disk,admission_pressure_pass=pressure,required_free_bytes=d['required_native_bytes'],peer_disk_reservation_evidence=v,resource_decision=d,true164_mount=mount,true164_free_bytes=archive['free_bytes'])
def archive_resources(spec):
 v=resources(spec,True)
 # Archive processing does not start a model and does not need its predicted
 # future model RAM; disk/full restore reservation is still mandatory.
 v['physical_RAM_pass']=True;return v
def preclaim_diagnostics():return []
