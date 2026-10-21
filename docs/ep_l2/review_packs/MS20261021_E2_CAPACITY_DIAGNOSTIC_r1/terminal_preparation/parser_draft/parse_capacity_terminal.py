"""New-runtime traditional-S capacity parser DRAFT; NOT native-qualified.

Only raw field decoders/17 wait-reason names are copied from the retained main61
parser. No old geometry parser, old qualifier or legacy validator is called.
CLI binds the original registered new Q by input_spec.json, with no registry
mutation or circular embedded Q hash. Exact new native replay is still required.
"""
import argparse,json,re,sys,hashlib
from pathlib import Path
# Resolve installed-original worktree by its canonical tool path, not cwd/raw.
TOOLS=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/util/ep_l2/mechanism_e')
sys.path.insert(0,str(TOOLS))
import capacity_validation as cv
from capacity_validation import require
SOURCE_MAPPING_CORE='add7893153175ec4552ddc5bf0e373da7e83c823'
SOURCE_MAPPING_FRAMEWORK='9dd1ee57a83d83b56b7874bc7c716185ab52c8f7'
LEGACY_DECODE_SOURCE_SHA256='f518aed003f2f70a4d84afc95c215773da2c14761315349b7600655a1e549c8e'

REASONS=('WB_DATA_SPACE','BANK_COMPATIBLE_LANDING','TAG_SET_PENDING','LINE_MSHR_FULL',
 'DESCRIPTOR_FULL','PER_LINE_CAP','WAD_FULL','SAME_ADDRESS_WB','PINNED_PAYLOAD',
 'FRONTEND_TRANSACTION','MISS_QUEUE_FULL','RESPONSE_QUEUE_FULL','DATA_SERVICE','COPY_PIPELINE',
 'ANY_FIRST_BLOCK_TO_ADMISSION','VICTIM_LOOKUP','READONLY_LOOKUP')

def numbers(parts):
    out={}
    for part in parts:
        key,value=part.split('=',1)
        require(key not in out,'duplicate terminal field: '+key)
        if key=='measurement':
            require(value=='DISABLED_NOT_OBSERVED','unreviewed measurement state')
            out[key]=value;continue
        out[key]=[int(n) for n in value.split(',')] if key=='hist_log2' else int(value)
        require(all(n>=0 for n in out[key]) if isinstance(out[key],list) else out[key]>=0,'negative source counter: '+key)
    return out

STRINGS={'diagnostic_profile','index_extension','name','coverage','ROP_storage','DRAM_ICNT_timing'}
RESOURCE_MAP={
 'Tag':('tag_slots','CONSERVATIVE_UPPER_BOUND','CONSERVATIVE_RESIDENT_IDENTITY_BOUND'),
 'resident':('resident_payload_slots','EXACT_EVENT_HIGHWATER','ALLOCATION_EVENTS'),
 'bypass':('bypass_payload_slots','SOURCE_PROVEN_NOT_APPLICABLE','S_NATIVE_NO_BYPASS_ALLOCATION'),
 'WB':('wb_payload_slots','EXACT_EVENT_HIGHWATER','ALLOCATION_EVENTS'),
 'payload':('payload_slots_total','CONSERVATIVE_UPPER_BOUND','SUM_OF_ROLE_EVENT_PEAK_UPPER_BOUND'),
 'WAD':('wad_entries','EXACT_EVENT_HIGHWATER','ALLOCATION_EVENTS'),
 'line_MSHR':('line_mshr_entries','EXACT_EVENT_HIGHWATER','ALLOCATION_EVENTS'),
 'descriptor':('descriptor_entries','EXACT_EVENT_HIGHWATER','ALLOCATION_EVENTS'),
 'per_address':('per_address_descriptors','EXACT_EVENT_HIGHWATER','ALLOCATION_EVENTS'),
 'MissQ':('miss_queue_entries','EXACT_EVENT_HIGHWATER','ENQUEUE_EVENTS_AND_CAPACITY_CHECKS'),
 'ready_responses':('ready_response_bound','CONSERVATIVE_UPPER_BOUND','ALL_LIVE_DESCRIPTORS_CONSERVATIVE_BOUND'),
 'ICNT_L2':('icnt_to_l2_queue','EXACT_EVENT_HIGHWATER','FIFO_EVENTS'),
 'L2_DRAM':('l2_to_dram_queue','EXACT_EVENT_HIGHWATER','FIFO_EVENTS'),
 'DRAM_L2':('dram_to_l2_queue','EXACT_EVENT_HIGHWATER','FIFO_EVENTS'),
 'L2_ICNT':('l2_to_icnt_queue','EXACT_EVENT_HIGHWATER','FIFO_EVENTS')}
