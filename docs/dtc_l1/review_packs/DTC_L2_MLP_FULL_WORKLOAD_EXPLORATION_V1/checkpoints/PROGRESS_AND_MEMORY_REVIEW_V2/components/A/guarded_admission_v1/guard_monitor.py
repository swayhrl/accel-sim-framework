"""Candidate read-only observer + atomic heartbeat writer. Never dispatch/signal.

Start only after coordinator metadata approval; no service auto-installation.
"""
import datetime,importlib.util,json,os,pathlib,time
P=pathlib.Path;HERE=P(__file__).resolve().parent
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 g=load('guard_monitor_rules',HERE/'guarded_native.py');e=load('guard_monitor_original_engine',g.R/'tools/l2_native.py')
 record,policy,epoch,q=g.approval(e,g.PILOT)
 if P(record['monitor_source']['path']).resolve()!=P(__file__).resolve():raise RuntimeError('Wrong monitor source')
 r=load('guard_monitor_frozen_resources',g.R/'tools/l2_resources.py')
 path=P(record['heartbeat_path']);path.parent.mkdir(parents=True,exist_ok=True)
 initial=time.monotonic();previous=None;prior_rss={};generations={};refresh=0
 while True:
  now=time.monotonic()
  if now-refresh>=2:
   reg,ep=e.authority();current=reg['registered_future_requests'][g.REQ]
   if current.get('resource_admission_overlays',{}).get(g.OVERLAY_ID)!=record:raise RuntimeError('Approval changed; stop heartbeat publication')
   for c,row in current['consumed'].items():
    if c in generations:continue
    p=g.R/'DTC/run/results'/row['uuid']/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
    try:v=g.read(p);generations[c]={'pid':v['pid'],'start_ticks':v['start_ticks'],'uuid':row['uuid']}
    except(OSError,ValueError,KeyError):pass
   refresh=now
  sample=r.resource_sample(True);age=time.monotonic()-sample['monotonic'];pause=r.pressure_reasons(sample,previous,policy)
  if age>policy['heartbeat_max_age_seconds']:pause.append('RESOURCE_OBSERVER_STALE')
  if sample['host_MemAvailable_bytes']<=policy['host_floor_bytes']:pause.append('HOST_BELOW_10G')
  cg=sample.get('cgroup_effective_headroom_bytes')
  if cg is not None and cg<=policy['cgroup_floor_bytes']:pause.append('CGROUP_BELOW_10G')
  live={};by_pid={v['pid']:v for v in sample['observed_models']}
  for c,ident in generations.items():
   row=by_pid.get(ident['pid'])
   if not row or row['start_ticks']!=ident['start_ticks']:continue
   rss=row['RSS_bytes'];prior=prior_rss.get(c);growth=0
   if prior and sample['monotonic']>prior[0]:growth=max(0,(rss-prior[1])/(sample['monotonic']-prior[0]))
   reserve=max(policy['minimum_live_growth_reserve_bytes'],int(rss*.10),int(growth*policy['growth_forecast_horizon_seconds']*policy['growth_rate_multiplier']))
   live[c]=dict(ident,RSS_bytes=rss,growth_reserve_bytes=reserve,observed_growth_bytes_per_second=growth)
   prior_rss[c]=(sample['monotonic'],rss)
  heartbeat={'schema':'L2MLP_GUARD_HEARTBEAT_V1','request':g.REQ,'overlay_id':g.OVERLAY_ID,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'monotonic':sample['monotonic'],'epoch':epoch['epoch'],'boot_id':sample['boot_id'],'monitor_pid':os.getpid(),'monitor_start_ticks':g.proc_start(os.getpid()),'registry_overlay_record_sha256':g.jsonsha(record),'policy_sha256':record['policy']['sha256'],'monitor_source_sha256':record['monitor_source']['sha256'],'warmup_complete':previous is not None and now-initial>=policy['minimum_monitor_warmup_seconds'],'pause_new_admission':bool(pause),'pause_reasons':pause,'host_MemAvailable_bytes':sample['host_MemAvailable_bytes'],'cgroup_effective_headroom_bytes':cg,'own_live_generations':live,'monitor_does_not_dispatch_signal_or_kill':True}
  tmp=path.with_name('.'+path.name+'.guardwriting')
  with tmp.open('w')as h:json.dump(heartbeat,h,sort_keys=True,indent=2);h.write('\n');h.flush();os.fsync(h.fileno())
  tmp.replace(path);previous=sample;time.sleep(policy['monitor_interval_seconds'])
if __name__=='__main__':main()
