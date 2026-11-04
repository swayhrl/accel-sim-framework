from pathlib import Path
import json,gzip,re,hashlib,datetime,collections,argparse
ROOT=Path(__file__).resolve().parent;O=ROOT;A=ROOT.parents[1];R=Path('/root/data/dtc_stage_iia_remaining48_20261104_v1');sha=lambda b:hashlib.sha256(b).hexdigest()
SNAP=A/'agents/B_runtime_analysis_v1/snapshot_runner_v1/snapshots/20261104T014550071642Z_5263ab47';MF_SHA='1292c386ef93ba0a49772b608a13310fe772db77611f769cc0082c0c35ea9a80';ap=argparse.ArgumentParser();ap.add_argument('--provider',type=Path);ap.add_argument('--output-dir',type=Path);args=ap.parse_args()
provider_at_capture=None
if args.provider:
 pb=args.provider.read_bytes();provider_at_capture=json.loads(pb);assert provider_at_capture['source_qualified']is True and provider_at_capture['request']=='DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1'and provider_at_capture['schema']=='DTC_STAGEII_REMAINING48_ANALYSIS_PUBLICATION_PROVIDER_V1';SNAP=Path(provider_at_capture['snapshot']);MF_SHA=provider_at_capture['manifest']['sha256']
if args.output_dir:
 O=args.output_dir.resolve();assert O.is_relative_to((ROOT/'updates').resolve())and not O.exists();O.mkdir(parents=True,exist_ok=False)
else:assert not(O/'MANIFEST.json').exists(),'FROZEN_PACKAGE_USE_NEW_UPDATE_CHILD'
mb=(SNAP/'MANIFEST.json').read_bytes();assert sha(mb)==MF_SHA;mf=json.loads(mb);assert mf['source_qualified']is True and mf['schema']=='DTC_REMAINING48_READONLY_ANALYSIS_SNAPSHOT_V1'and mf['adapter']['sha256']=='0383daa67804db3b92779f2520cbbc0978c195c759e27357938319c942442e1c'and mf['runtime_plan']['sha256']=='9f257eeea3ebe81610a88cef8ad37512b54bdb50728f965e8d73ccf5dd89a4b3';files={x['name']:x for x in mf['files']};loaded={}
for name,x in files.items():
 b=Path(x['path']).read_bytes();assert sha(b)==x['sha256'];
 if name.endswith('.json.gz'):loaded[name]=json.loads(gzip.decompress(b))
core=next(v for k,v in loaded.items()if'CORE32_RESULTS.json.gz'in k);obs=next(v for k,v in loaded.items()if'OBSERVATIONS.json.gz'in k);summary=next(v for k,v in loaded.items()if'SUMMARY.json.gz'in k);assert obs['request']=='DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1'and obs['source_qualified']is True and obs['registration_granted']is True and summary['accepted_CH']+summary['archived_negative_CH']==48 and summary['verification_hold']==summary['await_result']==0 and summary['registered_consumed']==48 and summary['registered_remaining']==0 and summary['all_registered48_terminal_verified']is True
programs=[x for x in core['all_programs']if x['population_origin']=='AUTHORIZED_REMAINING24'];accepted_obs={r['cohort']:r for r in obs['observations']if r['accepted']};assert len(accepted_obs)==summary['accepted_CH'];closed=[];checks=[]
def check(n,v):
 assert v,n;checks.append({'check':n,'pass':True})
