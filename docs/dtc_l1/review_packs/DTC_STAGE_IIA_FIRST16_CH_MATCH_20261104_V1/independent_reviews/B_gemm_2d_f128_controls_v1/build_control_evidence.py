from pathlib import Path
import json,re,gzip,hashlib,sys,importlib.util,datetime
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent
A=O.parents[1];P=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_preparation_20261103_v1/agents/B')
sha=lambda b:hashlib.sha256(b).hexdigest()
sp=importlib.util.spec_from_file_location('control_typed',O/'typed_active_path.py');mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
checks=[];check=lambda n,c:(checks.append({'check':n,'pass':bool(c)}),None if c else (_ for _ in ()).throw(AssertionError(n)))
all_data={};typed=[];prewarm=[];source_rows=[]
for prog in ['GEMM','2DCONV']:
 d=json.loads((O/prog/'MATCHED_FOUR_SOURCE_DATA.json').read_text());b=json.loads((O/prog/'INPUT_CONTRACT_PROJECTION.json').read_text());q=b['qualification'];rows=d['four_closed_sources'];by={(r['cell'],r['profile']):r for r in rows};all_data[prog]=d
 check(prog+'_four_unique_closed_identity_pairs',len(by)==4 and len(set(r['uuid']for r in rows))==4)
 check(prog+'_actual_one_kernel_contract',q['expected_kernels']==1 and all(len(r['kernels'])==1 and r['kernels'][0]['kernel']==q['rows'][0]['kernel'] and r['kernels'][0]['instructions']==q['expected_instructions'] and r['kernels'][0]['cumulative_CTA']==q['expected_CTA']for r in rows))
 entry=Path(b['trace_entry']);entryb=entry.read_bytes();check(prog+'_commandlist_SHA_current',sha(entryb)==b['commandlist_sha256']);commands=[x.strip()for x in entryb.decode().splitlines()if x.strip()];check(prog+'_frozen_commands_exact',commands==q['expected_commands']);expected_copy=[x for x in commands if x.startswith('MemcpyHtoD,')]
 headerp=Path(q['rows'][0]['path']);
 with headerp.open('rb')as f:header=f.read(4096).decode(errors='replace')
 headerlines=[x for x in header.splitlines()if x.startswith('-')];gridline=next(x for x in headerlines if 'grid dim' in x);blockline=next(x for x in headerlines if 'block dim' in x);dims=lambda s:[int(x)for x in re.findall(r'\d+',s)]
 grid=dims(gridline);block=dims(blockline);check(prog+'_bounded_header_grid_matches_full_body_CTA',len(grid)==3 and grid[0]*grid[1]*grid[2]==q['expected_CTA'])
 source_rows.append({'program':prog,'evidence_level':'BOUNDED_HEADER_PLUS_EXISTING_FULL_BODY_QUALIFICATION','header_path':str(headerp),'whole_member_SHA_already_frozen':q['rows'][0]['sha256'],'new_header_read_limit':4096,'selected_header_lines':headerlines,'grid':grid,'block':block,'body_qualification_from_input_binding':b['input_binding_path'],'binding_SHA':b['input_binding_sha256']})
 for r in rows:
  typed.append(dict(program=prog,**mod.typed_domains(r)));rawb=gzip.decompress(Path(r['raw_path']).read_bytes());check(prog+r['cell']+r['profile']+'_closed_raw_SHA_repeat',sha(rawb)==r['raw_uncompressed_sha256']);raw=rawb.decode();matches=list(re.finditer(r'^launching memcpy command : (MemcpyHtoD,[^\r\n]+)$',raw,re.M));actual=[m[1].strip()for m in matches];kp=raw.index('Processing kernel ')
  check(prog+r['cell']+r['profile']+'_explicit_memcpy_invocations_before_kernel',actual==expected_copy and all(m.start()<kp for m in matches));opts=r['effective_options'];check(prog+r['cell']+r['profile']+'_fixed_memcpy_no_L2flush_and_clocks',opts['-gpgpu_perf_sim_memcpy']==['1']and opts['-gpgpu_flush_l2_cache']==['0']and opts['-gpgpu_clock_domains']==['1410.0:1410.0:1410.0:850.0'])
  t=r['totals'];tr=r['strict_traffic'];check(prog+r['cell']+r['profile']+'_traffic_matches_strict',t['DRAM_issued_read_atoms32B']==tr['DRAM_issued_read_atoms']and t['DRAM_issued_write_atoms32B']==tr['DRAM_issued_write_atoms']and t['L2_GLOBAL_read_accepted_sectors']==tr['L2_accepted_read_32B_sectors']and r['kernels'][0]['L2_buckets_cumulative']==tr['L2_buckets'])
  controllers=tr['DRAM_controllers'];check(prog+r['cell']+r['profile']+'_20_explicit_DRAM_controllers',set(controllers)==set(map(str,range(20))))
  prewarm.append({'program':prog,'cell':r['cell'],'profile':r['profile'],'RESULT_path':r['RESULT_path'],'RESULT_sha256':r['RESULT_sha256'],'raw_gzip_path':r['raw_path'],'raw_uncompressed_sha256':r['raw_uncompressed_sha256'],'ordered_invocations':[{'raw_line_1based':raw.count('\n',0,m.start())+1,'command':m[1]}for m in matches],'first_processing_kernel_line_1based':raw.count('\n',0,kp)+1,'commands_before_kernel':True,'copy_bytes':sum(int(x.split(',')[2])for x in actual),'perf_memcpy_option':opts['-gpgpu_perf_sim_memcpy'],'L2flush_option':opts['-gpgpu_flush_l2_cache'],'DRAM_20_controller_sums':{k:sum(v[k]for v in controllers.values())for k in ['n_req','n_act','n_pre','n_rd','n_rd_L2_A','n_write','n_wr_bk']},'bounded_header_grid':grid,'bounded_header_block':block,'initial_state_scope':'Runtime invocation plus fixed code establishes state prefill path; not ordinary simulated host-transfer DRAM timing or all-address residency certificate'})
 for cell in ['CH','DH']:
  a,z=by[cell,'P0'],by[cell,'F128'];check(prog+cell+'_only_target_option_changes',next(x for x in d['within_design_changes']if x['cell']==cell)['option_diff']=={'-gpgpu_frfcfs_dram_sched_queue_size':{'P0':['64'],'F128':['128']}})
  check(prog+cell+'_complete_additive_key_sets',set(a['totals'])==set(z['totals']))
  if prog=='GEMM'or cell=='CH':check(prog+cell+'_cycle_additive_L2_and_reason_identity',a['cycles']==z['cycles']and a['totals']==z['totals']and a['kernels'][0]['L2_buckets_cumulative']==z['kernels'][0]['L2_buckets_cumulative']and a['raw_reason_final_explicitly_printed']==z['raw_reason_final_explicitly_printed'])
 if prog=='GEMM':check('GEMM_no_DRAM_data_requests_all_four_closed',all(x['DRAM_20_controller_sums'][k]==0 for x in prewarm if x['program']=='GEMM'for k in ['n_req','n_act','n_pre','n_rd','n_rd_L2_A','n_write','n_wr_bk']))
 for rel in ['atlas/programs/polybench_gpu/'+prog+'.md','atlas/contributions/polybench/source_snapshot/'+prog+'/'+('gemm.cu'if prog=='GEMM'else'2DConvolution.cu')]:
  p=P/rel;blob=p.read_bytes();source_rows.append({'program':prog,'evidence_level':'FIXED_CANDIDATE_SOURCE_NOT_CAPTURE_ELF_BINDING','path':str(p),'sha256':sha(blob),'atlas_commit':'47a097aad4406893a07f8d230e1e0a850609bf39','candidate_source_commit':'dad09cb0487845edc7524ded814c6cde9f0ef6a1','capture_ELF_bound':False})
 check(prog+'_CHcommon_DHOO_fields_never_cross_filled',all((x['CH_common_frontend']is not None and x['DH_PAPER_OO_frontend']is None and x['DH_finite_service']is None)if x['cell']=='CH'else(x['CH_common_frontend']is None and x['DH_PAPER_OO_frontend']['active_OO_PIB_capacity']==128 and x['DH_PAPER_OO_frontend']['OO_PIB_full_events']is None)for x in typed if x['program']==prog))
