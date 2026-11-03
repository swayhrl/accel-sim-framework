#!/usr/bin/env python3
"""Main-approved 72MiB hard bound: exactly three accepted ON raw, one streaming pass each."""
import pathlib,json,hashlib,gzip,collections,datetime,time,csv
P=pathlib.Path;Q=P(__file__).resolve().parent
J=P('/root/data/ep_l2_full_workload_performance_20261027_v1');E=J/'execution_v2_20261103_v1'
LIMIT=72*1024*1024;EXACT=70235553;used=0;records=[];receipts=[];started=time.time()
def need(x,m):
 if not x:raise AssertionError(m)
def ref(p):
 p=P(p);b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def load(p):return json.loads(P(p).read_text())
def dump(p,d):P(p).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
pre=[]
for arm in ['A_F_MINUS_T','B_LEGACY_F','C_CORRECTED_F']:
 m=load(E/'control/MECHANISM_METRICS'/('EP_PERF_T3_CONV16X8_'+arm+'_ON_V1.json'));vp=P(m['validation_ref']['path']);v=load(vp);ni=load(E/'control/NI_RESULTS'/('EP_PERF_T3_CONV16X8_'+arm+'_OFF_V1.json'));need(all(ni['equal'].values()),'NI');need(v['source_identity']==ni['source_identity'],'Source same NI');need(v['input_identity_sha256']==ni['input_identity_sha256'],'input same NI')
 ap=load(vp.parent/'ACCEPTED_POINT.json');need(ap['source_identity']==v['source_identity'],'accepted Source');raw=vp.parent/'raw.log.gz';need(raw.stat().st_size==v['raw_stored_bytes'],'stored size before scan');pre.append((arm,m,vp,v,ni,raw,ap))
need(sum(x[3]['raw_uncompressed_bytes']for x in pre)==EXACT and EXACT<LIMIT,'exact Main scope bytes')
class HashReader:
 def __init__(self,p):self.f=p.open('rb');self.h=hashlib.sha256();self.n=0
 def read(self,n=-1):
  b=self.f.read(n);self.h.update(b);self.n+=len(b);return b
 def tell(self):return self.f.tell()
 def close(self):self.f.close()
