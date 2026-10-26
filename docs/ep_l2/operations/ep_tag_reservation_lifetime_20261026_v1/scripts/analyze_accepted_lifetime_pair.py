#!/usr/bin/env python3
"""Bounded read-only derivative of Main's already accepted NI analysis; no launch/acceptance."""
import sys
sys.dont_write_bytecode=True
import argparse,collections,csv,hashlib,json,math,pathlib,resource,time
P=pathlib.Path
ROOT=P('/root/data/ep_tag_reservation_lifetime_20261026_v1')
GOAL='EP_L2_TAG_RESERVATION_LIFETIME_CAUSAL_V1'
HEADER='d88efa5012f1bd24c0b55be42504c1b8e3727bcabdf46a2c96385ee61082b8e1'
TOOLS={'accepted_pair_pipeline.py':'7bca05de662a1346da9b890b2608ebd72fa34375a5385c58bf5b770299d9a65f','lifetime_parser.py':'7b3f119b019a93dda216f994a4b805a6c118f25619b3cb41b747d42773937abe','wire_contract.json':'ff13db1b2ff841e1f6358a0bdb0f9d93f68e6e932ec815adca2efff22de14bd2','new_source_acceptance.py':'8221eb9d4ea6872be39ff020534312dfd134dce036a5f2fc0feb5a7c3c46dcad'}
IDENTITY={'core_source_commit':'11c02df1034112013523429894f1f931323adbef','framework_source_commit':'9dd1ee57a83d83b56b7874bc7c716185ab52c8f7','vendor_pybind11_commit':'f90c430c3a1ce8f08c09942a5a1c3a797bb2295b','binary_sha256':'8d55f19bbe74c72e5da688f0ede6c2de1c3aa13040015475f23c9c6c521b9bef','archive_sha256':'685b497b50328deff4b96741c9a770b4b37e5d4bb2c8a1b5db90558b90be73c4'}
SOURCEQ='8ed4d41852f6e26bc9c1ced140f4dc2ecc6f287f3c4df5d0e5cc6e883dfe2814'
ROLES={r:'EP_NATIVE_VECTOR_TAG_LIFETIME_'+r+'_20261026_V2' for r in ['OFF','ON']}
class NotReady(ValueError):pass
def need(x,msg):
 if not x:raise NotReady(msg)
def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(P(p).read_bytes(),parse_constant=lambda x:(_ for _ in ()).throw(NotReady('nonfinite JSON')))
def ref(x):
 need(isinstance(x,dict) and set(x)=={'path','sha256'},'exact file ref required');p=P(x['path']);need(p.is_absolute() and p.is_file() and sha(p)==x['sha256'],'file ref absent/SHA drift '+str(p));return p
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def ratio(a,b):return a/b if b else None
def nums(x):return [int(y)for y in x.split(',')]
def identity_row(row):return int(row['slice']),int(row['set'])
def window_key(row):return int(row['slice']),int(row['begin']),int(row['end'])
def fields(line):
 out={}
 for t in line.rstrip('\n').split('|')[2:]:
  k,v=t.split('=',1);need(k not in out,'duplicate wire key');out[k]=v
 return out

