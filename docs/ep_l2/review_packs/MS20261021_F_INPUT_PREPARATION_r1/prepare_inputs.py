"""Prepare saved-input dossiers. Never opens trace bodies, compiles, downloads or launches.

The single historical 2048-byte FWT header observation is described as a prior
bounded read; this script reuses all complete body hashes/statistics.
"""
from pathlib import Path
import collections,csv,datetime,hashlib,json,os,subprocess

ROOT=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-f-env-v1')
OUT=Path(__file__).resolve().parent
E=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1')
D=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-d-analysis-v1')
APP=Path('/workspace/worktrees/gpu-app-collection-decoupled-l2')
ORIG=Path('/workspace/worktrees/accel-sim-decoupled-l2')
RESEARCH=E/'docs/ep_l2/review_packs/MS20261021_E2_CAPACITY_DIAGNOSTIC_r1/workload_research_r1'
DS=D/'docs/ep_l2/mechanism_study_2026_10_19_v1/lane_d'
AUDIT=DS/'input_suitability_20261020_r1'
FWT_OLD=Path('/workspace/ep_l2_ms20261019_e_results/E011_618407f0')
FWT_ORACLE=DS/'full_system_v2/readonly_evidence/FWT_7_21'
APP_COMMIT=subprocess.check_output(['git','-C',str(APP),'rev-parse','HEAD'],text=True).strip()
SOURCES={}

def small(path):
    p=Path(path)
    if p.name.endswith(('.traceg','.traceg.gz','.tracez')):
        raise ValueError('Trace body reads prohibited: '+str(p))
    if p.stat().st_size>2**20:raise ValueError('Not a small source/metadata file: '+str(p))
    return p.read_bytes()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def reference(path):
    p=Path(path);raw=small(p);r={'path':str(p),'bytes':len(raw),'sha256':sha(raw),'read_scope':'SMALL_SOURCE_OR_SAVED_METADATA'}
    for repo in [E,D,APP,ORIG]:
        if p.is_relative_to(repo):
            relative=str(p.relative_to(repo));head=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
            r.update(repository=str(repo),repository_HEAD=head,repository_path=relative)
            blob=subprocess.run(['git','-C',str(repo),'show',head+':'+relative],capture_output=True)
            r['matches_tracked_HEAD']=blob.returncode==0 and sha(blob.stdout)==r['sha256']
            break
    SOURCES[str(p)]=r
    return r
def load(path):reference(path);return json.loads(small(path))
def write(path,data):
    p=OUT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def state(path):
    p=Path(path);r={'path':str(p),'exists':p.is_file()}
    if p.is_file():
        s=p.stat();r.update(bytes=s.st_size,mtime_ns=s.st_mtime_ns,device=s.st_dev,inode=s.st_ino,readable=os.access(p,os.R_OK))
    return r
def composite(rows):return sha(json.dumps(sorted(rows,key=lambda r:r['name']),sort_keys=True,separators=(',',':')).encode())
def missing(key,owner,scope,need,observed):return dict(id=key,owner=owner,scope=scope,required_evidence=need,observed=observed,status='MISSING')

# Consume the whole named research pack without invoking its inventory generator.
for p in sorted(RESEARCH.iterdir()):
    if p.is_file() and p.suffix in ['.md','.json','.py']:reference(p)
