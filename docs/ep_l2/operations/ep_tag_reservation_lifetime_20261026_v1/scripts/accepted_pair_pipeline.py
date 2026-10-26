#!/usr/bin/env python3
"""Offline analysis of already accepted fresh OFF/ON; never launches or accepts science."""
import sys
sys.dont_write_bytecode=True
import argparse,csv,hashlib,json,pathlib,re
import lifetime_parser as wire
P=pathlib.Path;HERE=P(__file__).resolve().parent
GOAL='EP_L2_TAG_RESERVATION_LIFETIME_CAUSAL_V1'
OLD_CORE='1093d2629e3d6a9130ba25b9dd119b6f3e16c092'
OLD_BINARY='e511cce7d8bcd5a3ebbe6255f42ebe153547484a69c6857ab55f7a8835a2dc33'
APP_ACCEPTED='EP_L2_TAG_RESERVATION_LIFETIME_APPLICATION_ACCEPTED'
NI_PASS='PASS_COMPLETE_OFF_ON_NONINTERFERENCE'
CHECKS=['cycles','instructions','CTA','slices','drain','requests_responses','cache_queue_behavior','observer_switch_only']
SCALARS=['gpu_tot_sim_cycle','gpu_tot_sim_insn','gpu_tot_issued_cta','gpgpu_n_mem_read_global','gpgpu_n_mem_write_global','icnt_total_pkts_simt_to_mem','icnt_total_pkts_mem_to_simt','L1D_total_cache_accesses','L1D_total_cache_misses','L1D_total_cache_reservation_fails','L2_total_cache_accesses','L2_total_cache_misses','L2_total_cache_reservation_fails','gpu_stall_dramfull','gpu_stall_icnt2sh']

import new_source_acceptance as v2authority
V2_IDENTITY={'archive_sha256': '685b497b50328deff4b96741c9a770b4b37e5d4bb2c8a1b5db90558b90be73c4', 'binary_sha256': '8d55f19bbe74c72e5da688f0ede6c2de1c3aa13040015475f23c9c6c521b9bef', 'core_source_commit': '11c02df1034112013523429894f1f931323adbef', 'framework_source_commit': '9dd1ee57a83d83b56b7874bc7c716185ab52c8f7', 'vendor_pybind11_commit': 'f90c430c3a1ce8f08c09942a5a1c3a797bb2295b'}
V2_ROLES={'OFF': 'EP_NATIVE_VECTOR_TAG_LIFETIME_OFF_20261026_V2', 'ON': 'EP_NATIVE_VECTOR_TAG_LIFETIME_ON_20261026_V2'}
V2_SOURCEQ_SHA='8ed4d41852f6e26bc9c1ced140f4dc2ecc6f287f3c4df5d0e5cc6e883dfe2814'
V2_VALIDATOR_SHA='8221eb9d4ea6872be39ff020534312dfd134dce036a5f2fc0feb5a7c3c46dcad'
class NotReady(ValueError):pass
def need(ok,why):
 if not ok:raise NotReady(why)
def sha(path):
 h=hashlib.sha256()
 with P(path).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def no_nonfinite(value):raise NotReady('non-finite JSON token '+value)
def read(path):return json.loads(P(path).read_bytes(),parse_constant=no_nonfinite)
def ref(value):
 need(type(value) is dict and set(value)=={'path','sha256'},'file reference requires exact path/SHA')
 p=P(value['path']);need(p.is_absolute() and p.is_file(),'referenced file not available')
 need(re.fullmatch('[0-9a-f]{64}',value['sha256']) is not None and sha(p)==value['sha256'],'referenced file SHA mismatch')
 return p

def terminal(raw):
 values={};lifetime=False
 # No full raw is retained. These are obvious terminal/traffic guards; main's
 # independently accepted normalized snapshots cover the full model semantics.
 with P(raw).open('rb') as f:
  for line in f:
   if line.startswith(b'EPL2LIFEV1|'):lifetime=True
   text=line.decode('ascii',errors='replace').strip()
   match=re.fullmatch(r'([A-Za-z0-9_]+)\s*=\s*([0-9]+)',text)
   if match and match[1] in SCALARS:values[match[1]]=int(match[2])
 need(set(values)==set(SCALARS),'actual terminal/scalar traffic population incomplete')
 return values,lifetime