CAP_FIELDS={'payload_slots_total':'payload','resident_payload_slots':'resident','bypass_payload_slots':'bypass',
 'wb_payload_slots':'wb','wad_entries':'wad','line_mshr_entries':'line_mshr','descriptor_entries':'descriptor',
 'per_address_descriptors':'per_address','miss_queue_entries':'missq','ready_response_bound':'ready_response_bound',
 'result_fifo_config_field':'result_fifo_field'}
EXEMPT=('response','fill','lower_wb','frontend','copy_read','copy_write')

def large_numbers(parts):
 out={}
 for part in parts:
  require('=' in part,'missing field separator');key,value=part.split('=',1)
  require(key not in out,'duplicate large-capacity field')
  if key in STRINGS:require(bool(value),'empty native literal');out[key]=value
  else:
   require(re.fullmatch(r'\d+',value) is not None,'invalid native capacity integer')
   out[key]=int(value)
 return out

def put(records,key,value):
 require(key not in records or records[key]==value,'conflicting same-clock native record')
 records[key]=value

def decode(raw):
 """Decode all snapshots, retaining exactly final cumulative-clock records."""
 state={'native':{},'final':{},'mechanism':{},'structure':{},'large':{},'resources':{},'unchanged':{},
        'requested_options':{},'launched_uids':set(),'completed_uids':set(),'normal':False,'snapshots':0}
 clock=None
 with Path(raw).open(errors='replace') as stream:
  for line in stream:
   require('** break due to reaching the maximum cycles' not in line,'native bounded cutoff is not a full application')
   state['normal']|='GPGPU-Sim: *** exit detected ***' in line
   m=re.fullmatch(r'gpu_tot_sim_(cycle|insn)\s*=\s*(\d+)\s*',line)
   if m:
    state['native'][m[1]]=int(m[2])
    if m[1]=='cycle':
     new=int(m[2]);require(clock is None or new>=clock,'native cumulative clock regressed')
     if clock!=new:
      for key in ('final','mechanism','structure','large','resources','unchanged'):state[key]={}
     clock=new;state['snapshots']+=1
   m=re.match(r'^\s*(-[A-Za-z0-9_:]+)\s+(.*?)\s*$',line)
   if m:
    option,value=m[1],m[2].rsplit(' # ',1)[0].strip()
    if option.startswith('-gpgpu_ep_l2_') or option in ('-gpgpu_cache:dl2','-gpgpu_cache:dl2_texture_only','-gpgpu_dram_partition_queues','-gpgpu_l2_rop_latency'):put(state['requested_options'],option,value)
   m=re.search(r'^launching kernel name: .* uid: (\d+) cuda_stream_id:',line)
   if m:
    uid=int(m[1]);require(uid not in state['launched_uids'],'duplicate native kernel launch UID');state['launched_uids'].add(uid)
   m=re.fullmatch(r'kernel_launch_uid\s*=\s*([0-9\s]*)',line)
   if m:state['completed_uids'].update(int(v) for v in m[1].split())
   if line.startswith(('EPL2FTV1|SUMMARY|','EPL2FTV1|TERMINAL|','EPL2B0V1|INVARIANT|')):
    require(clock is not None,'terminal record has no native clock');prefix,kind,*parts=line.strip().split('|');v=numbers(parts)
    if kind=='INVARIANT' and v['kernel_uid']!=18446744073709551615:continue
    put(state['final'],(kind,v['slice']),v)
   elif line.startswith(('EPL2MSV1|','EPL2MSV2|')):
    require(clock is not None,'observer record has no clock');prefix,kind,*parts=line.strip().split('|');v=numbers(parts)
    require(kind in ('OBSERVER','WAIT','LOCAL_DIAGNOSTIC'),'unknown native mechanism kind')
    reason=v.get('reason',-1);require((prefix=='EPL2MSV2')==(kind=='WAIT' and reason>=15),'wait reason namespace mismatch')
    put(state['mechanism'],(kind,v['slice'],reason),v)
   elif line.startswith('EPL2STRUCTV1|'):
    require(clock is not None,'structural record has no clock');prefix,kind,*parts=line.strip().split('|');v=numbers(parts)
    require(kind in ('BANK_PEAK','WB_QUOTA','CONFIG'),'unknown native structural kind');put(state['structure'],(kind,v['slice']),v)
   elif line.startswith('EPL2LARGEV1|'):
    require(clock is not None,'capacity record has no clock');prefix,kind,*parts=line.strip().split('|');v=large_numbers(parts)
    if kind=='CONFIG':put(state['large'],v['slice'],v)
    elif kind=='RESOURCE':
     require(v['name'] in RESOURCE_MAP,'unreviewed native capacity resource');put(state['resources'],(v['slice'],v['name']),v)
    elif kind=='UNCHANGED':put(state['unchanged'],v['slice'],v)
    else:require(False,'unreviewed native capacity record kind')
   elif line.startswith(('EPL2TVDV2|','EPL2TVDV3|','EPL2ROV1|','EPL2ROC1|')):
    require(False,'V/RO records are outside traditional-S capacity scope')
 require(state['normal'] and set(state['native'])=={'cycle','insn'} and min(state['native'].values())>0,'missing normal native complete counters')
 require(set(state['final'])=={(kind,s) for kind in ('SUMMARY','TERMINAL','INVARIANT') for s in range(64)},'missing exact64 final terminal scope')
 require(set(state['large'])==set(range(64)),'missing64 actual effective capacity configs')
 require(set(state['structure'])=={(kind,s) for kind in ('CONFIG','BANK_PEAK','WB_QUOTA') for s in range(64)},'missing64 actual structural configs/bank/quota')
 return state

