from pathlib import Path
from fractions import Fraction
import json,gzip,hashlib,re,math,datetime,subprocess
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1');B=A/'agents/B_completed_short_programs_v1';O=A/'agents/C_five_completed_programs_review_v1';rd=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();checks=[]
def ck(n,b,detail=None):checks.append({'check':n,'PASS':bool(b),'detail':detail});assert b,n
MANIFEST_EXPECTED='f3905ebdd86f3d67da889bebb9dc0ac98360dc658388ba7f2e4d574521ee3b9d'
ck('Frozen five-program manifest and all members',sha(B/'MANIFEST.json')==MANIFEST_EXPECTED and all(sha(B/z['path'])==z['sha256']for z in rd(B/'MANIFEST.json')['files']))
D=json.loads(gzip.decompress((B/'CLOSED_SOURCE_KERNEL_COUNTERS.json.gz').read_bytes()));by={};rawsummaries=[];synthetic={'DRAM_read_atoms32B','DRAM_write_atoms32B','DRAM_controller_n_req','L2_GLOBAL_read_accepted_sectors','L2_GLOBAL_read_miss_sectors'}
for r in D['rows']:
 key=r['program'],r['cell'],r['profile'];by[key]=r;rawb=gzip.decompress(Path(r['raw_gzip_path']).read_bytes());raw=rawb.decode();rr=rd(r['RESULT_path']);ex=rd(r['native_exit_path']);bind=rd(r['input_binding_path']);ks=r['kernels'];marks=list(re.finditer(r'^kernel_name = (\S+)',raw,re.M));blocks=[raw[m.start():marks[i+1].start()if i+1<len(marks)else len(raw)]for i,m in enumerate(marks)];ident=sha(r['RESULT_path'])==r['RESULT_sha256']and sha(r['raw_gzip_path'])==r['raw_gzip_sha256']and hashlib.sha256(rawb).hexdigest()==r['raw_plain_sha256']and sha(r['native_exit_path'])==r['native_exit_sha256']and sha(r['input_binding_path'])==r['input_binding_sha256']and ex['stop_reason']is None and ex['launcher_wait_returncode']==0 and rr['proof']['performance_accepted']and rr['cycles']==r['cycles']==sum(k['cycles']for k in ks)and len(ks)==len(blocks)==r['kernel_count']==bind['qualification']['expected_kernels']and r['core_commit']=='9eedb3131937748f0492fa83aad37d3691118d70'and r['framework_commit']=='02775fd795cde5aae1480d81cee6eb481d0a08f4'and r['binary_sha256']=='02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d';counterok=True
 for i,(block,k)in enumerate(zip(blocks,ks)):
  nums={a:int(b)for a,b in re.findall(r'^\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*(-?\d+)\s*$',block,re.M)};buckets={a+':'+b:int(c)for a,b,c in re.findall(r'L2_cache_stats_breakdown\[(\w+)\]\[(\w+)\]\s*=\s*(\d+)',block)};types={typ:sum(v for x,v in buckets.items()if x.startswith(typ+':')and x.split(':')[1]in ['MISS','SECTOR_MISS'])for typ in {x.split(':')[0]for x in buckets}};dr=[]
  for l in block.splitlines():
   if l.startswith('n_cmd='):dr.append({a:int(v)for a,v in re.findall(r'(n_\w+)=(\d+)',l)})
  vals={'L2_GLOBAL_read_accepted_sectors':sum(buckets['GLOBAL_ACC_R:'+z]for z in ['HIT','HIT_RESERVED','MISS','SECTOR_MISS']),'L2_GLOBAL_read_miss_sectors':buckets['GLOBAL_ACC_R:MISS']+buckets['GLOBAL_ACC_R:SECTOR_MISS'],'DRAM_read_atoms32B':sum(x['n_rd']+x['n_rd_L2_A']for x in dr),'DRAM_write_atoms32B':sum(x['n_write']+x['n_wr_bk']for x in dr),'DRAM_controller_n_req':sum(x['n_req']for x in dr)};curr=k['selected_cumulative'];prior={}if i==0 else ks[i-1]['selected_cumulative'];want={f:curr.get(f)if i==0 else curr[f]-prior[f]if f in curr and f in prior else None for f in set(curr)|set(prior)};counterok &=len(dr)==20 and all(all(f in x for f in ['n_rd','n_rd_L2_A','n_write','n_wr_bk','n_req'])for x in dr)and all(nums.get(f)==v for f,v in curr.items()if f not in synthetic)and all(vals[f]==curr[f]for f in synthetic)and types==k['L2_type_miss_sectors']and sum(types.values())==nums['L2_total_cache_misses']and want==k['print_interval_additive']and nums['gpu_sim_cycle']==k['cycles']and k['kernel']==marks[i].group(1)and k['instructions']==bind['qualification']['rows'][i]['active_thread_instructions']
  reasons={a+':'+b+':'+c:int(d)for a,b,c,d in re.findall(r'(L2_cache_stats_fail_breakdown|Total_core_cache_fail_stats_breakdown)\[(\w+)\]\[(\w+)\]\s*=\s*(\d+)',block)};counterok &=reasons==k['positive_only_retry_reasons']
 ck(':'.join(key)+' naturalclosed source/input/build/ROI identity',ident);ck(':'.join(key)+' numeric/type/20controller/endpoint counters rawverified',counterok)
 commands=[]
 for no,line in enumerate(raw.splitlines(),1):
  if line.startswith('launching memcpy command : '):commands.append({'raw_line':no,'kind':'MEMCPY','command':line.split(' : ',1)[1]})
  if line.startswith('Processing kernel '):commands.append({'raw_line':no,'kind':'KERNEL','command':Path(line[len('Processing kernel '):]).name})
 ck(':'.join(key)+' actualorderedmemcpy commands matchfrozen list and warmoptions',commands==r['runtime_commands']and [x['command']for x in commands]==r['expected_commands']==bind['qualification']['expected_commands']and r['effective_options']['-gpgpu_perf_sim_memcpy']==['1']and r['effective_options']['-gpgpu_flush_l2_cache']==['0'])
 rawsummaries.append({'program':r['program'],'cell':r['cell'],'profile':r['profile'],'RESULT_sha256':r['RESULT_sha256'],'raw_gzip_sha256':r['raw_gzip_sha256'],'kernel_count':len(ks),'cycles':r['cycles']})
