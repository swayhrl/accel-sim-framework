"""Read-only Oracle status/per-kernel reducer. No engine imports or mutations."""
import argparse,collections,csv,gzip,hashlib,itertools,json,math,os,pathlib,re,time
P=pathlib.Path;MODES=('OFF_MATCHED','M_DATAREAD','L2_DATAREAD','L1_DATAREADY')
AUTH='18b1ee9d339902e555fc2e04ef51c84f77dfe1b1';MATRIX_SHA='11d5bfc7642a6262fde719119603c940ca64eb98de69d2554124f24b2302a3ee'
PASS='PASS_CONTROLLED_ORACLE_DH_STRICT_ARCHIVE_NATIVE_RESTORE'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def js(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def put(p,v,gz=False):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True);b=(json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n').encode();tmp=p.with_name('.'+p.name+'.'+str(os.getpid())+'.tmp')
 tmp.write_bytes(gzip.compress(b,mtime=0) if gz else b);os.replace(tmp,p)
def require(x,why):
 if not x:raise ValueError(why)
def stat(v,n):
 s=[x['S_oracle'] for x in v];h=[x['H'] for x in v]
 return {'accepted_pairs':len(v),'population':n,'missing':n-len(v),'GM_S_oracle':math.exp(sum(math.log(z) for z in s)/len(s)) if s else None,'faster':sum(z>1 for z in s),'equal':sum(z==1 for z in s),'slower':sum(z<1 for z in s),'S_sorted':sorted(s),'H_sorted':sorted(h)}
def raw_kernel_evidence(raw_path,raw_sha,kernels):
 """As-printed facts only: no assumed reset/delta, missing counter -> null."""
 require(sha(raw_path)==raw_sha,'raw gzip SHA mismatch')
 selected=('DTC_L1_oo_valid_hits','DTC_L1_oo_pending_hits','DTC_L1_oo_new_misses','DTC_L1_oo_tag_evictions','DTC_L1_oo_physical_allocated','DTC_L1_oo_lower_created','DTC_L1_oo_lower_issued','DTC_L1_oo_lower_responses','DTC_L1_oo_lower_create_queue_full_stalls','DTC_L1_oo_ready_but_writeback_blocked_cycles','DTC_L1_lower_cap_full_events','DTC_L1_lower_outstanding','DTC_L1_oo_pib_occupancy','DTC_L1_oo_active_refs','DTC_SERVICE_V1_collected_sectors','DTC_SERVICE_V1_collection_cycles','DTC_SERVICE_V1_fully_ready_to_complete_sum','DTC_SERVICE_V1_ready_to_collect_sum','DTC_SERVICE_V1_wb_wait','DTC_SERVICE_V1_physical_integral','DTC_SERVICE_V1_pib_integral','DTC_SERVICE_V1_samples','gpu_stall_dramfull','gpu_stall_icnt2sh','gpgpu_n_stall_shd_mem','gpu_reg_bank_conflict_stalls','avg_mrq_latency','averagemflatency','avg_icnt2mem_latency','avg_icnt2sh_latency')
 out=[];block=[]
 def consume(lines):
  text=''.join(lines);numeric={k:int(v) for k,v in re.findall(r'^\s*(\w+)\s*=\s*(\d+)\s*$',text,re.M)}
  groups={}
  for prefix in ('DTC_ORACLE_M_V1 ','dtc_oracle_l2 '):
   units=[]
   for line in lines:
    if line.startswith(prefix):units.append({k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',line)})
   keys=set().union(*(set(v) for v in units)) if units else set()
   groups[prefix.strip()]={'printed_units':len(units),'sum_counts':{k:sum(v[k] for v in units) if all(k in v for v in units) else None for k in keys-{'mode','cluster','sub_partition'}} if units else None}
  return {'as_printed_counters':{k:numeric.get(k) for k in selected},'oracle_physical_unit_aggregates':groups,'scope':'As printed in this kernel statistics block. Reset/cumulative/delta semantics are not inferred. Missing is null; correlations are not causal proof.'}
 with gzip.open(raw_path,'rt') as f:
  for line in f:
   if line.startswith('kernel_name = '):
    if block:out.append(consume(block))
    block=[line]
   elif block:block.append(line)
  if block:out.append(consume(block))
 require(len(out)==len(kernels),'raw/strict kernel count mismatch')
 return out
def accept_closed(root,point,result,result_path,derived):
 c=point['cohort'];sp=root/'control/specs'/(c+'.json');s=read(sp);plan=read(root/'control/EXECUTION_PLAN.json');build=read(root/'control/BUILD_PROFILE.json');proof=result['proof']
 require(plan['preparation_phase']=='SCIENCE_FINAL_FROZEN' and not plan.get('mock',False),'not science-final runtime')
 require(s['plan_id']==point['plan_id']==result['plan_id'] and s['input_digest']==point['input_digest']==result['input_digest'],'fixed full input/plan mismatch')
 require(s['oracle_mode']==point['mode']==result['oracle_mode'] and s['cell']==result['cell']=='DH','mode/design mismatch')
 require(proof['performance_accepted'] is True and type(result['cycles']) is int and result['cycles']>0 and proof['cycles']==result['cycles'],'strict performance not accepted')
 require(proof['core_commit']==s['core_commit']==build['core_commit'] and proof['framework_commit']==s['framework_commit']==build['framework_commit'] and proof['binary_sha256']==s['binary_sha256']==build['binary_sha256'],'same-build identity mismatch')
 require(len(s['expected_options'])==271 and proof['effective_options']==s['expected_options'],'full 271 option proof mismatch')
 require(proof['effective_options']['-gpgpu_dtc_oracle_mode']==[str(MODES.index(point['mode']))] and proof['effective_options']['-gpgpu_perfect_mem']==proof['effective_options']['-l2_ideal']==['0'],'mode/stock flag mismatch')
 require(proof.get('actual_libcudart_sha256')==build['libcudart_sha256'],'new libcudart proof mismatch')
 ip=root/'control/qualification_ledger'/(c+'.INTENT.json');dp=ip.with_name(c+'.DONE.json');i=read(ip);d=read(dp)
 require(i['uuid']==d['uuid']==result['uuid'] and d['stop_reason'] is None and d['launcher_wait_returncode']==0 and d['native_simulator_observed'] is True,'not natural actual terminal')
 native=P(i['output']);require(read(native/'NATIVE_EXIT.json')==d and read(native/'L2_STRICT.json')==proof,'native terminal/strict payload mismatch')
 ar=result['archive'];receipt=ar['receipt'];require(receipt['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET' and receipt['source_disposition']=='SOURCE_KEEP' and receipt['source_release_bytes']==0,'archive/restore/SOURCE_KEEP not verified')
 require('/root/share/mnt164/' in receipt['target_mount_path'] and ar['independently_verified_entries']>0,'missing true164 typed restore report')
 require(proof['instructions']==s['expected']['instructions'] and proof['CTA']==s['expected']['CTA'] and len(proof['kernels'])==s['expected']['kernels'],'full work/ROI mismatch')
 ks=proof['kernels'];require([k['ordinal'] for k in ks]==list(range(1,len(ks)+1)),'kernel order identity mismatch')
 require(sum(k['cycles'] for k in ks)==result['cycles'] and sum(k['active_instructions'] for k in ks)==s['expected']['instructions'],'kernel work/cycles mismatch')
 digest=sha(result_path);cache=derived/('KERNEL_FACTS.'+digest+'.json.gz')
 if not cache.exists():
  raw=raw_kernel_evidence(native/'raw.log.gz',proof['raw_gzip_sha256'],ks);previous_cta=0;records=[]
  oracle=proof.get('oracle_kernel_counters',[])
  for index,k in enumerate(ks):
   delta=k['cumulative_CTA']-previous_cta;previous_cta=k['cumulative_CTA']
   require(delta>=0,'nonmonotonic cumulative CTA')
   records.append({**k,'CTA_delta':delta,'result_path':str(result_path),'result_sha256':digest,'strict_path':str(native/'L2_STRICT.json'),'strict_sha256':sha(native/'L2_STRICT.json'),'raw_path':str(native/'raw.log.gz'),'raw_gzip_sha256':proof['raw_gzip_sha256'],'raw_uncompressed_sha256':proof['raw_uncompressed_sha256'],'oracle':oracle[index] if index<len(oracle) else None,**raw[index]})
  put(cache,{'schema':'DTC_ORACLE_DERIVED_KERNEL_FACTS_V1','program':point['program'],'mode':point['mode'],'input_digest':point['input_digest'],'uuid':result['uuid'],'records':records},gz=True)
 facts=read_gz(cache)
 return {'spec_path':str(sp),'spec_sha256':sha(sp),'execution_plan_path':str(root/'control/EXECUTION_PLAN.json'),'execution_plan_sha256':sha(root/'control/EXECUTION_PLAN.json'),'core_commit':s['core_commit'],'framework_commit':s['framework_commit'],'binary_sha256':s['binary_sha256'],'libcudart_sha256':build['libcudart_sha256'],'configuration_file_pins':s['configs'],'non_oracle_options_sha256':js({k:v for k,v in s['expected_options'].items() if k!='-gpgpu_dtc_oracle_mode'}),'native_strict_path':str(native/'L2_STRICT.json'),'native_strict_sha256':sha(native/'L2_STRICT.json'),'archive_receipt':receipt,'kernel_evidence_path':str(cache),'kernel_evidence_sha256':sha(cache),'kernel_records':facts['records'],'actual_mechanism_exposure':proof.get('actual_mechanism_exposure'),'terminal_metrics_as_printed':proof.get('metrics'),'traffic_as_printed':proof.get('traffic'),'latency_counters_as_printed':proof.get('latency_counters')}
def read_gz(p):
 with gzip.open(p,'rt') as f:return json.load(f)
def snapshot(base_root,matrix_path,out_dir):
 require(sha(matrix_path)==MATRIX_SHA,'frozen PLAN matrix changed');matrix=read(matrix_path);out=P(out_dir);out.mkdir(parents=True,exist_ok=True)
 plans={r['plan_id']:r for r in matrix['rows']};require(len(plans)==128,'not128 static slots')
 actual={};errors=[];closed=[]
 for stage in ('initial8','remaining24'):
  root=P(base_root)/stage;p=root/'control/MATRIX.fixed.json'
  if not p.exists():continue
  for point in read(p)['points']:
   pid=point['plan_id'];require(pid in plans,'unfrozen actual plan ID');require(pid not in actual,'duplicate stage slot')
   require(all(point[k]==plans[pid][k] for k in ('program','suite','input_digest','mode')),'actual point differs from frozen full input/mode')
   actual[pid]=(root,point)
 rows=[];accepted={};prior_path=out/'TERMINAL_RESULT_PINS.json';prior=read(prior_path) if prior_path.exists() else {};pins=dict(prior)
 for pid,p in plans.items():
  row={k:p[k] for k in ('plan_id','program','suite','input_digest','mode','stage','initial_fixed8')};row.update(status='HOLD_NOT_RELEASED',classification='missing',raw_status=None,result_path=None,result_sha256=None,uuid=None,cycles=None,S_oracle=None,H=None,historical_DH0_context_cycles=p['historical_DH0_reference']['cycles'],independent_review_status='NOT_YET_FINAL_INDEPENDENT_REVIEW')
  if pid in actual:
   root,point=actual[pid];row['stage']=root.name;row['cohort']=point['cohort'];row['request']=point['request'];pp=root/'control/EXECUTION_PLAN.json';plan=read(pp)
   row['status']='CPU_DRAFT_UNREGISTERED' if plan['preparation_phase']!='SCIENCE_FINAL_FROZEN' else 'UNSTARTED_OR_NOT_REGISTERED'
   ip=root/'control/qualification_ledger'/(point['cohort']+'.INTENT.json')
   if ip.exists():row.update(status='RUNNING_OR_POSTPROCESS_PENDING',uuid=read(ip)['uuid'])
   rp=root/'analysis'/(point['cohort']+'.RESULT.json')
   if rp.exists():
    v=read(rp);h=sha(rp);row.update(raw_status=v.get('state'),result_path=str(rp),result_sha256=h,uuid=v.get('uuid'))
    closed.append([str(rp),h,v.get('uuid'),v.get('state')])
    try:
     require(str(rp) not in prior or prior[str(rp)]==h,'IMMUTABLE_CLOSED_RESULT_CHANGED')
     if v.get('state')!=PASS:
      row.update(status='NEGATIVE_OR_HOLD_RETAINED',classification='negative_or_hold',raw_failure_proof=v.get('proof'),observed_cycles_not_accepted=v.get('cycles'));pins[str(rp)]=h
     else:
      detail=accept_closed(root,point,v,rp,out);row.update(status='ACCEPTED_RUNTIME_CLOSER',classification='accepted',cycles=v['cycles'],**{k:x for k,x in detail.items() if k!='kernel_records'});accepted[p['input_digest'],p['mode']]=(row,detail);pins[str(rp)]=h
    except Exception as e:row.update(status='HOLD_EVIDENCE_VALIDATION',classification='HOLD',validation_error=str(e));errors.append({'result_path':str(rp),'error':str(e)})
  rows.append(row)
 pairs=[];kpairs=[]
 for row in rows:
  key=(row['input_digest'],row['mode']);off=(row['input_digest'],'OFF_MATCHED')
  if row['mode']=='OFF_MATCHED' or key not in accepted:continue
  if off not in accepted:row['pair_status']='MISSING_MATCHED_ACCEPTED_OFF';continue
  a,ad=accepted[key];o,od=accepted[off]
  if any(a[k]!=o[k] for k in ('core_commit','framework_commit','binary_sha256','libcudart_sha256','non_oracle_options_sha256')):row['pair_status']='HOLD_SAMEBUILD_OR_270_MISMATCH';continue
  ak=ad['kernel_records'];ok=od['kernel_records']
  if [(x['kernel'],x['active_instructions'],x['CTA_delta']) for x in ak]!=[(x['kernel'],x['active_instructions'],x['CTA_delta']) for x in ok]:row['pair_status']='HOLD_KERNEL_WORK_MISMATCH';continue
  s=o['cycles']/a['cycles'];h=1-a['cycles']/o['cycles'];row.update(S_oracle=s,H=h,pair_status='MATCHED_ACCEPTED')
  pair={k:row[k] for k in ('program','suite','input_digest','mode','initial_fixed8','cycles','S_oracle','H')};pair.update(OFF_cycles=o['cycles'],OFF_uuid=o['uuid'],Oracle_uuid=a['uuid'],OFF_result_sha256=o['result_sha256'],Oracle_result_sha256=a['result_sha256']);pairs.append(pair)
  for x,y in zip(ak,ok):kpairs.append({**pair,'ordinal':x['ordinal'],'kernel':x['kernel'],'Oracle_kernel_cycles':x['cycles'],'OFF_kernel_cycles':y['cycles'],'kernel_S_oracle':y['cycles']/x['cycles'],'kernel_H':1-x['cycles']/y['cycles'],'Oracle_kernel_exposure':x.get('oracle'),'Oracle_as_printed_counters':x['as_printed_counters'],'OFF_as_printed_counters':y['as_printed_counters'],'Oracle_raw_path':x['raw_path'],'OFF_raw_path':y['raw_path'],'Oracle_strict_sha256':x['strict_sha256'],'OFF_strict_sha256':y['strict_sha256']})
 stats={m:{'CORE32':stat([x for x in pairs if x['mode']==m],32),'fixed8':stat([x for x in pairs if x['mode']==m and x['initial_fixed8']],8),'suites':{s:stat([x for x in pairs if x['mode']==m and x['suite']==s],len({p['input_digest'] for p in plans.values() if p['suite']==s})) for s in sorted({p['suite'] for p in plans.values()})}} for m in MODES[1:]}
 common={}
 for a,b in itertools.combinations(MODES[1:],2):
  aa={x['input_digest']:x for x in pairs if x['mode']==a};bb={x['input_digest']:x for x in pairs if x['mode']==b};keys=sorted(set(aa)&set(bb));common[a+'__'+b]={'common_inputs':keys,a:stat([aa[k] for k in keys],32),b:stat([bb[k] for k in keys],32),'GM_cycles_'+a+'_over_'+b:math.exp(sum(math.log(aa[k]['cycles']/bb[k]['cycles']) for k in keys)/len(keys)) if keys else None}
 report={'schema':'DTC_ORACLE_LIVE_READONLY_SNAPSHOT_V1','authority_commit':AUTH,'generated_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'matrix_sha256':MATRIX_SHA,'closed_result_count':len(closed),'closed_fingerprint_sha256':js(sorted(closed)),'rows':rows,'matched_program_pairs':pairs,'statistics':stats,'mode_common_intersections':common,'status_counts':dict(collections.Counter(x['status'] for x in rows)),'validation_errors':errors,'scientific_starts_by_consumer':0,'CH_budget':0,'boundaries':['Accepted means reported by the frozen runtime strict/archive closer; final independent review remains separately labeled.','S=matched samebuild OFF/Oracle and H=1-Oracle/OFF; negative H is retained.','No historical DH-P0 substitution, per-program best-mode GM, strict mathematical, additive or feasible-DTC upper-bound claim.','As-printed kernel counters do not establish reset/delta timing or a causal critical path; absent is null.','Trace/kernel/per-warp semantics and ROI checks do not prove identical global cross-warp issue order.','Source-event/sidecar checks do not certify original HtoD/capture ELF/native application numerical correctness.']}
 put(out/'TERMINAL_RESULT_PINS.json',pins);put(out/'ORACLE_LIVE_RESULTS.json',report);put(out/'MATCHED_KERNEL_PAIRS.json.gz',{'schema':'DTC_ORACLE_MATCHED_KERNEL_PAIRS_V1','pairs':kpairs},True)
 fields=('program','suite','input_digest','mode','stage','status','classification','raw_status','uuid','cycles','S_oracle','H','result_path','result_sha256')
 with (out/'ORACLE_LIVE_RESULTS.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
 lines=['# Controlled Oracle live results','','Read-only derived snapshot; no model, scientific registration or dispatcher action.','',f'Closed results: {len(closed)}; matched accepted pairs: {len(pairs)}.','','| Mode | Matched / 32 | GM S | Faster / equal / slower |','|---|---:|---:|---:|']
 for m in MODES[1:]:
  z=stats[m]['CORE32'];lines.append(f'| {m} | {z["accepted_pairs"]}/32 | {z["GM_S_oracle"] if z["GM_S_oracle"] is not None else "UNKNOWN"} | {z["faster"]}/{z["equal"]}/{z["slower"]} |')
 lines+=['','All raw statuses, negative/zero/slow cases and missing cells remain. Per-kernel comparisons and actual source/strict/raw/archive SHA references are linked from JSON. Counter correlation is not causal attribution; unprinted values remain null.','','The English v0.23 manuscript, historical science and production Core are unchanged.']
 (out/'REPORT.md').write_text('\n'.join(lines)+'\n');return report
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--base',required=True);ap.add_argument('--matrix',required=True);ap.add_argument('--out',required=True);ap.add_argument('--watch',action='store_true');ap.add_argument('--interval',type=float,default=60);a=ap.parse_args();require(a.interval>=5,'refresh>=5sec')
 while True:
  r=snapshot(a.base,a.matrix,a.out);print(json.dumps({'closed_result_count':r['closed_result_count'],'closed_fingerprint_sha256':r['closed_fingerprint_sha256'],'status_counts':r['status_counts']}),flush=True)
  if not a.watch:break
  time.sleep(a.interval)
if __name__=='__main__':main()