def validated_inputs(path):
 need(P(v2authority.__file__).resolve()==HERE/'new_source_acceptance.py' and sha(v2authority.__file__)==V2_VALIDATOR_SHA,'exact V2 normalizer required')
 need(P(v2authority.life.__file__).resolve()==HERE/'lifetime_parser.py','foreign wire parser')
 v2authority.sourceq()
 m=read(path)
 need(m.get('schema')=='EP_L2_LIFETIME_ANALYSIS_INPUT_V1','analysis input schema')
 need(m.get('status')=='ACCEPTED_OFF_ON_NONINTERFERING_INPUTS','WAITING_FOR_ACCEPTED_OFF_ON; no application CSV generated')
 need(m.get('goal')==GOAL and m.get('scientific_acceptance_owner')=='EP-MAIN','owner/goal identity')
 need(set(m['cases'])=={'OFF','ON'},'exact two endpoints required')
 points={};raws={};refs={};scalars={};source=None;semantic_config=None
 for role in ['OFF','ON']:
  c=m['cases'][role];raw=ref(c['raw']);receipt=ref(c['accepted_receipt']);point=read(receipt)
  need(point.get('status')==APP_ACCEPTED and point.get('goal')==GOAL,'main accepted application receipt required')
  need(point.get('cohort')==V2_ROLES[role] and point.get('source_identity')==V2_IDENTITY and point.get('source_qualification_sha256')==V2_SOURCEQ_SHA,'exact V2 accepted authority required')
  need(point.get('observer_enabled') is (role=='ON'),'observer role mismatch')
  need(point.get('raw_sha256')==c['raw']['sha256'],'accepted/raw SHA mismatch')
  need(type(point.get('instructions')) is int and point['instructions']==56000000,'full56M required')
  need(point.get('CTA')==15625 and point.get('slices')==64 and point.get('hardware_drained') is True,'CTA/64slice/drain required')
  need(type(point.get('cycles')) is int and point['cycles']>0,'positive actual cycle count')
  need(point.get('observer_header_sha256')==read(HERE/'wire_contract.json')['header_sha256'],'header identity mismatch')
  s=point['source_identity'];need(s['core_source_commit']!=OLD_CORE and s['binary_sha256']!=OLD_BINARY,'new lifetime producer cannot inherit old1093/e511 identity')
  need(re.fullmatch('[0-9a-f]{40}',s['core_source_commit']) is not None and re.fullmatch('[0-9a-f]{64}',s['binary_sha256']) is not None,'source/binary identity format')
  if source is None:source=s
  need(s==source,'OFF/ON source identity differs')
  need(point.get('clock_domains_MHz')=='1132.0:1132.0:1132.0:850.0','exact original science clocks required')
  config=point.get('semantic_config_sha256');need(type(config) is str and re.fullmatch('[0-9a-f]{64}',config) is not None,'semantic config binding missing')
  if semantic_config is None:semantic_config=config
  need(config==semantic_config,'OFF/ON scientific config differs')
  actual,has_life=terminal(raw)
  need(actual['gpu_tot_sim_cycle']==point['cycles'] and actual['gpu_tot_sim_insn']==point['instructions'] and actual['gpu_tot_issued_cta']==point['CTA'],'actual raw terminal mismatch')
  need(has_life is (role=='ON'),'OFF must have no life frames; ON must have them')
  points[role]=point;raws[role]=raw;refs[role]=dict(raw=c['raw'],accepted_receipt=c['accepted_receipt']);scalars[role]=actual
 need(points['OFF']['cycles']==points['ON']['cycles'] and scalars['OFF']==scalars['ON'],'actual OFF/ON terminal/cache/traffic scalars differ')
 need(points['OFF']['uuid']!=points['ON']['uuid'],'OFF/ON cannot be same execution')
 npath=ref(m['noninterference']);ni=read(npath)
 need(ni.get('status')==NI_PASS and ni.get('goal')==GOAL,'complete main noninterference receipt required')
 need(ni.get('source_identity')==source,'NI source identity')
 need(ni.get('raw_sha256')=={r:m['cases'][r]['raw']['sha256'] for r in ['OFF','ON']},'NI raw SHA pair mismatch')
 need(all(ni.get('checks',{}).get(k) is True for k in CHECKS),'NI checks missing/failed')
 need(ni.get('source_qualification_sha256')==V2_SOURCEQ_SHA and ni['normalizer_code']['sha256']==V2_VALIDATOR_SHA,'V2 NI authority/normalizer pin')
 normalizer=ref(ni['normalizer_code'])
 snapshots={};srefs={}
 for role in ['OFF','ON']:
  p=ref(ni['normalized_semantics'][role]);snapshot=read(p)
  need(snapshot.get('schema')=='EP_L2_LIFETIME_PRODUCTION_SEMANTIC_SNAPSHOT_V1','normalized production snapshot schema')
  need(snapshot.get('raw_sha256')==m['cases'][role]['raw']['sha256'] and snapshot.get('source_identity')==source,'normalized snapshot raw/source binding')
  need(snapshot.get('normalizer_sha256')==ni['normalizer_code']['sha256'],'normalizer source binding')
  metrics=snapshot['metrics'];need(set(['terminal_scalars','requests_responses','cache_behavior','queue_behavior']).issubset(metrics),'full semantic groups missing')
  need(metrics['terminal_scalars']==scalars[role],'normalized scalars differ from actual raw')
  need(all(type(metrics[k]) is dict and bool(metrics[k]) for k in ['requests_responses','cache_behavior','queue_behavior']),'normalized semantic group empty')
  snapshots[role]=metrics;srefs[role]=ni['normalized_semantics'][role]
 need(snapshots['OFF']==snapshots['ON'],'normalized production behavior differs')
 return dict(manifest=m,source_identity=source,points=points,raws=raws,refs=refs,noninterference=m['noninterference'],snapshots=srefs,normalizer=ni['normalizer_code'],terminal_scalars=scalars['ON'])

