"""Archive the actual authorized A50G continuation and its unchanged quality STOP."""
import os,pathlib,json,hashlib,subprocess,shutil,time
os.sched_setaffinity(0,[0,2,4,6]);W=pathlib.Path(__file__).resolve().parents[2];R=pathlib.Path('/data/c16/aiarch_a50g_glove100_default_full_109_recovery_v1');O=pathlib.Path('/data/c16/aiarch_a47_cagra_glove100_109_v1');P=pathlib.Path('/data/c16/aiarch_a50g_glove100_default_full_109_v1');D=W/'docs/ai_workload_research/runs/AI_ARCH_A50G_GLOVE100_CAGRA_DEFAULT_FULL_109_RECOVERY_V1';D.mkdir(parents=True,exist_ok=True);(D/'raw').mkdir(exist_ok=True)
def read(n):return json.loads((R/n).read_text())
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()
def clean(s):
 for a,b in [(str(W),'<RECOVERY_WORKTREE>'),(str(R),'<RECOVERY_OUTPUT>'),(str(P),'<PRIOR_A50G_READONLY>'),(str(O),'<A47_READONLY>'),('/home/huangrulin','<HOME>')]:s=s.replace(a,b)
 return s
def write(n,x):(D/n).write_text(clean(x if isinstance(x,str) else json.dumps(x,indent=2)+'\n'))
obs=read('supervisor_receipt.json');pre=read('preflight.json');idx=read('index_identity.json');can=read('functional_canary.json');cal=read('calibration.json');check=read('independent_cpu_verification.json');build=read('build_observation.json');start=read('start.json')
assert obs['reason']=='QUALITY_NO_GO' and obs['stages'][0]['returncode']==20 and check['quality_stop_confirmed'] and can['status']=='PASS' and idx['status']=='PASS_SAME_SERIALIZED_INDEX_RELOADED' and cal['eligible_h']==[]
assert not (R/'report_quality.json').exists() and not list((R/'raw').glob('process_*timing.jsonl'))
for rel,digest in pre['code_sha256'].items():assert sha(W/rel)==digest,(rel,'executed source changed')
prior=json.loads((W/'docs/ai_workload_research/runs/AI_ARCH_A50G_GLOVE100_CAGRA_DEFAULT_FULL_109_V1/RESOURCE_RECEIPT.json').read_text())
for p in (R/'raw').glob('*'):
 if p.is_file():
  if p.suffix=='.npz':shutil.copyfile(p,D/'raw'/p.name)
  else:write('raw/'+p.name,p.read_text())
