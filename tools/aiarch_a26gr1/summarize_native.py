"""Summarize actual windows without adding overlapping segment durations."""
import collections,json,pathlib,statistics
from control import ROOT
def records(path):
 if not path.exists():return []
 return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
def union(intervals):
 intervals=sorted(intervals);total=0;end=None
 for lo,hi in intervals:
  if end is None or lo>end:total+=hi-lo;end=hi
  elif hi>end:total+=hi-end;end=hi
 return total
def summarize(rows):
 if not rows:return {'status':'NOT_OBSERVED','sample_count':0}
 times=[r['whole_pipeline_cycle_wall_seconds'] for r in rows];tags=collections.defaultdict(list);unhidden=[];adam=[];allhost=[]
 for r in rows:
  blocking=[];cpu=[];allregions=[]
  for x in r['regions']:
   lo,hi=x['begin_host_monotonic'],x['end_host_monotonic'];d=hi-lo;tag=x['tag'].split('@L')[0];tags[tag].append(d);allregions.append((lo,hi))
   if tag in {'synchronize','join','ID_D2H_host','metadata_D2H_host','gradient_D2H_host'}:blocking.append((lo,hi))
   if tag=='cpu_adam':cpu.append((lo,hi))
  unhidden.append(union(blocking));adam.append(union(cpu));allhost.append(union(allregions))
 return {'status':'OBSERVED','sample_count':len(rows),'steps':[min(x['step'] for x in rows),max(x['step'] for x in rows)],'gaussian_range':[min(x['gaussians'] for x in rows),max(x['gaussians'] for x in rows)],'whole_cycle_mean_seconds':statistics.mean(times),'whole_cycle_median_seconds':statistics.median(times),'whole_cycle_p10_seconds':sorted(times)[int(.1*(len(times)-1))],'whole_cycle_p90_seconds':sorted(times)[int(.9*(len(times)-1))],'region_mean_host_seconds':{k:statistics.mean(v) for k,v in tags.items()},'blocking_D2H_sync_join_union_mean_seconds':statistics.mean(unhidden),'cpu_adam_interval_union_mean_seconds':statistics.mean(adam),'all_tagged_host_intervals_union_mean_seconds':statistics.mean(allhost),'cpu_adam_exposed_tail':'NOT_IDENTIFIED_BY_HOST_INTERVALS_ALONE','parameter_H2D':'host pin/enqueue duration, not standalone transfer service time','gpu_and_host_time_domains_not_summed':True}
def main():
 arms={}
 for arm in ['host_wall','gpu_wall','host_diag','host_late','host_late_verified']:
  rows=records(ROOT/'native'/arm/'raw_steps.jsonl');windows={}
  for lo,hi in [(100,200),(14500,14600),(15100,15200)]:
   part=[r for r in rows if lo<=r['step']<hi]
   windows[str(lo)+'-'+str(hi)]={'all':summarize(part),'outer_original_body':summarize([r for r in part if r['timing_kind']!='opt_in_diagnostic']),'diagnostic':summarize([r for r in part if r['timing_kind']=='opt_in_diagnostic'])}
  arms[arm]={'reached_step':max([x['step'] for x in rows],default=0),'windows':windows}
 host=records(ROOT/'native/host_wall/raw_steps.jsonl');gpu=records(ROOT/'native/gpu_wall/raw_steps.jsonl');diag=records(ROOT/'native/host_diag/raw_steps.jsonl')
 compare={'early_camera_sequences_match':len(host)==len(gpu)==len(diag) and all(x['camera_ids']==y['camera_ids']==z['camera_ids'] for x,y,z in zip(host,gpu,diag)),'same_early_gaussian_count':all(x['gaussians']==1694315 for x in host+gpu+diag),'optimizer_algorithms_not_bitwise_same':True,'early_only_no_time_to_quality_ratio':True}
 events={}
 for arm in ['host_diag','host_late','host_late_verified']:
  data=json.loads((ROOT/'native'/arm/'gpu_event_spans.json').read_text()) if (ROOT/'native'/arm/'gpu_event_spans.json').exists() else []
  events[arm]={str(lo)+'-'+str(hi):{'sample_count':len(v:=[x for x in data if lo<=x['step']<hi]),'gpu_event_span_mean_ms':statistics.mean(x['gpu_forward_backward_optimizer_span_ms'] for x in v) if v else None} for lo,hi in [(100,200),(14500,14600),(15100,15200)]}
 result={'status':'ACTUAL_NATIVE_OBSERVATIONS','arms':arms,'comparability':compare,'gpu_event_spans':events,'residual_decision':'REVIEW_PENDING_ACTUAL_EXPOSED_INTERVAL_EVIDENCE','explanation':'blocking host waits can be observed; CPU Adam/GPU overlap and thread policy do not isolate a physical memory/cache/PCIe cause. CUDA spans include launch gaps. No physical resource counterfactual or long converged quality matching was executed.','gaussian_reuse_identity':'NOT_MEASURED; row indices across densification are not permanent IDs'}
 (ROOT/'native_measurement_summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
