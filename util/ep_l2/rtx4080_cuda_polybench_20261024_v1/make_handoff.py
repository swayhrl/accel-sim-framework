from pathlib import Path
import json,hashlib,re,time,collections
R=Path('/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1');P=Path('/data/c16/rtx4080_suite_fill_20261024_v1');records=[];seen=set()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for root in [R/'native_control']:
 for p in sorted(root.glob('NATIVE_BATCH_*.json')):
  for x in json.loads(p.read_text()):
   out=x.get('output');rec=Path(out)/'NATIVE_RECEIPT.json' if out else None
   if rec and rec.is_file() and str(rec) not in seen:records.append((rec,x));seen.add(str(rec))
for name in ['sdk42_hist13_v3','sdk42_histogram_atomic_v1','sdk42_scan_sync_v1','poly_repair2_v4']:
 p=P/'control'/('NATIVE_BATCH_'+name+'.json')
 if p.exists():
  for x in json.loads(p.read_text()):
   rec=Path(x['output'])/'NATIVE_RECEIPT.json'
   if str(rec) not in seen:records.append((rec,x));seen.add(str(rec))
for p in sorted((P/'attempts').glob('polybench_1_0_*/native_attempt*/NATIVE_RECEIPT.json')):
 if str(p) not in seen:records.append((p,json.loads(p.read_text())));seen.add(str(p))
ov={}
for name in ['SOURCE_REVIEW_QUALIFICATIONS_V1.json','SOURCE_REVIEW_QUALIFICATIONS_V2.json']:
 p=R/'native_control'/name
 if p.exists():
  for x in json.loads(p.read_text()):ov[x['task_id']]={'status':x['qualified_native_status'],'receipt':str(p),'receipt_sha256':sha(p),'details':x.get('evidence')}
for name in ['BICUBIC_ALL5_INDEPENDENT_CPU_V1.json','IMAGEDENOISING_ALL4_REFERENCE_CHECK_V1.json']:
 p=R/'native_control'/name
 if p.exists():
  for x in json.loads(p.read_text()):ov[x['task_id']]={'status':x['status'],'receipt':str(p),'receipt_sha256':sha(p),'details':x}