def qualify(directory):
 # Check owner acceptance and complete NI before even hashing/reading the ON raw.
 d=P(directory).resolve();index=d/'ANALYSIS_SOURCE_INDEX.json';need(index.is_file(),'accepted analysis source index absent; no live raw fallback');ix=read(index)
 need(ix['schema']=='EP_L2_LIFETIME_ANALYSIS_SOURCE_INDEX_V1' and ix['status']=='ANALYSIS_FROM_REFERENCED_MAIN_ACCEPTED_NONINTERFERING_PAIR' and ix['goal']==GOAL,'accepted NI analysis index required')
 need(ix['scientific_acceptance_granted_by_C'] is False and ix['actual_pair_provenance_required'] is True and ix['source_identity']==IDENTITY,'index authority/source boundary');need(ix['wire_header_sha256']==HEADER,'header drift')
 for n,h in TOOLS.items():need(sha(ROOT/'tools_v2'/n)==h,'reviewed frozen tool changed '+n)
 need(ref(ix['pipeline'])==ROOT/'tools_v2/accepted_pair_pipeline.py','unexpected pipeline path');need(ref(ix['parser'])==ROOT/'tools_v2/lifetime_parser.py','unexpected parser path');need(ref(ix['wire_contract'])==ROOT/'tools_v2/wire_contract.json','unexpected contract path')
 points={};raws={};bundles={}
 need(set(ix['source_cases'])=={'OFF','ON'},'exact OFFON endpoints')
 for role in ['OFF','ON']:
  source=ix['source_cases'][role];p=ref(source['accepted_receipt']);point=read(p)
  need(point['status']=='EP_L2_TAG_RESERVATION_LIFETIME_APPLICATION_ACCEPTED' and point['qualified_by']=='EP-MAIN' and point['goal']==GOAL,'Main accepted endpoint required')
  need(point['cohort']==ROLES[role] and point['source_identity']==IDENTITY and point['source_qualification_sha256']==SOURCEQ and point['observer_header_sha256']==HEADER,'exact V2 endpoint identity')
  need(point['observer_enabled'] is (role=='ON') and point['instructions']==56000000 and point['CTA']==15625 and point['slices']==64 and point['kernel_count']==1 and point['hardware_drained'] is True,'full app scope/role')
  need(point['clock_domains_MHz']=='1132.0:1132.0:1132.0:850.0' and point['raw_sha256']==source['raw']['sha256'],'clock/raw join');points[role]=point
 ni=read(ref(ix['noninterference']));need(ni['status']=='PASS_COMPLETE_OFF_ON_NONINTERFERENCE' and ni['goal']==GOAL and ni['source_identity']==IDENTITY and ni['source_qualification_sha256']==SOURCEQ,'complete exact NI required')
 need(all(ni['checks'].get(k)is True for k in ['cycles','instructions','CTA','slices','drain','requests_responses','cache_queue_behavior','observer_switch_only']),'NI check missing')
 need(points['ON']['noninterference']=='PASS' and points['ON']['noninterference_sha256']==ix['noninterference']['sha256'],'accepted ON NI hash binding');need(ni['raw_sha256']=={r:ix['source_cases'][r]['raw']['sha256']for r in ROLES},'NI raw pair');need(ni['normalizer_code']['sha256']==TOOLS['new_source_acceptance.py'] and ref(ni['normalizer_code'])==ROOT/'tools_v2/new_source_acceptance.py','normalizer pin')
 need(points['OFF']['cycles']==points['ON']['cycles'] and points['OFF']['uuid']!=points['ON']['uuid'],'pair cycles/UUID mismatch')
 snapshots={r:read(ref(ix['normalized_snapshots'][r]))for r in ROLES}
 for r,s in snapshots.items():need(s['raw_sha256']==points[r]['raw_sha256'] and s['source_identity']==IDENTITY and s['normalizer_sha256']==TOOLS['new_source_acceptance.py'],'snapshot binding')
 need(canon(snapshots['OFF']['metrics'])==canon(snapshots['ON']['metrics']),'normalized scoped semantics differ');del snapshots
 manifest=read(ref(ix['manifest']));need(manifest['schema']=='EP_L2_LIFETIME_ANALYSIS_INPUT_V1' and manifest['status']=='ACCEPTED_OFF_ON_NONINTERFERING_INPUTS' and manifest['goal']==GOAL,'analysis manifest status')
 for r in ROLES:
  raws[r]=ref(ix['source_cases'][r]['raw']);need(manifest['cases'][r]['raw']==ix['source_cases'][r]['raw'] and manifest['cases'][r]['accepted_receipt']==ix['source_cases'][r]['accepted_receipt'],'manifest refs changed')
  bundle=raws[r].parent/'VALIDATED_APPLICATION_BUNDLE.json';need(sha(bundle)==points[r]['validation_bundle_sha256'],'accepted bundle drift');bundles[r]=bundle
 validation=read(ref(ix['observer_wire_validation']));need(validation['parser_status']=='VALID_OBSERVER_WIRE_ONLY' and validation['slices']==64 and validation['sets_per_slice']==64 and validation['summary_rows']==4096 and validation['synthetic_fixture'] is False and validation['scientific_acceptance_granted'] is False,'actual strict64 wire qualification')
 need(validation['raw_sha256']==points['ON']['raw_sha256'] and validation['header_sha256']==HEADER and validation['parser_sha256']==TOOLS['lifetime_parser.py'],'wire identity')
 need(set(ix['outputs'])=={'PER_SET_OCCUPANCY_AND_LIFETIME.csv','SECTOR_MERGE_AND_REQUEST_OVERLAP.csv'},'exact4096 outputs')
 files={}
 for name,x in ix['outputs'].items():need(x['rows']==4096,'output row qualification');files[name]=ref({'path':x['path'],'sha256':x['sha256']});need(files[name]==d/name,'output outside analyzed dir')
 windows=ref(ix['temporal_csv']);need(windows==d/'STRICT_OBSERVER_ON/PER_SET_TEMPORAL_WINDOWS.csv','window path scope')
 return d,index,ix,points,raws,bundles,files,windows,validation