inventory=load(RESEARCH/'LOCAL_COVERAGE_INVENTORY.json')
decision=load(RESEARCH/'DECISION_REPORT.json')
selection=load(DS/'input_registrations/FWT_7_21.json')
proposal=load(AUDIT/'SGEMM_PROPOSAL_TO_E.json')
candidates=load(AUDIT/'EXISTING_CANDIDATE_MANIFESTS.json')
sg_audit=next(x for x in load(AUDIT/'CANDIDATE_AUDIT.json')['results'] if x['workload']=='sgemm')
sg_source=next(x for x in candidates['candidates'] if x['workload']=='sgemm')
sg_registration=load(E/'docs/ep_l2/review_packs/MS20261020_E2_MAIN_ROLLING_r1/EXPLORATORY_SGEMM_REGISTRATION.json')
fw_atomic=load(FWT_OLD/'atomic_scope.json')
fw_native=next(x for x in load(FWT_OLD/'native_input_semantics.json')['workloads'] if x['workload']=='FWT_7_21')
fw_audit=load(FWT_OLD/'input_audit.json')
fw_scope=load(FWT_OLD/'current_input_scope_binding.json')
fw_oracle=load(FWT_ORACLE/'manifest.json')
fw_history=[load(Path('/workspace/ep_l2_ms20261019_e_results')/n/'run_status.json') for n in ['E011_618407f0','E012_63be0bb4']]
exit_scope=load(Path('/workspace/ep_l2_ft20261016_shared/mechanism_study_20261019_v1/inbox/E2_TO_D_FWT_EXECUTION_EVIDENCE_SCOPE.json'))
wave=load(D/'docs/l2_char_v1/ROUND1_WAVE1_TRACE_MANIFEST.json')
sg_old=next(x for x in wave['trace_body_sha256'] if x['workload']=='sgemm')
for p in [DS/'main61_attribution_20261020_r2/CANDIDATE_DECISION.md',DS/'main61_attribution_20261020_r2/CANDIDATE_SHORTLIST.csv',AUDIT/'REPLAY_REPRODUCIBILITY_AND_COST_SCOPE.md']:
    reference(p)
appfiles=['README.md','src/README.md','get_data.sh','src/Makefile','src/setup_environment',
 'src/cuda/NVIDIA_CUDA-11.0_Samples/fastWalshTransform/fastWalshTransform.cu',
 'src/cuda/NVIDIA_CUDA-11.0_Samples/fastWalshTransform/fastWalshTransform_kernel.cuh',
 'src/cuda/NVIDIA_CUDA-11.0_Samples/fastWalshTransform/fastWalshTransform_gold.cpp',
 'src/cuda/NVIDIA_CUDA-11.0_Samples/fastWalshTransform/Makefile',
 'src/cuda/parboil/benchmarks/sgemm/DESCRIPTION',
 'src/cuda/parboil/benchmarks/sgemm/src/cuda/main.cu',
 'src/cuda/parboil/benchmarks/sgemm/src/cuda/sgemm_kernel.cu',
 'src/cuda/parboil/benchmarks/sgemm/src/cuda/io.cc',
 'src/cuda/parboil/benchmarks/sgemm/src/cuda/Makefile',
 'src/cuda/parboil/benchmarks/sgemm/tools/compare-output',
 'src/cuda/parboil/common/platform/cuda.default.mk',
 'src/cuda/parboil/common/mk/cuda.mk','src/cuda/parboil/README.buildsystem','src/cuda/parboil/parboil']
apprefs=[reference(APP/p) for p in appfiles]
yaml_ref=reference(ORIG/'util/job_launching/apps/define-all-apps.yml')
reference(ORIG/'util/job_launching/run_simulations.py')

fw_entry=Path(selection['full_input_identity']['runtime_independent_input_source']['entry_trace_path'])
sg_entry=Path(sg_audit['commandlist_path'])
fw_run=fw_entry.parent.parent/'run.sh'
run_ref=reference(fw_run)
fw_run_literal=small(fw_run).decode()
fw_rows=fw_audit['traces']
sg_rows=sg_audit['trace_content_manifest']
assert composite(fw_rows)==selection['full_input_identity']['trace_content_sha256']
assert composite(sg_rows)==sg_audit['trace_content_sha256']==proposal['trace_content_sha256']
assert {r['name']:r['sha256'] for r in fw_rows if r['name']!='kernelslist.g'}=={r['name']:r['sha256'] for r in fw_atomic['trace_files']}
assert {r['name']:r['sha256'] for r in fw_rows if r['name']!='kernelslist.g'}=={r['name']:r['sha256'] for r in fw_native['files']}
assert fw_oracle['commandlist_sha256']==next(r['sha256'] for r in fw_rows if r['name']=='kernelslist.g')
assert {Path(k['path']).name:k['sha256'] for k in fw_oracle['kernels']}=={r['name']:r['sha256'] for r in fw_rows if r['name']!='kernelslist.g'}
oracle_copy=OUT/'FWT_7_21/readonly';oracle_copy.mkdir(parents=True,exist_ok=True)
(oracle_copy/'manifest.json').write_bytes(small(FWT_ORACLE/'manifest.json'))
for name in ['certified_lines.txt','certified_ranges.csv']:
    original=Path('/workspace/ep_l2_ms20261019_e_results/D_OFFLINE_INPUT_ANALYSIS/FWT_7_21_v2_r1/oracle')/name
    data=small(original)
    assert sha(data)==fw_oracle['artifacts'][name]
    (oracle_copy/name).write_bytes(data)

