from pathlib import Path
import json,subprocess,hashlib,gzip,csv,io,collections,datetime,sys,os
sys.dont_write_bytecode=True
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1');O=A/'agents/A_longtail_kernel_mapping_v1';O.mkdir(parents=True,exist_ok=True);G='/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_preparation_20261103_v1/planning-isolated.git';C='47a097aad4406893a07f8d230e1e0a850609bf39';U='dad09cb0487845edc7524ded814c6cde9f0ef6a1';BASE='docs/workload_atlas/';H=lambda b:hashlib.sha256(b).hexdigest();sha=lambda p:H(Path(p).read_bytes());read=lambda p:json.loads(Path(p).read_bytes());blob=lambda p:subprocess.check_output(['git','--git-dir='+G,'show',C+':'+BASE+p]);pins=[];checks=[]
def put(n,v):p=O/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def snapshot(p):
 b=blob(p);d=O/'fixed_atlas'/p;d.parent.mkdir(parents=True,exist_ok=True);d.write_bytes(b);pins.append(dict(commit=C,git_path=BASE+p,sha256=H(b),local_copy=str(d.relative_to(O))));return b
programs=['cutcp','histo','GESUMMV','3DCONV','3MM','myocyte','srad_v1'];dirs={'cutcp':'parboil','histo':'parboil','GESUMMV':'polybench_gpu','3DCONV':'polybench_gpu','3MM':'polybench_gpu','myocyte':'rodinia','srad_v1':'rodinia'}
for p in programs:snapshot('programs/'+dirs[p]+'/'+p+'.md')
phasebytes=snapshot('KERNEL_PHASE_FEATURES_V1R1.tsv');phases=[x for x in csv.DictReader(io.StringIO(phasebytes.decode()),delimiter='\t')if x['program']in programs];assert len(phases)==18
pb=json.loads(snapshot('contributions/parboil/source_hashes.json'));rod=json.loads(snapshot('contributions/rodinia/source_manifest.json'));poly=json.loads(snapshot('contributions/polybench/source_manifest.json'));# preserve small authority records, not all metadata header inventories
sources=[]
need={'cutcp':['main.c','cutoff6overlap.cu','cutoff.h','cutcpu.c','excl.c'],'histo':['main.cu','histo_prescan.cu','histo_intermediates.cu','histo_main.cu','histo_final.cu'],'GESUMMV':['gesummv.cu'],'3DCONV':['3DConvolution.cu'],'3MM':['3mm.cu'],'myocyte':['main.cu','define.c','work.cu','master.cu','solver.cu','embedded_fehlberg_7_8.cu','kernel.cu','kernel_ecc.cu','kernel_cam.cu','kernel_fin.cu'],'srad_v1':['main.cu','define.c','extract_kernel.cu','prepare_kernel.cu','reduce_kernel.cu','srad_kernel.cu','srad2_kernel.cu','compress_kernel.cu']}
app=Path('/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection')
for prog in programs:
 for name in need[prog]:
  if prog in ['cutcp','histo']:
   rel='src/cuda/parboil/benchmarks/'+prog+'/src/cuda/'+name;ref=next(x for x in pb if x['path']==rel);native=app/rel;expected=ref['sha256'];b=native.read_bytes()
  elif prog in ['myocyte','srad_v1']:
   ref=next(x for x in rod if x['program']==prog and Path(x['path']).name==name);rel=ref['path'];native=Path(ref['local_path']);expected=ref['sha256'];b=native.read_bytes()
  else:
   ref=poly[prog][name];native=Path(ref['path']);rel=str(native.relative_to(app));expected=ref['sha256'];b=blob(ref['snapshot']);assert native.read_bytes()==b
  assert H(b)==expected;(O/'source_bytes'/prog).mkdir(parents=True,exist_ok=True);dst=O/'source_bytes'/prog/name;dst.write_bytes(b);sources.append(dict(program=prog,file=name,source_commit=U,source_repo='accel-sim/gpu-app-collection',upstream_path=rel,upstream_url='https://github.com/accel-sim/gpu-app-collection/blob/'+U+'/'+rel,sha256=H(b),lines=len(b.splitlines()),native_readonly_path=str(native),local_copy=str(dst.relative_to(O)),capture_ELF_bound=False));checks.append(prog+'/'+name+'_SHA_matches_fixedAtlas_upstream_manifest')
sourceindex={(x['program'],x['file']):x for x in sources}
def cite(prog,file,a,b):
 x=sourceindex[(prog,file)];assert 1<=a<=b<=x['lines'],(prog,file,a,b,x['lines']);return dict(source_commit=U,upstream_path=x['upstream_path'],sha256=x['sha256'],line_start=a,line_end=b,url=x['upstream_url']+'#L'+str(a)+'-L'+str(b),local_copy=x['local_copy'])
