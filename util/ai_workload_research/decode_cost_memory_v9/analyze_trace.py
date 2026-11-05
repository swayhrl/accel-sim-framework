"""CPU-only NSYS timeline analysis;clock/correlation joins staywithinNSYS."""
from pathlib import Path
import sqlite3,json,statistics,collections,gzip,hashlib,csv
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'docs/ai_workload_research/runs/QWEN_DECODE_COST_MEMORY_MECHANISM_109_V9'
def union(intervals):
 merged=[]
 for a,b in sorted(intervals):
  if not merged or a>merged[-1][1]:merged.append([a,b])
  else:merged[-1][1]=max(b,merged[-1][1])
 return sum(b-a for a,b in merged),merged
def main():
 db=sqlite3.connect(OUT/'.private/NSYS/trace.sqlite');db.row_factory=sqlite3.Row
 ids={r['id']:r['value'] for r in db.execute('select * from StringIds')}
 nv=[dict(r) for r in db.execute('select * from NVTX_EVENTS')]
 for r in nv:r['label']=r['text'] or ids.get(r['textId'],'')
 request=[r for r in nv if str(r['label']).startswith('V9_REQUEST_') and r['end'] is not None]
 phase=[r for r in nv if str(r['label']).startswith(('V9_FORWARD_','V9_SAMPLE_')) and r['end'] is not None]
 runtime={r['correlationId']:dict(r) for r in db.execute('select * from CUPTI_ACTIVITY_KIND_RUNTIME')}
 kernel=[dict(r) for r in db.execute('select * from CUPTI_ACTIVITY_KIND_KERNEL')]
 copies=[dict(r) for r in db.execute('select * from CUPTI_ACTIVITY_KIND_MEMCPY')];sets=[dict(r) for r in db.execute('select * from CUPTI_ACTIVITY_KIND_MEMSET')]
 for k in kernel:
  k['kernel_name']=ids[k['demangledName']];k['short_name']=ids[k['shortName']]
  api=runtime.get(k['correlationId']);found=[]
  if api:
   found=[r for r in phase if r['globalTid']==api['globalTid'] and r['start']<=api['start'] and api['end']<=r['end']]
  k['phase_label']=min(found,key=lambda x:x['end']-x['start'])['label'] if found else None
 prof=json.loads((OUT/'raw/NSYS.json').read_text());native=json.loads((OUT/'CURVE_ANALYSIS.json').read_text())
 results=[]
 for req in request:
  point=req['label'].removeprefix('V9_REQUEST_');rows=[k for k in kernel if req['start']<=k['start'] and k['end']<=req['end']]
  mem=[v for v in copies+sets if req['start']<=v['start'] and v['end']<=req['end']]
  kbusy,_=union([(v['start'],v['end']) for v in rows]);busy,merged=union([(v['start'],v['end']) for v in rows+mem])
  span=req['end']-req['start'];decoded=[k for k in rows if k['phase_label'] and '_DECODE_' in k['phase_label']];prefill=[k for k in rows if k['phase_label'] and '_PREFILL_' in k['phase_label']]
  unknown=[k for k in rows if k['phase_label'] is None]
  steps=collections.defaultdict(list)
  for k in decoded:steps[int(k['phase_label'].rsplit('STEP',1)[1])].append(k)
  stepstats=[]
  for step,ks in sorted(steps.items()):
   duration,_=union([(v['start'],v['end']) for v in ks]);start=min(x['start'] for x in ks);end=max(x['end'] for x in ks)
   stepstats.append(dict(step=step,kernels=len(ks),GPU_kernel_union_ms=duration/1e6,GPU_kernel_span_ms=(end-start)/1e6,first_kernel_ns=start,last_kernel_ns=end))
  names=collections.defaultdict(lambda:[0,0])
  for k in decoded:names[k['kernel_name']][0]+=1;names[k['kernel_name']][1]+=k['end']-k['start']
  top=sorted([dict(kernel=n,count=v[0],summed_profiled_kernel_ms=v[1]/1e6) for n,v in names.items()],key=lambda x:x['summed_profiled_kernel_ms'],reverse=True)
  prebusy,_=union([(v['start'],v['end']) for v in prefill]);decBusy,_=union([(v['start'],v['end']) for v in decoded])
  profile_sample=next(s for s in prof['samples'] if s['role']=='PROFILED' and s['point']==point)
  mode=profile_sample['mode'];n=profile_sample['output_tokens_each'];nativepoint=native['modes'][mode]['points'][str(n)]['GPU']['median_ms']
  launchapis=[r for r in runtime.values() if req['start']<=r['start'] and r['end']<=req['end']]
  apiBusy,_=union([(r['start'],r['end']) for r in launchapis])
  stepgaps=[(b['first_kernel_ns']-a['last_kernel_ns'])/1e6 for a,b in zip(stepstats,stepstats[1:])]
  results.append(dict(point=point,grade='OBSERVED_PROFILED_SCOPE',request_NVTX_ms=span/1e6,profiled_CUDA_event_ms=profile_sample['request_gpu_elapsed_ms'],
    native_curve_median_ms=nativepoint,profiled_over_native_ratio=profile_sample['request_gpu_elapsed_ms']/nativepoint,
    kernel_count=len(rows),kernel_busy_union_ms=kbusy/1e6,GPU_activity_union_ms=busy/1e6,
    NVTX_window_not_covered_by_collected_GPU_activity_ms=(span-busy)/1e6,uncovered_fraction=(span-busy)/span,
    prefill_kernel_count=len(prefill),prefill_kernel_union_ms=prebusy/1e6,decode_kernel_count=len(decoded),decode_kernel_union_ms=decBusy/1e6,
    unclassified_kernel_count=len(unknown),runtime_correlation_matches=sum(k['correlationId'] in runtime for k in rows),graph_node_kernel_count=sum(bool(k['graphNodeId']) for k in rows),
    CPU_CUDA_API_union_ms=apiBusy/1e6,CPU_API_overlap_warning='AlreadyoverlapsGPUtimeline;neveraddmechanically',
    decode_steps=stepstats,inter_decode_kernel_span_gaps_ms=stepgaps,median_interstep_gap_ms=statistics.median(stepgaps) if stepgaps else None,
    top_decode_kernel_groups=top[:20],all_decode_kernel_groups=top,scope_limit='GPUactivitygapincludesCPU/control/untracedactivity/profileroverhead;notprovennativeCPUfraction'))
 coverage=dict(kernel_rows=len(kernel),kernel_runtime_correlation_matches=sum(k['correlationId'] in runtime for k in kernel),
  kernel_phase_classified=sum(k['phase_label'] is not None for k in kernel),NVTX_request_count=len(request),tool_diagnostics=[r[0] for r in db.execute('select text from DIAGNOSTIC_EVENT')],driver_CUDA13_fallback_CUPTI12p8=True,complete_application_trace_coverage_not_guaranteed=True,
  decodeGraph_pushes=sum(r['label']=='decodeGraph' for r in nv),
  empty_forward_markers=[r['label'] for r in phase if str(r['label']).startswith('V9_FORWARD_') and not any(k['phase_label']==r['label'] and r['start']<=runtime[k['correlationId']]['start']<=r['end'] for k in kernel if k['correlationId'] in runtime)],
  table_counts={name:db.execute('select count(*) from "'+name+'"').fetchone()[0] for name in ['StringIds','NVTX_EVENTS','CUPTI_ACTIVITY_KIND_RUNTIME','CUPTI_ACTIVITY_KIND_KERNEL','CUPTI_ACTIVITY_KIND_MEMCPY','CUPTI_ACTIVITY_KIND_MEMSET']})
 # Export full high-value collected activitytables;excludeenvironment/process-private metadata.
 export=OUT/'raw/NSYS_ACTIVITY_TABLES.jsonl.gz'
 names=['StringIds','NVTX_EVENTS','CUDA_GRAPH_NODE_EVENTS','CUPTI_ACTIVITY_KIND_RUNTIME','CUPTI_ACTIVITY_KIND_KERNEL','CUPTI_ACTIVITY_KIND_MEMCPY','CUPTI_ACTIVITY_KIND_MEMSET','PROFILER_OVERHEAD','DIAGNOSTIC_EVENT']
 with gzip.GzipFile(filename=str(export),mode='wb',mtime=0) as f:
  for table in names:
   for row in db.execute('select * from "'+table+'"'):
    f.write((json.dumps(dict(table=table,row=dict(row)),separators=(',',':'))+'\n').encode())
 result=dict(grade='OBSERVED',tool='NsightSystems2024.6.2',trace_mode='cuda,nvtx;graphnode;noCPUsampling;noGPUmetrics',coverage=coverage,requests=results,
   profiler_time_not_native=True,cross_tool_timestamps_not_joined=True,activity_archive=dict(path=str(export.relative_to(OUT)),sha256=hashlib.sha256(export.read_bytes()).hexdigest(),bytes=export.stat().st_size),
   sql_source_sha256=hashlib.sha256((OUT/'.private/NSYS/trace.sqlite').read_bytes()).hexdigest())
 (OUT/'TIMELINE_ANALYSIS.json').write_text(json.dumps(result,indent=2)+'\n')
 # NCUrawcountswithunits;singlekernel_scopeonly.
 raw=list(csv.reader((OUT/'raw/NCU_B1_RAW_BASE.csv').open()));headers,units,values=raw[:3]
 metrics={name:dict(unit=units[i],value=values[i]) for i,name in enumerate(headers) if name.startswith(('dram__','gpu__','lts__','sm__','profiler__'))}
 ncu=dict(grade='OBSERVED',status='B1_SINGLE_NODE_COMPLETE_B2_RESOURCE_CENSORED',kernel=values[headers.index('Kernel Name')],grid=values[headers.index('Grid Size')],block=values[headers.index('Block Size')],metrics=metrics,
   selected_metrics=json.loads((OUT/'raw/NCU_METRIC_SELECTION.json').read_text())['selected'],passes=7,replay='kernel',clock='none',cache='none',
   coverage='ExactlyonefilteredkernelinfirstDecodeGraphofA00N32;notallkernelsorentireDecode. B2countertaskkilledbysafetyguardbeforecompletedreport.',
   no_application_DRAM_sum=True,no_counter_B2_ratio=True,model_QKV_weight_bytes=2048*(2048+256+256)*2,
   interpretation='B1readbytesnearfirstpackedQKVweightbytesMODEL_CONSISTENT;kernelmappingdimensionnotdirectlycaptured,caches/replays/backupaffectrepresentativeness.',
   backup_bytes_not_DRAM=True)
 (OUT/'HARDWARE_COUNTERS.json').write_text(json.dumps(ncu,indent=2)+'\n')
 print(json.dumps(dict(coverage=coverage,requests=[{k:v for k,v in row.items() if k not in ['top_decode_kernel_groups','all_decode_kernel_groups','decode_steps','inter_decode_kernel_span_gaps_ms']} for row in results],
   top=[dict(point=x['point'],groups=x['top_decode_kernel_groups'][:4]) for x in results],archive_bytes=export.stat().st_size)))
if __name__=='__main__':main()
