#!/usr/bin/env python3
"""Bounded read-only accepted-raw overlap extraction; never grants science authority.
Usage: python3 -B joint_attribution.py --inputs INPUTS.json --output-dir PRIVATE_DIR
Manifest: {"cases":[{"label":...,"mode":"S"|"F_MINUS_T"|"F", "raw_path":...,"raw_sha256":...,"spec_path":...,"spec_sha256":...,"accepted_point_path":...,"accepted_point_sha256":...,"dram_command_analysis_path":optional,"dram_command_analysis_sha256":optional}]}
No model/controller import. Input identity fails closed; source-dependent missing stats stay UNKNOWN.
"""
import argparse,collections,csv,hashlib,importlib.util,json,pathlib,re,sys
sys.dont_write_bytecode=True
P=pathlib.Path;MAX_RAW=192<<20
COUNTERS='ENTER EXIT ALLOC REENTER SECTOR_ADD MUTATE TICK_PEAK EVENT_PEAK NEW_UNIQUE NEW_HEAD RAW_FAIL_HEAD NEW_COMMIT MERGE REQUESTER INC_END UNIQUE_SECTOR SECTOR_TRANSITION CLOSED_NEW CLOSED_RE CLOSED_LEFT RIGHT LEFT SUM_NEW SUM_RE SUM_LEFT SUM_RIGHT MAX_NEW MAX_RE MAX_LEFT RO_ADMIT RO_RETIRE RO_TIME RO_LOWER_TIME RO_RESPONSE_ONLY_TIME RO_WAITER_ADDS RO_MAX_WAITERS RO_REQUIRED_ADD RO_ISSUED_ADD RO_READY_ADD NEW_PENDING_SECTORS_SUM NEW_CAN_DETACH_SUM NEW_AT_2 NEW_AT_3 NEW_AT_4 NEW_AT_8 NEW_AT_12 NEW_AT_15 NEW_AT_16 NEW_WITH_PENDING NEW_WITH_ELIGIBLE WAIT_COUNT WAIT_SUM WAIT_MAX PROD_TAGFAIL RO_INITIAL_READY'.split()
STAGES='L1_ACCESS L1_MISS L1_MERGE L1_MISSQ_BLOCK L1_SEND ICNT_INJECT_ACCEPT ICNT_INJECT_DENY L2_INGRESS FRONTEND_HEAD FRONTEND_DENY FRONTEND_COMMIT TVD_EARLY LOWER_QUEUE_BLOCK L2_MISSQ_BLOCK DRAM_ACCEPT DRAM_RETURN RO_READY_EVENT RESPONSE_ACCEPT DRAM_SERVICE'.split()
WINDOW_COUNTERS='ENTER EXIT ALLOC SECTOR_ADD NEW_UNIQUE NEW_HEAD RAW_FAIL_HEAD MERGE RO_ADMIT RO_READY_ADD REENTER NEW_WITH_PENDING NEW_WITH_ELIGIBLE WAIT_SUM WAIT_COUNT'.split()
FUNNEL='raw_reservation_fail pressure_eligible pressure_live_ro_no_eligible pressure_no_live_ro pressure_prod_probe_reached pressure_prod_probe_not_reached pressure_relief_not_consulted pressure_frontend_admitted pressure_frontend_denied raw_tag_fail_commit relieve_calls relieve_eligible_selected relieve_no_eligible detach_calls detach_success detach_false trigger_accepted_after_detach trigger_denied_after_detach commit_accepted commit_denied'.split()
def need(v,m):
 if not v:raise ValueError(m)
def digest(p):
 h=hashlib.sha256()
 with P(p).open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(P(p).read_text())
def pinned(p,h):need(digest(p)==h,'SHA mismatch '+str(p));return read(p)
def atom(v):
 if re.fullmatch(r'-?\d+',v):return int(v)
 try:return float(v)if re.fullmatch(r'-?\d+\.\d+',v)else v
 except ValueError:return v
def kv(line):return {k:atom(v)for x in line.rstrip().split('|')[1:]if '='in x for k,v in[x.split('=',1)]}
def vec(v):return [int(x)for x in str(v).split(',')]
def mapped(v,names):
 a=vec(v);need(len(a)==len(names),'counter vector schema mismatch');return dict(zip(names,a))
