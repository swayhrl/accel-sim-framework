#!/usr/bin/env python3
import pathlib,json,gzip,csv,hashlib,math,time
D=pathlib.Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def pin(p):return {'path':str(p),'sha256':sha(p.read_bytes())}
E=json.loads(gzip.decompress((D/'snapshots/capture11_v1/KERNEL_COUNTER_EVIDENCE.json.gz').read_bytes()));closed=[r for r in E['sources']if r['program']in['MVT','BICG']and r['cell']=='DH'];assert len(closed)==4
out=[];checks=[]
for r in closed:
 res=json.loads(pathlib.Path(r['RESULT']['path']).read_bytes());assert sha(pathlib.Path(r['RESULT']['path']).read_bytes())==r['RESULT']['sha256'];receipt=res['archive']['receipt'];mp=pathlib.Path(receipt['target_mount_path'])/'SOURCE_MANIFEST.json';mb=mp.read_bytes();assert sha(mb)==receipt['manifest_sha256'];mf=json.loads(mb);root=pathlib.Path(r['native_EXIT']['path']).parent
 def archived(p):
  real=p.resolve();rel=str(real.relative_to(root));entry=next(e for e in mf['entries']if e['path']==rel);assert entry['type']=='file';b=real.read_bytes();assert sha(b)==entry['sha256']and len(b)==entry['size'];return {'native':pin(real),'archive_manifest':pin(mp),'archive_member':entry['path'],'archive_member_sha256':entry['sha256']}
 f=root/'perf_counter.csv.gz';witness=archived(f);rows=[]
 with gzip.open(f,'rt')as h:
  rd=csv.DictReader(h);names=rd.fieldnames;assert len(set(names))==len(names)
  for row in rd:
   cyc=int(row['gpu_tot_sim_cycle'])+int(row['gpu_sim_cycle']);n={};bankreads=[];bankmiss=[]
   for status in ['HIT','HIT_RESERVED','MISS','SECTOR_MISS','RESERVATION_FAIL','LINE_ALLOC_FAIL','MISS_QUEUE_FULL','MSHR_ENRTY_FAIL','MSHR_MERGE_ENRTY_FAIL']:
    vs=[int(row[f'L2_bank_{i:03d}_GLOBAL_ACC_R_{status}'])for i in range(40)];n[status]=sum(vs)
    if status in ['MISS','SECTOR_MISS']:bankmiss.append(vs)
   br=[sum(int(row[f'L2_bank_{i:03d}_GLOBAL_ACC_R_{k}'])for k in ['HIT','HIT_RESERVED','MISS','SECTOR_MISS'])for i in range(40)];bm=[sum(v[i]for v in bankmiss)for i in range(40)]
   rows.append({'cycle':cyc,'kernel_current_cycles':int(row['gpu_sim_cycle']),'prior_kernel_cycles':int(row['gpu_tot_sim_cycle']),'cumulative_instructions':int(row['gpu_tot_sim_insn'])+int(row['gpu_sim_insn']),'prior_kernel_issued_CTA':int(row['gpu_tot_issued_cta']),'current_completed_CTA':int(row['gpu_completed_cta']),'L2_GLOBAL_R_cumulative':n,'bank40_GLOBAL_R_accepted_cumulative':br,'bank40_GLOBAL_R_miss_cumulative':bm,'host_monotonic_wall_clock_ms':row.get('wall_clock_ms')})
 assert rows[-1]['cycle']==r['cycles'];assert all(a['cycle']<=b['cycle']for a,b in zip(rows,rows[1:]));assert all(all(b['L2_GLOBAL_R_cumulative'][k]>=a['L2_GLOBAL_R_cumulative'][k]for k in a['L2_GLOBAL_R_cumulative'])for a,b in zip(rows,rows[1:]));boundaries=[];prev={k:0 for k in rows[0]['L2_GLOBAL_R_cumulative']};prevbank=[0]*40
 for k in r['kernels']:
  matches=[x for x in rows if x['cycle']==k['cumulative_cycles']and x['kernel_current_cycles']==k['cycles']];assert len(matches)==1;x=matches[0];assert x['cumulative_instructions']==k['cumulative_instructions']and x['prior_kernel_issued_CTA']+x['current_completed_CTA']==k['cumulative_CTA'];n=x['L2_GLOBAL_R_cumulative'];assert sum(n[z]for z in ['HIT','HIT_RESERVED','MISS','SECTOR_MISS'])==k['cumulative_additive']['L2_GLOBAL_read_accepted_sectors'];assert n['MISS']+n['SECTOR_MISS']==k['cumulative_additive']['L2_GLOBAL_read_miss_sectors']
  for reason in ['LINE_ALLOC_FAIL','MISS_QUEUE_FULL','MSHR_ENRTY_FAIL','MSHR_MERGE_ENRTY_FAIL']:
   name='L2_cache_stats_fail_breakdown:GLOBAL_ACC_R:'+reason
   if name in k['positive_only_retry_reasons']:assert n[reason]==k['positive_only_retry_reasons'][name]
  interval={key:n[key]-prev[key]for key in n};assert all(v>=0 for v in interval.values());bank=[v-p for v,p in zip(x['bank40_GLOBAL_R_miss_cumulative'],prevbank)];mu=sum(bank)/40;cv=math.sqrt(sum((v-mu)**2 for v in bank)/40)/mu if mu else None
  boundaries.append({'ordinal':k['ordinal'],'kernel':k['kernel'],'cycle':x['cycle'],'current_kernel_cycles':k['cycles'],'explicit_all40_bank_cumulative':n,'explicit_all40_bank_interval':interval,'interval_miss_atoms32B_per_L2bank':bank,'L2_bank_miss_count_CV_population':cv,'CV_scope':'40L2subpartitions, not DRAMbanks, SMs or latency; overall phase counts do not capture short-time hotspots.'});prev=n;prevbank=x['bank40_GLOBAL_R_miss_cumulative']
 checks.append(r['program']+r['profile']+'_archived_CSV_SHA_explicit_zero_kernel_endpoints_raw_reconciliation')
 resource=root/'RESOURCE_SAMPLES.jsonl.gz';rs={'available':resource.exists()}
 if resource.exists():
  rs['source']=archived(resource);count=0;observations=0;first=None;last=None;peak=0;minhost=None;mincg=None;maxmempsi=None;maxiopsi=None
  with gzip.open(resource,'rt')as h:
   for line in h:
    x=json.loads(line);count+=1
    if x.get('utc')is not None and 'host_MemAvailable_bytes'in x:
     observations+=1
     if first is None:first=x
     last=x
    peak=max(peak,x.get('process_tree_observed_rss_bytes',0));z=x.get('host_MemAvailable_bytes');minhost=z if minhost is None else min(minhost,z)if z is not None else minhost;z=x.get('cgroup_effective_headroom_bytes');mincg=z if mincg is None else min(mincg,z)if z is not None else mincg
    val=x.get('memory_pressure',{}).get('some',{}).get('avg10')
    if isinstance(val,(int,float)):maxmempsi=val if maxmempsi is None else max(maxmempsi,val)
    val=x.get('io_pressure',{}).get('some',{}).get('avg10')
    if isinstance(val,(int,float)):maxiopsi=val if maxiopsi is None else max(maxiopsi,val)
  def delta(key,sub=None):
   a=first.get(key);z=last.get(key)
   if sub is not None:a=a.get(sub)if isinstance(a,dict)else None;z=z.get(sub)if isinstance(z,dict)else None
   return z-a if isinstance(a,(int,float))and isinstance(z,(int,float))else None
  rs.update(total_records=count,timestamped_resource_observations=observations,first_utc=first.get('utc'),last_utc=last.get('utc'),peak_process_tree_observed_rss_bytes=peak,min_host_MemAvailable_bytes=minhost,min_cgroup_effective_headroom_bytes=mincg,max_cgroup_mem_some_avg10=maxmempsi,max_cgroup_io_some_avg10=maxiopsi,host_oom_kill_delta=delta('host_oom_kill_count'),cgroup_oom_kill_delta=delta('cgroup_memory_events','oom_kill'),cgroup_throttled_usec_delta=delta('cgroup_cpu_stat','throttled_usec'),host_pswpout_pages_delta=delta('host_pswpout_pages'),scope='Sampled whole host/cgroup counters include other workloads. RSS is observed process tree, not hardware area or cache occupancy. Hostwall time is not simulated cycles; no exclusive attribution or no-between-sample event claim.')
 ep=json.loads(pathlib.Path(r['native_EXIT']['path']).read_bytes());out.append({'program':r['program'],'input_digest':r['input_digest'],'profile':r['profile'],'RESULT':r['RESULT'],'bottom_RESULT':r['bottom_RESULT'],'CSV_source':witness,'csv_rows':len(rows),'csv_columns':len(names),'CSV_compact_sampling_rows':rows,'kernel_endpoints':boundaries,'resource_summary':rs,'native_exit':r['native_EXIT'],'exit_elapsed_seconds':ep['elapsed_seconds'],'exit_peak_observed_rss_bytes':ep['peak_observed_rss_bytes'],'scope':'Closed qualified input only. CSV explicit zero adds evidence beyond positive-only stdout; old packs not modified.'})
dump(D/'CLOSED_CSV_RESOURCE_EVIDENCE.json',out);dump(D/'CSV_RESOURCE_CPU_CHECKS.json',{'all_pass':True,'checks':checks,'closed_sources':len(closed),'live_raw_reads':0,'models_started':0,'native_writes':0});print([(r['program'],r['profile'],r['csv_rows'],r['resource_summary'].get('timestamped_resource_observations'))for r in out])