def schemas():
 k=read(HERE/'wire_contract.json')
 occupancy=['raw_sha256','slice','set','begin_l2tick','end_l2tick','begin_gpu_corecycle','end_gpu_corecycle']+[f'area_R{i}' for i in range(17)]
 occupancy += ['TICK_PEAK','EVENT_PEAK','ENTER','EXIT','ALLOC','REENTER','LEFT','RIGHT','CLOSED_NEW','CLOSED_RE','CLOSED_LEFT','SUM_NEW','SUM_RE','SUM_LEFT','SUM_RIGHT','MAX_NEW','MAX_RE','MAX_LEFT','NEW_COMMIT','WAIT_COUNT','WAIT_SUM','WAIT_MAX','PROD_TAGFAIL']
 occupancy += [f'new_hist_b{i}' for i in range(33)]+[f're_hist_b{i}' for i in range(33)]
 occupancy += ['weighted_reserved_area','mean_reserved','reservation_enters_per_l2tick','included_episode_count','mean_observed_episode_overlap_ticks','complete_population_product_defined','complete_population_mean_lifetime_ticks','mean_completed_NEW_ticks','mean_completed_RE_ticks','area_overlap_exact']
 sector=['raw_sha256','slice','set']+k['incarnation_stats']+['REQUESTER','MERGE','UNIQUE_SECTOR','SECTOR_TRANSITION','SECTOR_ADD','NEW_HEAD','NEW_UNIQUE','NEW_WITH_PENDING','NEW_WITH_ELIGIBLE','NEW_PENDING_SECTORS_SUM','NEW_CAN_DETACH_SUM','RO_ADMIT','RO_RETIRE','RO_TIME','RO_LOWER_TIME','RO_RESPONSE_ONLY_TIME','RO_WAITER_ADDS','RO_MAX_WAITERS','RO_REQUIRED_ADD','RO_ISSUED_ADD','RO_READY_ADD','RO_INITIAL_READY']
 sector += [f'head_reserved_R{i}' for i in range(17)]+[f'unique_reserved_R{i}' for i in range(17)]
 sector += ['observed_requesters_per_closed_incarnation','observed_requesters_per_right_incarnation','observed_distinct_requested_sectors_per_closed_incarnation','observed_distinct_requested_sectors_per_right_incarnation','mean_reserved_at_unique_newTag','newTag_unique_given_pending_fraction','newTag_unique_given_structural_eligible_fraction','Tag_merge_marker_per_observed_requester','not_DRAM_request_savings']
 return {'PER_SET_OCCUPANCY_AND_LIFETIME.csv':occupancy,'SECTOR_MERGE_AND_REQUEST_OVERLAP.csv':sector}