refs={
'cutcp':[('cutoff6overlap.cu',135,277),('cutoff6overlap.cu',340,360),('cutoff6overlap.cu',554,622),('main.c',121,169)],
'histo':[('main.cu',128,201),('histo_prescan.cu',15,84),('histo_intermediates.cu',14,66),('histo_main.cu',14,98),('histo_main.cu',118,189),('histo_final.cu',12,108)],
'GESUMMV':[('gesummv.cu',61,74),('gesummv.cu',104,118),('gesummv.cu',120,153)],
'3DCONV':[('3DConvolution.cu',121,144),('3DConvolution.cu',154,178)],
'3MM':[('3mm.cu',109,122),('3mm.cu',125,138),('3mm.cu',141,154),('3mm.cu',215,254),('3mm.cu',271,280)],
'myocyte':[('main.cu',136,184),('work.cu',113,159),('solver.cu',144,268),('embedded_fehlberg_7_8.cu',199,469),('master.cu',37,92),('kernel.cu',7,124),('kernel_ecc.cu',435,930),('kernel_cam.cu',175,348),('kernel_fin.cu',4,106)],
'srad_v1':[('main.cu',268,429),('reduce_kernel.cu',2,104),('srad_kernel.cu',21,80),('srad2_kernel.cu',20,50)]}
for p in ['srad_v1']:
 for n in ['extract_kernel.cu','prepare_kernel.cu','compress_kernel.cu']:refs[p].append((n,1,sourceindex[(p,n)]['lines']))
allrefs={p:[cite(p,*r)for r in refs[p]]for p in programs}
qualification=read(A/'agents/A_resource_config_v1/CONFIG_INPUT_QUALIFICATION.json');inputs={x['program']:x for x in qualification['inputs24']};plan=read(A/'root_remaining48_proposal_v1/PROPOSED_MATRIX.json')if(A/'root_remaining48_proposal_v1/PROPOSED_MATRIX.json').exists()else read('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1/root_remaining48_proposal_v1/PROPOSED_MATRIX.json');data=[];seq=[];commandrows=[]
expectedcounts={'cutcp':11,'histo':80,'GESUMMV':1,'3DCONV':254,'3MM':3,'myocyte':5993,'srad_v1':502}
for prog in programs:
 x=inputs[prog];bp=Path(x['input_binding']['path']);assert sha(bp)==x['input_binding']['sha256'];bd=read(bp);q=bd['qualification'];assert q['status']=='BODY_COMPLETE_SHA_AND_BASIC_FORMAT_PASS'and not q['issues'];kr=q['rows'];assert len(kr)==expectedcounts[prog];assert [z['ordinal']for z in kr]==list(range(1,len(kr)+1));ep=Path(x['trace_entry']);raw=ep.read_bytes();assert H(raw)==bd['asset']['commandlist_sha256'];commands=[v for v in raw.decode().splitlines()if v.strip()];commands=[v for v in commands if not v.startswith('#')];cmdkernels=[Path(v).name for v in commands if '.traceg'in v];assert cmdkernels==[Path(z['path']).name for z in kr],prog
 symbols=[z['kernel']for z in kr];unique=collections.Counter(symbols);pattern=None
 if prog=='histo':pattern=symbols[:4];assert all(symbols[k:k+4]==pattern for k in range(0,80,4))
 if prog=='3MM':assert ['kernel1'in symbols[0],'kernel2'in symbols[1],'kernel3'in symbols[2]]==[True]*3
 if prog=='srad_v1':pattern=symbols[1:6];assert 'extract'in symbols[0]and'compress'in symbols[-1];assert all(symbols[k:k+5]==pattern for k in range(1,501,5));assert len(pattern)==5
 if prog=='myocyte':assert len(unique)==1 and len(kr)%13==0
 preceding=[];ki=0;copy_count=0;copy_bytes=0;perlaunch=[]
 for ci,cmd in enumerate(commands,1):
  if cmd.startswith('MemcpyHtoD'):
   preceding.append(cmd);copy_count+=1;copy_bytes+=int(cmd.split(',')[-1]);continue
  if '.traceg'not in cmd:commandrows.append(dict(program=prog,input_digest=x['input_digest'],command_ordinal=ci,kind='OTHER',command=cmd));continue
  r=kr[ki];ki+=1;o=r['ordinal'];phase=(('PRESCAN','INTERMEDIATES','MAIN','FINAL')[(o-1)%4]if prog=='histo'else('EXTRACT'if o==1 else'COMPRESS'if o==502 else('PREPARE','REDUCE450','REDUCE1','SRAD','SRAD2')[(o-2)%5])if prog=='srad_v1'else'E'if prog=='3MM'and o==1 else'F'if prog=='3MM'and o==2 else'G'if prog=='3MM'else'RHS'if prog=='myocyte'else'CONV_PLANE'if prog=='3DCONV'else'CUTOFF_PLANE'if prog=='cutcp'else'GESUMMV');item=dict(program=prog,input_digest=x['input_digest'],kernel_ordinal=o,command_ordinal=ci,trace_file=Path(r['path']).name,trace_path=r['path'],trace_sha256=r['sha256'],symbol=r['kernel'],source_phase=phase,complete_CTAs=r['complete_ctas'],active_thread_instructions=r['active_thread_instructions'],declared_body_coverage=r['coverage'],trace_facts_reused_from_binding_SHA=x['input_binding']['sha256'],preceding_HtoD_commands=preceding,source_refs_key=prog,runtime_metrics=None,awaiting_closed_qualified_six_source_evidence=True)
  # Repeated SOURCE grouping is explicitly not application progress.
  if prog=='histo':item['registered_four_kernel_pattern_group']=(o-1)//4+1
  if prog=='srad_v1'and 2<=o<=501:item['registered_five_kernel_pattern_group']=(o-2)//5+1
  if prog=='myocyte':item['accepted_ODE_step_or_adaptive_attempt_id']=None
  seq.append(item);perlaunch.append(len(preceding));preceding=[]
 commandscope=dict(command_count=len(commands),HtoD_command_count=copy_count,HtoD_total_bytes=copy_bytes,HtoD_counts_before_launch_distribution=dict(collections.Counter(perlaunch)),source_CPU_DtoH_and_computation_not_replayed_by_these_commands=True)
 data.append(dict(program=prog,suite=x['suite'],input_digest=x['input_digest'],input_binding=x['input_binding'],trace_entry=x['trace_entry'],commandlist_sha256=H(raw),bundle_id=bd['asset']['bundle_id'],expected=x['expected'],asset_extent=bd['asset']['extent'],capture_complete_native_input=q['capture_complete_native_input'],native_numerical_correctness=q['native_numerical_correctness'],whole_application_semantics='NOT_NEWLY_CERTIFIED',kernel_count=len(kr),ordered_symbols_counts=dict(unique),commands=commandscope,source_refs=allrefs[prog],Atlas_report=next(z for z in pins if z['git_path'].endswith('/'+prog+'.md')),Atlas_phase_ids=[z['phase_id']for z in phases if z['program']==prog],runtime_result_status='NOT_CONSUMED_THIS_PREPARATION;AWAIT_NATURAL_CLOSED_SOURCE_PROVIDER',candidate_ids=[z['candidate_id']for z in plan['candidates']if z['program']==prog]));checks.append(prog+'_exact_kernel_order_count_and_input_binding_identity')
