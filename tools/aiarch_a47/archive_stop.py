"""Archive actual legal STOP evidence only; never invent missing native samples."""
import hashlib,json,pathlib,subprocess,os,time,shutil,platform
from budget_io import ROOT
WORK=pathlib.Path(__file__).resolve().parents[2];PUB=WORK/'docs/ai_workload_research/runs/AI_ARCH_A47_CAGRA_GLOVE100_109_V1';PUB.mkdir(parents=True,exist_ok=True);(PUB/'raw').mkdir(exist_ok=True)
def sanitize(s):return s.replace(str(WORK),'<WORKTREE>').replace(str(ROOT),'<TASK_ROOT>').replace('/home/huangrulin','<HOME>')
def read(name):return json.loads((ROOT/name).read_text())
def write(name,obj):
 s=json.dumps(obj,indent=2)+'\n' if not isinstance(obj,str) else obj
 (PUB/name).write_text(sanitize(s))
ledger=read('gpu_resource_receipt.json');assert ledger['cumulative_lock_seconds']<2700
first=ledger['attempts'][0];assert first['stages'][0]['returncode']==-11
stack=(ROOT/'logs/small_api_gdb.log').read_text();assert 'received signal SIGSEGV' in stack and 'cuStreamGetId' in stack and 'ivf_pq::build' in stack and 'FIXTURE_PADDED_DATASET_PASS' in stack
assert not (ROOT/'cagra_glove.index').exists() and not (ROOT/'calibration.json').exists() and not (ROOT/'report_quality.json').exists()
old=read('old_preservation.json')
for row in old:
 p='/home/huangrulin/workspace/worktrees/'+row['worktree_label'];env={**os.environ,'GIT_OPTIONAL_LOCKS':'0'}
 assert subprocess.check_output(['git','-C',p,'rev-parse','HEAD'],text=True,env=env).strip()==row['head'];assert subprocess.check_output(['git','-C',p,'status','--porcelain'],text=True,env=env)==''