for arm,m,vp,v,ni,raw,ap in pre:
 h=hashlib.sha256();n=0;hr=HashReader(raw);phase={};slices={};globals_={};p1={};sources=[];linecount=0;counts=collections.Counter();kernel_lines=[]
 with gzip.GzipFile(fileobj=hr,mode='rb')as z:
  while True:
   b=z.readline(LIMIT-used+1)
   if not b:break
   n+=len(b);used+=len(b);need(used<=LIMIT and n<=v['raw_uncompressed_bytes'],'logical byte cap');h.update(b);linecount+=1
   if b.startswith(b'EPL2DETACH_DIAG_V1|'):
    r=json.loads(b.split(b'|',1)[1]);counts[r['record']]+=1
    if r['record']=='PHASE':phase[(int(r['cycle']),int(r['slice']),int(r['phase']))]=r
    elif r['record']=='SLICE':slices[(int(r['cycle']),int(r['slice']))]=r
    elif r['record']=='GLOBAL':globals_[int(r['cycle'])]=r
    elif r['record']=='SOURCE':sources.append(r)
   elif b.startswith(b'EPL2P1V2|SET_ELIGIBILITY_QUERY|'):
    r=dict(x.split('=',1)for x in b.decode().strip().split('|')[2:]);p1[int(r['slice'])]=r
   elif b.startswith((b'kernel_name = ',b'kernel_launch_uid = ',b'kernel_uid = ')):
    kernel_lines.append(b.decode().strip())
 # gzip drains its one forward compressed stream; no second raw read.
 need(hr.read(1)==b'','compressed EOF');hr.close()
 need(n==v['raw_uncompressed_bytes'] and h.hexdigest()==v['raw_logical_sha256'],'logical bytes/SHA')
 need(hr.n==v['raw_stored_bytes'] and hr.h.hexdigest()==v['raw_stored_sha256'],'stored bytes/SHA')
 final=max(globals_);g=globals_[final];need(g==m['DETACH_DIAG_final_GLOBAL'],'final GLOBAL matches existing compact byte-independent object')
 rows=[r for (cy,si,ph),r in phase.items()if cy==final];sl=[r for(cy,si),r in slices.items()if cy==final];need(len(sl)==64 and len(rows)==256,'final64slice 4phases')
 allkeys=list(g['counters']);agg={};catalog={}
 for r in rows:
  need(r['closure_ok']and r['epoch_closed']and not r['output_invalid']and not r['overflow_invalid'],'finalPHASE closure');ph=r['phase'];catalog.setdefault(ph,{'kernel_uid':r['kernel_uid'],'kernel_scope':r['kernel_scope']});need(catalog[ph]=={'kernel_uid':r['kernel_uid'],'kernel_scope':r['kernel_scope']},'samephasekernel acrossslice')
  if ph not in agg:agg[ph]=dict.fromkeys(allkeys,0)
  for k in allkeys:agg[ph][k]+=r['counters'][k]
 for k in allkeys:need(sum(c[k]for c in agg.values())==g['counters'][k],'phase?global '+k)
 for sr in sl:
  for k in allkeys:need(sum(r['counters'][k]for r in rows if r['slice']==sr['slice'])==sr['counters'][k],'phase?slice '+k)
 selected=['raw_reservation_fail','pressure_eligible','eligible_frontend_admitted','eligible_frontend_denied','eligible_capacity_consulted','eligible_capacity_not_consulted','eligible_rewrite_miss','eligible_relief_not_consulted','eligible_early_query','ft_access_attempts','commit_raw_probe_reached','raw_tag_fail_commit','relieve_calls','relieve_eligible_selected','relieve_no_eligible','detach_calls','detach_success','detach_false','detach_exception','post_relief_miss','commit_accepted','commit_denied','trigger_accepted_after_detach','trigger_denied_after_detach','trigger_exception_after_detach','detached_return_packets','detached_return_sectors','detached_responses','detached_retired','ro_admits','ro_merges','ro_responses','ro_retired','denied_tag','denied_bank','denied_pin','denied_wad_full','denied_missq','denied_mshr','closure_errors','selected_identity_mismatch']
 out={'schema':'EP_T3_ACCEPTED_RAW_FINAL_PHASE_REDUCTION_V1','arm':arm,'final_cycle':final,'phase_catalog':catalog,'final_global_selected':{k:g['counters'][k]for k in selected},'final_phase_selected':{str(ph):{k:c[k]for k in selected}for ph,c in agg.items()},'final_phase_all_counters':agg,'final_slice_phase_selected':[dict(slice=r['slice'],phase=r['phase'],kernel_uid=r['kernel_uid'],kernel_scope=r['kernel_scope'],counters={k:r['counters'][k]for k in selected},original_full_record_sha256=hashlib.sha256(json.dumps(r,sort_keys=True,separators=(',',':')).encode()).hexdigest())for r in sorted(rows,key=lambda r:(r['slice'],r['phase']))],'snapshot_cycles':sorted(globals_),'snapshots_global_selected':[dict(cycle=cy,epoch_closed=r['epoch_closed'],detach_success=r['counters']['detach_success'],detached_retired=r['counters']['detached_retired'])for cy,r in sorted(globals_.items())],'SOURCE_records':sources,'kernel_catalog_lines':kernel_lines,'query_phase':'NOT_INSTRUMENTED: EPL2P1V2 is cumulative per-slice, not phase','backend_requester_class':'NOT_INSTRUMENTED: PHASE counters have no RO/ordinary backend detach split','P1_final_cumulative':p1,'phase_to_slice_to_global_all_counter_closure':'PASS','raw_ref':{'path':str(raw),'stored_bytes':hr.n,'stored_sha256':hr.h.hexdigest(),'logical_bytes':n,'logical_sha256':h.hexdigest()},'validation_ref':ref(vp),'accepted_point_ref':ref(vp.parent/'ACCEPTED_POINT.json'),'spec_ref':ref(vp.parent/'FROZEN_SPEC.json'),'NI_ref':ref(E/'control/NI_RESULTS'/('EP_PERF_T3_CONV16X8_'+arm+'_OFF_V1.json')),'source_identity':v['source_identity'],'input_identity_sha256':v['input_identity_sha256'],'complete_population':{k:v[k]for k in ['cycles','instructions','CTA','kernel_count','hardware_drained']},'records_seen':dict(counts),'lines':linecount}
 dest=Q/(arm+'_ACCEPTED_FINAL_PHASE.json');dump(dest,out);receipts.append(dict(arm=arm,raw=out['raw_ref'],summary_ref=ref(dest),validation_ref=out['validation_ref'],accepted_point_ref=out['accepted_point_ref'],spec_ref=out['spec_ref'],NI_ref=out['NI_ref'],source_identity=v['source_identity'],phase_closure='PASS'))
 print(arm,json.dumps({ph:{k:c[k]for k in ['detach_success','trigger_accepted_after_detach','trigger_denied_after_detach','detached_retired','raw_tag_fail_commit']}for ph,c in agg.items()}))
need(used==EXACT,'all3 exact accepted bytes')
receipt={'schema':'EP_T3_BOUNDED_PHASE_READ_RECEIPT_V1','status':'PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'Main_authorization':'Three accepted ON raw exact70235553B; Main raised initial64MiB to hard72MiB after accepted-size precheck; no new simulation authorization','logical_bytes_hard_limit':LIMIT,'logical_bytes_actual':used,'compressed_bytes_actual':sum(x['raw']['stored_bytes']for x in receipts),'raw_passes':3,'passes_per_raw':1,'Trace_reads':0,'active_raw_reads':0,'science_starts':0,'CPU_fixture_starts':0,'production_edits':0,'elapsed_seconds':time.time()-started,'summaries':receipts,'claim_boundaries':['PHASE attribution is actual backend event count in active-kernel interval, not oldRO ownerkernel','PHASE backend class unknown; frontend class totals cannot fill it','query issued/wait cost is cumulative slice only; no perphase measured query tickets','future triggerUID accept/completion remains NOT_MEASURED']};dump(Q/'BOUNDED_PHASE_READ_RECEIPT.json',receipt)
print('COMPLETE',used,receipt['elapsed_seconds'])
