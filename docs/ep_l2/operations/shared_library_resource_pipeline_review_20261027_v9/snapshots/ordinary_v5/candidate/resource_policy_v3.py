"""Exact resource admission only; creates no cgroup, lock or grant."""
import os,pathlib,resource
GIB=2**30
PROFILE='ORDINARY_WHOLEJOB_VALIDATOR_BOUNDED_1_2_4_8_V3'
SCHEMA='ROOT_EXACT_ORDINARY_VALIDATOR_BOUNDED_V3'
def need(c,m):
 if not c:raise RuntimeError(m)
def integer(x):return type(x)is int
def policy(g,workers,allowed):
 need(integer(workers)and workers in(1,2,4,8),'EXACT_WORKER_CHOICE')
 need(integer(g['max_workers'])and g['max_workers']in(1,2,4,8)and workers<=g['max_workers'],'ROOT_MAX_WORKERS')
 need(integer(g['actual_workers'])and g['actual_workers']==workers,'ROOT_ACTUAL_WORKER_COUNT')
 cpus=g['total_cpu_set']; aff=g['worker_affinity']
 need(type(cpus)is list and cpus and all(integer(c)and c>=0 for c in cpus)and len(cpus)==len(set(cpus)),'ROOT_TOTAL_CPU_SET')
 need(type(aff)is list and len(aff)==workers,'ROOT_AFFINITY_COUNT')
 union=[]
 for group in aff:
  need(type(group)is list and group and all(integer(c)and c>=0 for c in group)and len(group)==len(set(group)),'ROOT_WORKER_CPU_SET')
  union.extend(group)
 need(len(union)==len(set(union)),'ROOT_DISJOINT_WORKER_AFFINITY')
 need(set(union)==set(cpus)and set(cpus)<=set(allowed),'ROOT_ALLOWED_CPU_SET')
 need(integer(g['worker_as_bytes'])and integer(g['parent_as_bytes'])and g['worker_as_bytes']==2*GIB and g['parent_as_bytes']==2*GIB,'EXACT_PER_PROCESS_AS')
 budget=g['exclusive_cgroup_memory_max_bytes']
 need(integer(budget)and 2*GIB*(workers+1)<=budget<=20*GIB,'FINITE_TOTAL_MEMORY_CANDIDATE')
 need(g['rate_scope']=='ONE_WHOLEJOB_SHARED_BUDGET'and integer(g['rate_multiplier'])and g['rate_multiplier']==1,'ONE_AGGREGATE_RATE')
 return dict(workers=workers,max_workers=g['max_workers'],total_cpu_set=sorted(cpus),worker_affinity=[sorted(x)for x in aff],worker_as_bytes=2*GIB,parent_as_bytes=2*GIB,exclusive_cgroup_memory_max_bytes=budget,rate_scope=g['rate_scope'],rate_multiplier=1)
def qualification_policy(workers,count,allowed):
 need(integer(workers)and workers in(1,2,4,8),'EXACT_WORKER_CHOICE')
 actual=max(x for x in(1,2,4,8)if x<=min(workers,count));cpus=sorted(allowed)
 need(len(cpus)>=actual,'QUALIFICATION_ALLOWED_CPU_COUNT')
 g=dict(max_workers=workers,actual_workers=actual,total_cpu_set=cpus[:actual],worker_affinity=[[x]for x in cpus[:actual]],worker_as_bytes=2*GIB,parent_as_bytes=2*GIB,exclusive_cgroup_memory_max_bytes=2*GIB*(actual+1),rate_scope='ONE_WHOLEJOB_SHARED_BUDGET',rate_multiplier=1)
 # The original private single-kernel fallback is retained without production grant authority.
 if actual not in(1,2,4,8):raise RuntimeError('QUALIFICATION_ACTUAL_WORKER_CHOICE')
 return policy(g,actual,allowed)
def verify_existing_cgroup(g):
 """Read-only admission; Root must provision this exact private cgroup separately."""
 path=pathlib.Path(g['exclusive_cgroup_path'])
 need(path.is_absolute()and not path.is_symlink()and path.resolve().is_relative_to(pathlib.Path('/sys/fs/cgroup'))and path.resolve()!=pathlib.Path('/sys/fs/cgroup'),'EXACT_PRIVATE_CGROUP_PATH')
 groups=pathlib.Path('/proc/self/cgroup').read_text().splitlines()
 unified=[x[3:]for x in groups if x.startswith('0::')]
 need(len(unified)==1 and pathlib.Path('/sys/fs/cgroup'+unified[0]).resolve()==path.resolve(),'EXACT_INHERITED_CGROUP_MEMBERSHIP')
 raw=(path/'memory.max').read_text().strip()
 need(raw.isdigit()and int(raw)==g['exclusive_cgroup_memory_max_bytes'],'EXACT_CGROUP_MEMORY_MAX')
 need(g['exclusive_cgroup_root_asserted']is True,'ROOT_EXCLUSIVE_CGROUP_ASSERTION')
 need(set(os.sched_getaffinity(0))==set(g['total_cpu_set']),'PARENT_EXACT_CPU_SET')
 soft,hard=resource.getrlimit(resource.RLIMIT_AS)
 need(0<soft<=2*GIB and 0<hard<=2*GIB,'PARENT_AS_ALREADY_BOUNDED')
 return dict(path=str(path.resolve()),memory_max_bytes=int(raw),current_bytes=int((path/'memory.current').read_text()),exclusivity_source='ROOT_EXACT_ASSERTION_NOT_INFERRED_FROM_RSS')