put('SOURCE_BINDINGS.json',dict(Atlas_commit=C,upstream_candidate_commit=U,Atlas_pins=pins,source_files=sources,source_line_refs=allrefs));put('PROGRAM_ROI_AND_SEQUENCE_SUMMARY.json',dict(schema='DTC_REMAINING7_FROZEN_KERNEL_ROI_MAPPING_V1',programs=data,total_registered_kernel_instances=len(seq),source_and_trace_identity_do_not_certify_capture_ELF_or_numerical_or_full_application=True,live_logs_read=0,new_simulations=0,new_traces=0));put('ATLAS_PHASE_ROWS.json',phases)
with (O/'KERNEL_SEQUENCE.json.gz').open('wb')as f:
 with gzip.GzipFile(fileobj=f,mode='wb',mtime=0)as gz:gz.write(json.dumps(dict(schema='DTC_REMAINING7_PER_KERNEL_STATIC_BINDING_V1',rows=seq,other_commands=commandrows),sort_keys=True,separators=(',',':')).encode())
put('CPU_IDENTITY_QUALIFICATION.json',dict(status='PASS',independent_invariants=['Fixed Atlas commit and source-manifest SHA binding','Each chosen source byte matches its fixed upstream content manifest','Source citations are valid1-based line ranges','Exact input binding and commandlist SHA','All q rows ordered kernel sequence matches commandlist','Explicit program pattern/count checks; no application completion inference','No live logs, simulations or scientific identity mutation'],loop_assertion_count=len(checks),checks=checks,programs=7,source_files=len(sources),kernel_instances=len(seq),phase_rows=len(phases),registered_simulator_starts=0,source_changes=0))
print(json.dumps(dict(path=str(O),source_files=len(sources),instances=len(seq),programs=[dict(program=x['program'],kernels=x['kernel_count'],commands=x['commands'])for x in data])))