# Consume established fixed memcpy source path evidence and independently check every source file SHA.
f=A/'agents/B_runtime_analysis_v1/readonly_findings/MEMCPY_INITIAL_L2_STATE_SOURCE_EVIDENCE.json';fb=f.read_bytes();mem=json.loads(fb)
for s in mem['source_refs']:check('fixed_memcpy_source_SHA_'+s['relative_path']+'_'+str(s['line_start']),sha((Path(s['repo'])/s['relative_path']).read_bytes())==s['sha256'])
(O/'CONSUMED_MEMCPY_SOURCE_EVIDENCE.json').write_bytes(fb)
core=Path('/root/data/dtc_failure_repair_20261025_v1/core');cp=core/'src/gpgpu-sim/l2cache.cc';cb=cp.read_bytes();ls=cb.decode().splitlines();source_rows.append({'evidence_level':'FIXED_SIMULATOR_SOURCE','commit':'9eedb3131937748f0492fa83aad37d3691118d70','path':str(cp),'sha256':sha(cb),'start':131,'end':149,'excerpt':'\n'.join(f'{i+1}: {ls[i]}'for i in range(130,149)),'shared_credit_P0':255,'shared_credit_F128':319,'formula':'FRFCFS_queue+return_queue192-(subpartitions2-1); private credit1/subpartition; separate write queue disabled'})
for name,obj in [('TYPED_ACTIVE_PATH_DATA.json',typed),('RUNTIME_MEMCPY_AND_GEOMETRY_WITNESS.json',prewarm),('SOURCE_AND_SCOPE_EVIDENCE.json',source_rows),('ACTIVE_PATH_FIXED_SOURCE.json',mod.active_path_sources())]:(O/name).write_text(json.dumps(obj,indent=2)+'\n')
(O/'CPU_VALIDATION.json').write_text(json.dumps({'schema':'READONLY_CONTROL_SCIENCE_CHECKS_V1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS','checks':checks,'new_model_starts':0,'F256_sources_consumed':0,'all_eight_closed_sources_SHA_verified':True,'both_new_CH_revalidated_by_frozen_readonly_archive_adapter':True},indent=2)+'\n')
print('CHECKS',len(checks),'PASS')
for prog,d in all_data.items():
 print(prog)
 for x in d['within_design_changes']:
  if x['stage']=='TOTAL':print(x['cell'],{k:(v['P0'],v['F128'],v['pct'])for k,v in x['counter_changes'].items()if k in ['DRAM_issued_write_atoms32B','L2_GLOBAL_read_accepted_sectors','gpu_stall_dramfull','L2_total_cache_reservation_fails','DTC_L1_oo_lower_created']})