programs={'transpose','mri-q','sad','sgemm','particlefilter_float'}
ck('Fixed five programs and exact 30 six-cell sources',len(D['rows'])==30 and set(r['program']for r in D['rows'])==programs and all({(r['cell'],r['profile'])for r in D['rows']if r['program']==p}=={(c,f)for c in ['CH','DH']for f in ['P0','F128','F256']}for p in programs))
comp=rd(B/'MATCHED_COMPARISONS.json');zero_responses=[];facts=[]
for r in comp:
 prog,pf=r['program'],r['profile'];p0,ch,d0,dh=[by[prog,c,p]for c,p in [('CH','P0'),('CH',pf),('DH','P0'),('DH',pf)]];metrics={'S_CH':Fraction(p0['cycles'],ch['cycles']),'S_DH':Fraction(d0['cycles'],dh['cycles']),'R':Fraction(ch['cycles'],dh['cycles']),'I':Fraction(ch['cycles']*d0['cycles'],p0['cycles']*dh['cycles'])};ok=all(math.isclose(r['metrics'][k],float(v),rel_tol=1e-13)for k,v in metrics.items());allzero=True;deltas_bycell={}
 for cell,p,v in [('CH',p0,ch),('DH',d0,dh)]:
  w=r['within_design'][cell];deltas=[b['cycles']-a['cycles']for a,b in zip(p['kernels'],v['kernels'])];exact=all(d==0 for d in deltas);ok &=w['cycle_delta']==v['cycles']-p['cycles']and w['all_kernel_cycles_identical']==exact and w['all_selected_final_additive_identical']==(p['totals']==v['totals'])and[w['cycles_delta']for w in w['kernel_cycle_changes']]==deltas;allzero &=exact and p['totals']==v['totals'];deltas_bycell[cell]=deltas
  diff={k:[p['effective_options'].get(k),v['effective_options'].get(k)]for k in set(p['effective_options'])|set(v['effective_options'])if p['effective_options'].get(k)!=v['effective_options'].get(k)};ck(prog+cell+pf+' option changes only F',diff=={'-gpgpu_frfcfs_dram_sched_queue_size':[['64'],['128'if pf=='F128'else'256']]})
 ck(prog+pf+' integer ratios, exact kernel deltas and zero semantics',ok)
 if allzero:zero_responses.append(prog+pf)
 if prog=='mri-q':ck('MRI-Q '+pf+' exact nonzero K2/K3/K4',deltas_bycell['CH']==[0,0,0,0]and deltas_bycell['DH']==[0,-321,4,-2]and d0['cycles']==360174 and dh['cycles']==359855)
 facts.append({'program':prog,'profile':pf,'cycles':{'CH_P0':p0['cycles'],'CH_F':ch['cycles'],'DH_P0':d0['cycles'],'DH_F':dh['cycles']},'metrics':{k:{'numerator':v.numerator,'denominator':v.denominator,'float':float(v)}for k,v in metrics.items()},'exact_kernel_cycle_deltas':deltas_bycell,'both_designs_cycles_and_selected_final_counters_exactly_unchanged':allzero})