def last_by(rows,keys):
 d={}
 for x in rows:d[tuple(x[k]for k in keys)]=x
 return list(d.values())
def rowsum(rows,key):return sum(int(x[key])for x in rows)
def hist_sum(rows,key):
 a=[0]*len(vec(rows[0][key])) if rows else []
 for r in rows:
  b=vec(r[key]);need(len(a)==len(b),'hist length');a=[x+y for x,y in zip(a,b)]
 return a
def extract(case):
 mode=case['mode'];need(mode in ['S','F_MINUS_T','F'],'exact mode');raw=P(case['raw_path']);need(raw.stat().st_size<=MAX_RAW,'bounded raw');need(digest(raw)==case['raw_sha256'],'raw SHA drift')
 s=pinned(case['spec_path'],case['spec_sha256']);point=pinned(case['accepted_point_path'],case['accepted_point_sha256']);need(point['raw_sha256']==case['raw_sha256']and point['source_identity']==s['source_identity'],'accepted source/raw join');need(point.get('qualified_by')=='EP-MAIN'and 'ACCEPTED'in point['status']and 'PENDING'not in point['status'],'actual Main accepted input required')
 need(point.get('native_spec_sha256',point.get('spec_sha256'))==case['spec_sha256'],'accepted spec join')
 opts=s['expected_effective_options'];need(len(opts)==282,'full282');clock=opts['-gpgpu_clock_domains'];need(opts['-dram_latency']in['100','200'],'only exact100to200 analysis background');need(opts['-gpgpu_simple_dram_model']=='0','detailed DRAM only');channels=int(opts['-gpgpu_n_mem']);subparts=int(opts['-gpgpu_n_sub_partition_per_mchannel']);slices=channels*subparts
 sets=s['geometry']['sets'];ways=s['geometry']['ways'];need((slices,sets,ways)==(64,32,8),'exact matched geometry')
 expected={'S':('1','0','0','0','0'),'F_MINUS_T':('2','1','1','0','1'),'F':('2','1','1','1','1')}[mode]
 fields=['-gpgpu_ep_l2_ft_mode','-gpgpu_ep_l2_tvd_clean','-gpgpu_ep_l2_tvd_dirty','-gpgpu_ep_l2_ro_tag_detach','-gpgpu_ep_l2_ro_line_mshr_bypass'];need(tuple(opts[k]for k in fields)==expected,'formal mode mismatch')
 meta=[];terminal=[];inc=[];stage=[];end=[];ws=[];wstage=[];b0=[];dram=[];b0app=[];dramapp=[];r4={};r5={};records=collections.Counter()
 with raw.open(errors='strict')as f:
  for line in f:
   if line.startswith('EPL2LIFEV1|'):
    kind=line.split('|',2)[1];x=kv(line);records['LIFE_'+kind]+=1
    {'META':meta,'SET':terminal,'INCARNATION':inc,'STAGE':stage,'END':end,'WINDOW_SET':ws,'WINDOW_STAGE':wstage}.get(kind,[]).append(x)
   elif line.startswith('EPL2B0V1|scope=window'):b0.append(kv(line))
   elif line.startswith('EPL2DRAMV1|scope=window'):dram.append(kv(line))
   elif line.startswith('EPL2B0V1|scope=application'):b0app.append(kv(line))
   elif line.startswith('EPL2DRAMV1|scope=application'):dramapp.append(kv(line))
   elif line.startswith(('EPL2DETACH_DIAG_V1|','EPL2TAGPRESSUREV1|')):
    x=json.loads(line.split('|',1)[1]);
    if x['record']!='SLICE':continue
    target=r4 if line.startswith('EPL2DETACH')else r5;target[x['slice']]=x
 need(set(r4)==set(range(slices))and set(r5)==set(range(slices)),'final64 R4/R5 unavailable');need(all(not x.get('overflow_invalid')and not x.get('output_invalid')and x.get('closure_ok')for x in [*r4.values(),*r5.values()]),'invalid observer source')
 # Select final snapshot per slice/channel, not duplicate process-print sums.
 b0app=last_by(b0app,['slice']);dramapp=last_by(dramapp,['channel']);need(len(b0app)==slices and len(dramapp)==channels,'application hardware coverage')
 life_complete=len(meta)==slices and len(end)==slices and len(terminal)==sets*slices and len(inc)==sets*slices and len(stage)==slices and all(x['closed']==1 and x['invalid']==0 for x in meta+end)and all(x['invalid']==0 for x in terminal+inc+stage)
 if mode!='S':need(life_complete,'F/FMT complete LIFE terminal required')
 if life_complete:
  for rows in [meta,end,stage]:need({x['slice']for x in rows}==set(range(slices)),'final LIFE exact64 slice coverage')
  need({(x['slice'],x['set'])for x in inc}=={(sl,st)for sl in range(slices)for st in range(sets)},'incarnation exactset coverage')
 warnings=[]
 if not life_complete:warnings.append('S_LIFE_TERMINAL_NOT_INSTRUMENTED: existing complete windows only; no full-run lifetime/unique histogram fabricated')
 sums=collections.Counter();unique=[];heads=[];newhist=[];rehist=[];area=[];complete_checks={}
 if life_complete:
  need({(x['slice'],x['set'])for x in terminal}=={(sl,st)for sl in range(slices)for st in range(sets)},'LIFE terminal exactset coverage')
  for x in terminal:
   c=mapped(x['c'],COUNTERS);a=vec(x['area']);nh=vec(x['new_hist']);rh=vec(x['re_hist']);need(len(a)>=ways+1 and not any(a[ways+1:]),'inactive area axis')
   need(sum(i*v for i,v in enumerate(a))==sum(c[k]for k in ['SUM_NEW','SUM_RE','SUM_LEFT','SUM_RIGHT']),'duration-area invariant')
   need(sum(nh)==c['CLOSED_NEW']and sum(rh)==c['CLOSED_RE'],'episode hist population')
   for k,v in c.items():
    if k in ['TICK_PEAK','EVENT_PEAK','MAX_NEW','MAX_RE','MAX_LEFT','RO_MAX_WAITERS','WAIT_MAX']:sums[k]=max(sums[k],v)
    else:sums[k]+=v
  area=hist_sum(terminal,'area');newhist=hist_sum(terminal,'new_hist');rehist=hist_sum(terminal,'re_hist');unique=hist_sum(inc,'unique_reserved');heads=hist_sum(inc,'head_reserved')
  need(sum(unique)==sums['NEW_UNIQUE']and sum(heads)==sums['NEW_HEAD'],'NEW histogram population');need(not any(unique[ways+1:])and not any(heads[ways+1:]),'inactive NEW axis')
  right=sum(int(x['ro_right_count'])for x in stage);right_time=sum(int(x['ro_right_time'])for x in stage);population_complete=sums['RO_ADMIT']==sums['RO_RETIRE'] and right==0 and right_time==0
  complete_checks={'duration_area_equality':True,'hist_counts_match_episode_counts':True,'NEW_hist_matches_unique_and_repeated_heads':True,'RO_all_admits_retired_without_right_censor':population_complete,'ro_right_count':right,'ro_right_time':right_time}
 else:population_complete=False
 N=sums['RO_RETIRE'];ro={'status':'N/A_MODE_S'if mode=='S'else 'COMPLETE_POPULATION'if population_complete else'UNKNOWN_CENSORED_POPULATION','unit':'L2_tick per RO transaction','admit':None if mode=='S'else sums['RO_ADMIT'],'retire':None if mode=='S'else N,'RO_TIME_sum':None if mode=='S'else sums['RO_TIME'],'RO_LOWER_TIME_sum':None if mode=='S'else sums['RO_LOWER_TIME'],'RO_RESPONSE_ONLY_TIME_sum':None if mode=='S'else sums['RO_RESPONSE_ONLY_TIME']}
 for name in ['RO_TIME','RO_LOWER_TIME','RO_RESPONSE_ONLY_TIME']:ro[name+'_mean_same_retired_population']=sums[name]/N if mode!='S'and population_complete and N else None
 ro['RO_LOWER_TIME_interpretation']='transaction state exposure while any issued sector is not ready; includes queues, fixed delay, DRAM, return path, and response processing; not pure DRAM latency or sum of per-packet latency'
 # Boundary join: map L2 tick intervals through actual WINDOW_STAGE GPU/core endpoints.
 smap={(x['slice'],x['begin'],x['end']):x for x in wstage};joins=[];coverage=[];window_sets=[]
 need(len(smap)==len(wstage),'unique actual stage intervals')
 for x in ws:
  need(x['invalid']==0,'invalid LIFE window');key=(x['slice'],x['begin'],x['end']);st=smap.get(key);need(st is not None,'missing matching WINDOW_STAGE by actual L2 begin/end')
  need(sum(vec(x['area']))==x['end']-x['begin'],'window set area coverage');c=mapped(x['c'],WINDOW_COUNTERS)
  window_sets.append({'label':case['label'],'slice':x['slice'],'set':x['set'],'begin_L2_tick':x['begin'],'end_L2_tick':x['end'],'begin_core_cycle':st['begin_gpu'],'end_core_cycle':st['end_gpu'],'reserved_area_R0_to_R8':','.join(str(v)for v in vec(x['area'])[:ways+1]),**c})
 for st in wstage:
  sl=st['slice'];lo=st['begin_gpu'];hi=st['end_gpu'];need(hi>=lo,'core boundary order')
  for family,rows,idkey,lowkey,highkey,objid in [('B0',b0,'slice','start_cycle','completion_cycle',sl),('C7E',dram,'channel','window_start_cycle','window_end_cycle',sl//subparts)]:
   matches=[]
   for q in rows:
    if q[idkey]!=objid:continue
    overlap=min(hi,q[highkey])-max(lo,q[lowkey])
    if overlap>0:matches.append((q,overlap))
   intervals=sorted((max(lo,q[lowkey]),min(hi,q[highkey]))for q,_ in matches);covered=0;last=lo
   for a,b in intervals:
    if b>last:covered+=b-max(a,last);last=b
   coverage.append({'label':case['label'],'slice':sl,'channel':sl//subparts,'life_begin_L2_tick':st['begin'],'life_end_L2_tick':st['end'],'life_begin_core_cycle':lo,'life_end_core_cycle':hi,'other_family':family,'actual_core_overlap_coverage':covered,'life_core_interval_uncovered_by_other_printed_windows':hi-lo-covered,'uncovered_semantics':'not recoverable by prorating application aggregates','other_clock_denominator':'L2_tick samples'if family=='B0'else'DRAM_domain_ticks'})
   for q,overlap in matches:
    joins.append({'label':case['label'],'slice':sl,'channel':sl//subparts,'life_begin_L2_tick':st['begin'],'life_end_L2_tick':st['end'],'life_begin_core_cycle':lo,'life_end_core_cycle':hi,'other_family':family,'other_begin_core_cycle':q[lowkey],'other_end_core_cycle':q[highkey],'core_overlap_cycles':overlap,'exact_same_boundaries':lo==q[lowkey]and hi==q[highkey],'other_sample_denominator':q['samples']if family=='B0'else q['dram_cycles'],'other_denominator_unit':'L2_tick samples'if family=='B0'else'DRAM_domain_ticks','counts_prorated':False,'causal_Tag_linkage':'NOT_MEASURED'})
 # R5 sparse rows are already actual joints. Never multiply separate margins.
 rawhead=collections.Counter();raweligible=0
 for x in r5.values():
  need(x['assoc']==ways and x['sets']==sets,'R5 geometry');
  for rawstatus,reserved,count in x['histograms']['heads_raw_reserved']:rawhead[(rawstatus,reserved)]+=count
  for rawstatus,reserved,eligible,count in x['histograms']['heads_raw_reserved_eligible']:
   if rawstatus==3 and eligible>0:raweligible+=count # cache RESERVATION_FAIL enum3 checked against source.
 funnel={k:sum(x['counters'][k]for x in r4.values())for k in FUNNEL}
 repeated_raw=[{'raw_status_enum':a,'reserved_ways':b,'repeated_frontend_head_observations':n}for(a,b),n in sorted(rawhead.items())]
 per_set_csv=[]
 if life_complete:
  for x in terminal:
   c=mapped(x['c'],COUNTERS);ir=next(y for y in inc if y['slice']==x['slice']and y['set']==x['set']);per_set_csv.append({'label':case['label'],'slice':x['slice'],'set':x['set'],**c,'new_unique_R0_R8':','.join(str(v)for v in vec(ir['unique_reserved'])[:ways+1]),'repeated_newhead_R0_R8':','.join(str(v)for v in vec(ir['head_reserved'])[:ways+1]),'NEW_lifetime_loghist33':x['new_hist'],'RE_lifetime_loghist33':x['re_hist'],'reserved_area_R0_R8':','.join(str(v)for v in vec(x['area'])[:ways+1])})
 b0_csv=[{'label':case['label'],**x}for x in b0];dram_csv=[{'label':case['label'],**x,'successful_bytes_semantics':'fixed_latency_queue_ingress_needs_return_vs_no_return_not_RD_WR_command_service'}for x in dram]
 result={'schema':'L2_DRAM_TAG_JOINT_ATTRIBUTION_READONLY_V1','label':case['label'],'mode':mode,'source_identity':s['source_identity'],'input_trace_composite_sha256':s['input_trace_composite_sha256'],'raw_path':str(raw),'raw_sha256':case['raw_sha256'],'native_spec_sha256':case['spec_sha256'],'clock_domains_MHz':clock,'dram_latency_config_core_cycles':opts['-dram_latency'],'scientific_acceptance_from_input_point_only':point['status'],'new_application_started_by_analyzer':False,'warnings':warnings,'RO_population':ro,'LIFE_terminal_status':'COMPLETE'if life_complete else'NOT_INSTRUMENTED','LIFE_invariants':complete_checks,'LIFE_totals':dict(sums)if life_complete else None,'NEW_unique_R0_R8':unique[:ways+1]if life_complete else None,'repeated_NEW_head_R0_R8':heads[:ways+1]if life_complete else None,'NEW_complete_lifetime_hist33':newhist if life_complete else None,'RE_complete_lifetime_hist33':rehist if life_complete else None,'RE_zero_lifetime_episodes':rehist[0]if life_complete else None,'NEW_zero_lifetime_episodes':newhist[0]if life_complete else None,'histogram_definition':'bin0 zero; bin1 one; bin2 2..3; ...bin32 >=2^31; exact SUM_NEW/RE supplied separately, no midpoint means','reserved_area_R0_R8':area[:ways+1]if life_complete else None,'full_or_partial_windows':{'WINDOW_SET':len(ws),'WINDOW_STAGE':len(wstage),'B0':len(b0),'C7E':len(dram),'boundary_overlap_links':len(joins),'coverage_rows':len(coverage),'windows_with_uncovered_B0_or_C7E_tails':sum(x['life_core_interval_uncovered_by_other_printed_windows']>0 for x in coverage),'sum_counts_across_overlaps_permitted':False},'true_trigger_funnel_same_R4_population':funnel,'R5_RAWFAIL_AND_eligible_actual_joint_head_observations':raweligible,'R5_repeated_head_joint_raw_reserved':repeated_raw,'m_dram_latency_queue_actual_enqueue_ready_sched_residency_hist':'NOT_INSTRUMENTED','m_dram_latency_queue_candidate_not_executed':'Only ready_cycle and req retained; packet status-change time overwritten; no perpacket exported actual enqueue→DRAMpush timestamp/duration. Configured delay is a deadline, not measured residence.','C7E_interpretation':'Window boundaries core cycles; channel metrics are shared by two slices and must not be counted twice through join links; samples/occupancy rates use DRAM-domain ticks; successful_read denotes requires-return packet, successful_write no-return writeback at FIFO pop into fixed-latency queue, not RD/WR column commands.','overlap_claim_boundary':'LowerFIFO/Credit/Scheduler/ReturnQ observations have distinct populations; may overlap or be sequential. Never add as lost cycles, prorate partial windows, infer per-Tag causality, or multiply independent margins.','B_true_DRAM_command_analysis':None}
 if case.get('dram_command_analysis_path'):
  d=pinned(case['dram_command_analysis_path'],case['dram_command_analysis_sha256']);need(d.get('raw_sha256')==case['raw_sha256'],'B command analysis raw join');result['B_true_DRAM_command_analysis']={'path':case['dram_command_analysis_path'],'sha256':case['dram_command_analysis_sha256'],'status':d.get('status'),'schema':d.get('schema'),'interpretation':'External pinned B actual-column-command extraction; its own population/denominator applies, not C7E ingress bytes'}
 else:
  bp=P('/root/data/ep_l2_matched_baseline_t_dram_latency_20261027_v1/agent_b/dram_terminal_extract.py');bh='93d6140bc630f6e61f6e625b0613f926946bede4244102a9fca8640536d0617a';need(digest(bp)==bh,'B exact pure column extractor drift')
  need(s['source_identity']['core_source_commit']=='c67b332db703f09571ba6628222c77d71440e141','B c67 command semantics require explicit new source audit')
  bm=importlib.util.spec_from_file_location('joint_readonly_true_dram_commands',bp);bb=importlib.util.module_from_spec(bm);bm.loader.exec_module(bb);dr=bb.extract(raw,int(point['cycles']),opts);need(dr['raw_sha256']==case['raw_sha256'],'B column raw join')
  result['B_true_DRAM_command_analysis']={'extractor_path':str(bp),'extractor_sha256':bh,'complete_result':dr,'interpretation':'Exact final32 detailed DRAM actual column commands; counter populations/denominators distinct from C7E ingress bytes'}
 result['blocking_observations_by_slice_nonadditive']={str(x['slice']):{k:v for k,v in x.items()if any(t in k for t in ['lowerq','l2_to_dram_full','credit_block','scheduler_full','returnq_block','dram_to_l2_full','dram_return_eligible','dram_issue_eligible'])}for x in b0app}
 result['blocking_counter_interpretation']='Raw per-slice observations retain original field populations: lowerFIFO fullness, credit-denied candidate attempts, scheduler observed/causal blocks, return eligibility/ReturnQ blockage. Causes may overlap or be sequential; no sum interpreted as total lost cycles. Channel C7E rows are separate and shared by two slices.'
 return result,{'B0_APPLICATION':[{'label':case['label'],**x}for x in b0app],'C7E_APPLICATION':[{'label':case['label'],**x}for x in dramapp],'LIFE_SET':per_set_csv,'LIFE_WINDOW_SET':window_sets,'WINDOW_BOUNDARY_JOINS':joins,'WINDOW_COVERAGE':coverage,'B0_WINDOWS':b0_csv,'C7E_WINDOWS':dram_csv}
def write_csv(path,rows):
 if not rows:return
 fields=list(dict.fromkeys(k for r in rows for k in r))
 with P(path).open('x',newline='')as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def run(manifest,out):
 need(set(manifest)=={'cases'}and 1<=len(manifest['cases'])<=6,'bounded input manifest');out=P(out);out.mkdir(parents=True,exist_ok=False);results=[];tables=collections.defaultdict(list)
 for case in manifest['cases']:
  result,rows=extract(case);results.append(result)
  for name,items in rows.items():tables[name].extend(items)
 for name,rows in tables.items():write_csv(out/(name+'.csv'),rows)
 result={'schema':'MULTI_CASE_L2_DRAM_TAG_JOINT_ATTRIBUTION_V1','analyzer_sha256':digest(__file__),'source_or_application_qualification_granted':False,'results':results,'cross_binary_performance_pair_automatically_claimed':False}
 (out/'JOINT_ATTRIBUTION.json').write_text(json.dumps(result,indent=2)+'\n');write_csv(out/'SUMMARY.csv',[{'label':r['label'],'mode':r['mode'],'latency_config':r['dram_latency_config_core_cycles'],'LIFE_terminal':r['LIFE_terminal_status'],**{k:v for k,v in r['RO_population'].items()if not isinstance(v,(dict,list))},**r['true_trigger_funnel_same_R4_population']}for r in results]);return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--inputs',required=True);p.add_argument('--output-dir',required=True);a=p.parse_args();r=run(read(a.inputs),a.output_dir);print(json.dumps({'output_dir':a.output_dir,'cases':len(r['results']),'labels':[x['label']for x in r['results']]}))