size=sum(p.stat().st_blocks*512 for r in [ROOT,WORK] for p in r.rglob('*') if p.is_file());free=shutil.disk_usage(ROOT).free;assert size<12*1024**3 and free>=64*1024**3
pre=read('preregistration.json');data=read('data_validation_receipt.json');envlock=read('resolved_env_lock.json');prep=read('prepare_resource.json')
resource={'limits':{'GPU_lock_seconds':2700,'download_bytes':6*1024**3,'data_download_bytes':int(.6*1024**3),'new_disk_bytes':12*1024**3,'free_disk_min_bytes':64*1024**3,'process_tree_RAM_bytes':8*1024**3,'GPU_VRAM_bytes':12*1024**3,'effective_CPU_workers':4,'CPU_preparation_seconds':7200,'public_raw_summary_bytes':64*1024**2},'downloads':read('download_budget.json'),'CPU_preparation_elapsed_seconds':read('G0_preflight.json')['prepare_elapsed_seconds'],'GPU_cumulative_lock_seconds':ledger['cumulative_lock_seconds'],'GPU_attempts':ledger['attempts'],'new_allocated_worktree_plus_private_bytes':size,'disk_free_bytes':free,'peak_tree_RAM_bytes_sampled':max(prep['peak_tree_rss_bytes_sampled'],*[x.get('peak_tree_rss_bytes_sampled',0) for x in ledger['attempts']]),'peak_GPU_MiB_sampled':max(x.get('peak_gpu_mib_sampled',0) for x in ledger['attempts']),'GPU_sampling_note':'native attempt sampled at approx0.6s; very short small debug process CUDA lifetime not captured by NVML, its reported sampled0 is not actual0','CPU_affinity_all_execution':[0,2,4,6],'OMP_thread_limit':4,'OMP_BLAS_requested_threads':1,'all_own_GPU_children_finished':True,'shared_lock_released':True,'system_or_old_environment_changes':False,'final_prepare_samples_count':len(prep['samples'])}
state={'terminal_scientific_state':'PLATFORM_OR_ASSET_NO_GO','STOP_reason':'Pinned native CAGRA IVF-PQ build SIGSEGV; small API diagnostic reproduced libcuda cuStreamGetId fault through RMM allocation. Exact stream/ABI/vendor root cause UNKNOWN; native build not qualified.','G0':{'status':'PASS','scope':'official frozen release/source/wheel closure, installed isolated env/offline pip check and resources'},'G1':{'status':'PASS','scope':'complete official GloVe bytes/schema/finite/norm and full-base CPU cosine/GT identity'},'G2':{'status':'STOP_NATIVE_BUILD_SIGSEGV','device_identity':'PASS','small_CuPy_arithmetic':'PASS_BY_EXECUTION_BEFORE_BUILD_MARKER','small_API_Dataset_wrapper':'PASS','full_GloVe_build_API_attempts':1,'full_GloVe_completed_graphs':0,'small_synthetic_API_build_attempts':1,'small_synthetic_API_build_result':'SIGSEGV','saved_or_reloaded_index':'NOT_CREATED','native_CAGRA_numerical_qualification':'NOT_RUN'},'G3':{'status':'NOT_RUN_BLOCKED_BY_G2','functional_search_configuration_checks':0,'calibration_configuration_checks':0,'formal_points_completed':0,'selected_h':'NOT_SELECTED','quality_status':'NOT_RUN','timing_status':'NOT_RUN'},'G4':{'status':'ARCHIVE_COMPLETE_FOR_SINGLE_BRANCH_PUBLICATION','exact_final_commit_tree_blob_readback':'external final_git_readback.json receipt and final user report'},'no_next_goal':True}
identity={'repository':'swayhrl/accel-sim-framework','branch':'hrl/aiarch-a47-cagra-glove100-native-109-v1','fixed_start':'26ef7b20172495f26ed53248bfab792ae8af9040','executor':'Codex Lane M node109, new worktree/env/output','G0':read('G0_preflight.json'),'release_source_binding':read('release_source_binding.json'),'device':read('device_identity.json'),'old_accepted_worktrees':old,'script_sha256':{str(p.relative_to(WORK)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((WORK/'tools/aiarch_a47').glob('*.py'))},'CPU_read_inputs':[{'path':p,'blob':subprocess.check_output(['git','rev-parse','HEAD:'+p],text=True).strip(),'sha256':hashlib.sha256((WORK/p).read_bytes()).hexdigest()} for p in ['docs/ai_workload_research/COORDINATION_PROTOCOL.md','docs/ai_workload_research/CURRENT_STATE.md','docs/ai_workload_research/goals/AI_ARCH_A47_CAGRA_GLOVE100_BOUNDED_NATIVE_109_V1.md','docs/ai_workload_research/reviews/AI_ARCH_A46_A45H_A45S_INDEPENDENT_SCIENTIFIC_REVIEW_2026-10-14_V1.md']],'A45S_fixed_commit':'e0236f9e34f25dc7c96d048b31754bcb74e05764','A45S_report_blob':'df46a84b7500defa52a4be7001f0adffcd5a9637'}
quality={'CPU_full_base_canary':data['numeric_CPU'],'CAGRA_energy_or_training':'NOT_APPLICABLE','CAGRA_native_search_numeric':'NOT_RUN','recall':'NOT_RUN','calibration':'NOT_RUN','four_points':[{'B':b,'arm':a,'state':'NOT_RUN_BLOCKED_G2','actual_queries':0,'actual_samples':0} for b in [1,256] for a in ['AUTO','SINGLE_CTA_SMALL']],'no_synthetic_performance_substitution':True}
write('GATES.json',state);write('RUN_IDENTITY.json',identity);write('ENV_LOCK.json',envlock);write('DATA_AND_INDEX_IDENTITY.json',{'data':data,'index':{'state':'NOT_CREATED','scientific_full_build_calls':1,'scientific_full_build_successes':0,'index_sha256':'NOT_AVAILABLE','graph_sha256':'NOT_AVAILABLE','dataset_serialization':'NOT_RUN'}});write('PREREGISTRATION.json',pre);write('QUALITY_AND_TIMING.json',quality);write('RESOURCE_RECEIPT.json',resource);write('SOURCE_IDENTITIES.json',read('all_source_identities.json'))
write('ENGINEERING_RECEIPTS.json',{'resolved':['official dataset HTTPS HEAD403; bound HTTPS GET range206 succeeded with matching HTTP/S entity ETag','NumPy historical non-PEP440 versions skipped; they could not satisfy current NumPy>=2 constraints','RMM26.10 allocator imported from documented rmm.allocators.cupy; verified from official wheel before any GPU attempt','proc/stat parser fixed for parenthesized names containing spaces in debug supervisor; initial failure held0.021s and preserved'],'critical_native_failure':{'full_process_returncode':-11,'signal':'SIGSEGV','small_API_gdb_exitcode_is_not_qualification':True,'CPU_stack_frames':['libcuda.so.1 cuStreamGetId','rmm/pylibrmm/memory_resource/_memory_resource.abi3.so','librmm.so rmm::_RMM_26_10::device_buffer::allocate_async','libcuvs.so cuvs::neighbors::ivf_pq::build'],'exact_root_cause':'UNKNOWN; cannot establish a legal wrapper-only correction from this stack without changing the admitted ABI/runtime path or retrying complete scientific build'},'scope':'one bounded small API diagnostic only, no search/quality/performance configuration or second scientific dataset; GDB CPU fault stack, not GPU profiler; debuginfod explicitly declined, no diagnostic downloads','old_assets_preserved':old})
for n in ['build_attempt_started.json','endpoint_checks.json','wheel_download_receipts.json','data_download_receipt.json','pre_GPU_script_sha256.json','G0_preflight.json']:write('raw/'+n,read(n))
for p in sorted((ROOT/'logs').glob('*.log')):(PUB/'raw'/p.name).write_text(sanitize(p.read_text()))
report=f'''# Round A47 | GloVe100 / cuVS CAGRA native platform gate / STOP

**Scientific state: PLATFORM_OR_ASSET_NO_GO.** Real GloVe data and frozen official distribution qualification passed. Actual full native graph-build entry failed with SIGSEGV; a permitted small API diagnostic reproduced a driver/RMM stream-allocation fault. No qualified index, recall, calibration selection or timing result exists. This is a native platform/ABI admission failure, not a recall failure, software performance negative or hardware-headroom result.

Independent branch `hrl/aiarch-a47-cagra-glove100-native-109-v1`, fixed start `26ef7b20172495f26ed53248bfab792ae8af9040`. Executor Codex Lane M/node109 used a new worktree, environment, output and cumulative budget. No coordinator merge. Prior A26GR1/A45H heads and contents remain clean; C16/AWMA were not operated.

## Actual gates

| Gate | Result | Actual evidence |
|---|---|---|
| G0 | PASS | official24-wheel closure, SHA/platform/Python checks, offline install and pip check; Python and native cuVS embedded source commit exactly match |
| G1 | PASS | complete author HDF5,1183514x100 base,10000 query,top100 GT; finite/zero-norm/IDs/links; complete-base CPU cosine oracle32 queries |
| G2 | STOP | one complete-base cagra.build call attempted, process exit-11; no graph/index returned or saved; small API Dataset preparation passed but build again SIGSEGV |
| G3 | NOT_RUN | functional searches0, calibration checks0, chosen h unavailable; all four formal points and recall/timing NOT_RUN |
| G4 | Archived for single-branch publication | raw returns/CPU stack/version/input/budget receipts and SHA list; exact enclosing commit/tree/blob readback recorded on closeout |

Before the full build marker, the single RTX4080 device/runtime identity and small CuPy FP32 arithmetic assertion completed. They do not qualify CAGRA numerical correctness. The full GPU function was actually attempted; it was not skipped merely because the gate was unverified.

## Input and scientific contract

Official author endpoint [GloVe100 HDF5](https://ann-benchmarks.com/glove-100-angular.hdf5): **485413888 bytes**, local complete SHA256 **`{data['source']['sha256']}`**. Entity ETag `9ef1a69a639809d4ae43efd5e6707fa1-58`; bound HTTPS range covered the full entity. Local SHA is execution identity, not an upstream-certified checksum. HTTPS HEAD403 was a packaging access issue: HTTP HEAD and HTTPS GET confirmed the same entity; no mirror or replacement input was used.

[ANN-Benchmarks fixed README](https://github.com/erikbern/ann-benchmarks/blob/2e081ad32c1eccab72dcb739ad886c310b90f715/README.md) supplies source/shape/GT provenance. [Stanford GloVe](https://nlp.stanford.edu/projects/glove/) states pre-trained vectors are PDDL1.0; the author benchmark derivative was used for approved research and is not redistributed. File attributes and source receipts are retained. HDF5 plugins disabled and external/virtual links or unknown filters rejected before reads. All original vectors retained, raw bytes unchanged; recorded FP32 unit normalization preserves cosine semantics. No FP16 or compression.

Fixed SHA256("20261014:"+decimal query ID) ordering yields2000 calibration/canary and8000 report queries, disjoint. The first2048 different report queries were frozen for timing; no query copying. Query index lists/digests, original field hashes and normalized-file hashes are in PREREGISTRATION/DATA_AND_INDEX_IDENTITY. CPU full-base oracle32 (FP64 evaluation of original cosine) matches publisher GT kth10 with maximum absolute error **{data['numeric_CPU']['GT_k10_threshold_max_abs_error']:.12g}**. Original GT IDs unchanged. Publisher knn tie criterion `GT_distance_k10+0.001` and GPU distance tolerances atol1e-5/rtol1e-4 were frozen before GPU. No GPU recall values were obtained.

The preregistered four points remain B1/B256 x AUTO versus calibrated SINGLE_CTA+SMALL. Common k10/itopk128/width1/max_iterations64/random-mask/quality0.95/delta0.005 preserved. Candidate h9/h11 was not evaluated or selected. No condition was relaxed, no extra parameter scan or synthetic performance substitute was made.

## Frozen software and failure

Python3.12.3, cuVS-cu12/libcuvs-cu12/pylibraft-cu12/RMM26.10.0; CuPy14.0.1, NumPy2.5.4, h5py3.16.0. ENV_LOCK contains all24 official PyPI wheel URLs/bytes/SHA, dependency constraints and installed closure. No full ML framework/Docker/source rebuild. Both Python and native cuVS wheel embedded `GIT_COMMIT` are **24ee1bf1cb17cad0ac611e39643af39ee1870124**; CAGRA binding blob27880c8dd63e1d59a53c7e0cfbcbc8aef2727ae7 and planner blobda42f637dcd6fd1b299c425d353c77b3f1fe2f85 verified. No core-version substitutions.

Actual device RTX4080,76 SM,CC8.9; driver580.178.04 (Driver API13000), isolated runtime12090. System CUDA/driver were not upgraded. New RMM pool initial512MiB/max10GiB, explicit CuPy stream/cuVS Resources; loaded library file SHA identities saved. Native full-base call used cosine/ivf_pq/degree64/intermediate128 and unchanged FP32 normalized input.

Full build process exited **-11/SIGSEGV** after entering the official build API. No serialization or graph was produced. One permitted1024x100 synthetic API fixture (not a second scientific dataset/graph/performance point) was examined under the same shared lock with installed GDB CPU backtrace. GPU input and `make_device_padded_dataset` succeeded (padded, non-owning view, input owner retained); `cagra.build` again faulted. Main CPU stack: **libcuda!cuStreamGetId -> RMM Python memory-resource bridge -> librmm device_buffer::allocate_async -> libcuvs IVF-PQ build**. GDB batch return0 means debugger completed, not API PASS. Driver symbols/ABI stream root cause remains **UNKNOWN**; the stack does not prove which component is defective. Changing driver/core versions or repairing vendor mathematics is outside this admission. No further GPU retry or complete graph reconstruction occurred.

Ordinary wrappers were solved in this Goal: invalid historical NumPy version parsing, official endpoint HEAD/GET access, documented RMM allocator import and `/proc/stat` parentheses parsing. All failures and overhead remain in receipts. The platform failure is separated from those resolved packaging issues. No NCU/NSYS/NVBit, simulator, SM scan, training or new mechanism was run.

## Four-point outcome

| Point | Native recall | Formal samples | Result |
|---|---:|---:|---|
| B1 AUTO | unavailable |0| NOT_RUN, G2 failed |
| B1 SINGLE_CTA+SMALL | unavailable |0| NOT_RUN, h not selected |
| B256 AUTO | unavailable |0| NOT_RUN, G2 failed |
| B256 SINGLE_CTA+SMALL | unavailable |0| NOT_RUN, h not selected |

No AUTO/SMALL performance difference or hardware inference is made. No GPU search numerical qualification is claimed from CPU GT checks or trivial device arithmetic. Source-derived prospective planner choices are not reported as device-observed search.

## Resources and closeout

CPU preparation **{resource['CPU_preparation_elapsed_seconds']:.3f}s**, below2h. Total counted download **{resource['downloads']['total_bytes']} bytes** ({resource['downloads']['total_bytes']/1024**3:.3f}GiB), data **{resource['downloads']['data_bytes']} bytes** ({resource['downloads']['data_bytes']/1024**3:.3f}GiB), including the probe and conservative Git metadata allowance. Download attempts never reset. Full checkout/private allocated **{size} bytes** ({size/1024**3:.3f}GiB), free FS **{free} bytes** ({free/1024**3:.3f}GiB). Peak sampled process-tree RSS **{resource['peak_tree_RAM_bytes_sampled']} bytes** ({resource['peak_tree_RAM_bytes_sampled']/1024**3:.3f}GiB). Effective CPU affinity0,2,4,6; OpenMP cap4, BLAS requested1.

Shared lock `/data/c16/locks/c16_gpu_campaign.lock` opened existing without creation and acquired nonblocking. Cumulative holds **{ledger['cumulative_lock_seconds']:.6f}s**, includes failed native and debug wrapper/API attempts. Sampled native GPU-process peak **{resource['peak_GPU_MiB_sampled']}MiB**; the short debug CUDA lifetime was not captured by its NVML samples, so sampled0 is not claimed as actual0. Pool max10GiB plus margin and independent sampling remained in force. All own GPU children ended, lock released; no resource limit violation was observed. Background prep was ended before GPU entry; formal measurement never started. HDF5/environment/normalized arrays stay private on109; no index exists and nothing was copied164.

Only this independent branch is published. SHA256SUMS verifies all evidence/scripts; the final Git ref is the enclosing commit to avoid self-reference. After commit/push/fetch-back, exact commit/tree/all new blobs and SHA/clean are verified in the final closeout receipt. **STOP; no next Goal.** Minimal follow-up is independent scientific/platform review of this pinned stream-allocation failure, not an authorized GPU experiment, parameter retry or driver upgrade.
'''
write('FINAL_REPORT.md',report)
# Hash every public evidence and execution script, excluding this self-hash file.
paths=sorted([p for p in PUB.rglob('*') if p.is_file() and p.name!='SHA256SUMS']+list((WORK/'tools/aiarch_a47').glob('*.py')))
(PUB/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(WORK))+'\n' for p in paths))
assert sum(p.stat().st_size for p in PUB.rglob('*') if p.is_file())<=64*1024**2
for p in PUB.rglob('*.json'):json.loads(p.read_text())
print('STOP_PACKET_READY',len(paths),'PUBLIC_BYTES',sum(p.stat().st_size for p in PUB.rglob('*') if p.is_file()),'STATE',state['terminal_scientific_state'])
print('RESOURCES',json.dumps({k:v for k,v in resource.items() if k not in ['limits','GPU_attempts']}))