ck('10 fixed comparisons; 8 exact zero responses and MRI small DH improvement',len(comp)==10 and len(zero_responses)==8 and set(z[:-4]for z in zero_responses)==programs-{'mri-q'})
zeroDRAM=[]
for prog in sorted(programs):
 rs=[r for r in D['rows']if r['program']==prog];none=all(all(r['totals'][f]==0 for f in ['DRAM_read_atoms32B','DRAM_write_atoms32B','DRAM_controller_n_req'])for r in rs)
 ck(prog+' six-source traffic explicitly zero versus missing',all(all(isinstance(r['totals'][f],int)for f in ['DRAM_read_atoms32B','DRAM_write_atoms32B','DRAM_controller_n_req'])for r in rs))
 if none:zeroDRAM.append(prog)
ck('Only transpose has explicitly zero DRAM read/write/request counts in all six sources',zeroDRAM==['transpose'])
# Independently recompute all proposed symbol groups from listed endpoint intervals.
for g in rd(B/'CANDIDATE_SYMBOL_PHASE_SUMMARIES.json'):
 r=by[g['program'],g['cell'],g['profile']];ks=[r['kernels'][i-1]for i in g['ordinals']];ok=all(k['kernel']==g['kernel_symbol_phase']for k in ks)and sum(k['cycles']for k in ks)==g['cycles_sum']
 for f,item in g['additive_sums'].items():
  vals=[k['print_interval_additive'].get(f)for k in ks];missing=sum(v is None for v in vals);ok &=item['missing_intervals']==missing and item['value']==(None if missing else sum(vals))
 ck(g['program']+g['cell']+g['profile']+' group '+g['kernel_symbol_phase'],ok)
for s in rd(B/'CANDIDATE_SOURCE_BINDINGS.json'):
 ck('Candidate source bytes '+s['copy'],sha(B/s['copy'])==s['sha256']and not s['capture_ELF_bound'])
for s in rd(B/'INPUT_AND_CAPTURE_BINDINGS.json'):
 ck('Input semantic boundary '+s['program'],s['no_CAPTURE_ELF_source_promotion']and sha(s['input_binding_path'])==s['input_binding_sha256'])
for r in rd(B/'FIXED_SIMULATOR_SOURCE_SEMANTICS.json'):
 lines=Path(r['path']).read_text().splitlines();ck('Core source witness '+Path(r['path']).name,sha(r['path'])==r['sha256']and all(e['text']=='\n'.join(str(i)+': '+lines[i-1]for i in range(e['start'],e['end']+1))for e in r['excerpts']))
for r in rd(B/'CONSUMED_MEMCPY_SOURCE_EVIDENCE.json')['source_refs']:
 p=Path(r['repo'])/r['relative_path'];lines=p.read_text().splitlines();ck('Memcpy source witness '+r['relative_path']+str(r['line_start']),sha(p)==r['sha256']and r['excerpt']=='\n'.join(str(i)+': '+lines[i-1]for i in range(r['line_start'],r['line_end']+1)))

for r in D['rows']:
 prior={}
 for i,k in enumerate(r['kernels']):
  curr=k['positive_only_retry_reasons'];want={f:curr[f]if i==0 and f in curr else curr[f]-prior[f]if f in curr and f in prior else None for f in set(curr)|set(prior)}
  ck(r['program']+r['cell']+r['profile']+' K'+str(i+1)+' positive-only reason endpoint null rule',want==k['positive_only_reason_interval']);prior=curr
for prog in programs:
 for cell in ['CH','DH']:
  x,y=by[prog,cell,'F128'],by[prog,cell,'F256'];ck(prog+cell+' F128/F256 all interval equality',[k['cycles']for k in x['kernels']]==[k['cycles']for k in y['kernels']]and[k['print_interval_additive']for k in x['kernels']]==[k['print_interval_additive']for k in y['kernels']])