def quotient(a,b):return a/b if b else ''

def generate(manifest,outdir):
 data=validated_inputs(manifest) # No output directories or application CSV before all gates.
 out=P(outdir);need(not out.exists(),'analysis output must be fresh');out.mkdir(parents=True)
 validation=wire.analyze(data['raws']['ON'],out/'STRICT_OBSERVER_ON',expected_slices=64,synthetic=False)
 need(validation['raw_sha256']==data['manifest']['cases']['ON']['raw']['sha256'],'closed ON raw drift after qualification')
 summary=out/'STRICT_OBSERVER_ON/PER_SET_RESERVATION_SUMMARY.csv';windows=out/'STRICT_OBSERVER_ON/PER_SET_TEMPORAL_WINDOWS.csv';anchors={}
 with windows.open() as f:
  for row in csv.DictReader(f):
   si=int(row['slice']);b=int(row['begin_gpu']);e=int(row['end_gpu'])
   if si not in anchors:anchors[si]=[b,e]
   else:anchors[si][1]=e
 schema=schemas();names=list(schema);handles=[(out/(name+'.partial')).open('w',newline='') for name in names];writers=[csv.DictWriter(f,fieldnames=schema[n],lineterminator='\n') for f,n in zip(handles,names)]
 for w in writers:w.writeheader()
 count=0;rawsha=validation['raw_sha256']
 try:
  with summary.open() as f:
   for row in csv.DictReader(f):
    v={k:int(x) for k,x in row.items() if x!='' and k not in ['unit','coverage','mean_reserved']};si=v['slice'];duration=v['end']-v['begin'];area=sum(i*v[f'area_R{i}'] for i in range(17));included=v['LEFT']+v['ENTER'];full=v['LEFT']==v['RIGHT']==0 and v['ENTER']>0
    occ={k:v[k] for k in schema[names[0]] if k in v};occ.update(raw_sha256=rawsha,begin_l2tick=v['begin'],end_l2tick=v['end'],begin_gpu_corecycle=anchors[si][0],end_gpu_corecycle=anchors[si][1],weighted_reserved_area=area,mean_reserved=quotient(area,duration),reservation_enters_per_l2tick=quotient(v['ENTER'],duration),included_episode_count=included,mean_observed_episode_overlap_ticks=quotient(area,included),complete_population_product_defined=int(full),complete_population_mean_lifetime_ticks=quotient(area,v['ENTER']) if full else '',mean_completed_NEW_ticks=quotient(v['SUM_NEW'],v['CLOSED_NEW']),mean_completed_RE_ticks=quotient(v['SUM_RE'],v['CLOSED_RE']),area_overlap_exact=int(area==sum(v[k] for k in ['SUM_NEW','SUM_RE','SUM_LEFT','SUM_RIGHT'])))
    sec={k:v[k] for k in schema[names[1]] if k in v};weighted_unique=sum(i*v[f'unique_reserved_R{i}'] for i in range(17))
    sec.update(raw_sha256=rawsha,observed_requesters_per_closed_incarnation=quotient(v['closed_requester_sum'],v['closed_count']),observed_requesters_per_right_incarnation=quotient(v['right_requester_sum'],v['right_count']),observed_distinct_requested_sectors_per_closed_incarnation=quotient(v['closed_distinct_requested_sector_sum'],v['closed_count']),observed_distinct_requested_sectors_per_right_incarnation=quotient(v['right_distinct_requested_sector_sum'],v['right_count']),mean_reserved_at_unique_newTag=quotient(weighted_unique,v['NEW_UNIQUE']),newTag_unique_given_pending_fraction=quotient(v['NEW_WITH_PENDING'],v['NEW_UNIQUE']),newTag_unique_given_structural_eligible_fraction=quotient(v['NEW_WITH_ELIGIBLE'],v['NEW_UNIQUE']),Tag_merge_marker_per_observed_requester=quotient(v['MERGE'],v['REQUESTER']),not_DRAM_request_savings=1)
    writers[0].writerow(occ);writers[1].writerow(sec);count+=1
 finally:
  for f in handles:f.close()
 need(count==4096,'final application CSV population incomplete')
 for name in names:(out/(name+'.partial')).rename(out/name)
 outputs={name:{'path':str(out/name),'sha256':sha(out/name),'rows':count} for name in names}
 index={'schema':'EP_L2_LIFETIME_ANALYSIS_SOURCE_INDEX_V1','status':'ANALYSIS_FROM_REFERENCED_MAIN_ACCEPTED_NONINTERFERING_PAIR','goal':GOAL,'scientific_acceptance_granted_by_C':False,'source_identity':data['source_identity'],'source_cases':data['refs'],'noninterference':data['noninterference'],'normalized_snapshots':data['snapshots'],'normalizer_code':data['normalizer'],'manifest':{'path':str(P(manifest).resolve()),'sha256':sha(manifest)},'parser':{'path':str(HERE/'lifetime_parser.py'),'sha256':sha(HERE/'lifetime_parser.py')},'pipeline':{'path':str(P(__file__).resolve()),'sha256':sha(__file__)},'wire_contract':{'path':str(HERE/'wire_contract.json'),'sha256':sha(HERE/'wire_contract.json')},'wire_header_sha256':validation['header_sha256'],'observer_wire_validation':{'path':str(out/'STRICT_OBSERVER_ON/OBSERVER_WIRE_VALIDATION.json'),'sha256':sha(out/'STRICT_OBSERVER_ON/OBSERVER_WIRE_VALIDATION.json')},'outputs':outputs,'temporal_csv':{'path':str(windows),'sha256':sha(windows)},'actual_pair_provenance_required':True,'causal_boundary':'Coexisting factors and temporal associations, no unique causal shares or T-cycle attribution','analysis_count_population':'same slice/set reservation episodes; exact overlap/carry before any product check'}
 (out/'ANALYSIS_SOURCE_INDEX.json').write_text(json.dumps(index,sort_keys=True,indent=2)+'\n');return index

if __name__=='__main__':
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--manifest');a.add_argument('--out-dir');a.add_argument('--schemas-only',action='store_true');a.add_argument('--validate-only',action='store_true');z=a.parse_args()
 try:
  if z.schemas_only:result=schemas()
  elif z.validate_only:validated_inputs(z.manifest);result={'status':'REFERENCED_ACCEPTED_PAIR_INPUTS_VALIDATED_ONLY','scientific_acceptance_granted_by_C':False}
  else:need(z.manifest and z.out_dir,'manifest and out-dir required');result=generate(z.manifest,z.out_dir)
  print(json.dumps(result,sort_keys=True,indent=2))
 except (NotReady,wire.InvalidWire,OSError,ValueError,KeyError,TypeError) as e:print(json.dumps({'status':'HOLD_NO_APPLICATION_CSV_PROMOTION','reason':str(e),'scientific_acceptance_granted_by_C':False}),file=sys.stderr);sys.exit(2)
