"""Read-only DTC downstream18 segmentation. No simulator/controller imports.

Writes only --output, independently of production control and result paths.
All interval comparisons are provisional sampled observations, never acceptance.
"""
import argparse
import bisect
import datetime as dt
import hashlib
import html
import json
import math
import os
from pathlib import Path
import re
import statistics
import time
import zlib

SCHEMA = 'DTC_DOWNSTREAM18_SEGMENTATION_V1'
BINS = [0, 5, 25, 50, 75, 95, 100]
DEFAULT_ROOT = '/root/data/dtc_hash_downstream18_20261027_v1'
DEFAULT_OUTPUT = '/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_hash_downstream18_20261027_v1/segmentation_v1'
CORE = '/root/data/dtc_failure_repair_20261025_v1/core'
FRAMEWORK = '/root/data/dtc_failure_repair_20261025_v1/framework'
APPS = '/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/polybench-gpu-1.0/CUDA'
APP_INFO = {
 'ATAX': ('atax.cu', [(84,96,'tmp = A*x',16384,4),(98,110,'y = A^T*tmp',4,16384)], 'bca826a6e4fbdad67b11400ef2193210f43d8181441a0b9883e19445db049cfb'),
 'MVT': ('mvt.cu', [(109,121,'x1 += A*y1',16384,4),(124,136,'x2 += A^T*y2',4,16384)], '83764e6633f3a0976423e0ba7ab351ac42b0eeb249bf59a9e3531c639d4923d6'),
 'BICG': ('bicg.cu', [(99,113,'s = A^T*r',4,16384),(117,131,'q = A*p',16384,4)], 'c38c3b0bb1a543ce37ee6d4d7abe433a36574f05b49574e6bf1004c45b68f6fe'),
}
SOURCE_EXCERPTS = [
 (CORE+'/src/abstract_hardware_model.cc',1280,1357),
 (CORE+'/src/gpgpu-sim/gpu-sim.cc',1240,1354),
 (CORE+'/src/gpgpu-sim/gpu-sim.cc',1527,1594),
 (CORE+'/src/gpgpu-sim/gpu-sim.cc',2633,2638),
 (CORE+'/src/gpgpu-sim/l2cache.cc',1113,1126),
 (CORE+'/src/gpgpu-sim/l2cache.h',448,455),
 (CORE+'/src/gpgpu-sim/mem_latency_stat.cc',283,294),
 (CORE+'/src/gpgpu-sim/gpu-sim.h',295,298),
 (CORE+'/src/gpgpu-sim/dram_sched.cc',231,252),
 (FRAMEWORK+'/gpu-simulator/accel-sim.cc',72,106),
 (FRAMEWORK+'/gpu-simulator/accel-sim.cc',158,200),
]
MISSING = [
 {'metric':'DTC Tag replacement / bank arbitration / duplicate lower requests', 'status':'NO_EXPLICIT_PERIODIC_DTC_COLUMNS', 'consequence':'Generic L1D columns are not a validated DTC counter interface; no DTC attribution.'},
 {'metric':'PIB/OO occupancy, full cycles and completion service', 'status':'NOT_PERIODICALLY_EXPORTED', 'consequence':'Cannot separate DTC admission/retirement bottlenecks from this CSV.'},
 {'metric':'DRAM scheduler wait distribution / sum / count', 'status':'NOT_PERIODICALLY_EXPORTED', 'consequence':'L2 FIFO-full events are not queue latency; no segment avg_mrq_latency.'},
 {'metric':'L2-to-DRAM request roundtrip and causal request cohorts', 'status':'NO_REQUEST_ID_STAGE_TIMESTAMPS', 'consequence':'Traffic completed during an interval may originate in earlier work.'},
 {'metric':'Exact per-warp loop iteration / source line / PC', 'status':'AGGREGATE_RETIRED_WORK_ONLY', 'consequence':'Work percent is not an exact common j or i for all warps.'},
 {'metric':'Time-average active SMs / instantaneous concurrency', 'status':'ONLY_RETIREMENT_PARTICIPATION_PROXY', 'consequence':'SMs with retired warps in a segment are not active-SM occupancy.'},
]

def digest(b): return hashlib.sha256(b).hexdigest()
def readj(p): return json.loads(Path(p).read_bytes())
def now(): return dt.datetime.now(dt.timezone.utc).isoformat()

def atomic(p, data):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 temp=p.with_name(p.name+'.tmp.'+str(os.getpid()))
 temp.write_bytes(data if isinstance(data,bytes) else data.encode('utf-8'))
 os.replace(temp,p)