for pf in ['P0','F128','F256']:
 tr=by['transpose','CH',pf];ck('Transpose write-miss and non-DRAM admission counter '+pf,tr['totals']['gpu_stall_dramfull']>0 and tr['totals']['L2_total_cache_misses']==tr['final_type_miss_sectors']['GLOBAL_ACC_W']==32768)
 ch,dh=by['particlefilter_float','CH',pf],by['particlefilter_float','DH',pf];pg=[g for g in rd(B/'CANDIDATE_SYMBOL_PHASE_SUMMARIES.json')if g['program']=='particlefilter_float'and g['profile']==pf];likelihood={g['cell']:g['cycles_sum']for g in pg if'likelihood'in g['kernel_symbol_phase']};ck('Particlefilter absolute negative and phase offset '+pf,dh['cycles']-ch['cycles']==239748 and likelihood['DH']-likelihood['CH']==374391 and (dh['cycles']-ch['cycles'])-(likelihood['DH']-likelihood['CH'])==-134643)
 for r,expected in [(ch,[14,4,4,2]),(dh,[182,4,255,2])]:ck('Particlefilter DRAM first4 explicit intervals '+r['cell']+pf,[k['print_interval_additive']['DRAM_read_atoms32B']for k in r['kernels']]==expected+[0]*32)

report=(B/'REPORT.md').read_text();ck('REPORT read as frozen bytes',bool(report)and sha(B/'MANIFEST.json')==MANIFEST_EXPECTED)
assert not O.exists();O.mkdir()
res={'schema':'C_REMAINING48_FIVE_COMPLETED_PROGRAMS_NARROW_REVIEW_V1','UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS','checks_all_PASS':True,'checks':checks,'count':len(checks),'frozen_B_manifest_sha256':MANIFEST_EXPECTED,'scope':{'programs':sorted(programs),'closed_sources':30,'comparisons':10,'exact_zero_responses_both_designs':8,'not_core32_GM_conclusion':True,'not_all48_final_review':True},'raw_sources_rehashed':rawsummaries,'exact_recomputed_comparisons':facts,'explicit_zero_DRAM_programs':zeroDRAM,'units_and_limits':['L2 accepted/miss counts are32B sectors; DRAM read/write commands are32B atoms, request-object counts are separately recorded.','Only explicit cumulative endpoints are differenced. Missing positive-only reason endpoints are not inferred zero; mean/peak/gauge values are excluded from grouped additive sums.','Transpose write misses coexist with zero measured DRAM traffic under fixed memcpy forced L2 fill and lazy write allocation. This is not proof of compute-bound execution, general real-GPU state, or final dirty-data drain.','MRI-Q DH total minus319 cycles combines K2 minus321, K3 plus4, K4 minus2; K1 unchanged. CH is exact zero response. This does not establish a unique critical-path queue cause.','Static source/symbol grouping is candidate evidence, not bound capture ELF, numerical correctness or full-application certification. Frozen whole-declared-trace identities are retained.','CH active commonPIB256 and DH activeOO128 have distinct meanings; capacity/cost equality is not claimed. F profiles also change shared credits.','No further archive body audit is duplicated in this narrow mechanism review. Full lifecycle/typed restoration is reserved for the final48 audit.'],'live_raw_read':False,'new_models_or_registration_owner_history_Git_actions':0}
(O/'REVIEW.json').write_text(json.dumps(res,indent=2)+'\n');(O/'README.md').write_text('Five completed short-program narrow independent review: PASS.\n\nThirty closed sources cover transpose, mri-q, sad, sgemm and particlefilter_float, each CH/DH by P0/F128/F256. Raw identity, all ordered kernel cycles, literal counters,20-controller traffic at every print boundary, explicit endpoint differences and symbol-group sums were independently recomputed. Eight comparisons preserve exact zero cycle and selected-final-counter responses; MRI-Q has CH unchanged and DH360174 to359855, with kernel deltas0,-321,+4,-2. Only transpose has explicit zero measured DRAM read/write/request counts across all six sources.\n\nThe report retains memcpy-prefill and write-miss boundaries, distinct request/32B units, candidate-source status, missing-counter semantics and causal limits. This is not a CORE32 suite result or full48 lifecycle final review. No live raw, model, control, history, paper or Git mutation was used.\n');print(json.dumps({'status':'PASS','checks':len(checks),'sources':len(rawsummaries),'review_sha256':sha(O/'REVIEW.json')}))
