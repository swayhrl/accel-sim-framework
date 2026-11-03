from pathlib import Path
import json,zlib,os,time,datetime,hashlib,re
R=Path('/root/data/dtc_stage_iia_first16_20261104_v1');BASE=Path(__file__).resolve().parent;O=BASE/'private'
C='E2-DTC2A16-eededb785179fc04-CH-F256-V1';PID=3521937;START=1049052693
sha=lambda b:hashlib.sha256(b).hexdigest()
def prefix_jsonl(p):
 b=p.read_bytes();z=zlib.decompressobj(31);plain=z.decompress(b);rows=[]
 for l in plain.splitlines():
  try:rows.append(json.loads(l))
  except json.JSONDecodeError:pass
 return rows,{'path':str(p),'point_in_time_gzip_prefix_sha256':sha(b),'prefix_bytes':len(b),'gzip_eof':z.eof,'rows_observed':len(rows)}
def sample(label):
 begin=time.monotonic_ns();sp=R/'control/specs'/(C+'.json');sb=sp.read_bytes();s=json.loads(sb);ip=R/'control/qualification_ledger'/(C+'.INTENT.json');ib=ip.read_bytes();i=json.loads(ib);out=Path(i['output']);mp=out/'NATIVE_SIMULATOR_PID_AND_MAPS.json';mb=mp.read_bytes();m=json.loads(mb);assert(m['pid'],m['start_ticks'])==(PID,START);proc=Path('/proc')/str(PID);stat=(proc/'stat').read_text().rsplit(')',1)[1].split();assert int(stat[19])==START;hz=os.sysconf('SC_CLK_TCK');up=float(Path('/proc/uptime').read_text().split()[0]);pr,pref=prefix_jsonl(out/'progress.jsonl.gz');assert pr and all((v['pid'],v['start_ticks'],v['generation'],v['input'],v['roi'])==(PID,START,i['uuid'],s['input_digest'],s['original_environment']['DTC_AG7_ROI_SHA'])for v in pr);assert all(y['seq']==x['seq']+1 and y['completed']>=x['completed']and y['mono_ns']>x['mono_ns']for x,y in zip(pr,pr[1:]));last=pr[-1]
 bp=Path(s['input_binding_path']);bb=bp.read_bytes();assert sha(bb)==s['input_binding_sha256'];krs=json.loads(bb)['qualification']['rows'];ks=[{'ordinal':n+1,'kernel':r['kernel'],'instructions':int(r['active_thread_instructions'])}for n,r in enumerate(krs)];assert sum(x['instructions']for x in ks)==s['expected']['instructions'];assert len(ks)==s['expected']['kernels'];lo=0;current=None
 for k in ks:
  hi=lo+k['instructions']
  if last['completed']<hi:current=dict(k,prior_instructions=lo,current_kernel_completed=last['completed']-lo,current_kernel_retired_fraction=(last['completed']-lo)/k['instructions']);break
  lo=hi
 pressure={}
 for scope,root in [('host',Path('/proc/pressure')),('process',proc/'pressure')]:
  pressure[scope]={}
  for name in ['cpu','io','memory']:
   p=root/name
   if p.exists():pressure[scope][name]=p.read_text()
 cg=(proc/'cgroup').read_text();cgroup={};rel=next((x.split('::',1)[1]for x in cg.splitlines()if x.startswith('0::')),None)
 if rel is not None:
  root=Path('/sys/fs/cgroup')/rel.lstrip('/')
  for name in ['cpu.max','cpu.stat','memory.current','memory.max','memory.events','memory.swap.current','memory.pressure','cpu.pressure','io.pressure','io.stat']:
   p=root/name
   if p.exists():cgroup[name]=p.read_text()
 meminfo={k:int(v)for k,v in re.findall(r'^(MemAvailable|SwapFree|SwapTotal|MemFree):\s+(\d+)',Path('/proc/meminfo').read_text(),re.M)}
 io=(proc/'io').read_text();status=(proc/'status').read_text();vm={k:int(v)for k,v in re.findall(r'^(VmRSS|VmSwap|VmSize|Threads):\s+(\d+)',status,re.M)};aff=sorted(os.sched_getaffinity(PID));cpu=int(stat[36]);freq={}
 for name in ['scaling_cur_freq','scaling_governor','cpuinfo_cur_freq']:
  p=Path('/sys/devices/system/cpu')/('cpu'+str(cpu))/'cpufreq'/name
  if p.exists():freq[name]=p.read_text().strip()
 resource,resource_ref=prefix_jsonl(out/'RESOURCE_SAMPLES.jsonl.gz')
 # Read bounded text tails solely to observe already-produced runtime diagnostics, never acceptance/speedup.
 rb=(out/'raw.log.gz').read_bytes();zz=zlib.decompressobj(31);raw=zz.decompress(rb).decode(errors='replace');tail='\n'.join(raw.splitlines()[-100:]);runtime_lines=[l for l in raw.splitlines()if 'uArch: inst.'in l or 'gpu_sim_cycle' in l or 'gpu_tot_sim_cycle'in l or 'DTC_L1_PROGRESS'in l][-12:]
 d={'schema':'DTC_ATAX_F256_LIVE_RUNTIME_SAMPLE_V1','label':label,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'capture_begin_mono_ns':begin,'capture_end_mono_ns':time.monotonic_ns(),'pid':PID,'start_ticks':START,'uuid':i['uuid'],'input_digest':s['input_digest'],'roi':s['original_environment']['DTC_AG7_ROI_SHA'],'identity_verified':True,'cohort':C,'spec_sha256':sha(sb),'intent_sha256':sha(ib),'native_maps_sha256':sha(mb),'input_binding_sha256':sha(bb),'process_state':stat[0],'processor_at_sample':cpu,'affinity':aff,'elapsed_seconds':up-START/hz,'utime_seconds':int(stat[11])/hz,'stime_seconds':int(stat[12])/hz,'minor_faults':int(stat[7]),'major_faults':int(stat[9]),'delayacct_blkio_ticks':int(stat[39])if len(stat)>39 else None,'proc_io':io,'proc_memory':vm,'proc_schedstat':(proc/'schedstat').read_text(),'wchan':(proc/'wchan').read_text(),'loadavg':Path('/proc/loadavg').read_text(),'meminfo_kB':meminfo,'pressure':pressure,'cgroup_path':cg,'cgroup':cgroup,'sampled_cpu_frequency':freq,'kernel_instruction_boundaries':ks,'current_kernel':current,'progress_ref':pref,'last_progress':last,'progress_freshness_seconds':(time.monotonic_ns()-last['mono_ns'])/1e9,'resource_ref':resource_ref,'last_resource_samples':resource[-4:],'live_raw_diagnostic_ref':{'path':str(out/'raw.log.gz'),'prefix_bytes':len(rb),'prefix_sha256':sha(rb),'gzip_eof':zz.eof,'scope':'runtime diagnostics only, never formal cycles/speedup or strict acceptance'},'live_raw_runtime_lines':runtime_lines,'scientific_performance':None,'native_RESULT_exists':(R/'analysis'/(C+'.RESULT.json')).exists(),'native_DONE_exists':(R/'control/qualification_ledger'/(C+'.DONE.json')).exists()}
 target=O/(label+'.json')
 if target.exists():raise ValueError('SAMPLE_LABEL_ALREADY_EXISTS_USE_NEW_LABEL')
 target.write_text(json.dumps(d,indent=2)+'\n');return d

