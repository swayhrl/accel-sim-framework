import pathlib,json,os,datetime,collections,hashlib
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2')
def read(p):return json.loads(P(p).read_bytes())
q=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests']['DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'];matrix=read(R/'control/MATRIX_CURRENT.json');meta={p['cohort']:p for p in matrix['points']};primary_cohorts=set(meta);supplemental_meta={}
for c in set(q['admitted_specs'])-primary_cohorts:
 s=read(R/'control/specs'/(c+'.json'));assert s.get('scientific_role')=='SUPPLEMENTAL_NEW_PERFORMANCE_TRIAL';supplemental_meta[c]=s;meta[c]=s
states=collections.Counter();supplemental_states=collections.Counter();profiles={};pending_post=0
for f in(R/'analysis').glob('*.RESULT.json'):
 d=read(f);c=d.get('cohort',f.name[:-12]);p=meta.get(c)
 if c in supplemental_meta:supplemental_states[d['state']]+=1
 else:states[d['state']]+=1
 if p and c in primary_cohorts:profiles.setdefault(p['profile'],collections.Counter())[p['cell']+'_'+d['state']]+=1
live=[];closed=0;unobserved=[]
for c,row in q['consumed'].items():
 if 'execution_receipt'in row:closed+=1;continue
 path=R/'DTC/run/results'/row['uuid']/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
 try:
  d=read(path);fields=(P('/proc')/str(d['pid'])/'stat').read_text().rsplit(')',1)[1].split();assert int(fields[19])==d['start_ticks']and fields[0]!='Z';live.append(dict(cohort=c,program=meta[c]['program'],cell=meta[c]['cell'],profile=meta[c]['profile'],pid=d['pid'],state=fields[0],CPU_ticks=int(fields[11])+int(fields[12]),RSS_GiB=int(fields[21])*os.sysconf('SC_PAGE_SIZE')/1024**3,cpu=sorted(os.sched_getaffinity(d['pid']))))
 except (OSError,AssertionError,KeyError,ValueError):unobserved.append(c)
old=[]
for pid,ticks in [(1262476,968887690),(1285886,969646089),(1498624,977759950),(1498660,977760065),(1498666,977760070)]:
 try:
  f=(P('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split();assert int(f[19])==ticks and f[0]!='Z';old.append(dict(pid=pid,state=f[0],RSS_GiB=int(f[21])*os.sysconf('SC_PAGE_SIZE')/1024**3))
 except(OSError,AssertionError):pass
res=read(R/'control/RESOURCE_OBSERVER.json');batch=read(R/'analysis/BATCH_STATE.json');vm={line.split()[0]:int(line.split()[1])*1024 for line in P('/proc/meminfo').read_text().splitlines()if line.startswith('MemAvailable:')};v=os.statvfs(R);typed=[]
proofpath=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/coordinator/scan_negative_closeout_v1/VERIFIED_ENGINEERING_NEGATIVE_V1.json')
if proofpath.exists():
 proof=read(proofpath);assert proof['status']=='VERIFIED_TYPED_ENGINEERING_NEGATIVE_UNACCEPTED'and proof['performance_accepted']is False and proof['accepted_cycles']is None;assert hashlib.sha256(P(proof['certificate']).read_bytes()).hexdigest()==proof['certificate_sha256'];assert q['consumed'][proof['cohort']]['uuid']==proof['uuid'];typed.append(dict(cohort=proof['cohort'],uuid=proof['uuid'],cached_Main_full_verification_UTC=proof['Main_execution_UTC'],certificate_sha256=proof['certificate_sha256'],proof_path=str(proofpath),accepted=False,cycles=None))
primary_admitted=set(q['admitted_specs'])&primary_cohorts;primary_spent=set(q['consumed'])&primary_cohorts
print(json.dumps(dict(CST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),matrix_cells=len(matrix['points']),matrix_revision=matrix['revision'],initial_registered_fresh=len(primary_admitted),total_registered_fresh_including_supplemental=q['budget'],spent=len(primary_spent),unspent=len(primary_admitted-primary_spent),closed_raw=sum('execution_receipt'in q['consumed'][c]for c in primary_spent),result_states=dict(states),supplemental=dict(registered_cohorts=sorted(supplemental_meta),spent=sum(c in q['consumed']for c in supplemental_meta),unspent=sum(c not in q['consumed']for c in supplemental_meta),result_states=dict(supplemental_states),actual_live_models=sum(x['cohort']in supplemental_meta for x in live)),actual_live_models=len(live),actual_live_program_counts=dict(collections.Counter(x['program']for x in live)),spent_without_native_receipt_or_live=unobserved,independently_archived_engineering_negative_receipts=typed,errors=batch['errors'],legacy_DTC_live=len(old),legacy_processes=old,host_available_GiB=vm['MemAvailable:']/1024**3,cgroup_current_GiB=res['cgroup_memory_current']/1024**3,cgroup_effective_headroom_GiB=res['cgroup_effective_headroom_bytes']/1024**3,native_free_GiB=v.f_bavail*v.f_frsize/1024**3,resource_events=res['cgroup_memory_events'],pressure=res['memory_pressure'],profiles=profiles,live_PID_examples=live[:4]),indent=2))
