#!/usr/bin/env python3
"""Read only frozen qualified provider + closed native outputs; new immutable report only."""
import argparse,collections,csv,gzip,hashlib,json,pathlib,re,time,datetime
P=pathlib.Path
HERE=P(__file__).resolve().parent
A=HERE.parents[1]
RULES=json.loads((HERE/'COUNTER_RULES.json').read_bytes())
ADDITIVE=set(RULES['cumulative_additive'])
GAUGES=set(RULES['terminal_gauges_no_difference'])
PEAKS=set(RULES['running_peaks_no_difference'])
CONFIG=set(RULES['configuration_no_difference'])
UNAVAILABLE=None
sha=lambda b:hashlib.sha256(b).hexdigest()
def hashfile(p):
 h=hashlib.sha256()
 with P(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def readpin(d):
 b=P(d['path']).read_bytes();assert sha(b)==d['sha256'],('SHA',d['path']);return json.loads(b)
def interval(now,prev,first=False):
 return {k:(now[k] if first else now[k]-prev[k]) if k in now and (first or k in prev) and (first or now[k]>=prev[k]) else None for k in sorted(set(now)|set(prev))}
def classified(k):
 if k in ADDITIVE:return 'cumulative_additive'
 if k in GAUGES:return 'terminal_gauge'
 if k in PEAKS:return 'running_peak'
 if k in CONFIG:return 'configuration'
 return 'UNCLASSIFIED_NO_DIFFERENCE'
def ratio(n,d):return n/d if n is not None and d else None
def build_raw(result_pin,binding_pin,cell,profile,program,digest,expected_cycles):
 t=time.monotonic();res=readpin(result_pin);proof=res['proof'];binding=readpin(binding_pin);q=binding['qualification'];qr=q['rows']
 assert proof['performance_accepted'] is True and proof['input_digest']==digest and proof['cell']==cell
 assert res['cycles']==proof['cycles']==expected_cycles
 assert proof['core_commit']=='9eedb3131937748f0492fa83aad37d3691118d70' and proof['framework_commit']=='02775fd795cde5aae1480d81cee6eb481d0a08f4'
 assert proof['binary_sha256']=='02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d'
 bottom=P(res.get('reference_result_path',result_pin['path']));bd=json.loads(bottom.read_bytes());assert bd['uuid']==res['uuid']
 root=bottom.parents[1]/'DTC/run/results'/res['uuid'];ep=root/'NATIVE_EXIT.json';eb=ep.read_bytes();ev=json.loads(eb)
 assert ev['launcher_wait_returncode']==0 and ev['stop_reason'] is None
 raw=root/'raw.log.gz';assert hashfile(raw)==ev['raw_sha256']
 if proof.get('raw_gzip_sha256'):assert proof['raw_gzip_sha256']==ev['raw_sha256']
 blocks=[];b=None;events=[];h=hashlib.sha256();ln=0;controller=None
 def finish(b):
  if b is None:return
  n=b.pop('numeric');b['ordinal']=len(blocks)+1;b['cycles']=n['gpu_sim_cycle'];b['instructions']=n['gpu_sim_insn'];b['cumulative_CTA']=n['gpu_tot_issued_cta'];b['cumulative_cycles']=n['gpu_tot_sim_cycle'];b['cumulative_instructions']=n['gpu_tot_sim_insn'];b['stream']=n['kernel_stream_id']
  v={k:n[k] for k in ADDITIVE if k in n};b['terminal_gauges']={k:n[k]for k in GAUGES if k in n};b['running_peaks']={k:n[k]for k in PEAKS if k in n};b['configuration']={k:n[k]for k in CONFIG if k in n}
  buckets=b.pop('L2_buckets');rs=['HIT','HIT_RESERVED','MISS','SECTOR_MISS'];assert all('GLOBAL_ACC_R:'+k in buckets for k in rs+['TOTAL_ACCESS']);v['L2_GLOBAL_read_accepted_sectors']=sum(buckets['GLOBAL_ACC_R:'+k]for k in rs);assert v['L2_GLOBAL_read_accepted_sectors']==buckets['GLOBAL_ACC_R:TOTAL_ACCESS'];v['L2_GLOBAL_read_miss_sectors']=buckets['GLOBAL_ACC_R:MISS']+buckets['GLOBAL_ACC_R:SECTOR_MISS']
  ctrl=b.pop('controllers');assert set(ctrl)==set(str(i)for i in range(20));v['DRAM_read_atoms32B']=sum(x['n_rd']+x['n_rd_L2_A']for x in ctrl.values());v['DRAM_write_atoms32B']=sum(x['n_write']+x['n_wr_bk']for x in ctrl.values());v['DRAM_controller_n_req']=sum(x['n_req']for x in ctrl.values())
  b['cumulative_additive']=v;b['unclassified_numeric_no_difference']={k:z for k,z in n.items()if k.startswith(('DTC_','L2_'))and classified(k)=='UNCLASSIFIED_NO_DIFFERENCE'}
  prev=blocks[-1]['cumulative_additive']if blocks else {};b['print_boundary_interval_additive']=interval(v,prev,not blocks)
  prevreason=blocks[-1]['positive_only_retry_reasons']if blocks else {};b['positive_only_reason_interval']=interval(b['positive_only_retry_reasons'],prevreason,not blocks)
  d=b['print_boundary_interval_additive'];sample=d.get('DTC_SERVICE_V1_samples');b['finite_service_window']={'samples':sample,'expected_64SM_cycle_samples':64*b['cycles'],'matches_64SM_clock_window':sample==64*b['cycles'] if sample is not None else None,'mean_pib_over_all64SM':ratio(d.get('DTC_SERVICE_V1_pib_integral'),sample),'mean_physical_over_all64SM':ratio(d.get('DTC_SERVICE_V1_physical_integral'),sample),'active_SM_mean_or_peak':'UNAVAILABLE','postready_sum_per_recorded_retired_entry':ratio(d.get('DTC_SERVICE_V1_fully_ready_to_complete_sum'),d.get('DTC_SERVICE_V1_retired')),'not_critical_path_or_per_kernel_request_origin':True}
  ss=['DTC_SERVICE_V1_fully_ready_to_complete_sum','DTC_SERVICE_V1_ready_to_collect_sum','DTC_SERVICE_V1_collection_cycles','DTC_SERVICE_V1_wb_wait']
  if all(k in v for k in ss):assert v[ss[0]]==sum(v[k]for k in ss[1:])
  oo=['DTC_L1_oo_lower_created','DTC_L1_oo_lower_issued','DTC_L1_oo_lower_responses']
  if all(k in v for k in oo):assert len({v[k]for k in oo})==1
  blocks.append(b)
 with gzip.open(raw,'rb') as f:
  for lb in f:
   ln+=1;h.update(lb);line=lb.decode(errors='replace').rstrip('\r\n')
   if line.startswith('launching memcpy command : '):events.append(line.split(' : ',1)[1])
   if line.startswith('Processing kernel '):events.append(P(line[len('Processing kernel '):]).name)
   m=re.match(r'^kernel_name = (\S+)\s*$',line)
   if m:finish(b);b={'kernel':m[1],'raw_stats_begin_line':ln,'numeric':{},'L2_buckets':{},'controllers':{},'positive_only_retry_reasons':{},'latency_tokens_diagnostic_only':{}};controller=None
   if b is None:continue
   m=re.match(r'^\s*(\w+)\s*=\s*(\d+)\s*$',line)
   if m:b['numeric'][m[1]]=int(m[2])
   m=re.match(r'^\s*L2_cache_stats_breakdown\[(\w+)\]\[(\w+)\]\s*=\s*(\d+)\s*$',line)
   if m:b['L2_buckets'][m[1]+':'+m[2]]=int(m[3])
   m=re.match(r'^\s*(\w*fail\w*)\[(\w+)\]\[(\w+)\]\s*=\s*(\d+)\s*$',line)
   if m:b['positive_only_retry_reasons'][m[1]+':'+m[2]+':'+m[3]]=int(m[4])
   m=re.match(r'^DRAM\[(\d+)\]:',line)
   if m:controller=m[1]
   elif controller is not None and line.startswith('n_cmd='):
    z={k:int(v)for k,v in re.findall(r'\b(n_rd|n_rd_L2_A|n_write|n_wr_bk|n_req)=(\d+)',line)};assert len(z)==5;b['controllers'][controller]=z;controller=None
   m=re.match(r'^\s*(avg_mrq_latency|averagemflatency|avg_icnt2mem_latency|avg_icnt2sh_latency)\s*=\s*(\S+)\s*$',line)
   if m:b['latency_tokens_diagnostic_only'][m[1]]=m[2]
 finish(b);assert h.hexdigest()==ev['raw_uncompressed_sha256']
 assert len(blocks)==q['expected_kernels'] and [x['kernel']for x in blocks]==[x['kernel']for x in qr] and [x['instructions']for x in blocks]==[x['active_thread_instructions']for x in qr]
 assert sum(x['cycles']for x in blocks)==expected_cycles and blocks[-1]['cumulative_cycles']==expected_cycles
 assert all(x['stream']==0 for x in blocks), 'SINGLE_STREAM_SCOPE_REQUIRED'
 assert events==q['expected_commands']
 last=blocks[-1]['cumulative_additive'];tr=proof['traffic'];assert last['DRAM_read_atoms32B']==tr['DRAM_issued_read_atoms'] and last['DRAM_write_atoms32B']==tr['DRAM_issued_write_atoms'] and last['L2_GLOBAL_read_accepted_sectors']==tr['L2_accepted_read_32B_sectors']
 sk=proof['kernels'];assert len(sk)==len(blocks)
 for x,y in zip(blocks,sk):assert x['kernel']==y['kernel'] and x['cycles']==y['cycles']
 return {'program':program,'input_digest':digest,'cell':cell,'profile':profile,'RESULT':result_pin,'bottom_RESULT':{'path':str(bottom),'sha256':hashfile(bottom)},'uuid':res['uuid'],'input_binding':binding_pin,'native_EXIT':{'path':str(ep),'sha256':sha(eb)},'raw_gzip':{'path':str(raw),'sha256':ev['raw_sha256']},'raw_uncompressed_sha256':ev['raw_uncompressed_sha256'],'cycles':expected_cycles,'kernels':blocks,'totals':last,'counter_scope':'Cumulative single-stream0; interval differences require explicit endpoints; missing=null/UNAVAILABLE','commands_verified':True,'parsing_wall_seconds':time.monotonic()-t}
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=True)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--provider',required=True);ap.add_argument('--output-dir',required=True);args=ap.parse_args();out=P(args.output_dir).resolve();assert out.is_relative_to(HERE/'snapshots') and not out.exists(),'New output below own snapshots only';out.mkdir(parents=True)
 pins=json.loads((HERE/'DEPENDENCY_PINS.json').read_bytes())
 for x in pins:assert hashfile(x['path'])==x['sha256'],x['path']
 pb=P(args.provider).read_bytes();pr=json.loads(pb);assert pr['schema']=='DTC_PERF_STRUCTURE48_READONLY_PUBLICATION_PROVIDER_V3' and pr['report_only'] and pr['native_writes']==0 and pr['new_models']==0
 assert pr['baseline_source_qualified'] and pr['all_existing_closed_results_qualified'] and pr['admission_hold_metadata_qualified']
 mf=readpin(pr['manifest']);assert mf['files']==pr['files'];assert mf['schema']=='DTC_PERF_STRUCTURE48_SNAPSHOT_MANIFEST_V3';loaded={}
 for x in pr['files']:
  assert P(x['path']).parent==P(pr['snapshot']) and hashfile(x['path'])==x['sha256'] and P(x['path']).stat().st_size==x['bytes']
  loaded[x['name']]=readpin(x) if x['name'].endswith('.json') else None
 s=loaded['SNAPSHOT.json'];assert s['report_overlay_source']['snapshot_source_sha256']=='9dfe6885ec7a7ec30608c677529dacabae78fc959dfd3befdbdc51d83471735e';assert s['report_overlay_source']['family_overlay_source_sha256']=='176e4a6f8c23b426fb0ff1a92ce4469567f841b7c2a3efd5665018ef7661b072'
 rows=[r for r in s['rows']if r['variant']in ['PHYS768_TAG64x8','PHYS1024_TAG64x8','OO_PIB192','TAG4BANK_PERBANK2_TOTAL8']];assert len(rows)==32 and len({(r['input_digest'],r['variant'])for r in rows})==32
 bases={(r['input_digest'],r['source_cell']):r for r in s['baseline_sources']};assert len(bases)==16
 sources={};planned=[];comparisons=[];kernel_comp=[]
 def base(d,c):
  key=(d,c,'P0')
  if key not in sources:
   b=bases[d,c];assert b['accepted'] and b['source_profile']=='P0';readpin(b['actual_bottom_RESULT']);sources[key]=build_raw(b['canonical_RESULT'],b['input_binding'],c,'P0',b['program'],d,b['cycles'])
  return sources[key]
 for r in rows:
  d=r['input_digest'];v=r['variant'];row={k:r.get(k)for k in ['program','suite','input_digest','variant','status','cycles','cohort','uuid','source_RESULT','source_scientific_role','route','science_qualification']};row['counter_evidence']='UNAVAILABLE';row['kernel_evidence']='UNAVAILABLE';row['provider_state_evidence']={k:r.get(k)for k in ['reason','explicit_admission_hold','admission_hold_verification','admission_hold_verification_error','unverified_admission_hold','science_qualification','source_RESULT','native_EXIT']}
  row['UNAVAILABLE_fields']=['OO_no_free_physical_event_counter','OO_pib_full_event_counter','OO_tag_bank_conflict_event_counter','active_SM_occupancy_peak']
  if r['status']=='ACCEPTED_STRICT_ARCHIVE_RESTORE':
   assert r['accepted'] is True
   res=readpin(r['source_RESULT']);sp=readpin(r['source_SPEC']);readpin(r['STRICT']);readpin(r['native_EXIT'])
   for w in r['archive_witness'].values():
    if isinstance(w,dict) and 'path'in w and 'sha256'in w:readpin(w)
   assert res['cycles']==r['cycles'] and res['proof']['structure_variant']==v and res['proof']['downstream_profile']=='P0';binding={'path':sp['input_binding_path'],'sha256':sp['input_binding_sha256']}
   z=build_raw(r['source_RESULT'],binding,'DH',v,r['program'],d,r['cycles']);sources[d,'DH',v]=z;a=base(d,'DH');ch=base(d,'CH');assert len(a['kernels'])==len(z['kernels'])==len(ch['kernels'])
   sd=a['cycles']/z['cycles'];assert abs(sd-r['S_DH'])<1e-12 and abs(ch['cycles']/z['cycles']-r['Rnew'])<1e-12
   diff={k:{'P0':a['totals'].get(k),'candidate':z['totals'].get(k),'delta':z['totals'][k]-a['totals'][k]if k in z['totals']and k in a['totals']else None}for k in sorted(ADDITIVE)}
   comp={'program':r['program'],'suite':r['suite'],'input_digest':d,'variant':v,'cycles':{'CH_P0':ch['cycles'],'DH_P0':a['cycles'],'DH_candidate':z['cycles']},'S_DH':sd,'I':sd,'Rold':ch['cycles']/a['cycles'],'Rnew':ch['cycles']/z['cycles'],'response':'ZERO_EXACT_CYCLES'if a['cycles']==z['cycles']else'POSITIVE'if sd>1 else'NEGATIVE','within_DH_additive_changes':diff,'cross_CH_DH_structural_events_equivalent':False,'fact':'Closed matched simulator replay only.','causal_attribution':'UNCONFIRMED: counters may correlate; no isolated critical-path occupancy/time observation.'};comparisons.append(comp)
   for x,y,c in zip(a['kernels'],z['kernels'],ch['kernels']):
    assert x['kernel']==y['kernel']==c['kernel'] and x['instructions']==y['instructions']==c['instructions'];kernel_comp.append({'program':r['program'],'input_digest':d,'variant':v,'ordinal':x['ordinal'],'kernel':x['kernel'],'CH_P0_cycles':c['cycles'],'DH_P0_cycles':x['cycles'],'candidate_cycles':y['cycles'],'within_DH_cycle_delta':y['cycles']-x['cycles'],'within_DH_additive_changes':{k:{'P0':x['print_boundary_interval_additive'].get(k),'candidate':y['print_boundary_interval_additive'].get(k),'delta':y['print_boundary_interval_additive'][k]-x['print_boundary_interval_additive'][k]if y['print_boundary_interval_additive'].get(k)is not None and x['print_boundary_interval_additive'].get(k)is not None else None}for k in sorted(ADDITIVE)}})
   row.update(counter_evidence='VERIFIED_CLOSED_RAW_EXPLICIT_ENDPOINTS',kernel_evidence='VERIFIED_CLOSED_RAW_ORDER_AND_INSTRUCTION_CONTRACT',S_DH=sd,Rold=comp['Rold'],Rnew=comp['Rnew'],I=sd,response=comp['response'])
  else:assert not r.get('accepted');row['cycles']=None
  planned.append(row)
 dump(out/'PROVIDER_CAPTURE.json',pr);dump(out/'SOURCE_PROVIDER_RECEIPT.json',{'path':str(P(args.provider)),'sha256':sha(pb),'manifest':pr['manifest'],'files':pr['files'],'source_dependency_pins':pins,'new_models':0,'native_writes':0,'live_raw_read':False});dump(out/'PLANNED32.json',planned);dump(out/'TAG16_SAFETY_HOLD.json',[{k:r.get(k)for k in ['program','input_digest','variant','status','cycles','reason']}for r in s['rows']if r not in rows]);dump(out/'MATCHED_COMPARISONS.json',comparisons)
 with (out/'KERNEL_CYCLES.csv').open('w',newline='')as f:
  fields=['program','input_digest','variant','ordinal','kernel','CH_P0_cycles','DH_P0_cycles','candidate_cycles','within_DH_cycle_delta'];w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(kernel_comp)
 detail={'counter_rules':RULES,'sources':list(sources.values()),'matched_kernels':kernel_comp}
 (out/'KERNEL_COUNTER_EVIDENCE.json.gz').write_bytes(gzip.compress((json.dumps(detail,ensure_ascii=True,separators=(',',':'))+'\n').encode(),mtime=0))
 with (out/'PLANNED32.csv').open('w',newline='')as f:
  fs=['program','suite','input_digest','variant','status','cycles','S_DH','I','Rold','Rnew','response','counter_evidence'];w=csv.DictWriter(f,fieldnames=fs,extrasaction='ignore');w.writeheader();w.writerows(planned)
 counts=dict(collections.Counter(r['status']for r in planned));summary={'planned_nonTag':32,'planned_inputs':8,'planned_families':4,'status_counts':counts,'accepted_mechanism_comparisons':len(comparisons),'closed_sources_parsed':len(sources),'kernel_source_rows':sum(len(r['kernels'])for r in sources.values()),'response_counts':dict(collections.Counter(r['response']for r in comparisons)),'not_CORE32_population':True,'no_best_stitching_or_partial_GM':True,'all32_mechanism_complete':len(comparisons)==32,'scientific_negatives_and_unused_HOLD_are_not_performance':True,'raw_audit_scope':'Closed raw and witness metadata recheck; no repeat full archive chunk/tar restore audit beyond qualified V3 provider and SHA-witness metadata','new_models':0,'native_writes':0};dump(out/'SUMMARY.json',summary)
 text=['# Fixed eight-input structural mechanism evidence','',f'Accepted matched points: {len(comparisons)}/32. Statuses: {counts}. This is the fixed eight-input exploratory set, not the previous CORE32 workload population.','', 'Facts: only accepted strict/archive/native-restore provider rows are read as performance. Raw gzip/plain SHA, source binding, exact ordered symbols/instructions, commandlist, strict cycles and traffic are rechecked. Each source is parsed once. Missing fields are UNAVAILABLE/null; negative and unused HOLD have no cycles. No per-program best configuration GM is made.','', 'Counter boundary: kernel cycles/instructions reset; L2/DRAM/DTC additive fields are cumulative; interval deltas require explicit monotone endpoints. Gauges, running peaks and latency means are not differenced. Finite-service integrals/samples cover all64 SMs and clock windows, not active-SM peak/mean. Postready per recorded retire is not critical-path delay. Positive-only retry omissions are unavailable. MSHR entry and merge events are distinct retries, not occupancy/time.','', 'Architecture/source facts: physical expansion retains512 lookup Tag mappings;128B slot arithmetic is nominal capacity, not PPA. PIB192 also expands bounded lower-create queue. Tag service2/8 is a quota change, not evidence of8 grants/cycle in the integrated path. CH common frontend and DH OO events remain separate. Static source/candidate ELF correspondence, numeric full-application validity and OO host-upload coherence remain unproven. Simulated HtoD may prefill L2, so zero DRAM pressure is not proof of compute-bound behavior.','', 'Correlation/hypothesis: within-DH kernel counter changes can accompany measured cycle changes; they do not isolate critical-path causality. If cycles are identical, report exact-cycle zero response only for that closed candidate. Do not extrapolate a family or other inputs.','', 'Follow-up suggestions (no automatic execution): (1) read-only compare all accepted same-family results and explicit retry/service endpoints, retaining negative/zero cases; (2) read-only check whether changed kernels change demand volume or only service-event sums; (3) new authorization needed for per-SM occupancy histograms or origin-linked queue/wait instrumentation; (4) separately authorize numerical/coherence validation before stronger application-validity claims.','']
 for c in comparisons:text.append(f"- {c['program']} {c['variant']}: {c['response']}; DH0={c['cycles']['DH_P0']}, candidate={c['cycles']['DH_candidate']}, S_DH={c['S_DH']:.9f}, Rnew={c['Rnew']:.9f}.")
 (out/'README.md').write_text('\n'.join(text)+'\n');dump(out/'CPU_CONSUMPTION_RECEIPT.json',{'success':True,'dependencies_verified':len(pins),'raw_sources_verified':len(sources),'accepted_points':len(comparisons),'model_starts':0,'native_writes':0,'live_raw_reads':0})
 files=[{'name':str(p.relative_to(out)),'bytes':p.stat().st_size,'sha256':hashfile(p)}for p in sorted(out.rglob('*'))if p.is_file()];assert all(p['bytes']<=8*1024*1024 for p in files);dump(out/'MANIFEST.json',{'schema':'DTC_STRUCTURAL_MECHANISM_READONLY_SNAPSHOT_V1','files':files,'new_models':0,'native_writes':0});print(json.dumps({'output':str(out),'manifest_sha256':hashfile(out/'MANIFEST.json'),'summary':summary}))
if __name__=='__main__':main()