def parse_summary(directory,k,onraw):
 summary=directory/'STRICT_OBSERVER_ON/PER_SET_RESERVATION_SUMMARY.csv';need(summary.is_file(),'strict fullcounter summary absent');sets={}
 with summary.open(newline='')as f:
  for row in csv.DictReader(f):
   key=identity_row(row);need(key not in sets and 0<=key[0]<64 and 0<=key[1]<64,'duplicate/invalid summary key');sets[key]={n:int(v)for n,v in row.items()if v!='' and n not in ['unit','coverage','mean_reserved']}
 need(len(sets)==4096,'strict summary population');setseen=set();incseen=set();stage={};meta={};offlife=False
 # The fullcounter spool has no standalone SHA in index: independently bind every
 # SET counter/area/histogram and INC field to the already accepted closed ON raw.
 with onraw.open()as stream:
  for line in stream:
   if not line.startswith('EPL2LIFEV1|'):continue
   kind=line.split('|',2)[1];x=fields(line);sid=int(x['slice'])
   if kind=='META':meta[sid]=x
   elif kind=='SET':
    key=sid,int(x['set']);need(key not in setseen,'duplicate raw SET');setseen.add(key);v=sets[key]
    for n,value in zip(k['counters'],nums(x['c'])):need(v[n]==value,'summary/raw counter mismatch '+n)
    for prefix,name in [('area_R','area'),('new_hist_b','new_hist'),('re_hist_b','re_hist')]:
     for i,value in enumerate(nums(x[name])):need(v[prefix+str(i)]==value,'summary/raw array mismatch')
   elif kind=='INCARNATION':
    key=sid,int(x['set']);need(key not in incseen,'duplicate raw INC');incseen.add(key);v=sets[key]
    for n,value in zip(k['incarnation_stats'],nums(x['stats'])):need(v[n]==value,'summary/raw incarnation mismatch '+n)
    for prefix,name in [('head_reserved_R','head_reserved'),('unique_reserved_R','unique_reserved')]:
     for i,value in enumerate(nums(x[name])):need(v[prefix+str(i)]==value,'summary/raw requesterjoint mismatch')
   elif kind=='STAGE':need(sid not in stage,'duplicate raw STAGE');stage[sid]=x
 need(len(setseen)==len(incseen)==4096 and set(meta)==set(stage)==set(range(64)),'raw SET/INC/META/STAGE population')
 return summary,sets,meta,stage