source_reference={'repository':'https://github.com/accel-sim/gpu-app-collection','local_path':str(APP),'commit':APP_COMMIT,
 'tracked_worktree_clean':not subprocess.check_output(['git','-C',str(APP),'status','--short','--untracked-files=no'],text=True).strip(),
 'role':'REFERENCE_SOURCE_ONLY_NOT_IDENTIFIED_AS_CAPTURE_SOURCE','capture_commit':None,
 'source_files':[r for r in apprefs if '/fastWalshTransform/' in r['path']]}
fw_miss=[
 missing('FWT-SOURCE','F / original capture asset owner','source_recapture','Exact scaled SDK4.2-family application source commit/patch, capture executable SHA and build flags/log.',
         'run.sh has -logK7 -logD21 and SDK4.2-scaled YAML mapping. Local pinned CUDA11 reference hardcodes log2Data23 and does not parse logK/logD; it is not a reconstruction of this input.'),
 missing('FWT-CAPTURE','F / original capture asset owner','capture_provenance','Capture GPU model/UUID, driver and actual toolkit build; original NVBit/tracer/postprocessor commits and executable hashes/session log.',
         'CUDA_VERSION9.1 and CUDA_VISIBLE_DEVICES4 are literal script declarations; binary version70 is recorded. GPU device index is not model/UUID. FWT saved/kernel1 header does not report NVBit/tracer version.'),
 missing('FWT-NUMERIC-DATA','F / original capture asset owner','numeric_reproduction','Original initialized HtoD payload or exact bound generator/seed, allocation/zeroing contract and captured numerical output/CPU check.',
         'Recorded list has only2 HtoD+19kernels. No numeric HtoD payload, memset or DtoH record in that list. Current reference srand2007/CPU checker cannot be rebound to unknown capture source.'),
 missing('FWT-RESTART','E2','execution_authorization','New explicit FWT restoration approval and E-selected source/binary/profile/input qualification with durable native exit/drain evidence for any future endpoints.',
         'E011/E012 both INCOMPLETE. Old elapsed/log appearance cannot establish exit0; no rerun is authorized by this preparation. Old main61 scope does not qualify new capacity runtime.')]
sg_miss=[
 missing('SGEMM-SOURCE','F / original capture asset owner','source_recapture','Application source commit/patch, actual executable SHA and original build/toolchain flags/log.',
         'Pinned local cuda SGEMM reference exists with matching mysgemmNT kernel family, but no binding from its commit to captured binary. Directory11.0 is not compiler proof.'),
 missing('SGEMM-CAPTURE','F / original capture asset owner','capture_provenance','Original run.sh/capture command, GPU model/UUID/driver/toolkit, NVBit/tracer/postprocessor commits+hashes and original archive/session identity.',
         'run.sh is absent beside frozen traces; YAML supplies a reference application invocation. Header records NVBit1.4/tracer3/binary70 only; exact source/GPU/CUDA build remain unknown.'),
 missing('SGEMM-DATA-ORACLE','F / original capture asset owner','numeric_reproduction','Exact matrix1.txt/matrix2t.txt content hashes and matrix dimensions; reference matrix3 output/hash or bound numeric generator/check.',
         'Trace list records two HtoD addresses/byte lengths, not payload values. Dataset root/expected files absent at checked source/data paths. Dimensions remain UNKNOWN; not inferred from copy lengths or grid.'),
 missing('SGEMM-RO','C / A2 / E2','runtime_input_qualification','Own full-input RO certificate or explicit independently reviewed empty-coverage ordinary-path fallback for chosen fixed-policy F.',
         'SGEMM RO certificate UNKNOWN; no Conv certificate reuse, no rewriting UNKNOWN as measured0.'),
 missing('SGEMM-EXECUTION','A2 / E2','execution_authorization','Exact supported producer/config/profile/full-input qualification and explicit new exploratory scientific scope/start approval.',
         'E2_EXP_SGEMM_MEDIUM_20261020_r1 already exists, REGISTERED_EXPLORATORY_HOLD_NOT_LAUNCHABLE; not missing registration and not an automatic Btree replacement.')]