def validate_requested(state,spec):
 expected=spec['profile_semantics']['effective_options'];actual=state['requested_options']
 scoped={k:v for k,v in expected.items() if k.startswith('-gpgpu_ep_l2_') or k in ('-gpgpu_cache:dl2','-gpgpu_cache:dl2_texture_only')}
 require(scoped and all(actual.get(k)==v for k,v in scoped.items()),'requested native option dump differs from exact whitelist')
 return actual

def actual_config(header,ft,struct,actual,expected):
 def opt(name):
  require(name in actual,'native requested option missing '+name);return int(actual[name])
 base={'native_tag_sets':header['sets'],'native_tag_ways':header['ways'],'native_line_bytes':header['line_bytes'],
  'copy_latch_bytes':struct['copy_latch_bytes'],'ft_mode':ft['mode'],'W':int(ft['mode']==2),
  'V':int(bool(opt('-gpgpu_ep_l2_tvd_clean') or opt('-gpgpu_ep_l2_tvd_dirty'))),
  'T':opt('-gpgpu_ep_l2_ro_tag_detach'),'M':opt('-gpgpu_ep_l2_ro_line_mshr_bypass'),
  'mq2':opt('-gpgpu_ep_l2_mq2'),'rg1':opt('-gpgpu_ep_l2_rg1'),'copy_free':header['copy_free'],
  'l2_data_free':header['data_free'],'hardware_P1_throughput_eligible':header['hardware_P1_throughput_eligible'],
  'bank_count':header['bank_count'],'bank_ops_per_physical_cycle':header['bank_ops']}
 optional={'native_max_tag_storage':'max_tag_storage','copy_latch_cycles':'copy_latch_cycles',
  'index_function':'index_function','index_extension':'index_extension','result_fifo_used_by_L2':'result_fifo_used_by_L2'}
 for key in set(expected)-set(base):
  require(key in optional,'unreviewed normalized native config field '+key);base[key]=header[optional[key]]
 require(base==expected,'actual effective native configuration differs from new qualification')
 return base