states=[];candidates=[];keys=set()
for path,x in records:
 j=x.get('task',{});n=j.get('program','UNKNOWN');task=j.get('task_id',n+'_'+hashlib.sha256(json.dumps(j,sort_keys=True).encode()).hexdigest()[:12]);out=Path(x.get('output',path.parent));logp=out/'stdout.log';text=logp.read_text(errors='replace') if logp.exists() else '';kind=j.get('workload_kind','FINITE_GPU_WORKLOAD');rc=x.get('exit');numeric='NOT_INDEPENDENTLY_ESTABLISHED';cap='PENDING_PRODUCER_AND_CONSUMER_PROFILE'
 if task in ov:numeric=ov[task]['status']
 elif 'SDK42_HOST_ADAPTER_QA_PASSED' in text:numeric='UPSTREAM_SAMPLE_REPORTED_PASS'
 elif rc==0 and re.search(r'(?i)\bPASSED\b|Test success|Test Succeeded|Test Successful|returned OK|Results Match',text):numeric='UPSTREAM_SAMPLE_REPORTED_PASS'
 elif 'SDK42_HOST_ADAPTER_QA_FAILED' in text:numeric='UPSTREAM_SAMPLE_REPORTED_FAIL'
 if kind=='OFFICIAL_TESTRUN_CPU_REFERENCE_ONLY':cap='NO_CUDA_WORK_CPU_CONFIGURATION'
 elif n in ['deviceQuery','deviceQueryDrv'] or kind=='GPU_COPY_API_ONLY_NO_SASS_KERNEL_EXPECTED':cap='NO_SASS_EXPECTED_API_ONLY'
 elif n=='simpleP2P' and x.get('status')=='PLATFORM_UNAVAILABLE_REQUIRES_2_GPUS':cap='SINGLE_GPU_PLATFORM_UNAVAILABLE'
 elif n=='simpleAssert':cap='EXPECTED_DEVICE_ASSERT_DIAGNOSTIC_ONLY';numeric='EXPECTED_ASSERT_NOT_FUNCTIONAL_CORRECTNESS'
 elif 'failed to open display' in text:cap='CURRENT_HEADLESS_GL_CONTEXT_ADAPTER_REQUIRED';numeric='NOT_EXECUTED_GPU_PATH'
 elif rc is None:cap='NOT_EXECUTED_RETAINED'
 elif rc!=0:cap='FAILED_EXECUTION_DIAGNOSTIC_CAPTURE_ONLY'
 if n=='clock':numeric='TIMING_PROBE_NO_RESULT_REFERENCE'
 if n=='segmentationTreeThrust':numeric='EXECUTION_ONLY_NO_GOLDEN_REFERENCE'
 flags=[]
 if n in ['matrixMulDynlinkJIT','matrixMulDrv','ptxjit','simpleTextureDrv','threadMigration','vectorAddDrv']:flags+=['DRIVER_API_OR_JIT_LOADED_CODE_PROFILE_REQUIRED']
 if n=='threadMigration':flags+=['MULTIPLE_CPU_THREADS_AND_CUDA_CONTEXTS']
 if n in ['convolutionFFT2D','oceanFFT','matrixMul','MonteCarlo','MonteCarloMultiGPU']:flags+=['VERIFY_LOADED_LIBRARY_ARCH_AND_CALLS_IF_PRESENT']
 if n in ['bicubicTexture','bilateralFilter','boxFilter','simpleTexture','simpleTextureDrv','simpleTexture3D','simpleCubemapTexture','simpleLayeredTexture','simplePitchLinearTexture','simpleSurfaceWrite','volumeRender','volumeFiltering','imageDenoising']:flags+=['TEXTURE_OR_SURFACE_PROFILE_REQUIRED']
 if n in ['marchingCubes','volumeFiltering'] and 'Bucky' not in task:flags+=['UPSTREAM_FILE_FLAG_ALSO_SELECTS_RAW_VOLUME_SOURCE']
 if n=='FDTD-2D' and 'repair' not in j.get('variant','').lower():flags+=['CANONICAL_GHOST_BOUNDARY_INITIALIZATION_UNDEFINED']
 if n=='GRAMSCHM' and 'repair' not in j.get('variant','').lower():flags+=['CANONICAL_RANK1_NUMERICAL_DEGENERACY']
 state={'task_id':task,'suite':j.get('suite'),'source_version':j.get('version'),'program':n,'canonical_program':'FDTD2D' if n=='FDTD-2D' else n,'variant':j.get('variant'),'argv':j.get('argv'),'binary_sha256':j.get('binary_sha256'),'native_exit':rc,'raw_native_classifier_status':x.get('status'),'numerical_status':numeric,'capture_disposition':cap,'profile_flags':flags,'native_receipt':str(path),'native_receipt_sha256':sha(path),'stdout_sha256':sha(logp) if logp.exists() else None,'independent_qualification':ov.get(task),'science_acceptance':False,'simulation_started':False};states.append(state)
 if rc==0 and cap=='PENDING_PRODUCER_AND_CONSUMER_PROFILE':
  content={'binary_sha256':j.get('binary_sha256'),'argv':j.get('argv',[])[1:],'input_files':sorted(f.get('sha256','') for f in j.get('input_files',j.get('inputs',[])))};key=hashlib.sha256(json.dumps(content,sort_keys=True).encode()).hexdigest()
  if key not in keys:
   q=dict(j);q.update(candidate_content_id=key,native_state=state,readiness='NATIVE_EXECUTED_PROFILE_PENDING',producer_semantic_profile='NOT_GRANTED_BY_ASSET_PREPARATION',copy_input_policy='INDEPENDENT_REGULAR_FILE_COPIES_IN_ABSENT_ATTEMPT',capture_scope='ALL_CUDA_KERNELS_OF_EXACT_INVOCATION_NO_SAMPLING_NO_WARMUP_REMOVAL');candidates.append(q);keys.add(key)
(R/'manifests/ALL_NATIVE_ASSET_STATES_V1.json').open('x').write(json.dumps(states,indent=2)+'\n');(R/'manifests/ALL_CAPTURE_CANDIDATES_PROFILE_PENDING_V1.json').open('x').write(json.dumps(candidates,indent=2)+'\n');summary={'native_attempt_records':len(states),'unique_candidate_content_objects':len(candidates),'disposition_counts':dict(collections.Counter(x['capture_disposition'] for x in states)),'numerical_status_counts':dict(collections.Counter(x['numerical_status'] for x in states)),'all_science_acceptance_false':True,'officialSDK429_source_programs':82,'old_source_snapshot_programs':73,'modern_mapped_programs':73,'modern_exact_invocations':103,'no_formal_capture_started_by_this_lane':True,'unix':time.time()};(R/'manifests/PREPARATION_HANDOFF_SUMMARY_V1.json').open('x').write(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