def analyze_rows(sets,k,files,points):
 for name,path in files.items():
  seen=set()
  with path.open(newline='')as f:
   for row in csv.DictReader(f):
    key=identity_row(row);need(key not in seen and key in sets,'final4096 duplicate/domain');seen.add(key);base=sets[key]
    need(row['raw_sha256']==points['ON']['raw_sha256'],'CSV raw identity')
    for field,text in row.items():
     if field in base and text!='':need(int(text)==base[field],'compact/fullcounter mismatch '+field)
  need(len(seen)==4096,'compact4096 row count')
 sums={n:sum(v[n]for v in sets.values())for n in k['counters']};areas=[sum(v['area_R'+str(i)]for v in sets.values())for i in range(17)];weighted=sum(i*n for i,n in enumerate(areas));per_slice=[];peaks=collections.Counter();mean_bins=collections.Counter();empty=0
 for sid in range(64):
  vs=[sets[sid,i]for i in range(64)];ends={v['end']for v in vs};need(len(ends)==1,'slice epoch duration mismatch');duration=next(iter(ends));area=sum(sum(i*v['area_R'+str(i)]for i in range(17))for v in vs)
  per_slice.append({'slice':sid,'epoch_L2_ticks':duration,'weighted_reserved_area_way_ticks':area,'mean_total_reserved_ways_in_slice':ratio(area,duration),'max_per_set_event_peak':max(v['EVENT_PEAK']for v in vs),'NEW_UNIQUE':sum(v['NEW_UNIQUE']for v in vs),'NEW_HEAD':sum(v['NEW_HEAD']for v in vs),'PROD_TAGFAIL':sum(v['PROD_TAGFAIL']for v in vs)})
 local_complete=0
 for key,v in sets.items():
  duration=v['end']-v['begin'];area=sum(i*v['area_R'+str(i)]for i in range(17));need(sum(v['area_R'+str(i)]for i in range(17))==duration,'set area partition');need(area==sum(v[n]for n in ['SUM_NEW','SUM_RE','SUM_LEFT','SUM_RIGHT']),'censored exposure conservation');need(v['LEFT']+v['ENTER']-v['EXIT']==v['RIGHT'],'episode balance');need(sum(v['unique_reserved_R'+str(i)]for i in range(17))==v['NEW_UNIQUE'] and sum(v['head_reserved_R'+str(i)]for i in range(17))==v['NEW_HEAD'],'new requester population');need(sum(v['unique_reserved_R'+str(i)]for i in range(1,17))==v['NEW_WITH_PENDING'],'unique pending joint')
  peaks[v['EVENT_PEAK']]+=1;mean_bins[str(int(area/duration*10)/10 if duration else 0)]+=1
  if v['LEFT']==v['RIGHT']==0 and v['ENTER']>0:local_complete+=1
  if not area:empty+=1
 hist={kind:[sum(v[prefix+str(i)]for v in sets.values())for i in range(33)]for kind,prefix in [('NEW','new_hist_b'),('RE','re_hist_b')]};need(sum(hist['NEW'])==sums['CLOSED_NEW'] and sum(hist['RE'])==sums['CLOSED_RE'],'closed lifetime histogram population')
 life={'completed_NEW':{'episodes':sums['CLOSED_NEW'],'sum_L2_ticks':sums['SUM_NEW'],'mean_L2_ticks':ratio(sums['SUM_NEW'],sums['CLOSED_NEW']),'hist33':hist['NEW'],'max_L2_ticks':max(v['MAX_NEW']for v in sets.values())},'completed_RE':{'episodes':sums['CLOSED_RE'],'sum_L2_ticks':sums['SUM_RE'],'mean_L2_ticks':ratio(sums['SUM_RE'],sums['CLOSED_RE']),'hist33':hist['RE'],'max_L2_ticks':max(v['MAX_RE']for v in sets.values())},'closed_left_censored':{'episodes':sums['CLOSED_LEFT'],'observed_overlap_L2_ticks':sums['SUM_LEFT'],'mean_observed_overlap_L2_ticks':ratio(sums['SUM_LEFT'],sums['CLOSED_LEFT'])},'right_censored':{'episodes':sums['RIGHT'],'observed_overlap_L2_ticks':sums['SUM_RIGHT'],'NEW_RE_split':'NOT_EMITTED_UNKNOWN'},'births':{'all':sums['ENTER'],'NEW':sums['ENTER']-sums['REENTER'],'RE':sums['REENTER'],'carry_at_begin':sums['LEFT']},'exact_area_conservation':True,'local_complete_population_set_count':local_complete,'Little_Law_scope':'No fullGPU inference. Only each set finite-epoch same-population identity when LEFT=RIGHT=0; censored overlap remains separate.'}
 unique=[sum(v['unique_reserved_R'+str(i)]for v in sets.values())for i in range(17)];heads=[sum(v['head_reserved_R'+str(i)]for v in sets.values())for i in range(17)]
 joint={'NEW_UNIQUE':sums['NEW_UNIQUE'],'NEW_HEAD_repeated_observations':sums['NEW_HEAD'],'NEW_COMMIT':sums['NEW_COMMIT'],'RAW_FAIL_HEAD':sums['RAW_FAIL_HEAD'],'PROD_TAGFAIL':sums['PROD_TAGFAIL'],'unique_newTag_reserved_joint17':unique,'repeated_head_reserved_joint17':heads,'NEW_WITH_PENDING':sums['NEW_WITH_PENDING'],'NEW_WITH_ELIGIBLE':sums['NEW_WITH_ELIGIBLE'],'unique_pending_fraction':ratio(sums['NEW_WITH_PENDING'],sums['NEW_UNIQUE']),'unique_structural_eligible_fraction':ratio(sums['NEW_WITH_ELIGIBLE'],sums['NEW_UNIQUE']),'NEW_CAN_DETACH_SUM_structural_count':sums['NEW_CAN_DETACH_SUM'],'request_wait':{'completions':sums['WAIT_COUNT'],'sum_L2_ticks':sums['WAIT_SUM'],'mean_completed_L2_ticks':ratio(sums['WAIT_SUM'],sums['WAIT_COUNT']),'max_L2_ticks':max(v['WAIT_MAX']for v in sets.values())},'boundary':'915784 old raw MISS heads never used as unique denominator; structural eligibility is not a production can_detach call.'}
 inc={n:sum(v[n]for v in sets.values())for n in k['incarnation_stats']if not n.endswith('_max')};inc.update({n:max(v[n]for v in sets.values())for n in k['incarnation_stats']if n.endswith('_max')});inc.update(observed_requesters=sums['REQUESTER'],merge_markers=sums['MERGE'],unique_requested_sectors=sums['UNIQUE_SECTOR'],sector_add=sums['SECTOR_ADD'],merges_per_observed_requester=ratio(sums['MERGE'],sums['REQUESTER']),not_DRAM_request_savings=True)
 return sums,life,joint,inc,{'area_R0_to_16_set_ticks':areas,'weighted_reserved_way_ticks':weighted,'set_event_peak_histogram':dict(sorted(peaks.items())),'mean_reserved_per_set_tenths_floor_histogram':dict(sorted(mean_bins.items())),'zero_reserved_area_sets':empty,'per_slice':per_slice,'no_sum_of_per_set_maxima_claim':True}

