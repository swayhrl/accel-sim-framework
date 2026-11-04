"""Read-only actual CPU2 two-snapshot occupied-mask diagnosis; no policy action."""
import pathlib,json,hashlib,importlib.util,time,os,collections
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');D=A/'agents/A/cpu_spare_current_hold_readonly_v1';D.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def ranges(values):
 v=sorted(set(values));out=[]
 for x in v:
  if out and out[-1][1]+1==x:out[-1][1]=x
  else:out.append([x,x])
 return ','.join(str(a)if a==b else f'{a}-{b}'for a,b in out)
def procmeta():
 result={}
 for p in P('/proc').iterdir():
  if not p.name.isdigit():continue
  try:
   text=(p/'stat').read_text();f=text.rsplit(')',1)[1].split();result[int(p.name)]=dict(comm=text.split('(',1)[1].rsplit(')',1)[0],state=f[0],ticks=int(f[11])+int(f[12]),start_ticks=int(f[19]),processor=int(f[36]))
  except(FileNotFoundError,ProcessLookupError,PermissionError):pass
 return result
lp=R/'control/operational_amendments/cpu_spare_memory_v2/cpu_memory.py';lib=load('actual_cpu2_readonly_sampler',lp);hz=os.sysconf('SC_CLK_TCK');t0=time.monotonic();pm0=procmeta();e=lib.sample_cpu_evidence(None,.5);pm1=procmeta();t1=time.monotonic();a,b=e['first'],e['second'];dt=b['monotonic']-a['monotonic'];top={r['cpu']:r for r in b['topology']};allowed=set(b['allowed'])
def core(c):return(top[c]['socket'],top[c]['core'])
groups={};occupied=set();perpid={}
for label,s in [('first',a),('second',b)]:
 for row in s['other_task_claims']:
  cpus=row['affinity']if row['affinity']is not None else[row['processor']];occupied.update(cpus);key=(row['kind'],tuple(cpus));g=groups.setdefault(key,dict(kind=row['kind'],affinity_width=row['affinity_width'],occupied_mask=ranges(cpus),pids=set(),tids=set(),states=collections.Counter(),snapshots=set()))
  g['pids'].add(row['pid']);g['tids'].add(row['tid']);g['states'][row['state']]+=1;g['snapshots'].add(label)
  pp=perpid.setdefault(row['pid'],dict(pid=row['pid'],comm=pm1.get(row['pid'],pm0.get(row['pid'],{})).get('comm','DISAPPEARED'),states=collections.Counter(),max_affinity_width=0,mask=set(),tids=set(),kind=set()))
  pp['states'][row['state']]+=1;pp['max_affinity_width']=max(pp['max_affinity_width'],row['affinity_width']);pp['mask'].update(cpus);pp['tids'].add(row['tid']);pp['kind'].add(row['kind'])
busy={}
for c in allowed:
 x=a['cpu_ticks'][str(c)];y=b['cpu_ticks'][str(c)];d=[bb-aa for aa,bb in zip(x,y)];total=sum(d);busy[c]=(total-d[3]-d[4])/total if total>0 else 1
physical={core(c)for c in allowed};occupiedcores={core(c)for c in occupied if c in top};idle=[];idle_unoccupied=[]
for key in physical:
 siblings=next(r['siblings']for r in top.values()if(r['socket'],r['core'])==key)
 if set(siblings)<=allowed and all(busy[c]<=.10 for c in siblings):
  idle.append(key)
  if key not in occupiedcores:idle_unoccupied.append(key)
for row in perpid.values():
 pid=row['pid'];v0=pm0.get(pid);v1=pm1.get(pid);row['cpu_used_cores_interval']=(v1['ticks']-v0['ticks'])/hz/(t1-t0)if v0 and v1 and v0['start_ticks']==v1['start_ticks']else None
 row['occupied_physical_cores']=len({core(c)for c in row['mask']if c in top});row['occupied_cpu_mask']=ranges(row.pop('mask'));row['states']=dict(row['states']);row['tids_count']=len(row.pop('tids'));row['kind']=sorted(row['kind'])