def hashfile(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def interval(now,prior,first):
 out={}
 for k in set(now)|set(prior):
  if k not in now or (not first and k not in prior):out[k]=None
  else:
   v=now[k]if first else now[k]-prior[k];assert v>=0;out[k]=v
 return out
selected=['L2_total_cache_accesses','L2_total_cache_misses','L2_total_cache_reservation_fails','gpu_stall_dramfull','DTC_L1_tag_conflicts','DTC_L1_pib_full_events','DTC_L1_oo_lower_created','DTC_L1_oo_valid_hits','DTC_L1_oo_pending_hits','DTC_L1_oo_new_misses','DTC_L1_oo_tag_evictions','DTC_SERVICE_V1_samples','DTC_SERVICE_V1_pib_integral','DTC_SERVICE_V1_retired','DTC_SERVICE_V1_fully_ready_to_complete_sum','DTC_SERVICE_V1_wb_wait']
for program in programs:
 digest=program['input_digest'];specp=R/'control/specs'/(program['six_source_cells']['CH_F128']['source_registered_slot_cohort']+'.json');spec=json.loads(specp.read_bytes());bp=Path(spec['input_binding_path']);bb=bp.read_bytes();assert sha(bb)==spec['input_binding_sha256'];binding=json.loads(bb);q=binding['qualification'];qrows=q['rows'];expectedcommands=q['expected_commands']
 for cell in['CH','DH']:
  for profile in['P0','F128','F256']:
   sr=program['six_source_cells'][cell+'_'+profile]
   if not sr['accepted']:continue
   p=Path(sr['source_RESULT_path']);rb=p.read_bytes();assert sha(rb)==sr['source_RESULT_sha256'];result=json.loads(rb);proof=result['proof'];assert proof['performance_accepted']and proof['input_digest']==digest and proof['cell']==cell and proof.get('profile',proof.get('downstream_profile'))==profile;assert result['cycles']==sr['cycles'];assert proof['core_commit']=='9eedb3131937748f0492fa83aad37d3691118d70'and proof['framework_commit']=='02775fd795cde5aae1480d81cee6eb481d0a08f4'and proof['binary_sha256']=='02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d';original=Path(result.get('reference_result_path',str(p)));root=original.parents[1]/'DTC/run/results'/result['uuid'];exitp=root/'NATIVE_EXIT.json';eb=exitp.read_bytes();ev=json.loads(eb);assert ev['launcher_wait_returncode']==0 and ev['stop_reason']is None;rawp=root/'raw.log.gz';assert hashfile(rawp)==ev['raw_sha256'];plain=hashlib.sha256();blocks=[];block=None;events=[];linecount=0;pending_controller=None
   def finish(b):
    if b is None:return
    n=b.pop('numeric');b['gauge_snapshot_no_differencing']={k:n[k]for k in ['DTC_L1_pib_occupancy','DTC_L1_lower_outstanding','DTC_L1_oo_inflight_current','DTC_L1_oo_pib_occupancy','DTC_L1_oo_active_refs','DTC_L1_oo_physical_allocated']if k in n};b['running_peak_snapshot_no_differencing']={k:v for k,v in n.items()if k.startswith('DTC_')and'peak'in k};b['stream']=n.get('kernel_stream_id');b['cycles']=n['gpu_sim_cycle'];b['instructions']=n['gpu_sim_insn'];b['cumulative_CTA']=n['gpu_tot_issued_cta'];b['cumulative_instructions']=n['gpu_tot_sim_insn'];b['cumulative_cycles']=n['gpu_tot_sim_cycle'];b['selected_cumulative']={k:n[k]for k in selected if k in n};bucket=b['L2_buckets'];readstatuses=['HIT','HIT_RESERVED','MISS','SECTOR_MISS'];assert all('GLOBAL_ACC_R:'+k in bucket for k in readstatuses+['TOTAL_ACCESS']);reads=sum(bucket['GLOBAL_ACC_R:'+k]for k in readstatuses);assert reads==bucket['GLOBAL_ACC_R:TOTAL_ACCESS'];readmiss=bucket['GLOBAL_ACC_R:MISS']+bucket['GLOBAL_ACC_R:SECTOR_MISS'];assert len(b['controllers'])==20;ctrl=b['controllers'];dr=sum(v['n_rd']+v['n_rd_L2_A']for v in ctrl.values());dw=sum(v['n_write']+v['n_wr_bk']for v in ctrl.values());req=sum(v['n_req']for v in ctrl.values());b['selected_cumulative'].update(L2_GLOBAL_read_accepted_sectors=reads,L2_GLOBAL_read_miss_sectors=readmiss,DRAM_read_atoms32B=dr,DRAM_write_atoms32B=dw,DRAM_controller_n_req=req);types=sorted(set(k.split(':')[0]for k in bucket));type_misses={k:bucket[k+':MISS']+bucket[k+':SECTOR_MISS']if k+':MISS'in bucket and k+':SECTOR_MISS'in bucket else None for k in types};b['L2_type_miss_sectors']=type_misses;b['L2_type_miss_sum_matches_all_L2']=all(v is not None for v in type_misses.values())and sum(type_misses.values())==n['L2_total_cache_misses'];b.pop('L2_buckets');b.pop('controllers');blocks.append(b)
   with gzip.open(rawp,'rb')as fh:
    for lineb in fh:
     plain.update(lineb);linecount+=1;line=lineb.decode(errors='replace').rstrip('\r\n')
     if line.startswith('launching memcpy command : '):events.append({'raw_line':linecount,'kind':'MEMCPY','command':line.split(' : ',1)[1]})
     if line.startswith('Processing kernel '):events.append({'raw_line':linecount,'kind':'KERNEL','command':Path(line[len('Processing kernel '):]).name})
     km=re.match(r'^kernel_name = (\S+)[ \t]*$',line)
     if km:
      finish(block);block={'kernel':km[1],'raw_stats_begin_line':linecount,'numeric':{},'L2_buckets':{},'controllers':{},'positive_only_retry_reasons':{},'printed_latency_tokens':{}};pending_controller=None
     if block is None:continue
     n=re.match(r'^\s*(\w+)\s*=\s*(\d+)\s*$',line)
     if n:block['numeric'][n[1]]=int(n[2])
     b=re.match(r'^\s*L2_cache_stats_breakdown\[(\w+)\]\[(\w+)\]\s*=\s*(\d+)\s*$',line)
     if b:block['L2_buckets'][b[1]+':'+b[2]]=int(b[3])
     fr=re.match(r'^\s*(\w*fail\w*)\[(\w+)\]\[(\w+)\]\s*=\s*(\d+)\s*$',line)
     if fr:block['positive_only_retry_reasons'][fr[1]+':'+fr[2]+':'+fr[3]]=int(fr[4])
     dc=re.match(r'^DRAM\[(\d+)\]:',line)
     if dc:pending_controller=dc[1]
     elif pending_controller is not None and line.startswith('n_cmd='):
      v={k:int(value)for k,value in re.findall(r'\b(n_rd|n_rd_L2_A|n_write|n_wr_bk|n_req)=(\d+)',line)};assert set(v)=={'n_rd','n_rd_L2_A','n_write','n_wr_bk','n_req'};block['controllers'][pending_controller]=v;pending_controller=None
     latency=re.match(r'^\s*(avg_mrq_latency|averagemflatency|avg_icnt2mem_latency|avg_icnt2sh_latency)\s*=\s*(\S+)\s*$',line)
     if latency:block['printed_latency_tokens'][latency[1]]=latency[2]
   finish(block);assert plain.hexdigest()==ev['raw_uncompressed_sha256'];check(program['program']+cell+profile+'_complete_raw_SHA_and_contract',len(blocks)==q['expected_kernels']and [b['kernel']for b in blocks]==[r['kernel']for r in qrows]and[b['instructions']for b in blocks]==[r['active_thread_instructions']for r in qrows]and sum(b['cycles']for b in blocks)==result['cycles']);check(program['program']+cell+profile+'_runtime_commandlist_exact',[x['command']for x in events]==expectedcommands);prior={};prior_reasons={}
   for ordinal,b in enumerate(blocks,1):
    b['ordinal']=ordinal;b['print_interval_additive']=interval(b['selected_cumulative'],prior,ordinal==1);b['positive_only_reason_interval']={k:(v if ordinal==1 else v-prior_reasons[k]if k in prior_reasons else None)for k,v in b['positive_only_retry_reasons'].items()};prior=b['selected_cumulative'];prior_reasons=b['positive_only_retry_reasons']
   final=blocks[-1];traffic=proof['traffic'];check(program['program']+cell+profile+'_strict_traffic_reconciliation',final['selected_cumulative']['DRAM_read_atoms32B']==traffic['DRAM_issued_read_atoms']and final['selected_cumulative']['DRAM_write_atoms32B']==traffic['DRAM_issued_write_atoms']and final['selected_cumulative']['L2_GLOBAL_read_accepted_sectors']==traffic['L2_accepted_read_32B_sectors']);scope='SINGLE_STREAM_ZERO_CUMULATIVE'if all(b['stream']==0 for b in blocks)else'MIXED_STREAM_COUNTER_SCOPE_UNRESOLVED'
   closed.append({'program':program['program'],'suite':program['suite'],'input_digest':digest,'cell':cell,'profile':profile,'source_role':sr['source_role'],'RESULT_path':str(p),'RESULT_sha256':sha(rb),'uuid':result['uuid'],'cycles':result['cycles'],'native_exit_path':str(exitp),'native_exit_sha256':sha(eb),'raw_gzip_path':str(rawp),'raw_gzip_sha256':ev['raw_sha256'],'raw_plain_sha256':ev['raw_uncompressed_sha256'],'input_binding_path':str(bp),'input_binding_sha256':sha(bb),'core_commit':proof['core_commit'],'framework_commit':proof['framework_commit'],'binary_sha256':proof['binary_sha256'],'effective_options':proof['effective_options'],'kernel_scope':scope,'kernel_count':len(blocks),'kernels':blocks,'totals':final['selected_cumulative'],'final_type_miss_sectors':final['L2_type_miss_sectors'],'final_type_miss_sum_matches_all_L2':final['L2_type_miss_sum_matches_all_L2'],'runtime_commands':events,'expected_commands':expectedcommands,'strict_latency_diagnostic_only':proof.get('latency_counters')})
rows_by={(r['input_digest'],r['cell'],r['profile']):r for r in closed};comparisons=[]
for p in programs:
 ident=p['input_digest']
 for profile in['F128','F256']:
  if not p['six_source_cells']['CH_'+profile]['accepted']:continue
  pp={c:rows_by[ident,c,'P0']for c in['CH','DH']};vv={c:rows_by[ident,c,profile]for c in['CH','DH']};sc=pp['CH']['cycles']/vv['CH']['cycles'];sd=pp['DH']['cycles']/vv['DH']['cycles'];metric={'S_CH':sc,'S_DH':sd,'R':vv['CH']['cycles']/vv['DH']['cycles'],'I':sd/sc};check(p['program']+profile+'_provider_metrics_exact',all(abs(metric[k]-p['metrics_by_profile'][profile][k])<1e-12 for k in metric));designs={}
  for c in['CH','DH']:
   a,z=pp[c],vv[c];changes=[{'ordinal':x['ordinal'],'kernel':x['kernel'],'cycles_P0':x['cycles'],'cycles_variant':y['cycles'],'cycles_delta':y['cycles']-x['cycles']}for x,y in zip(a['kernels'],z['kernels'])];ct={k:{'P0':a['totals'].get(k),'variant':z['totals'].get(k),'delta':z['totals'][k]-a['totals'][k]if k in a['totals']and k in z['totals']else None}for k in sorted(set(a['totals'])|set(z['totals']))};designs[c]={'cycle_delta':z['cycles']-a['cycles'],'all_kernel_cycles_identical':all(v['cycles_delta']==0 for v in changes),'all_selected_final_additive_identical':a['totals']==z['totals'],'kernel_cycle_changes':changes,'changed_kernels_only':[v for v in changes if v['cycles_delta']!=0],'counter_changes':ct}
  comparisons.append({'program':p['program'],'suite':p['suite'],'input_digest':ident,'profile':profile,'metrics':metric,'within_design':designs})
check('exact_accepted_comparison_and_closed_source_counts',len(comparisons)==len(accepted_obs) and len(closed)==4*len(programs)+len(accepted_obs));check('all_counter_scopes_single_stream_zero',all(r['kernel_scope']=='SINGLE_STREAM_ZERO_CUMULATIVE'for r in closed));check('no_counter_type_miss_conservation_gap',all(r['final_type_miss_sum_matches_all_L2']for r in closed));receipt={'source_qualified_snapshot_manifest':{'path':str(SNAP/'MANIFEST.json'),'sha256':MF_SHA},'provider_pointer_observed_at_start_sha256':sha(pb)if provider_at_capture else'e1b0e1cbf67b931911edd6203df9efd3d1b6ecd4efb933a25a31c48469f9b6db','as_of_utc':summary['observed_utc'],'source_summary':summary,'files':mf['files'],'closed_newCH_n':len(accepted_obs),'new_program_n':len(programs),'all_32_population_not_reselected':True,'no_partial_GM_in_this_analysis':True}
(O/'SOURCE_SNAPSHOT_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');(O/'CLOSED_SOURCE_KERNEL_COUNTERS.json.gz').write_bytes(gzip.compress((json.dumps({'schema':'DTC_REMAINING48_CLOSED_SAMPLE_KERNEL_EVIDENCE_V1','rows':closed,'counter_catalog_commit':'Core9eed/FW02775','scope_warning':'Selected final additive counters cumulative; explicit endpoint differences only; means/gauges/peaks never differenced; positive-only omissions missing'},indent=2)+'\n').encode(),mtime=0));(O/'MATCHED_COMPARISONS.json').write_text(json.dumps(comparisons,indent=2)+'\n');(O/'CPU_VALIDATION.json').write_text(json.dumps({'checks':checks,'all_pass':True,'count':len(checks),'new_models_or_runtime_actions':0,'live_raw_read':False,'no_partial_GM':True},indent=2)+'\n');print('PROGRAMS',len(programs),'CLOSED',len(closed),'COMP',len(comparisons),'CHECKS',len(checks))
for x in comparisons:
 print(x['program'],x['profile'],x['metrics'],'CHchanges',x['within_design']['CH']['changed_kernels_only'],'DHchanges',x['within_design']['DH']['changed_kernels_only'])