def analyze_windows(path,sets,k,rawstage,meta):
 groups={};rows=0
 with path.open(newline='')as f:
  for row in csv.DictReader(f):
   key=window_key(row);sid,b,e=key;si=int(row['set']);need(0<=si<64 and e>b,'window domain');a=[int(row['area_R'+str(i)])for i in range(17)];need(sum(a)==e-b,'window area partition');st=tuple(int(row['stage_'+x])for x in k['stages']);anchor=(int(row['begin_gpu']),int(row['end_gpu']));g=groups.setdefault(key,{'sets':set(),'stage':st,'anchors':anchor,'area':[0]*17,'events':{x:0 for x in k['window_counters']}});need(si not in g['sets'] and g['stage']==st and g['anchors']==anchor,'duplicate windowset/inconsistent repeatedstage');g['sets'].add(si)
   need(int(row['reserved_end_pre_boundary'])==int(row['reserved_begin_pre_boundary'])+int(row['ENTER'])-int(row['EXIT']),'window carry');g['area']=[u+v for u,v in zip(g['area'],a)]
   for n in g['events']:g['events'][n]+=int(row[n])
   rows+=1
 result=[];stage_sums={sid:[0]*len(k['stages'])for sid in range(64)}
 for (sid,b,e),g in sorted(groups.items()):
  need(len(g['sets'])==64,'window set population');need(g['events']['RO_READY_ADD']==g['stage'][k['stages'].index('RO_READY_EVENT')],'window ROready stage');stage_sums[sid]=[a+b for a,b in zip(stage_sums[sid],g['stage'])]
  result.append({'slice':sid,'begin_L2_tick':b,'end_L2_tick':e,'begin_GPU_core_cycle':g['anchors'][0],'end_GPU_core_cycle':g['anchors'][1],'mean_total_reserved_ways_in_slice_window':sum(i*n for i,n in enumerate(g['area']))/(e-b),'area_R0_to_16_summed_over_sets':g['area'],'set_events':g['events'],'deduplicated_stage_counts':dict(zip(k['stages'],g['stage'])),'stage_rate_per_L2_tick':{n:v/(e-b)for n,v in zip(k['stages'],g['stage'])}})
 for sid,v in stage_sums.items():need(v==nums(rawstage[sid]['c']),'deduplicated windows/rawSTAGE totals')
 need(rows==64*len(groups) and len(groups)==sum((int(meta[s]['end'])+8191)//8192 for s in meta),'window record population')
 return {'per_set_window_rows':rows,'deduplicated_slice_window_rows':len(result),'stage_context_replication_factor':64,'dedup_key':['slice','begin_L2_tick','end_L2_tick'],'stage_units':k['stage_units'],'boundary':k['stage_unit_boundary'],'window_NEW_RE_histograms_and_RO_phase_durations':'NOT_EMITTED_UNKNOWN; no inferred reconstruction','rows':result}

def run(analysis_dir,output_dir):
 start=time.monotonic();d,index,ix,points,raws,bundles,files,window,validation=qualify(analysis_dir);k=read(ROOT/'tools_v2/wire_contract.json');index_before=sha(index);summary,sets,meta,rawstage=parse_summary(d,k,raws['ON']);summary_before=sha(summary);sums,life,joint,inc,occupancy=analyze_rows(sets,k,files,points);temporal=analyze_windows(window,sets,k,rawstage,meta)
 right_count=sum(int(x['ro_right_count'])for x in rawstage.values());right_time=sum(int(x['ro_right_time'])for x in rawstage.values());phase=sums['RO_LOWER_TIME']+sums['RO_RESPONSE_ONLY_TIME'];need(sums['RO_ADMIT']==sums['RO_RETIRE']+right_count and phase<=sums['RO_TIME']+right_time,'RO lifetime population');ro={n:sums[n]for n in ['RO_ADMIT','RO_RETIRE','RO_TIME','RO_LOWER_TIME','RO_RESPONSE_ONLY_TIME','RO_WAITER_ADDS','RO_REQUIRED_ADD','RO_ISSUED_ADD','RO_READY_ADD','RO_INITIAL_READY']};ro.update(max_RO_waiters=max(v['RO_MAX_WAITERS']for v in sets.values()),right_censored_count=right_count,right_censored_exposure_L2_ticks=right_time,mean_completed_RO_L2_ticks=ratio(sums['RO_TIME'],sums['RO_RETIRE']),other_or_preissue_RO_exposure_L2_ticks=sums['RO_TIME']+right_time-phase,phase_unit='RO owner exposure L2ticks, not wallstallcycles or packetcounts',lower_phase='issued-notreadysector exposure',response_only_phase='requiredsectorsready but ROstilllive exposure',not_Tag_reservation_lifetime=True)
 bundle=read(bundles['ON']);G=bundle['R5']['global_record'];H=G['histograms'];r5={}
 for code,label in [(2,'MISS_repeated_head'),(3,'RESERVATION_FAIL_repeated_head'),(4,'SECTOR_MISS_repeated_head')]:
  r5[label]={'observations':sum(x[-1]for x in H['heads_raw_reserved']if x[0]==code),'with_eligible':sum(x[-1]for x in H['heads_raw_reserved_eligible']if x[0]==code and x[2]>0),'with_reuse':sum(x[-1]for x in H['heads_raw_reserved_reasonmask']if x[0]==code and x[2]&4),'with_reuse_and_eligible_same_targetset':sum(x[-1]for x in H['heads_raw_reserved_reasonmask']if x[0]==code and x[2]&4 and x[2]&1)}
 del bundle
 out=P(output_dir).resolve();need(out.is_relative_to(ROOT/'agent_c') and not out.is_relative_to(d) and not out.exists(),'fresh agent_c derivative directory required');result={'status':'DERIVED_FROM_MAIN_ACCEPTED_NONINTERFERING_OFF_ON_ONLY_NOT_NEW_ACCEPTANCE','goal':GOAL,'source_identity':IDENTITY,'source_analysis_index':{'path':str(index),'sha256':sha(index)},'source_strict_summary':{'path':str(summary),'sha256':sha(summary),'all_SET_INC_fields_revalidated_against_accepted_ON_raw':True},'script':{'path':str(P(__file__).resolve()),'sha256':sha(__file__)},'actual_pair':{r:{'uuid':points[r]['uuid'],'raw_sha256':points[r]['raw_sha256'],'cycles':points[r]['cycles']}for r in ROLES},'full_set_rows':4096,'reservation_lifetimes':life,'per_set_population_and_occupancy':occupancy,'unique_NEW_and_same_set_joint':joint,'Tag_incarnation_sector_merge':inc,'RO_owner_lifetime_phases':ro,'R5_repeated_head_targetset_joint':r5,'slice_window':temporal,'wire_validation':validation,'claims':{'scientific_acceptance_granted':False,'new_model_starts':0,'authority_or_budget_mutations':0,'source_directory_writes':0,'no_fullGPU_LittleLaw_or_marginal_products':True,'only_same_slice_window_time_association_no_request_ancestry':True,'unemitted_distributions_remain_UNKNOWN':True},'elapsed_seconds':time.monotonic()-start,'max_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
 # Recheck closed inputs after bounded reads; never promote a changing spool/raw.
 need(sha(index)==index_before and sha(summary)==summary_before,'analysis index/summary changed during read')
 for r in ROLES:need(sha(raws[r])==points[r]['raw_sha256'],'accepted raw changed during derivative')
 for item in ix['outputs'].values():ref({'path':item['path'],'sha256':item['sha256']})
 ref(ix['temporal_csv'])
 # All checks finish before first output; source accepted analysis is never edited.
 out.mkdir(parents=True);(out/'DERIVED_LIFETIME_ANALYSIS.json').write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n')
 md='''# Accepted ON lifetime derivative\n\nThis is bounded offline analysis of Main\'s already accepted, noninterfering OFF/ON pair. It issues no new acceptance or launch authority.\n\n'''
 md+=f"Strict4096sets and {temporal['deduplicated_slice_window_rows']} unique slice/windows passed; windowstage counts were deduplicated from64set copies.\n\nNEW completed episodes={life['completed_NEW']['episodes']}, mean={life['completed_NEW']['mean_L2_ticks']} L2ticks; RE completed episodes={life['completed_RE']['episodes']}, mean={life['completed_RE']['mean_L2_ticks']} L2ticks. Closedleftcensored={life['closed_left_censored']['episodes']}, rightcensored={life['right_censored']['episodes']}. Censored exposure remains separate.\n\nUnique newTag offers={joint['NEW_UNIQUE']}; repeated newTag head observations={joint['NEW_HEAD_repeated_observations']}; productionTagFAIL={joint['PROD_TAGFAIL']}, observedrawFAILheads={joint['RAW_FAIL_HEAD']}. Direct uniqueNEW withpending={joint['NEW_WITH_PENDING']}, witheligible={joint['NEW_WITH_ELIGIBLE']}. No independent-marginal multiplication.\n\nRO admits/retires={ro['RO_ADMIT']}/{ro['RO_RETIRE']}, completedROtime={ro['RO_TIME']}, lowerexposure={ro['RO_LOWER_TIME']}, responseonlyexposure={ro['RO_RESPONSE_ONLY_TIME']} L2ticks. These are ROowner populations, distinct from Tagreservationepisodes. Incarnationmerges are not claimed as DRAMpacket savings.\n\nPer-kind per-window lifetime distributions/ROphase durations are not emitted and remain UNKNOWN. Temporalstage relations are same-slice/window associations with different packet/command/sector/retry units; no requestancestry, wholeGPU LittleLaw probability, exclusive causalshares or Tperformance attribution is inferred.\n"
 (out/'DERIVED_LIFETIME_ANALYSIS.md').write_text(md);return {'status':result['status'],'output_dir':str(out),'json_sha256':sha(out/'DERIVED_LIFETIME_ANALYSIS.json'),'markdown_sha256':sha(out/'DERIVED_LIFETIME_ANALYSIS.md'),'scientific_acceptance_granted':False}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--analysis-dir',required=True);p.add_argument('--output-dir',required=True);a=p.parse_args()
 resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
 try:print(json.dumps(run(a.analysis_dir,a.output_dir),sort_keys=True,indent=2))
 except (NotReady,OSError,ValueError,KeyError,TypeError)as e:print(json.dumps({'status':'HOLD_NO_DERIVED_ANALYSIS_PROMOTED','reason':str(e),'scientific_acceptance_granted':False}),file=sys.stderr);raise SystemExit(2)