def off_fifo_capacity(name,actual,qualification):
 """OFF source/config interpretation plus new-archive native getter evidence.

 OFF emits no dynamic FIFO resource records in this source. Do not fabricate
 OFF highwater/refusal0; only actual requested four-field native config can be
 interpreted using independently qualified constructor/native getter evidence.
 """
 names=('icnt_to_l2_queue','l2_to_dram_queue','dram_to_l2_queue','l2_to_icnt_queue')
 require(name in names,'not a native local FIFO')
 value=actual.get('-gpgpu_dram_partition_queues');require(value is not None,'native OFF local FIFO requested config missing')
 fields=value.split(':');require(len(fields)==4 and all(re.fullmatch(r'\d+',x) for x in fields),'native local FIFO config malformed')
 capacity=int(fields[names.index(name)])
 review=qualification['capacity_diagnostic'].get('off_fifo_capacity_review',{})
 require(review.get('status')=='INDEPENDENTLY_REVIEWED' and
         review.get('requested_native_queue_config')==value and
         review.get('actual_new_archive_native_getter_capacities',{}).get(name)==capacity,
         'OFF FIFO identity needs exact config/source and new-archive native getter evidence')
 return capacity

def parse(raw,spec,qualification):
 scope=qualification['capacity_diagnostic']['validation_scope'];source=qualification['source_identity'];profile=spec['profile']
 cv.validate_scope(scope,source,qualification['supported_profiles'])
 require(source['core_source_commit']==SOURCE_MAPPING_CORE and source['framework_source_commit']==SOURCE_MAPPING_FRAMEWORK,'source mapping requires formal exact revision review')
 require(profile in (cv.OFF,cv.ON) and spec['selection_id']==scope['input_selection_id'],'wrong exact scoped profile/input')
 require(spec['profile_semantics']==qualification['supported_profiles'][profile],'profile differs from new E qualification')
 require(all(spec['identity'][k]==source[k] for k in cv.SOURCE_KEYS),'different new producing runtime')
 state=decode(raw);actual=validate_requested(state,spec);native=state['native'];p=scope['profiles'][profile];master=p['master'];caps=p['capacities'];enabled=int(actual['-gpgpu_ep_l2_ms_observer'])
 require(enabled in (0,1),'observer mode is not explicit')
 expected={(kind,sid,-1) for kind in ('OBSERVER','LOCAL_DIAGNOSTIC') for sid in range(64)}
 if enabled:expected|={('WAIT',sid,r) for sid in range(64) for r in range(len(REASONS))}
 require(set(state['mechanism'])==expected,'missing/unexpected64slice observer/wait mechanism scope')
 require(type(spec.get('expected_kernel_count')) is int and spec['expected_kernel_count']>0,'exact full-input kernel count not bound')
 require(len(state['launched_uids'])==spec['expected_kernel_count'] and state['launched_uids']==state['completed_uids'],'kernel launch/completion full-input mismatch')
 if master:require(set(state['unchanged'])==set(range(64)),'missing64 unchanged finite-service scope')
 else:require(not state['unchanged'],'unexpected ON unchanged-service records in OFF')
 rows={};summaries=[];observers=[];locals_=[];waits={reason:[] for reason in REASONS}
 coverage=qualification['capacity_diagnostic'].get('counter_coverage_review',{})
 for sid in range(64):
  s,t,i=(state['final'][kind,sid] for kind in ('SUMMARY','TERMINAL','INVARIANT'));h=state['large'][sid]
  structure=state['structure']['CONFIG',sid];bank=state['structure']['BANK_PEAK',sid];quota=state['structure']['WB_QUOTA',sid]
  require(s['observed_cycles']==native['cycle'],'FT snapshot not final native cycle')
  require(h['switch_requested']==h['switch_effective']==master and h['diagnostic_profile']==('S_L2_DATA_FREE_LARGE_CAPACITY' if master else 'MASTER_OFF'),'actual master/profile mismatch')
  require(h['capacity_scale']==(64 if master else 1) and h['copy_latch_cycles']==1 and h['result_fifo_used_by_L2']==0,'unreviewed common vector/copy latch/unused field')
  config=actual_config(h,s,structure,actual,p['configuration'])
  expected_struct={'slice':sid,'static_s64':0,'physical_slots':caps['payload_slots_total'],
   'resident_nominal':caps['resident_payload_slots'],'bypass_capacity':caps['bypass_payload_slots'],
   'wb_begin':caps['resident_payload_slots']+caps['bypass_payload_slots'],'static_wb_capacity':caps['wb_payload_slots'],
   'legacy_wbuf':caps['wb_payload_slots'],'bank_count':4,'bank_ops_per_physical_cycle':1,'copy_latch_bytes':128}
  require(structure==expected_struct,'actual structural finite layout differs')
  require(s['mode']==1 and s['wbuf']==caps['wb_payload_slots'] and s['physical_slots']==caps['payload_slots_total'],'actual FT layout differs')
  require(bank['ops_per_physical_cycle']==1 and all(0<=bank['bank'+str(n)]<=1 for n in range(4)),'physical bank budget exceeded')
  require(quota['cap']==quota['reserved']==quota['live']==0,'unexpected WB quota or live responsibility')
  require(i['line_mshr_capacity']==caps['line_mshr_entries'] and i['descriptor_capacity']==i['descriptor_free']==caps['descriptor_entries'] and i['wad_capacity']==caps['wad_entries'],'actual scaled metadata capacity/free closure changed')
  require(i['resident_capacity']==caps['resident_payload_slots'] and i['bypass_capacity']==caps['bypass_payload_slots'] and i['terminal_clean']==1,'actual native payload capacity or closure changed')
  require(t['requester_live']==0,'live requester tokens at terminal')
  d=state['mechanism']['LOCAL_DIAGNOSTIC',sid,-1];o=state['mechanism']['OBSERVER',sid,-1]
  require(o['enabled']==enabled and d['copy_free']==0 and d['l2_data_free']==master and d['hardware_P1_throughput_eligible']==1-master,'actual observer/local-service profile mismatch')
  if enabled:
   require(o['sampled_cycles']>0 and o['unfinished_head']==o['head_changes_without_admission']==0,'observer unfinished identity')
   for r,name in enumerate(REASONS):
    w=state['mechanism']['WAIT',sid,r];require(len(w['hist_log2'])==65 and sum(w['hist_log2'])==w['resolved']==w['requests'],'wait histogram/closure mismatch');waits[name].append(w)
  else:require(o.get('measurement')=='DISABLED_NOT_OBSERVED','disabled observer falsely measured')
  resources={};native_rows={RESOURCE_MAP[name][0]:r for (ss,name),r in state['resources'].items() if ss==sid}
  for name,cap in caps.items():
   r=native_rows.get(name);getter=h['sets']*h['ways'] if name=='tag_slots' else h.get(CAP_FIELDS.get(name,''))
   if getter is None and not master and name in ('icnt_to_l2_queue','l2_to_dram_queue','dram_to_l2_queue','l2_to_icnt_queue'):getter=off_fifo_capacity(name,actual,qualification)
   if r is not None:
    require(r['capacity']==cap and (getter is None or getter==cap),'native resource/header capacity mismatch')
   else:require(getter==cap,'native capacity getter missing/differs for '+name)
   used={'wad_entries':i['wad_live'],'line_mshr_entries':i['line_mshr_used'],'descriptor_entries':i['descriptor_used'],
    'per_address_descriptors':i['descriptor_used'],'wb_payload_slots':s['wb_slots'],'bypass_payload_slots':i['bypass_live'],
    'miss_queue_entries':0 if t['hardware_drained'] else None,'ready_response_bound':i['descriptor_used'],
    'dram_to_l2_queue':t['pending_returns'],'l2_to_icnt_queue':t['pending_responses'],
    'icnt_to_l2_queue':0 if t['hardware_drained'] else None,'l2_to_dram_queue':0 if t['hardware_drained'] else None}.get(name)
   kind='UNKNOWN';covered=False;review=coverage.get(name,{})
   if r is not None:
    raw_name=next(n for n,v in RESOURCE_MAP.items() if v[0]==name);_,declared_kind,literal=RESOURCE_MAP[raw_name]
    require(r.get('coverage') in (None,literal),'unreviewed native counter coverage literal')
    counters_present=type(r.get('highwater')) is int and type(r.get('capacity_denial_checks')) is int
    if counters_present and 'near_nonbinding' in r:require(r['near_nonbinding']==int(not r['capacity_denial_checks'] and 2*r['highwater']<=r['capacity']),'native convenience threshold inconsistent')
    # Raw literal is not scientific coverage. Exact source/native reviewed Q
    # must explicitly authorize the instrumented event/counter scope.
    if counters_present and r.get('coverage')==literal and review.get('status')=='INDEPENDENTLY_REVIEWED' and review.get('native_coverage')==literal:
     kind=declared_kind;covered=review.get('capacity_refusal_coverage_complete') is True
   resources[name]={'capacity':cap,'highwater':r.get('highwater') if r else None,
    'capacity_refusals':r.get('capacity_denial_checks') if r else None,'counter_covered':covered,
    'full_input_scope':True,'coverage_kind':kind,'terminal_used':used,
    'refusal_semantics':'CAPACITY_FULL_CHECK_OBSERVATIONS_NOT_UNIQUE_REJECTED_REQUESTERS',
    'native_coverage_literal':r.get('coverage','UNKNOWN_NOT_ASSUMED_COVERED') if r else 'NOT_EMITTED_NOT_ASSUMED_ZERO'}
  closure={k:s[k] for k in ('reserved','read_refs','wb_live','wb_slots','ownership_consistent')}
  closure.update({k:i[k] for k in ('bank_pending','descriptor_used','descriptor_free','line_mshr_used','wad_live','resident_pending','bypass_live','resident_tag_payload_consistent','payload_double_owner')})
  closure.update({k:t[k] for k in ('hardware_drained','requester_exact_once','unique_requesters','responses','pending_lower_reads','pending_returns','pending_responses')})
  closure.update(wb_created=s['wb_created'],wb_lower_accepted=s['wb_lower_accept'],wb_completed=s['wb_completed'],payload_free=s['role_free'],payload_roles={'RESIDENT_OR_FILL':s['role_resident'],'BYPASS':s['role_bypass'],'WB_STAGED':s['wb_slots']})
  local={'physical_grants':d['physical_grants'],'logical_copy_reads':d['logical_copy_reads'],'logical_copy_writes':d['logical_copy_writes'],'exempt_services':{name:d['exempt_'+name] for name in EXEMPT}}
  if master:
   u=state['unchanged'][sid];require(u['ROP_storage']=='NATIVE_DYNAMIC' and u['DRAM_ICNT_timing']=='UNCHANGED' and u['copy_latch_capacity']==1 and u['ROP_fixed_latency']==int(spec['profile_semantics']['effective_options']['-gpgpu_l2_rop_latency']) and type(u['ROP_highwater']) is int and u['ROP_highwater']>=0 and u['ROP_capacity_denial_checks']==0,'finite ROP/copy/DRAM scope changed')
  rows[str(sid)]={'observed_cycles':native['cycle'],'configuration':config,'resources':resources,'closure':closure,'local_service':local}
  summaries.append(s);observers.append(o);locals_.append(d)
 def total(records,key):return sum(row[key] for row in records)
 metric={'bottleneck':'UNKNOWN_OBSERVER_DISABLED','trigger':{'logical_copy_reads':total(locals_,'logical_copy_reads'),'logical_copy_writes':total(locals_,'logical_copy_writes'),'exempt_services':{name:total(locals_,'exempt_'+name) for name in EXEMPT},'diagnostic_flags':dict(copy_free=False,l2_data_free=bool(master))},'local_service':{'physical_bank_grants':total(locals_,'physical_grants'),'physical_throughput_eligible':not bool(master)},'interpretation_limits':'Wait sums overlap requests/slices and are not disjoint GPU critical stall cycles; conservative capacity bounds are not exact occupancy; ON not hardware throughput.'}
 if master:metric['unchanged_local_service']={'ROP_storage':'NATIVE_DYNAMIC','ROP_highwater_by_slice':{str(sid):state['unchanged'][sid]['ROP_highwater'] for sid in range(64)},'ROP_in_enlarged_capacity_vector':False,'scope':'Dynamic native ROP storage unchanged; actual highwater preserved, not a finite enlarged capacity or guaranteed hardware upper bound'}
 if enabled:
  metric['bottleneck']={name:{'distinct_requests_first_block':total(ww,'requests'),'blocked_observations_over_slices':total(ww,'observations'),'resolved_first_waits':total(ww,'resolved'),'request_wait_cycle_sum':total(ww,'sum'),'request_wait_max':max(w['max'] for w in ww),'unknown_while_unresolved':total(ww,'unknown_while_unresolved'),'hist_log2':[sum(w['hist_log2'][b] for w in ww) for b in range(65)]} for name,ww in waits.items()}
  metric['local_service'].update({key:total(observers,key) for key in ('lower_reads','lower_read_bytes','lower_write_bytes','lower_wb_bytes','unclassified_refusal_observations')})
 closures=[row['closure'] for row in rows.values()]
 result={'diagnostic_scope':'CAPACITY_DIAGNOSTIC_V1','profile':profile,'cycles':native['cycle'],'instructions':native['insn'],'slices':64,
  'unique_requesters':total(closures,'unique_requesters'),'responses':total(closures,'responses'),
  'live_descriptors':total(closures,'descriptor_used'),'live_line_mshrs':total(closures,'line_mshr_used'),'live_wad':total(closures,'wad_live'),
  'pending_lower_reads':total(closures,'pending_lower_reads'),'pending_returns':total(closures,'pending_returns'),'pending_responses':total(closures,'pending_responses'),
  'wb_created':total(closures,'wb_created'),'wb_lower_accepted':total(closures,'wb_lower_accepted'),'wb_completed':total(closures,'wb_completed'),
  'payload_capacity':64*caps['payload_slots_total'],'payload_free':total(closures,'payload_free'),
  'payload_roles':{role:sum(c['payload_roles'][role] for c in closures) for role in cv.ROLES},
  'transient_payloads':sum(c['wb_slots']+c['resident_pending']+c['bypass_live'] for c in closures),
  'hardware_drained':all(c['hardware_drained']==1 for c in closures),'workload_termination':spec['identity']['termination_contract'],
  'requester_exact_once_audit':True,'data_correctness_qualification':True,'raw_log_sha256':hashlib.sha256(Path(raw).read_bytes()).hexdigest(),
  'mechanism_metrics':metric,'mechanism_slice_records':{'observer':observers,'local_diagnostic':locals_},
  'capacity_diagnostic':{'schema':'E2_CAPACITY_NORMALIZED_TERMINAL_V1','requested_master':master,'effective_master':master,'capacity_manifest_sha256':scope['capacity_manifest_sha256'],'complete_input_scope':True,'slices':rows},
  'native_capacity_records':{'config':state['large'],'resources':[v for v in state['resources'].values()],'unchanged':state['unchanged']},
  'structural_observations':{kind:{str(sid):state['structure'][kind,sid] for sid in range(64)} for kind in ('CONFIG','BANK_PEAK','WB_QUOTA')},
  'kernel_completion':{'expected':spec['expected_kernel_count'],'launched_uids':sorted(state['launched_uids']),'completed_uids':sorted(state['completed_uids'])},
  'source_map':{'raw_decoder_origin':LEGACY_DECODE_SOURCE_SHA256,'new_capacity_source':SOURCE_MAPPING_CORE,'numeric_SASS_output_validated':False,'native_exit':'Actual durable exit and exact runtime/input hashes remain runner responsibilities'}}
 result['capacity_classification']=cv.validate_summary(result,spec['identity'],scope)['capacity_classification']
 return result