for p in (R/'logs').glob('*.log'):write('raw/'+p.name,p.read_text())
for n in ['preflight.json','start.json','device_identity.json','full_build_enter.json','build_observation.json','index_identity.json','functional_canary.json','calibration.json','supervisor_receipt.json','independent_cpu_verification.json']:write('raw/'+n,read(n))
formal=[{'B':b,'arm':a,'status':'NOT_RUN','reason':'CALIBRATION_QUALITY_NO_GO','actual_timing_samples':0,'report_quality_queries':0,'chosen_h':None} for b in [1,256] for a in ['AUTO','SINGLE_CTA_SMALL']]
gates={'terminal_scientific_state':'QUALITY_NO_GO','G0':'PASS_FROZEN_IDENTITY_ENVIRONMENT_RESOURCES_AND_SCRIPT','G1':{'pinned_real_allocation_transfer_preflight':'PASS_B1_B256','additional_full_build_API_calls':1,'cumulative_A50G_full_build_API_calls':2,'latest_explicit_user_continuation_allows_one_additional_build':True,'index_fields':'ALL_PASS','save':'PASS','reload':'PASS_OWNER_ALIVE','returned_IDs_distances_numeric':'PASS','full_base_FP64_oracle_threshold_identity':'PASS_32_QUERIES','approximate_topk_recall_is_separate_from_distance_numeric':True},'G2':{'status':'QUALITY_NO_GO','calibration_queries_each':2000,'configurations':6,'functional_configurations':2,'threshold':.95,'same_B_difference_limit':.005,'eligible_h':[],'chosen_h':None,'calibration_timing':'NOT_RUN_NO_ELIGIBLE_H','report_quality':'NOT_RUN'},'G3':{'status':'NOT_RUN','formal_points':formal,'fresh_measurement_processes':0},'G4':'EVIDENCE_ARCHIVED_FOR_EXACT_SINGLE_BRANCH_PUBLICATION','no_future_GPU_task_started':True};write('GATES.json',gates)
write('ENV_LOCK.json',json.loads((O/'resolved_env_lock.json').read_text()))
write('DATA_AND_INDEX_IDENTITY.json',{'frozen_source_data':read('frozen_data_identity.json')['data'],'preregistration':read('frozen_preregistration.json'),'new_build':build,'serialized_index':idx,'private_index_path':str(R/'glove.index'),'no_graph_logical_hash':'UNKNOWN_PUBLIC_VIEW_NOT_REQUIRED','one_saved_index_for_all_actual_searches':True,'all_report_queries_untouched':True,'original_A50G_unsaved_index_not_reused':True})
write('QUALITY_AND_TIMING.json',{'numerical_qualification':can,'independent_CPU_verification':check,'calibration':cal,'formal_points':formal,'performance_classification':'UNAVAILABLE_QUALITY_GATE_FAILED','all_4_formal_points_have_0_samples':True,'no_search_performance_claim':True,'calibration_wall_selection':'NOT_RUN_NO_ELIGIBLE_H','calibration_report_sets_disjoint':True})
source_files=['search_plan.cuh','search_single_cta.cuh','search_multi_cta.cuh','compute_distance_standard.hpp','compute_distance_standard-impl.cuh','compute_distance_standard_matrix.json','cagra.pyx','dataset.pyx','resources.pyx']
planning=[]
for x in cal['configurations']:
 b=x['B'];arm=x['arm'];h=x['h'];multi=arm=='A' and b==1;bits=11 if multi else (9 if arm=='A' else h)
 planning.append({'B':b,'arm':arm,'h':h,'REQUESTED':x['requested_params'],'SOURCE_DERIVED':{'source_git_commit':'24ee1bf1cb17cad0ac611e39643af39ee1870124','algo':'MULTI_CTA' if multi else 'SINGLE_CTA','hash_structure':'global traversed HASH + per-CTA visited SMALL' if multi else 'SMALL','hash_bitlen':bits,'visited_small_bitlen':9 if multi else bits,'small_reset_interval':1 if multi else (2 if bits==9 else 14),'multi_CTA_count_per_query':4 if multi else 1,'multi_CTA_internal_topk_per_CTA':32 if multi else None,'team_size':8,'team_size_basis':'fixed descriptor standard Matrix dim128/team8 for FP32 cosine dim100; source-derived, not launch-observed','max_iterations_upper_bound':64,'AUTO_selection_basis':'itopk128<=512 and max_queries>=2*76 => SINGLE_CTA, otherwise MULTI_CTA','thread_block_size':128 if arm=='B' else 'UNKNOWN_FINAL_DYNAMIC_SELECTION'},'DEVICE_OBSERVED':{'SM_count':76,'default_CuPy_stream':True,'RMM_type':'CudaMemoryResource','index_metadata':build['fields']['fields'],'kernel_algo':'UNKNOWN_NOT_PROFILED','iteration_count':'UNKNOWN','distance_count':'UNKNOWN'}})