all_manifests=[]
for work,entry,rows,stats,expected,miss in [
 ('FWT_7_21',fw_entry,fw_rows,fw_atomic['trace_files'],791609344,fw_miss),
 ('SGEMM_medium',sg_entry,sg_rows,sg_audit['files'],1658916864,sg_miss)]:
    folder=OUT/work;folder.mkdir(exist_ok=True)
    command_raw=small(entry)
    expected_command=next(r for r in rows if r['name']=='kernelslist.g')
    assert sha(command_raw)==expected_command['sha256'] and len(command_raw)==expected_command['bytes']
    commands=[];kernels=[];by_name={x['name']:x for x in stats};tracefiles=[]
    for seq,line in enumerate(command_raw.decode().splitlines(),1):
        if line.startswith('Memcpy'):
            op,address,count=line.split(',');commands.append(dict(sequence=seq,kind=op,address=address,bytes=int(count),raw=line))
        else:
            kernel=by_name[line];metadata=kernel.get('metadata',{})
            row=dict(sequence=seq,kernel_ordinal=len(kernels)+1,trace_name=line,kernel_name=metadata.get('kernel name'),
                grid=metadata.get('grid dim'),block=metadata.get('block dim'),shared_memory_bytes=metadata.get('shmem'),registers_per_thread=metadata.get('nregs'),
                binary_version=metadata.get('binary version'),instruction_records=kernel['instruction_records'],
                active_lane_instruction_records=kernel['active_lane_instruction_records'],trace_bytes=kernel['bytes'],trace_sha256=kernel['sha256'])
            kernels.append(row);commands.append(dict(sequence=seq,kind='kernel',trace_name=line,kernel_ordinal=len(kernels),raw=line))
    assert sum(x['active_lane_instruction_records'] for x in kernels)==expected
    for r in sorted(rows,key=lambda r:r['name']):
        current=state(entry.parent/r['name']);current.update(name=r['name'],published_bytes=r['bytes'],published_sha256=r['sha256'],current_full_content_rehashed=False)
        current['size_matches_published']=current.get('bytes')==r['bytes'];assert current['exists'] and current['size_matches_published']
        tracefiles.append(current)
    assert {k['trace_name'] for k in kernels}=={x['name'] for x in rows if x['name']!='kernelslist.g'}
    (folder/'kernelslist.g').write_bytes(command_raw)
    write(work+'/COMMANDS.json',{'scope':'COMPLETE_RECORDED_KERNELSLIST_NOT_COMPLETE_CUDA_API_OR_NUMERICAL_PAYLOAD_LOG','commands':commands,
       'counts':dict(kernels=len(kernels),MemcpyHtoD=sum(c['kind']=='MemcpyHtoD' for c in commands),MemcpyDtoH=sum(c['kind']=='MemcpyDtoH' for c in commands),
                     MemcpyDtoD=sum(c['kind']=='MemcpyDtoD' for c in commands)),
       'not_recorded':['HtoD numerical contents','memset/allocation details','CPU validation output'],
       'missing_DtoH_is_not_synthesized':True})
    with (folder/'KERNELS.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(kernels[0]),lineterminator='\n');writer.writeheader();writer.writerows(kernels)
    write(work+'/REUSED_FULL_STATISTICS.json',{'provenance':reference(FWT_OLD/'atomic_scope.json') if work=='FWT_7_21' else reference(AUDIT/'CANDIDATE_AUDIT.json'),
       'statistics_kind':'SAVED_COMPLETE_STATIC_TRACE_REVIEW_NOT_NEW_NATIVE_EXECUTION','expected_full_active_lane_instructions':expected,'kernels':stats})
    manifest=dict(schema='EPL2_F_WORKLOAD_INPUT_PACKAGE_V1',campaign_id='EPL2_MECHANISM_STUDY_20261019_V1',workload=work,
       status='MISSING',review_packet_status='READY_FOR_E_REVIEW',ready_to_launch=False,source_recapture_ready=False,
       formal_execution_site='original174; E2 only',
       trace_identity={'entry':str(entry),'content_sha256':composite(rows),'hash_definition':'sha256 of canonical JSON list sorted lexicographically by name, each row{name,sha256,bytes}; reused complete body digests, small commandlist freshly checked',
          'files':tracefiles,'trace_body_bytes':sum(r['bytes'] for r in rows if r['name']!='kernelslist.g'),
          'total_trace_and_commandlist_bytes':sum(r['bytes'] for r in rows),'kernel_launch_count':len(kernels),'expected_full_active_lane_instructions':expected,
          'current_content_claim':'Saved complete SHA/statistics plus current stat sizes. No fresh full-body content equality assertion.'},
       complete_sequence='COMMANDS.json',kernel_table='KERNELS.csv',missing=miss,
       cost={'new_starts_if_later_separately_approved':2,'per_endpoint_hard_result_cap_bytes':384*2**20,'pair_hard_result_reservation_bytes':768*2**20,
          'cost_source':reference(RESEARCH/'DECISION_REPORT.json'),'no_resource_reservation_by_F':True,'no_walltime_benchmark_executed':True},
       scientific_scope={'input_static_grammar_is_not_runtime_qualification':True,'numeric_SASS_or_algorithm_correctness_proven':False,
          'readonly_certificate_is_not_numeric_output_oracle':True,'no_Btree_SpMV_Scan_HOLD_change':True,'no_original_denominator_change':True})
    if work=='FWT_7_21':
        manifest.update(selection_id='D_V1_FWT_7_21',input_parameters={'literal_arguments':'-logK 7 -logD 21','source':run_ref,'recorded_HtoD_bytes':[512,8388608]},
          source=source_reference,
          commands={'application_run_from_original_capture':'$ORIGINAL_CAPTURE_BINARY -logK 7 -logD 21','captured_run_sh_literal':fw_run_literal,
             'original_build_command':None,'original_build_command_status':'MISSING; original scaled source/binary/build log absent',
             'reference_build_command_not_for_this_frozen_input':'make -j2 -C <admitted-reference-tree>/src/cuda/NVIDIA_CUDA-11.0_Samples/fastWalshTransform CUDA_PATH=<admitted-CUDA>',
             'reference_build_input_compatible':False,'reference_incompatibility':'Current CUDA11 source has const log2Data=23, no logK/logD parsing; input script uses -logD21. No source patched to force agreement.',
             'historical_run_sh_is_evidence_not_executable_recipe':'Contains original capture and rm *.trace cleanup; never executed by this preparation.',
             'replay_template':'<E-approved-binary> -config <E-bound-configs> -trace <absolute-entry-from-trace_identity>; template only, no launchable producer/profile selected'},
          capture={'CUDA_VERSION_declared':'9.1','CUDA_VERSION_evidence':run_ref,'actual_cuda_compiler_build':None,'GPU_visible_device_index_declared':'4',
             'GPU_model':None,'GPU_UUID':None,'driver_version':None,'binary_target_version':70,
             'nvbit_version':None,'tracer_version':None,'nvbit_or_tracer_commit':None,
             'tracer_shared_object_literal':'/home/tgrogers-raid/a/abdallm/traces/gpgpu-sim_simulations/util/correlation/../../../nvbit/tools/traceall/traceall.so',
             'postprocessor_literal':'/home/tgrogers-raid/a/abdallm/traces/gpgpu-sim_simulations/util/correlation/../../../nvbit/tools/traceall/traces-processing/post-traces-processing',
             'evidence_limits':'device4 is an index, binary70 a target, neither proves exact GPU; no source revision inferred from cudasdk/9.1 directory.',
             'bounded_header_observation':{'path':str(fw_entry.parent/'kernel-1.traceg'),'bytes_read_once':2048,'observed_keys':list(stats[0]['metadata']),'NVBit_tracer_version_not_in_observed_header':True,'rescan_performed_by_this_builder':False}},
          data_and_oracles={'original_numerical_payload_SHA':None,'captured_numerical_reference_output_SHA':None,
             'reference_CPU_source':reference(APP/'src/cuda/NVIDIA_CUDA-11.0_Samples/fastWalshTransform/fastWalshTransform_gold.cpp'),
             'reference_algorithm':'dyadicConvolutionCPU computes sum_j h_Data[i xor j]*h_Kernel[j]; current reference initializes srand2007 and tests relative L2 norm<1e-6',
             'reference_is_capture_bound':False,'reference_generator_seed_is_not_capture_evidence':True,
             'reference_API_scope_difference':'Reference has cudaMemset and DtoH/CPU comparison absent from recorded kernelslist. Do not invent missing CUDA commands or payload.',
             'readonly_oracle':{'manifest':reference(FWT_ORACLE/'manifest.json'),'scope':fw_oracle['scope'],'epoch':fw_oracle['epoch'],
                'manifest_in_packet':'readonly/manifest.json','small_artifacts_in_packet':['readonly/certified_lines.txt','readonly/certified_ranges.csv'],
                'kernel_count':fw_oracle['kernel_count'],'counts':fw_oracle['counts'],'certified_RO_lines':0,
                'counts_zero_RO_basis':'Saved complete epoch classifies131072 lines /41943040 read lane-line references SAME_LINE_STORE.',
                'assumptions':fw_oracle['assumptions'],'host_updates_excluded':fw_oracle['host_updates_excluded'],'artifacts':fw_oracle['artifacts'],
                'scope_limit':'Address eligibility only, not numeric correctness or T/M runtime acceptance.'}},
          retained_qualification={'complete_non_atomic_input_proof':reference(FWT_OLD/'atomic_scope.json'),'complete_original_byte_native_proof':reference(FWT_OLD/'native_input_semantics.json'),
             'runtime_input_binding_history':reference(FWT_OLD/'current_input_scope_binding.json'),'prior_qualification_id':fw_audit['qualification_sha256'],
             'reusability':'E may reuse exact old main61 input facts only after matching chosen producer/input/profile; no new-capacity qualification implied.',
             'old_attempts':[{'attempt_id':h['attempt_id'],'status':h['status'],'independent_acceptance':h.get('independent_acceptance'),'receipt':reference(FWT_OLD.parent/h['attempt_id']/'run_status.json')} for h in fw_history],
             'old_attempts_remain_INCOMPLETE':True,'no_exit0_inference':True,'E_exit_scope':reference(Path('/workspace/ep_l2_ft20261016_shared/mechanism_study_20261019_v1/inbox/E2_TO_D_FWT_EXECUTION_EVIDENCE_SCOPE.json'))})
        manifest['cost'].update(old_main61_prior_minutes={'S':[80,110],'F':[85,120]},old_INCOMPLETE_elapsed_not_completion_cost=True,current_runtime_walltime='UNKNOWN')
    else:
        data_root=APP/'data_dirs/parboil/parboil-sgemm';dataset_root=APP/'data_dirs/parboil/datasets/sgemm'
        checked=[data_root/'medium/input/matrix1.txt',data_root/'medium/input/matrix2t.txt',dataset_root/'medium/input/matrix1.txt',dataset_root/'medium/input/matrix2t.txt',entry.parent.parent/'run.sh',entry.parent.parent/'matrix3.txt']
        src=dict(source_reference);src['source_files']=[r for r in apprefs if '/sgemm/' in r['path'] or '/common/platform/' in r['path']]
        manifest.update(original_workload_key='sgemm',exploratory_registration={'record':reference(E/'docs/ep_l2/review_packs/MS20261020_E2_MAIN_ROLLING_r1/EXPLORATORY_SGEMM_REGISTRATION.json'),
             'registration_id':sg_registration['registration_id'],'status':sg_registration['status'],'hold_reasons':sg_registration['hold_reasons'],
             'supersession_note':'Earlier D proposal discussed replacement; actual E2 registration preserves Btree HOLD/original7 and places SGEMM in separate exploratory cohort.'},
          input_parameters={'literal_reference_arguments':'-i ./data/medium/input/matrix1.txt,./data/medium/input/matrix2t.txt,./data/medium/input/matrix2t.txt -o matrix3.txt',
             'source':yaml_ref,'repeated_matrix2t_argument_intent':'Preserved literally. Reference main requires3 filenames but reads A from arg0 and B-transpose from arg2.',
             'logical_matrix_dimensions':'UNKNOWN; no inference from transfer sizes or launch geometry','recorded_HtoD_bytes':[4063232,4190208]},source=src,
          commands={'original_build_command':None,'original_capture_command':None,
             'reference_build_command_not_capture_reconstruction':'cd <admitted-reference-tree>/src/cuda/parboil && CUDA_INSTALL_PATH=<admitted-CUDA> python2 ./parboil compile sgemm cuda',
             'reference_build_prerequisites':['legacy Parboil Python2 driver','admitted CUDA/host compiler/link libraries','reviewed common/Makefile.conf','E-approved output/tmp/cache paths and build peak'],
             'reference_build_flags_from_files':['APP_CFLAGS/APP_CXXFLAGS=-ffast-math -g3','PLATFORM_CUDACFLAGS=-O3','APP_CUDALDFLAGS=-lm -lstdc++','PLATFORM_CUDALDFLAGS=-lm -lpthread plus NVCC_ADDITIONAL_ARGS; actual captured flags unknown'],
             'reference_application_run':'<admitted-parboil-sgemm> -i ./data/medium/input/matrix1.txt,./data/medium/input/matrix2t.txt,./data/medium/input/matrix2t.txt -o matrix3.txt',
             'reference_recipe_warning':'Do not source src/setup_environment blindly: it can download/install/build SDK4.2. make parboil invokes make data and all suite benchmarks. This packet runs neither.',
             'replay_template':'<E-approved-binary> -config <E-bound-configs> -trace <absolute-entry-from-trace_identity>; template only, no qualified producer/profile selected'},
          capture={'binary_target_version':70,'nvbit_version':'1.4','accelsim_tracer_version':3,'source':reference(AUDIT/'CANDIDATE_AUDIT.json'),
             'GPU_model':None,'GPU_UUID':None,'driver_version':None,'actual_cuda_compiler_build':None,'nvbit_or_tracer_commit':None,'capture_script':None,
             'directory_label':'11.0 is a label, not compiler evidence','exact_archive_SHA_or_capture_session_manifest':None},
          data_and_oracles={'reference_dataset_filenames':['matrix1.txt','matrix2t.txt'],'original_dataset_content_SHA':None,'matrix_dimensions':None,'captured_matrix3_SHA':None,
             'exact_paths_checked':[state(p) for p in checked],'dataset_symlink':{'path':str(APP/'src/cuda/parboil/datasets'),'literal_target':os.readlink(APP/'src/cuda/parboil/datasets'),'target_exists':(APP/'src/cuda/parboil/datasets').exists()},
             'reference_data_acquisition_script':reference(APP/'get_data.sh'),'reference_archive_URL':'https://engineering.purdue.edu/tgrogers/gpgpu-sim/benchmark_data/all.gpgpu-sim-app-data.tgz',
             'reference_archive_not_downloaded_or_availability_verified':True,
             'numeric_oracle_reference':{'compare_output':reference(APP/'src/cuda/parboil/benchmarks/sgemm/tools/compare-output'),'rule':'Same float count; each abs(r-c)<0.01 OR abs(r-c)<0.01*abs(r); then EOF.',
                'exact_reference_file_missing':True,'reference_main_does_not_execute_computeGold':'computeGold declared only; output needs external checker/reference. No CPU numerical PASS claimed.'},
             'readonly_oracle':{'status':'UNKNOWN','artifact':None,'required_action':'C/A2/E2 own full-input certificate or explicitly qualified zero-coverage ordinary fallback; no Conv reuse.'}},
          retained_qualification={'D_proposal':reference(AUDIT/'SGEMM_PROPOSAL_TO_E.json'),'D_complete_input_proof':reference(AUDIT/'CANDIDATE_AUDIT.json'),
             'D_status':sg_audit['status'],'static_check_seconds_already_spent':sg_audit['wall_seconds'],'global_atomic_records':0,'shared_atomic_records':0,'native_or_numeric_acceptance_granted':False},
          distinct_hash_scopes={'legacy_ROUND1_tree_sha256':sg_old['trace_tree_sha256'],'native_trace_content_sha256':composite(rows),
             'legacy_manifest':reference(D/'docs/l2_char_v1/ROUND1_WAVE1_TRACE_MANIFEST.json'),'different_definitions_not_a_content_mismatch':True})
        manifest['cost'].update(current_runtime_walltime='UNKNOWN',prior_static_review_seconds=sg_audit['wall_seconds'],prior_static_review_is_not_native_walltime=True)
    write(work+'/MANIFEST.json',manifest);all_manifests.append(manifest)

# Freeze only small, critical decision originals; statistics extracts above are self-contained.
for label,path in [('E_DECISION_REPORT',RESEARCH/'DECISION_REPORT.json'),('E_SGEMM_REGISTRATION',E/'docs/ep_l2/review_packs/MS20261020_E2_MAIN_ROLLING_r1/EXPLORATORY_SGEMM_REGISTRATION.json'),('D_SGEMM_PROPOSAL',AUDIT/'SGEMM_PROPOSAL_TO_E.json')]:
    p=OUT/'saved_evidence'/f'{label}.json';p.parent.mkdir(exist_ok=True);p.write_bytes(small(path))
write('MISSING.json',{'schema':'EPL2_F_INPUT_PREPARATION_MISSING_V1','status':'MISSING','packet_ready_for_E_review':True,
    'items':[dict(workload=m['workload'],**x) for m in all_manifests for x in m['missing']],
    'interpretation':'Source recapture/numeric reproduction/execution gaps are explicit. Full frozen trace replay metadata is prepared for E review; no status here is an input, runtime or launch waiver.'})
write('SOURCE_BINDINGS.json',{'observed_at_beijing':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
    'repositories':[{'role':role,'path':str(repo),'HEAD':subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()} for role,repo in [('E2',E),('D',D),('reference_gpu_app_collection',APP),('original_trace_wrapper',ORIG)]],
    'sources':list(SOURCES.values()),'captured_source_identity_not_inferred_from_reference_HEAD':True})
write('DELIVERY.json',{'schema':'EPL2_F_APPLICATION_INPUT_PREPARATION_DELIVERY_V1','campaign_id':'EPL2_MECHANISM_STUDY_20261019_V1',
    'status':'MISSING','engineering_review_packet_status':'READY_FOR_E_REVIEW','not_launchable':True,
    'scope':'FWT and SGEMM existing input preparation only; old environment Goal remains blocked and untouched.',
    'manifests':[{'workload':m['workload'],'path':m['workload']+'/MANIFEST.json','trace_content_sha256':m['trace_identity']['content_sha256'],
      'body_bytes':m['trace_identity']['trace_body_bytes'],'kernels':m['trace_identity']['kernel_launch_count'],
      'expected_full_instructions':m['trace_identity']['expected_full_active_lane_instructions'],'missing_ids':[x['id'] for x in m['missing']]} for m in all_manifests],
    'corrections':['SGEMM already has an E2 independent exploratory registration; it remains HOLD/not launchable, not a Btree replacement.',
      'Available CUDA11 reference FWT is not compatible source for -logD21 capture; no invented original source commit.',
      'SGEMM legacy tree SHA2074532f and native composite694ce08c have different definitions; full-body SHA agrees.'],
    'preserved':{'FWT_E011_E012':'INCOMPLETE; no exit0 or acceptance inferred','Btree_SpMV_Scan':'HOLD unchanged','original_cohort_and_denominators':'unchanged','formal_execution_site':'original174','E2_unique_scheduler':'unchanged'},
    'operations':{'full_trace_scans':0,'large_trace_rehashes':0,'prior_single_bounded_FWT_header_bytes_read':2048,'compiler_or_native_starts':0,'complete_application_starts':0,
      'GPU_capture':0,'large_transfers_or_downloads':0,'environment_surveys':0,'new_controller':False,'old_Goal_resumed':False,'central_state_modified':False},
    'next_owners':{'F':'Recover exact capture/source/data artifacts from named original owners if supplied; no bulk retrieval/build without E admission.',
      'D':'Confirm frozen restoration/exploratory scope; original statistical denominators unchanged.',
      'C':'SGEMM certificate or reviewed ordinary fallback; FWT zero-RO address proof only.',
      'A2':'Exact producer/input/opcode/profile compatibility review, no hot binary replacement.',
      'E2':'Review identities and explicit missing provenance; independent qualification and separate scientific start approval before any run.'}})
print(json.dumps({'status':'MISSING','engineering_packet':'READY_FOR_E_REVIEW','workloads':[m['workload'] for m in all_manifests],'sources':len(SOURCES),'output':str(OUT)},ensure_ascii=False))