group_rows=[]
for g in groups.values():
 g['pids']=[dict(pid=pid,comm=perpid[pid]['comm'],cpu_used_cores_interval=perpid[pid]['cpu_used_cores_interval'])for pid in sorted(g['pids'])];g['tids_count']=len(g.pop('tids'));g['states']=dict(g['states']);g['snapshots']=sorted(g['snapshots']);group_rows.append(g)
group_rows.sort(key=lambda x:(x['affinity_width'],x['tids_count']),reverse=True)
quota=[];ca=a['cgroups'];cb=b['cgroups'];cgdt=cb['sample_monotonic']-ca['sample_monotonic']
for x,y in zip(ca['visible'],cb['visible']):
 quota.append(dict(path=y['path'],quota=y['quota'],used_cores=(y['stat']['usage_usec']-x['stat']['usage_usec'])/cgdt/1e6,nr_throttled_delta=y['stat']['nr_throttled']-x['stat']['nr_throttled'],throttled_usec_delta=y['stat']['throttled_usec']-x['stat']['throttled_usec']))
summary=dict(schema='ACTUAL_CPU2_SPARE_HOLD_READONLY_DIAGNOSIS_V1',utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),sampler_source=str(lp),sampler_source_sha256=sha(lp),driver_sha256=sha(__file__),assessment=e['assessment'],eligible=e['eligible'],two_real_snapshots=True,sample_interval_seconds=dt,process_cpu_measure_interval_seconds=t1-t0,allowed_logical_cpus=len(allowed),allowed_cpu_mask=ranges(allowed),allowed_physical_cores=len(physical),claimed_occupied_logical_cpus=len(occupied&allowed),claimed_occupied_cpu_mask=ranges(occupied&allowed),claimed_occupied_physical_cores=len(occupiedcores&physical),idle_physical_cores_if_ignore_affinity_claims=len(idle),idle_and_unoccupied_physical_cores=len(idle_unoccupied),mean_logical_CPU_busy_fraction=sum(busy.values())/len(busy),logical_cpu_busy_over10pct=sum(x>.1 for x in busy.values()),max_logical_CPU_busy_fraction=max(busy.values()),quota=quota,unreadable_tasks=[len(a['unreadable_tasks']),len(b['unreadable_tasks'])],scanned_tasks=[a['scanned_tasks'],b['scanned_tasks']],occupied_mask_groups=group_rows,process_contributors=sorted(perpid.values(),key=lambda x:(x['occupied_physical_cores'],x['max_affinity_width']),reverse=True),mechanism='For every non-Z/X task with affinity width smaller than sampler allowed width, frozenCPU2 marks its ENTIRE affinity mask occupied regardless of S/D/R state or measured CPU duty. Occupancy propagated to full physical core siblings. Broad R tasks only claim observed processor. No exclusion/affinity/policy changes were performed.',caveat='Sleeping narrow affinity can still represent a legitimate owner; idle measurements alone do not authorize ignoring it. Hidden ancestors remain UNKNOWN, not proven absent.',production_changes=0,model_starts=0,signals=0,affinity_changes=0)
(D/'DIAGNOSIS.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:summary[k]for k in ['utc','assessment','allowed_logical_cpus','allowed_physical_cores','claimed_occupied_logical_cpus','claimed_occupied_physical_cores','idle_physical_cores_if_ignore_affinity_claims','idle_and_unoccupied_physical_cores','mean_logical_CPU_busy_fraction','quota']},ensure_ascii=False));print('TOP_GROUPS',json.dumps(group_rows[:8],ensure_ascii=False));print('TOP_PIDS',json.dumps(summary['process_contributors'][:12],ensure_ascii=False));print('PATH',str(D/'DIAGNOSIS.json'),'SHA',sha(D/'DIAGNOSIS.json'))