write('EFFECTIVE_PATHS.json',{'source_provenance':'read-only official source frozen by prior A47 and bound to installed cuVS26.10 wheel commit; cached source files hash/mtime rechecked','source_SHA256':{n:sha(O/'source'/n) for n in source_files},'planning':planning,'caution':'All effective plan details labelled SOURCE_DERIVED are inferences from source and fixed requested values, not observed kernel telemetry. No performance data, tracer or profiling was collected.'})
repair={'prior_STOP_commit':'d74ba0225516e60aa1c18b7ee87c88abfc34e0c9','user_instruction':'那你改正。然后接着做','announced_interpretation':'one additional complete build within all original cumulative caps; quality/science unchanged','changes':['explicit element count for all pinned NumPy views','actual B1/B256 pinned allocation and H2D/D2H roundtrip before full-build consumption','save/hash immediately after full index fields pass before any functional search helper','saved-only qualification recovery mode never invokes cagra.build','record raw search outputs before numerical verdict','carry original GPU/disk/CPU consumption in ledger'],'actual_preflight_allocated_vs_logical_bytes':{'B1':{'allocated':[512,512,512],'logical':[400,40,40]},'B256':{'allocated':[131072,16384,16384],'logical':[102400,10240,10240]}},'resume_mode_used':False,'native_failure_or_wrapper_exception':False,'actual_STOP':'unchanged recall gate failed; no retries or adjustments','old_A50G_evidence_unchanged':True};write('ENGINEERING_REPAIR.json',repair)
write('RUN_IDENTITY.json',{'repository':'swayhrl/accel-sim-framework','publish_branch':'hrl/aiarch-a50g-glove100-default-native-full-109-v1','local_recovery_branch':'hrl/aiarch-a50g-glove100-default-native-full-109-recovery-v1','local_recovery_branch_will_not_be_pushed':True,'original_fixed_start':'ea32eb190cf9697556f3560263b7a637563c69e7','recovery_parent':'d74ba0225516e60aa1c18b7ee87c88abfc34e0c9','old_STOP_report_retained_in_tree':True,'client_date':'2026-10-15 Asia/Shanghai','executed_and_archived_code_sha256':{str(p.relative_to(W)):sha(p) for p in (W/'tools/aiarch_a50g_recovery').glob('*.py')},'preflight':pre,'device':read('device_identity.json'),'output':str(R),'prior_assets_hash_and_mtime_rechecked':check['original_assets_hash_mtime_checked'],'old_worktree_HEAD_clean_unchanged':True,'new_download_install':0,'only_current_execution_branch_publication':True})
nextstep={'status':'PROPOSAL_ONLY_NOT_STARTED','unique_minimum_next_step':'Independent CPU-only source/output audit of the quality deficit before proposing any further GPU work. No native performance experiment is currently quality-qualified.','concrete_plan':['Verify this commit/tree, SHA256SUMS, ENV/input/query identities and serialized-index SHA receipt. Do not import CUDA/Torch or acquire GPU lock.','Using archived six calibration NPZ outputs and their query IDs, compare per-query neighbor overlap and misses for B1 AUTO versus the five identical single-CTA/h9/h11 outputs; verify the frozen GT tie rule from the recorded full-base FP64 oracle.','Read the exact frozen search_plan.cuh and single/multi-CTA sources to assess termination/candidate-retention semantics for fixed itopk128/search_width1/max_iterations64, without changing core math or generating new measurements.','Issue a review decision: close the current fixed-quality configuration as NO_GO, or draft a separately approved quality-first search-budget contract. Do not reuse these failed-quality points as a speed comparison.'],'minimum_incremental_budget_envelope':{'GPU_seconds':0,'downloads_install_bytes':0,'CPU_effective_workers':4,'RAM_GiB':2,'new_disk_MiB':64,'wall_minutes':20},'executable_inputs':{'raw_pattern':'raw/cal_*_outputs.npz','quality_manifest':'QUALITY_AND_TIMING.json','source_manifest':'EFFECTIVE_PATHS.json','original_readonly_gt':'<A47_READONLY>/gt_distances.npy','source_directory':'<A47_READONLY>/source'},'STOP':['hash/identity mismatch or original asset would need mutation','requires CUDA execution/downloads or extra source version','quality threshold/precision/GT alteration','CPU/RAM/disk/time bound reached'],'future_GPU_work':'requires an independently reviewed, explicitly authorized new quality-first contract; no automatic execution or parameter expansion'};write('NEXT_STEP_PROPOSAL.json',nextstep)
# Resource bookkeeping includes the original STOP, this worktree, preserved index,
# private caches and all archived copies; large data/environment are not recopied.
size=sum(p.stat().st_blocks*512 for root in [R,W] for p in root.rglob('*') if p.is_file())+6111232;free=shutil.disk_usage(R).free
prep_upper=obs['samples'][0]['monotonic']+(time.time()-time.monotonic())-start['epoch']+278.1733889579773
assert size<2*1024**3 and free>=64*1024**3 and obs['GPU_lock_seconds_cumulative']<2700 and prep_upper<1800
resources={'limits':{'GPU_lock_seconds':2700,'RAM_bytes':8*1024**3,'VRAM_bytes':12*1024**3,'new_disk_bytes':2*1024**3,'free_FS_bytes':64*1024**3,'CPU_effective_workers':4,'CPU_prepare_seconds':1800,'new_download_install_bytes':0,'raw_summary_bytes':64*1024**2,'additional_full_build_calls':1},'actual':{'GPU_lock_seconds_cumulative':obs['GPU_lock_seconds_cumulative'],'prior_A50G_GPU_seconds':obs['prior_A50G_GPU_lock_seconds'],'this_recovery_GPU_seconds':obs['GPU_lock_seconds_this_recovery'],'RSS_bytes_sampled_cumulative_max':max(prior['peak_RSS_bytes_sampled'],obs['peak_tree_RSS_bytes_sampled'],check['peak_CPU_verifier_RSS_bytes']),'GPU_MiB_sampled_cumulative_max':max(prior['peak_GPU_MiB_sampled'],obs['peak_GPU_MiB_sampled']),'this_recovery_GPU_MiB_sampled':obs['peak_GPU_MiB_sampled'],'new_allocated_bytes_current_cumulative':size,'prior_new_allocated_bytes_carried':6111232,'free_FS_bytes_at_archive':free,'CPU_prepare_seconds_cumulative_upper_estimate':prep_upper,'CPU_prepare_estimation_method':'first resource sample monotonic mapped to wall time minus recovery start epoch, plus original278.173s; includes first monitor sample overhead','download_install_bytes':0,'CPU_effective_affinity':[0,2,4,6],'OMP_limit':4,'OMP_BLAS_requested':1,'sampled_running_threads_max':max(x['running_threads'] for x in obs['samples']),'raw_bytes_before_git':sum(p.stat().st_size for p in D.rglob('*') if p.is_file()),'additional_full_build_API_calls':1,'cumulative_full_build_API_calls':2,'actual_formal_points':0},'supervisor':obs,'original_resource_receipt':prior,'old_assets_unchanged':True,'own_GPU_children_ended':True,'shared_lock_released':True,'no_next_goal':True,'no_observed_budget_violation':True,'sampling_caveat':'RAM and VRAM are sampled, not guaranteed exact instantaneous peaks; early watchdog margins were used. Final archival sizes below are before the small report and checksum files; exact final inventory is read back after publication.'};write('RESOURCE_RECEIPT.json',resources)
rows='\n'.join('| '+str(x['B'])+' | '+('AUTO' if x['arm']=='A' else 'SINGLE_CTA+SMALL h'+str(x['h']))+' | '+format(x['recall_at10'],'.4f')+' | '+format(x['strict_ID_recall'],'.4f')+' | FAIL |' for x in cal['configurations'])
report=f'''# A50G corrected continuation — native index/reload/numerics pass, calibration QUALITY_NO_GO

**Final scientific state: QUALITY_NO_GO.** The packaging correction was actually executed successfully. One additional full-base build, authorized by the user's instruction “那你改正。然后接着做”, was saved and reloaded with identical search outputs. All six fixed 2000-query calibration configurations then failed the unchanged recall>=0.95 gate. No common h was eligible; h selection, independent report recall and all four formal timing points are NOT_RUN. This is measured negative quality evidence, not a performance or hardware result.

## Identity and authorized recovery

Publish only `hrl/aiarch-a50g-glove100-default-native-full-109-v1`, with original start `ea32eb190cf9697556f3560263b7a637563c69e7` and immediate parent `d74ba0225516e60aa1c18b7ee87c88abfc34e0c9`. A new recovery worktree/output and local-only recovery branch isolate all changes. The old A50G STOP report and code remain unchanged in this tree; the original A50G worktree remains at d74ba022 and clean. No coordination branch merge, old environment/cache change or old task restart occurred.

The earlier full build returned fields but its process lost the unsaved index on a pinned-memory NumPy reshape error. The latest explicit user continuation was interpreted and announced as permission for **one additional complete build**, without resetting GPU/download/disk/CPU budgets or changing scientific conditions. Total A50G complete-base build API calls=2: original1 + recovery1. There was no third build, no saved-only retry and no algorithm/source repair.

Original official GloVe100 HDF5:485413888B, SHA256 `544af1d5e84e112cd4749571dcfd8ca109818a572f850af75a3a09e093a953c4`. Full FP32 normalized1183514x100 base, original10k queries/GT and frozen2000calibration/8000report split were reused read-only. Split SHA `0fb3e14cd9b4b9c97397235c5dddcd73b1a53bb5979b04ac5e3762f8c559c650`; timing2048-list SHA `f7ebf0825b6ba7e351df18c20f8e0cb559b37fdbf0775142d989161df7baafea`. No query split, seed mask, dtype, normalization, GT, threshold or build/search parameter change.

## Gates and corrected execution

| Gate | Actual result |
|---|---|
| G0 | PASS; all167 frozen A47 files hash/mtime/size, environment metadata, source, query identity and script AST checked |
| G1 | PASS; real pinned allocation and transfer preflight, full build fields, save/hash, owner-safe reload, ID/distance numeric checks |
| G2 | QUALITY_NO_GO; all6 fixed calibration settings tested on2000queries each, no eligible h |
| G3 | NOT_RUN; all4 formal points have0samples; no fresh timing processes launched |
| G4 | Actual raw results, negative evidence, budget/SHA receipts and publication; STOP |

Actual pinned allocation exposed B1 buffers512/512/512B for logical400/40/40B and B256 buffers131072/16384/16384B for logical102400/10240/10240B. Explicit element counts fixed the view shapes. Actual default-stream H2D/D2H roundtrips passed **before** the additional complete build. The full index was saved and hashed immediately after required-field qualification, before any canary helper. No subsequent wrapper exception occurred.

Observed cuVS26.10 wheel commit `24ee1bf1cb17cad0ac611e39643af39ee1870124`, CuPy14.0.1/default allocator None.malloc, default RMM CudaMemoryResource, default Resources/default CuPy stream; RTX4080/76SM/CC8.9. No explicit pool, nondefault stream, allocator/resource override, installation, download or core compilation. Exact versions and source/library hashes are recorded, and frozen files were rechecked after GPU exit.

## Index, numerical qualification and recall

Built and reloaded fields independently all passed: trained=True, size1183514, dim100, graph_degree64, dtype repr class numpy.float32, normalized float32. Build cosine/ivf_pq/degree64/intermediate128 unchanged. The normal initial dimension100/old0 dataset-attach warning remains in raw logs and was not treated as a failure.

Saved index **{idx['bytes']}B**, SHA256 **`{idx['sha256']}`**, include_dataset=True. Precreated Index plus live owning padded-device Dataset were used for reload. All actual searches use that one graph. Logical graph element hash is UNKNOWN; serialized SHA does not prove an independently hashed graph view. The complete index remains private at `<RECOVERY_OUTPUT>/glove.index` and is not in Git or copied164.

Two fixed AUTO functional configurations used B1/32canary queries and B256/256calibration queries; before/after reload IDs **and distances were byte-identical**. Returned IDs legal/nonduplicate; distances finite and consistent with original FP64 cosine reference at atol1e-5/rtol1e-4. The frozen32-query **full1183514-base** FP64 oracle's kth10 threshold agrees with original GT. Worst returned-distance absolute error across the actual calibration outputs was about **2.061e-7**. Numerical distance PASS is distinct from approximate top-k recall PASS: the former passed, the latter failed. The functional B1 canary recall was0.93125; B256's256-query aggregate was0.848046875, both retained without hiding misses.

| B | Fixed configuration | Tie-aware recall@10 | Strict ID recall@10 | Quality |
|---|---|---:|---:|---|
{rows}

All6 candidates are below0.95. B1 AUTO vs either SMALL differs by0.0939, above the0.005 same-B limit; B256 deltas are0 but both sides fail0.95. No h9/h11 is eligible and neither is selected. Five single-CTA calibration outputs have identical neighbor/distance SHA, including both h values and B256 AUTO; this is output identity, not an explanation of all quality loss. No h-timing selection or quality-threshold relaxation was attempted.

An independent **CPU-only** verifier reloaded all10 raw NPZ sets (4before/after canary +6calibration), recomputed FP64 distances using a separately expressed NumPy sum, frozen tie-aware and strict recalls, all output hashes, and reload identity. It confirmed the actual quality STOP. It also rechecked188 old asset hashes/mtimes (167frozen +21prior-A50G files), the old clean worktrees/HEADs and serialized-index SHA. Its peak RSS was{check['peak_CPU_verifier_RSS_bytes']}B. Full outputs/query IDs/per-query hits are archived; no report-query result was generated.

| Formal point | Report recall | Formal samples |
|---|---|---:|
| B1 AUTO | NOT_RUN |0|
| B1 SMALL | NOT_RUN; h unselected |0|
| B256 AUTO | NOT_RUN |0|
| B256 SMALL | NOT_RUN; h unselected |0|

No GPU-resident service or CPU/H2D/search/D2H formal wall was measured. Build/save/load elapsed values are budget bookkeeping only. No 3fresh-process x10paired-block comparison or speedup can be reported.

## Source-qualified path interpretation

`EFFECTIVE_PATHS.json` separates REQUESTED, SOURCE_DERIVED and DEVICE_OBSERVED facts. Fixed source with observed76SM selects AUTO B1 MULTI_CTA (global traversed HASH bit11 plus CTA-local visited SMALL bit9,4CTAs/query), AUTO B256 SINGLE_CTA+SMALL bit9, and forced SINGLE_CTA+SMALL bit9 or11. Small reset intervals are source-derived2/14 for bit9/11; multi-CTA visited table resets each iteration. Standard FP32 cosine descriptor dim100 selects source-derived team8. Forced block128 is requested; AUTO final dynamic block and actual device iteration/distance counts are UNKNOWN. No launch tracer/profiler was added. These are possible software-path differences, with no qualified timing or hardware-benefit claim.

## Cumulative resources and preserved assets

Original shared lock was acquired nonblocking, no external compute task was found, and it was held through the owned GPU child exit. Recovery held **{obs['GPU_lock_seconds_this_recovery']:.6f}s**, prior held3.959299s, cumulative **{obs['GPU_lock_seconds_cumulative']:.6f}s** of2700s. Sampled cumulative RSS peak **{resources['actual']['RSS_bytes_sampled_cumulative_max']}B** ({resources['actual']['RSS_bytes_sampled_cumulative_max']/1024**3:.3f}GiB); sampled cumulative VRAM peak **{resources['actual']['GPU_MiB_sampled_cumulative_max']}MiB** (recovery{obs['peak_GPU_MiB_sampled']}MiB). Sampling can miss instantaneous peaks; early watchdog margins retained. Effective CPU affinity0,2,4,6/OMP limit4, requested OMP/BLAS1. No limit violation was observed.

Current original-plus-recovery new allocation at archival inventory **{size}B** ({size/1024**3:.3f}GiB), including the776387032B serialized index, separate new worktree/cache/raw and original6111232B carried usage. Same FS free **{free}B** ({free/1024**3:.3f}GiB), above64GiB. Small final report/checksum/Git publication growth is checked again in final private readback receipt. CPU preparation cumulative upper estimate{prep_upper:.3f}s, below1800s. Added data/dependency downloads/installations=0. No old caches/env were cleaned or modified; no NequIP/3DGS/C16/AWMA task was started. All task GPU children ended, original lock released, final compute-process metadata empty.

## Unique minimal next proposal — not started

Perform an **independent CPU-only source/output audit** of this fixed-quality deficit before proposing more GPU work: compare per-query misses/neighbor overlap between B1 AUTO and the five identical single-CTA outputs, check recorded full-base GT/tie identities and exact fixed-source termination/candidate-retention semantics. Inputs and executable steps are in NEXT_STEP_PROPOSAL; no rebuilding, searching, CUDA import or new data. A sufficient small audit envelope is GPU0/download-install0, CPU<=4, RAM<=2GiB, newdisk<=64MiB, <=20minutes. Stop on identity mismatch, need for old-file mutation, CUDA/new dependencies or envelope exceed. The proposed audit is not executed as a new Goal here.

Current frozen configuration cannot support the intended equal-quality four-point performance comparison. Any subsequent GPU quality repair requires a separately reviewed and explicitly approved quality-first contract; do not silently expand itopk/iteration/hash choices or lower recall. No AUTO/SMALL performance or cache/SMEM headroom conclusion follows from failed recall. Await independent scientific review; **no automatic next GPU task**.

## Publication

Only the original A50G execution branch is pushed. This recovery adds a distinct report/raw directory and minimal recovery scripts, preserving every earlier STOP blob. Raw NPZ identities are unchanged; text paths are redacted while API parameters/return codes remain intact. The index, base/HDF5 and environment remain private. SHA256SUMS covers the report/evidence/scripts. Exact commit/tree/all added blob+SHA fetch-back and clean worktree checks are completed separately to avoid a self-referential commit SHA. STOP.
'''
write('FINAL_REPORT.md',report)
files=sorted([p for p in D.rglob('*') if p.is_file() and p.name!='SHA256SUMS']+list((W/'tools/aiarch_a50g_recovery').glob('*.py')));(D/'SHA256SUMS').write_text(''.join(sha(p)+'  '+str(p.relative_to(W))+'\n' for p in files))
for p in D.rglob('*.json'):json.loads(p.read_text())
assert sum(p.stat().st_size for p in D.rglob('*') if p.is_file())<64*1024**2
print('ARCHIVE_READY',len(files)+1,'QUALITY_NO_GO','cumulative_disk',size,'free',free,'prep_upper',prep_upper)