def dumpj(p,data): atomic(p,json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n')

def inflate_live(data):
 """Read concatenated gzip members, including complete lines of an open tail.

 A truncated tail is normal while writing. A corrupt member fails closed.
 """
 chunks=[];complete=0;tail_open=False
 while data:
  dec=zlib.decompressobj(31)
  try: out=dec.decompress(data)
  except zlib.error as e: raise ValueError('CORRUPT_GZIP_MEMBER: '+str(e)) from e
  chunks.append(out)
  if not dec.eof:
   tail_open=True;break
  complete+=1;data=dec.unused_data
 raw=b''.join(chunks)
 end=raw.rfind(b'\n')+1
 return raw[:end], {'complete_members':complete,'open_tail':tail_open,'discarded_partial_line_bytes':len(raw)-end}

def groups(header):
 idx={k:i for i,k in enumerate(header)}
 def match(pattern):return [i for i,h in enumerate(header)if re.fullmatch(pattern,h)]
 return idx, {
  'dram_read_atoms':match(r'dram_reads_per_mc_\d+'),
  'dram_write_atoms':match(r'dram_writes_per_mc_\d+'),
  'l2_fifo_full_events':match(r'L2_dram_queue_full_\d+'),
  'l2_read_hit':match(r'L2_bank_\d+_GLOBAL_ACC_R_HIT'),
  'l2_read_reserved':match(r'L2_bank_\d+_GLOBAL_ACC_R_HIT_RESERVED'),
  'l2_read_miss':match(r'L2_bank_\d+_GLOBAL_ACC_R_MISS'),
  'l2_read_sector_miss':match(r'L2_bank_\d+_GLOBAL_ACC_R_SECTOR_MISS'),
  'l2_read_mshr_hit':match(r'L2_bank_\d+_GLOBAL_ACC_R_MSHR_HIT'),
  'l2_read_reservation_fail':match(r'L2_bank_\d+_GLOBAL_ACC_R_RESERVATION_FAIL'),
 }

def parse_perf(data):
 raw,meta=inflate_live(data);lines=raw.decode('utf-8').splitlines()
 if not lines:return [],dict(meta,reason='NO_COMPLETE_HEADER')
 header=lines[0].split(',')
 if header[-1]=='':header.pop()
 if len(set(header))!=len(header):raise ValueError('DUPLICATE_COUNTER_NAME')
 idx,gs=groups(header)
 needed=['gpu_tot_sim_cycle','gpu_sim_cycle','gpu_tot_sim_insn','gpu_sim_insn','wall_clock_ms']
 if any(k not in idx for k in needed):raise ValueError('MISSING_IDENTITY_COUNTER')
 sm=[i for i,h in enumerate(header)if re.fullmatch(r'm_num_sim_winsn_\d+',h)]
 rows=[]
 for line_no,line in enumerate(lines[1:],2):
  vals=line.split(',')
  if vals[-1]=='':vals.pop()
  if len(vals)!=len(header):raise ValueError('CSV_WIDTH_MISMATCH_LINE_'+str(line_no))
  def val(k):return int(vals[idx[k]])
  metrics={k:sum(int(vals[i])for i in ids)if ids else None for k,ids in gs.items()}
  for k in ['gpu_stall_icnt2core','gpu_stall_icnt2mem','gpu_stall_core2icnt','gpu_stall_mem2icnt','gpgpu_n_stall_shd_mem']:
   metrics[k]=val(k)if k in idx else None
  rows.append({'line':line_no,'cycles':val('gpu_tot_sim_cycle')+val('gpu_sim_cycle'),
   'instructions':val('gpu_tot_sim_insn')+val('gpu_sim_insn'),
   'past_instructions':val('gpu_tot_sim_insn'),'kernel_instructions':val('gpu_sim_insn'),
   'wall_ms':val('wall_clock_ms'),'metrics':metrics,
   'dram_per_mc':[int(vals[i])for i in gs['dram_read_atoms']],
   'fifo_per_sp':[int(vals[i])for i in gs['l2_fifo_full_events']],
   'retired_warp_per_sm':[int(vals[i])for i in sm]})
 for a,b in zip(rows,rows[1:]):
  if b['cycles']<a['cycles']or b['instructions']<a['instructions']or b['wall_ms']<a['wall_ms']:
   raise ValueError('NONMONOTONE_GLOBAL_PROGRESS')
 return rows,dict(meta,columns=len(header),data_rows=len(rows),header_sha256=digest(lines[0].encode()),
  groups={k:len(v)for k,v in gs.items()},missing_groups=[k for k,v in gs.items()if not v],
  explicit_DTC_columns=[h for h in header if any(s in h.lower()for s in ['dtc','pib','mrq_latency'])])

def zero_row(reference):
 return {'line':0,'cycles':0,'instructions':0,'past_instructions':0,'kernel_instructions':0,'wall_ms':None,
  'metrics':{k:0 if v is not None else None for k,v in reference['metrics'].items()},
  'dram_per_mc':[0]*len(reference['dram_per_mc']),'fifo_per_sp':[0]*len(reference['fifo_per_sp']),
  'retired_warp_per_sm':[0]*len(reference['retired_warp_per_sm'])}

def kernel_curves(rows,kernels):
 curves=[];prefix=0;prior_terminal=None
 for k in kernels:
  population=k['active_thread_instructions']
  selected=[r for r in rows if r['past_instructions']==prefix and 0<=r['kernel_instructions']<=population]
  pts=[]
  if rows and prefix==0:pts.append(dict(work=0,row=zero_row(rows[0]),boundary='PROCESS_ZERO'))
  elif prior_terminal is not None:pts.append(dict(work=0,row=prior_terminal,boundary='PREVIOUS_KERNEL_TERMINAL'))
  for r in selected:pts.append(dict(work=r['kernel_instructions'],row=r,boundary='SAMPLED'))
  # At repeated retired-work frontiers retain the last sample, including drain.
  unique={p['work']:p for p in pts};pts=[unique[w]for w in sorted(unique)]
  terminal=next((p['row']for p in reversed(pts)if p['work']==population),None)
  curves.append({'ordinal':k['ordinal'],'kernel':k['kernel'],'population':population,'points':pts,
   'complete_population_observed':terminal is not None,'baseline_observed':bool(pts and pts[0]['work']==0)})
  prior_terminal=terminal;prefix+=population
 return curves

def anchor(curve,target):
 pts=curve['points'];works=[p['work']for p in pts];j=bisect.bisect_left(works,target)
 if j==len(pts)or not pts or (j==0 and works[0]>target):return None
 if works[j]==target:lo=hi=pts[j]
 else:lo,hi=pts[j-1],pts[j]
 fraction=0 if lo['work']==hi['work']else(target-lo['work'])/(hi['work']-lo['work'])
 def bound(a,b):return dict(low=a,estimate=a+(b-a)*fraction,high=b)if a is not None and b is not None and b>=a else None
 counters={k:bound(lo['row']['metrics'][k],hi['row']['metrics'][k])for k in lo['row']['metrics']}
 return {'target_work':target,'bracket_work':[lo['work'],hi['work']],
  'bracket_rows':[lo['row']['line'],hi['row']['line']],
  'bracket_width_pp':100*(hi['work']-lo['work'])/curve['population'],
  'cycles':bound(lo['row']['cycles'],hi['row']['cycles']),'counters':counters,
  'lo_row':lo['row'],'hi_row':hi['row'],'fraction':fraction}

def delta_bound(a,b):
 if a is None or b is None:return None
 # Negative central deltas reveal reset/unvalidated semantics, not zero events.
 if b['estimate']<a['estimate']:return None
 return {'low':max(0,b['low']-a['high']),'estimate':b['estimate']-a['estimate'],'high':b['high']-a['low']}

def segment(curve,p0,p1):
 target0=curve['population']*p0/100;target1=curve['population']*p1/100
 a,b=anchor(curve,target0),anchor(curve,target1)
 out={'kernel_ordinal':curve['ordinal'],'start_percent':p0,'end_percent':p1,'work':target1-target0}
 if a is None or b is None:return dict(out,status='PENDING_OR_MISSING_BOUNDARY',metrics=None)
 cycles=delta_bound(a['cycles'],b['cycles'])
 if cycles is None or cycles['estimate']<=0:return dict(out,status='INVALID_CYCLE_INTERVAL',metrics=None)
 metrics={k:delta_bound(a['counters'][k],b['counters'][k])for k in a['counters']}
 cpi={k:v/out['work']for k,v in cycles.items()}
 out.update(status='SAMPLED_COMPLETE',cycles=cycles,cpi=cpi,IPC_estimate=out['work']/cycles['estimate'],
  boundary_brackets=[{k:z[k]for k in ['target_work','bracket_work','bracket_rows','bracket_width_pp']}for z in [a,b]],
  coarse=(cycles['high']-cycles['low'])/cycles['estimate']>.20,
  metrics=metrics,unvalidated_or_reset_metrics=[k for k,v in metrics.items()if v is None])
 # Exact enclosure of actual sample interval; no interpolated per-SM participation.
 lo,hi=a['lo_row'],b['hi_row']
 smdiff=[y-x for x,y in zip(lo['retired_warp_per_sm'],hi['retired_warp_per_sm'])]
 out['retirement_participating_SMs_enclosing_samples']=sum(v>0 for v in smdiff)if all(v>=0 for v in smdiff)else None
 mc=[y-x for x,y in zip(lo['dram_per_mc'],hi['dram_per_mc'])]
 out['DRAM_MC_peak_over_mean_enclosing_samples']=max(mc)/statistics.mean(mc)if mc and min(mc)>=0 and sum(mc)>0 else None
 return out

def ratio_bounds(n,d):
 if not n or not d or d['estimate']<=0:return None
 return {'low':n['low']/d['high']if d['high']>0 else None,'estimate':n['estimate']/d['estimate'],
  'high':n['high']/d['low']if d['low']>0 else None}

def compare_cases(cases):
 result=[]
 for program in APP_INFO:
  subset={x['cell']+'_'+x['profile']:x for x in cases if x['program']==program and not x.get('error')}
  pairs=[('CH_P0','CH_PQ'),('DH_P0','DH_PQ'),('CH_P0','CH_PS'),('DH_P0','DH_PS'),('CH_P0','DH_P0'),('CH_PQ','DH_PQ'),('CH_PS','DH_PS')]
  for left,right in pairs:
   for ordinal in [1,2]:
    for p0,p1 in list(zip(BINS,BINS[1:]))+[(0,100)]:
     o={'program':program,'kernel_ordinal':ordinal,'start_percent':p0,'end_percent':p1,'left':left,'right':right,'definition':'left CPI / right CPI; >1 means right uses fewer core cycles at same retired work'}
     if left not in subset or right not in subset:result.append(dict(o,status='CASE_UNAVAILABLE'));continue
     if subset[left]['input_digest']!=subset[right]['input_digest']:raise ValueError('INPUT_IDENTITY_MISMATCH')
     def get(case):return next(s for s in case['segments']+case.get('whole_kernel_segments',[])if s['kernel_ordinal']==ordinal and s['start_percent']==p0 and s['end_percent']==p1)
     a,b=get(subset[left]),get(subset[right])
     if a['metrics']is None or b['metrics']is None:result.append(dict(o,status='PENDING_COVERAGE'));continue
     r=ratio_bounds(a['cpi'],b['cpi'])
     bounded=r['low']is not None and r['high']is not None
     verdict=('RIGHT_FEWER_CYCLES'if r['low']>1 else 'LEFT_FEWER_CYCLES'if r['high']<1 else 'UNRESOLVED_AT_SAMPLE_PRECISION')if bounded else 'UNBOUNDED_SAMPLE_PRECISION'
     metrics={}
     for k in ['dram_read_atoms','l2_fifo_full_events','l2_read_miss','l2_read_reservation_fail']:
      metrics[k]={'left':a['metrics'][k],'right':b['metrics'][k]}
     result.append(dict(o,status='PROVISIONAL_SAMPLED_COMPARISON',cycle_ratio=r,verdict=verdict,coarse=a['coarse']or b['coarse'],metrics=metrics,
      source_rows={'left':a['boundary_brackets'],'right':b['boundary_brackets']}))
 return result

def configs(spec):
 options={};evidence=[]
 for entry in spec['configs']:
  p=Path(entry['path']);b=p.read_bytes()
  if digest(b)!=entry['sha256']:raise ValueError('FROZEN_CONFIG_SHA_CHANGED:'+str(p))
  evidence.append(entry)
  for line in b.decode().splitlines():
   parts=line.split('#',1)[0].split()
   if len(parts)>=2 and parts[0].startswith('-'):options[parts[0]]=' '.join(parts[1:])
 return options,evidence

def process_state(path):
 if not path.exists():return {'live':False,'reason':'NO_PID_RECEIPT'}
 identity=readj(path);pid=identity['pid'];p=Path('/proc')/str(pid)
 try:
  fields=(p/'stat').read_text().rsplit(')',1)[1].split()
  matches=int(fields[19])==identity['start_ticks']
  return {'live':matches and fields[0]not in ['Z','X'],'pid':pid,'start_ticks':identity['start_ticks'],'generation_matches':matches}
 except (FileNotFoundError,ProcessLookupError):return {'live':False,'pid':pid,'start_ticks':identity['start_ticks'],'reason':'PROCESS_EXITED'}

def source_map(program,binding):
 filename,semantics,expected_sha=APP_INFO[program];p=Path(APPS)/program/filename;b=p.read_bytes()
 if digest(b)!=expected_sha:raise ValueError('APP_SOURCE_CHANGED:'+str(p))
 ks=[]
 for q,info in zip(binding['qualification']['rows'],semantics):
  lo,hi,operation,lane_stride,loop_stride=info
  # Small trace header read only. Historical full-body SHA remains explicitly historical.
  with open(q['path'],'rb')as f:header=f.read(3072).decode(errors='replace').split('#BEGIN_TB')[0]
  stream=re.search(r'-cuda stream id\s*=\s*(\d+)',header)
  if stream is None or int(stream.group(1))!=0:raise ValueError('UNPROVEN_SINGLE_STREAM_KERNEL_ORDER')
  ks.append({'ordinal':q['ordinal'],'kernel':q['kernel'],'active_thread_instructions':q['active_thread_instructions'],
   'complete_ctas':q['complete_ctas'],'complete_warps':q['complete_warps'],'trace_path':q['path'],'qualification_trace_sha256':q['sha256'],
   'trace_header':header[:1900],'source_lines':[lo,hi],'operation':operation,'lane_matrix_stride_bytes':lane_stride,
   'inner_loop_matrix_stride_bytes':loop_stride,'mapping_status':'SOURCE_SEMANTICS_AND_KERNEL_IDENTITY; NOT_DEBUG_LINE_PROOF',
   'global_reference_histogram':q['global_reference_histogram']})
 return {'program':program,'source_path':str(p),'source_sha256':expected_sha,'size':4096,'element_bytes':4,
  'input_digest':binding['input_digest'],'capture_scope':binding['qualification']['capture_complete_native_input'],
  'numerical_correctness':binding['qualification']['native_numerical_correctness'],'kernels':ks,
  'source_excerpt':'\n'.join(f'{i+1}: {line}'for i,line in enumerate(b.decode().splitlines())if any(lo<=i+1<=hi for lo,hi,*_ in semantics))}

def collect(root):
 root=Path(root);scope_bytes=(root/'control/SCOPE.json').read_bytes();scope=json.loads(scope_bytes)
 maps={};cases=[];config_profiles={};build=readj(root/'control/BUILD_PROFILE.json')
 for pt in scope['points']:
  case={k:pt[k]for k in ['program','cell','profile','cohort','input_digest']}
  try:
   specpath=root/'control/specs'/(pt['cohort']+'.json');sb=specpath.read_bytes();spec=json.loads(sb)
   intent=readj(root/'control/qualification_ledger'/(pt['cohort']+'.INTENT.json'))
   if digest(sb)!=intent['spec_sha256']:raise ValueError('SPEC_INTENT_HASH_MISMATCH')
   if spec['core_commit']!=build['core_commit']or spec['framework_commit']!=build['framework_commit']:raise ValueError('MODEL_SOURCE_MISMATCH')
   bp=Path(spec['input_binding_path']);bb=bp.read_bytes()
   if digest(bb)!=spec['input_binding_sha256']:raise ValueError('INPUT_BINDING_HASH_MISMATCH')
   binding=json.loads(bb)
   if binding['input_digest']!=pt['input_digest']:raise ValueError('WRONG_INPUT_BINDING')
   if pt['program']not in maps:maps[pt['program']]=source_map(pt['program'],binding)
   kernels=maps[pt['program']]['kernels']
   if sum(k['active_thread_instructions']for k in kernels)!=pt['expected']['instructions']:raise ValueError('INPUT_POPULATION_MISMATCH')
   options,config_files=configs(spec);profile=pt['cell']+'_'+pt['profile'];config_profiles[profile]={'options':options,'files':config_files}
   atom=int(options['-gpgpu_dram_burst_length'])*int(options['-gpgpu_dram_buswidth'])*int(options['-gpgpu_n_mem_per_ctrlr'])
   result=root/'DTC/run/results'/intent['uuid'];path=result/'perf_counter.csv.gz';data=path.read_bytes();rows,parse=parse_perf(data)
   curves=kernel_curves(rows,kernels)
   segments=[segment(curve,a,b)for curve in curves for a,b in zip(BINS,BINS[1:])]
   intervals=[]
   for curve in curves:
    for a,b in zip(curve['points'],curve['points'][1:]):
     dw=b['work']-a['work'];dc=b['row']['cycles']-a['row']['cycles']
     dm={k:b['row']['metrics'][k]-a['row']['metrics'][k]if a['row']['metrics'][k]is not None and b['row']['metrics'][k]is not None and b['row']['metrics'][k]>=a['row']['metrics'][k]else None for k in a['row']['metrics']}
     intervals.append({'kernel_ordinal':curve['ordinal'],'start_work':a['work'],'end_work':b['work'],
      'start_percent':100*a['work']/curve['population'],'end_percent':100*b['work']/curve['population'],
      'rows':[a['row']['line'],b['row']['line']],'cycles':dc,'IPC':dw/dc if dc>0 else None,'metrics':dm})
   progress=None;progress_evidence=None;pp=result/'progress.jsonl.gz'
   if pp.exists():
    pb=pp.read_bytes();pr,pm=inflate_live(pb);pl=pr.splitlines()
    progress=json.loads(pl[-1])if pl else None
    progress_evidence={'path':str(pp),'read_bytes':len(pb),'sha256_of_read_prefix':digest(pb),**pm}
   donepath=root/'control/qualification_ledger'/(pt['cohort']+'.DONE.json');done=readj(donepath)if donepath.exists()else None
   rp=root/'analysis'/(pt['cohort']+'.RESULT.json');strict=readj(rp)if rp.exists()else None
   live=process_state(result/'NATIVE_SIMULATOR_PID_AND_MAPS.json')
   wall_rate=None
   if len(rows)>=2:
    last=rows[-1];start=min(rows,key=lambda r:abs(r['wall_ms']-(last['wall_ms']-600000)))
    if last['wall_ms']>start['wall_ms']:wall_rate=(last['instructions']-start['instructions'])/((last['wall_ms']-start['wall_ms'])/1000)
   case.update(uuid=intent['uuid'],spec_sha256=digest(sb),input_binding_path=str(bp),input_binding_sha256=digest(bb),
    performance_scope='PROVISIONAL_NEW_DOWNSTREAM18_ONLY',acceptance='PENDING'if strict is None else strict.get('state','UNKNOWN_RESULT_SCHEMA'),
    DONE=done is not None,strict_result_path=str(rp)if strict else None,process=live,progress=progress,progress_evidence=progress_evidence,
    host_recent_active_instructions_per_second=wall_rate,perf_source={'path':str(path),'read_bytes':len(data),'sha256_of_read_prefix':digest(data),**parse},
    DRAM_atom_bytes=atom,subpartitions=len(rows[-1]['fifo_per_sp'])if rows else None,
    samples=rows,intervals=intervals,segments=segments,whole_kernel_segments=[segment(curve,0,100)for curve in curves],
    kernels=[{k:v for k,v in curve.items()if k!='points'}|{'observed_work':curve['points'][-1]['work']if curve['points']else 0}for curve in curves])
  except Exception as e:case.update(error=type(e).__name__+': '+str(e),acceptance='ANALYSIS_UNAVAILABLE',segments=[])
  cases.append(case)
 comparisons=compare_cases(cases)
 source_records=[]
 for p,lo,hi in SOURCE_EXCERPTS:
  b=Path(p).read_bytes();source_records.append({'path':p,'sha256':digest(b),'start_line':lo,'end_line':hi,
   'excerpt':'\n'.join(f'{i+1}: {l}'for i,l in enumerate(b.decode().splitlines())if lo<=i+1<=hi)})
 return {'schema':SCHEMA,'observed_UTC':now(),'root':str(root),'scope_sha256':digest(scope_bytes),
  'freeze_manifest_sha256':digest((root/'control/FREEZE_MANIFEST.json').read_bytes()),
  'core_commit':build['core_commit'],'framework_commit':build['framework_commit'],'binary_sha256':build['binary_sha256'],
  'core_library_sha256':build['core_library_sha256'],'new_model_starts':0,'controller_or_model_changes':0,
  'bins_percent':BINS,'source_maps':maps,'counter_source':source_records,'missing':MISSING,'config_profiles':config_profiles,
  'cases':cases,'comparisons':comparisons,'summary':{'cases':len(cases),'analysis_errors':sum(bool(c.get('error'))for c in cases),
   'live':sum(c.get('process',{}).get('live',False)for c in cases),'DONE':sum(c.get('DONE',False)for c in cases),
   'accepted_states':{state:sum(c['acceptance']==state for c in cases)for state in sorted({c['acceptance']for c in cases})},
   'sampled_complete_segments':sum(s['status']=='SAMPLED_COMPLETE'for c in cases for s in c['segments']),
   'total_segments':len(cases)*2*(len(BINS)-1),
   'paired_available':sum(c['status']=='PROVISIONAL_SAMPLED_COMPARISON'for c in comparisons),'paired_total':len(comparisons)}}

def report(data):
 lines=['DTC downstream18 分段观察报告',data['observed_UTC'],'',
  '这是当前固定 Core/Framework 的只读周期观察，不是 accepted 全程性能结果。',
  '输入范围仍为已声明 trace；源码语义映射不晋升 whole-application 正确性或捕获完整性。','',
  json.dumps(data['summary'],ensure_ascii=False),'',
  '方法：按 kernel 精确动态人口划分；0/5/25/50/75/95/100% 为完成 active-thread instructions 的前沿。',
  '使用真实快照夹住每个前沿；线性插值仅作图示估计，另保留 cycles/计数器单调边界。',
  '不能把前沿百分比解释为所有 warp 的同一循环迭代。快段采样过粗时会显示不确定。',
  'kernel 末尾使用最终计数器行；跨 kernel 从该行建立基线。没有基线时保留缺失。',
  '单位：cycles 为 core cycles；DRAM atom 字节数由实际有序配置计算；FIFO-full 为子分区-周期事件。',
  'FIFO-full / (子分区数 × core cycles) 只是按核心周期归一化的事件密度，并非 DRAM 调度队列等待时间。',
  'L2 HIT/MISS/SECTOR_MISS/RESERVATION_FAIL 原样分列，不凭未经证明的互斥性拼出 miss rate。',
  '段内流量按事件发生时间统计，可能包括先前工作发出的未完成请求；不等于严格请求 cohort。','',
  '当前已观察到的具体情况：']
 first_slow=[c for c in data['comparisons']if c['status']=='PROVISIONAL_SAMPLED_COMPARISON'and c['start_percent']==0 and c['end_percent']==5 and c['kernel_ordinal']==(2 if c['program']=='BICG'else 1)]
 pq=[c for c in first_slow if c['right'].endswith('_PQ')and c['left'].endswith('_P0')]
 ps=[c for c in first_slow if c['right'].endswith('_PS')and c['left'].endswith('_P0')]
 for label,items in [('PQ',pq),('PS',ps)]:
  if items:
   estimates=[c['cycle_ratio']['estimate']for c in items]
   lines.append(f"慢 kernel 的 0–5% 工作段已有 {len(items)}/6 个 {label} 配对，P0/{label} 周期比值插值估计范围 {min(estimates):.4f}–{max(estimates):.4f}。")
   if label=='PQ':
    zero=sum(c['metrics']['l2_fifo_full_events']['right']is not None and c['metrics']['l2_fifo_full_events']['right']['high']==0 and c['metrics']['l2_fifo_full_events']['left']['low']>0 for c in items)
    lines.append(f"其中 {zero} 个配对的 PQ 入口 FIFO-full 事件在该采样边界内为零，而 P0 大于零；性能判断仍按下列周期比值范围，不能用事件消失直接推出加速。")
   else:
    lines.append(f"其中 {sum(c['verdict']=='RIGHT_FEWER_CYCLES'for c in items)} 个配对在保守采样边界下仍确认 PS 使用更少核心周期。这是早段敏感性，不能外推完整应用加速或唯一瓶颈。")
 lines+=['','已有可比较段（0–100% 为整 kernel，其余为预设分段）：']
 for c in data['comparisons']:
  if c['status']!='PROVISIONAL_SAMPLED_COMPARISON':continue
  r=c['cycle_ratio'];hi='unbounded'if r['high']is None else f"{r['high']:.5f}"
  lines.append(f"{c['program']} K{c['kernel_ordinal']} {c['start_percent']}-{c['end_percent']}% {c['left']}/{c['right']}: {r['estimate']:.5f} [{r['low']:.5f}, {hi}], {c['verdict']}, coarse={c['coarse']}")
 lines+=['','事实、关联和未解问题：',
  '事实层只使用以上快照、源码定义和区间边界。当前未完成段不补值，不借用旧 accepted 性能。',
  '若 PQ FIFO-full 降低但同工作前沿 cycles 区间仍重叠，只能说入口背压减少、性能改善尚未被当前精度确认。',
  '若 PS 段内 core cycles 明显减少，说明该配置对 DRAM 时间域速度敏感；不能单独区分带宽、排队、bank/row 或返回路径。',
  'DRAM 流量、L2 miss 和 SM 退休参与度与性能变化可以关联；没有请求 cohort 和队列积分就不能断言因果。','',
  '明确缺失：']
 lines += [m['metric']+': '+m['status']+'; '+m['consequence']for m in data['missing']]
 lines += ['','最小后续观测方案（仅设计，未实现、未编译、未启动新实验）：',
  '1. 优先输出每个 DRAM 调度器累计 mrq_latency_sum / mrq_count、请求注入和返回数、等待队列长度 cycle integral/max、服务 busy cycles；标清 core/DRAM 时间域。复用既有 tot_mrq_latency/tot_mrq_num，在安全采样出口追加只读字段。',
  '2. 若仍无法解释 DH 劣势，再输出各 SM DTC PIB/OO occupancy integral/full cycles、Tag replacement/bank arbitration、lower issue/response、completion service 累计数；复用现有观测计数，缺失才添加纯观察计数。',
  '3. 只有源码循环位置仍是关键疑点时，为少量 kernel/CTA/warp 记录 PC/迭代前沿；CTA/warp 进度分布不能压成一个伪精确 j。',
  '验证：新观测身份；默认关闭；独立工作树；CPU fixture 验证累计数/重置/边界；对同配置开关观测验证 cycles、instructions、CTA、最终统计完全一致；真实模拟验证须另行批准。',
  '本轮18点运行期间不注入观测、不改采样频率、不挂接调试器、不截断输入。','']
 return '\n'.join(lines)

def render(data,template):
 payload=json.dumps(data,ensure_ascii=False,separators=(',',':'),allow_nan=False).replace('<','\\u003c')
 return template.replace('__PAYLOAD__',payload)

def save(data,out,template,immutable=False):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 dumpj(out/'latest.json',data);atomic(out/'dashboard.html',render(data,template));atomic(out/'REPORT.txt',report(data))
 dumpj(out/'SOURCE_MAP.json',{'core_commit':data['core_commit'],'framework_commit':data['framework_commit'],
  'maps':data['source_maps'],'counter_source':data['counter_source'],'missing':data['missing']})
 if immutable:
  stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ');p=out/'snapshots'/stamp
  p.mkdir(parents=True,exist_ok=False)
  for name in ['latest.json','dashboard.html','REPORT.txt','SOURCE_MAP.json']:
   atomic(p/name,(out/name).read_bytes())
  dumpj(p/'MANIFEST.json',{'observed_UTC':data['observed_UTC'],'files':{f.name:digest(f.read_bytes())for f in p.iterdir()if f.is_file()}})
 return dict(data['summary'],observed_UTC=data['observed_UTC'],output=str(out))

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--root',default=DEFAULT_ROOT);parser.add_argument('--output',default=DEFAULT_OUTPUT)
 parser.add_argument('--watch',action='store_true');parser.add_argument('--interval',type=int,default=300);parser.add_argument('--max-hours',type=float,default=36)
 args=parser.parse_args();root=Path(args.root).resolve();out=Path(args.output).resolve()
 # No output in or above production. Only designated separate analysis destination.
 if out==root or root in out.parents or out in root.parents:raise ValueError('OUTPUT_OVERLAPS_PRODUCTION')
 if 'segmentation'not in out.name:raise ValueError('OUTPUT_MUST_BE_EXPLICIT_SEGMENTATION_DIRECTORY')
 template=Path(__file__).with_name('dashboard.template.html').read_text(encoding='utf-8')
 start=time.monotonic();last_snapshot=-3601;iteration=0
 if args.watch:
  try:os.nice(15)
  except (AttributeError,PermissionError):pass
 while True:
  try:
   data=collect(root);elapsed=time.monotonic()-start
   terminal=all(c.get('DONE')and c['acceptance']!='PENDING'for c in data['cases'])
   status=save(data,out,template,immutable=iteration==0 or elapsed-last_snapshot>=3600 or terminal)
   if iteration==0 or elapsed-last_snapshot>=3600:last_snapshot=elapsed
   dumpj(out/'SIDECAR_STATUS.json',dict(status,pid=os.getpid(),iteration=iteration,started_UTC=(dt.datetime.now(dt.timezone.utc)-dt.timedelta(seconds=elapsed)).isoformat(),
    state='ALL_TERMINAL'if terminal else 'OBSERVING',interval_seconds=args.interval,max_hours=args.max_hours,model_starts=0))
   print(json.dumps(status,ensure_ascii=False),flush=True)
   if terminal:
    dumpj(out/'FINAL_OBSERVATION.json',dict(status,strict_states=data['summary']['accepted_states'],analysis_errors=data['summary']['analysis_errors'],all_terminal=True));break
  except Exception as e:
   dumpj(out/'SIDECAR_LAST_ERROR.json',{'UTC':now(),'error':type(e).__name__+': '+str(e),'production_changes':0})
   if not args.watch:raise
  iteration+=1
  if not args.watch:break
  if time.monotonic()-start>=args.max_hours*3600:
   dumpj(out/'SIDECAR_TIME_LIMIT.json',{'UTC':now(),'state':'ANALYSIS_WATCH_LIMIT','model_action':'NONE'});break
  time.sleep(args.interval)

if __name__=='__main__':main()