if __name__=='__main__':
 import sys
 for program,profile,PID,START,digest in [('scan','F128',3495633,1048139893,'6df3a84b612086e8'),('scan','F256',3501039,1048216855,'6df3a84b612086e8'),('ATAX','F256',3521937,1049052693,'eededb785179fc04'),('MVT','F256',3534697,1049386468,'f437190767aaed49')]:
  C='E2-DTC2A16-'+digest+'-CH-'+profile+'-V1';label=program+'_'+profile+'_'+sys.argv[1];d=sample(label)
  public={k:v for k,v in d.items()if k not in ['last_resource_samples','cgroup','pressure','live_raw_runtime_lines','loadavg']};cg=d['cgroup'];public['bounded_pressure_cgroup']={k:cg.get(k)for k in ['cpu.max','cpu.stat','memory.current','memory.max','memory.events','memory.swap.current','memory.pressure','cpu.pressure','io.pressure']};public['host_pressure']=d['pressure'].get('host');public['runtime_cycle_observability']={'diagnostic_lines_present':bool(d['live_raw_runtime_lines']),'observed_line_count':len(d['live_raw_runtime_lines']),'scope':'May be completed prior-kernel prints/uArch diagnostics; not a matched numeric current-cycle interval','formal_performance':None};fullp=O/(label+'.json');public['private_full_capture']={'path':str(fullp),'sha256':sha(fullp.read_bytes()),'publish':False};(BASE/(label+'.json')).write_text(json.dumps(public,indent=2)+'\n');print(program,profile,d['utc'],'elapsed',round(d['elapsed_seconds'],2),'retired',d['last_progress']['completed'],'kernel',d['current_kernel'],'fresh',d['progress_freshness_seconds'])