def main():
 from coordinator import Coordinator,NATIVE_GATES,digest,tooling_binding,write_json
 import capacity_policy
 args=argparse.ArgumentParser(description=__doc__);args.add_argument('--raw',type=Path,required=True);args.add_argument('--out',type=Path,required=True);a=args.parse_args()
 tooling_binding();spec=json.loads(Path('input_spec.json').read_text());coord=Coordinator();snap=coord.snapshot();coord.require_no_hold(snap,spec['qualification_id'])
 qrow=snap['qualifications'][spec['qualification_id']];require(qrow['sha256']==spec['qualification_id']==digest(qrow['path']),'exact new registered qualification changed');q=qrow['qualification']
 require(q['status']=='INDEPENDENTLY_QUALIFIED' and q['qualified_by']=='E','new E independent qualification required')
 capacity_policy.qualification(q,digest)
 review=q['capacity_diagnostic'].get('off_fifo_capacity_review')
 if review:
  evidence=review['new_archive_native_getter_evidence'];require(digest(evidence['path'])==evidence['sha256'],'OFF native getter evidence changed')
 require(spec['parser']==q['terminal_parser'] and digest(__file__)==q['terminal_parser']['sha256'],'parser not bound to exact new qualification')
 for name in NATIVE_GATES|set(q['affected_additional_gates']):
  gate=q['gates'][name];require(gate['status']=='PASS' and gate['production_driven'] is True and digest(gate['evidence_path'])==gate['evidence_sha256'],'changed new native gate '+name)
 write_json(a.out,parse(a.raw,spec,q))

if __name__=='__main__':main()
