from pathlib import Path
import json,re,shlex,hashlib,subprocess,collections
R=Path('/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1');a=json.loads((R/'manifests/SDK42_MIGRATION_V118_BUILDS_V6.json').read_text());queue=[];den=[]
for row in a:
 n=row['program'];d=Path(row['migration_path']);mk=(d/'Makefile').read_text();m=re.search(r'^testrun:.*\n((?:\t.*\n|\n)*)',mk,re.M);commands=[]
 if m:
  for line in m.group(1).splitlines():
   line=line.strip().replace('$(EXEC)','').strip()
   if not line or line.startswith('#'):continue
   if line.startswith('./'):commands.append(shlex.split(line))
 no_predefined_commands=not commands
 if not commands:commands=[[str(row.get('binary',d/d.name))]]
 if n=='nbody':commands.append([str(row['binary']),'-qatest'])
 data=[{'relative_path':str(p.relative_to(d)),'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted((d/'data').rglob('*')) if p.is_file()]
 srcs=[{'relative_path':str(p.relative_to(d)),'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(d.rglob('*')) if p.is_file() and p.suffix in ['.cu','.cpp','.h','.cuh','.c','.ptx']]
 bins=row.get('binary');elf=''
 if bins:
  cp=subprocess.run(['/usr/local/cuda-12.8/bin/cuobjdump','--list-elf',bins],capture_output=True,text=True);elf=cp.stdout
  if n!='matrixMulDynlinkJIT':assert 'sm_89' in elf,(n,elf)
 for i,tokens in enumerate(commands):
  q={'suite':'CUDA Samples','version':'v11.8','source_head':'81992093d2b8c33cab22dbf6852c070c330f1715','program':n,'sample_path':str(d),'source_files':srcs,'input_files':data,'task_id':'cuda118_'+n+'_'+str(i),'variant':('finite_source_default_no_testrun' if no_predefined_commands else 'official_testrun_'+str(i)),'argv':([bins]+tokens[1:]) if bins else tokens,'binary_sha256':row.get('binary_sha256'),'binary_cubin_listing':elf,'build_status':'PASS_FIXED_ELF' if bins else 'MISSING_ELF_DEPENDENCY','runtime_env':row.get('runtime_env',{}),'cwd_policy':'Create ABSENT attempt directory; link data/ read-only to fixed input directory, outputs stay in attempt','runtime_links':[{'name':'data','target':str(d/'data')}] if (d/'data').is_dir() else [],'correctness':{'exit':0,'stdout_regex':'(?i)(passed|test.*pass|result.*pass)'},'native_timeout_sec':600,'capture_timeout_sec':21600,'capture_max_bytes':80*1024**3,'capture_scope':'ALL GPU kernels, no warmup removal, no iteration truncation, no sampling','historical_relation':'Independently frozen official CUDA Samples v11.8 migration; not claimed original SDK4.2 or historic capture9.1 binary'}
  if n=='bandwidthTest':q['workload_kind']='GPU_COPY_API_ONLY_NO_SASS_KERNEL_EXPECTED';q['correctness']={'exit':0,'stdout_regex':'(?i)(result.*pass|test.*pass|bandwidth)'}
  elif n=='simpleAssert':q['workload_kind']='EXPECTED_DEVICE_ASSERT_NEGATIVE_API_TEST';q['capture_eligibility']='DIAGNOSTIC_ONLY_TERMINAL_ASSERT_NOT_REGULAR_TRACE'
  elif n=='simpleP2P':q['platform_requirement']='At least2 CUDA GPU devices;109currently1RTX4080, expect native WAIVED';q['capture_eligibility']='PENDING_MULTIGPU_PLATFORM'
  elif n=='nbody' and '-cpu' in q['argv']:q['workload_kind']='OFFICIAL_TESTRUN_CPU_REFERENCE_ONLY';q['capture_eligibility']='NO_GPU_WORK_IN_THIS_ARGV'
  elif n=='simpleMPI':q['workload_kind']='MPI_SINGLE_RANK_GPU_COMPUTE';q['platform_requirement']='PrivateOpenMPI installed; direct launch MPI_Init single-rank is allowed by source'
  elif n=='matrixMulDynlinkJIT':q['capture_eligibility']='RUNTIME_JIT_CUBIN_IDENTITY_MUST_BE_FROZEN';q['correctness']={'exit':0,'stdout_regex':'(?i)pass'}
  else:q['workload_kind']='FINITE_GPU_WORKLOAD'
  if row.get('device_helper_patch'):q['device_helper_patch']=row['device_helper_patch']
  if n=='bilateralFilter' and '-radius=7' in q['argv'] and '-file=ref_08.ppm' in q['argv']:q['upstream_testrun_issue']='OfficialMakefile radius7 pairedref08; retain original row even if numericFAIL, correctedradius8 must distinct variant'
  queue.append(q)
 den.append({'program':n,'official_testrun_commands':commands,'no_testrun_commands':no_predefined_commands,'real_binary_present':bool(bins),'source_file_count':len(srcs),'data_file_count':len(data),'task_count':len(commands)})
(R/'manifests/CUDA_SAMPLES_V118_FULL_DENOMINATOR_V1.json').write_text(json.dumps(den,indent=2)+'\n');(R/'manifests/CUDA_SAMPLES_V118_ALL_TESTRUN_QUEUE_V1.json').write_text(json.dumps(queue,indent=2)+'\n');print('programs',len(den),'tasks',len(queue),'realELF',sum(x['real_binary_present'] for x in den),'datafiles',sum(x['data_file_count'] for x in den));print('nocommands',[x['program'] for x in den if x['no_testrun_commands']])
