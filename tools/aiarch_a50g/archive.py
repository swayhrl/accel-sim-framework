"""Archive actual A50G engineering stop; no GPU calls or inferred performance."""
import pathlib,json,hashlib,subprocess,os,time,shutil,re
ROOT=pathlib.Path('/data/c16/aiarch_a50g_glove100_default_full_109_v1');OLD=pathlib.Path('/data/c16/aiarch_a47_cagra_glove100_109_v1');WORK=pathlib.Path(__file__).resolve().parents[2];PUB=WORK/'docs/ai_workload_research/runs/AI_ARCH_A50G_GLOVE100_CAGRA_DEFAULT_FULL_109_V1';PUB.mkdir(parents=True,exist_ok=True);(PUB/'raw').mkdir(exist_ok=True)
def read(n):return json.loads((ROOT/n).read_text())
def digest(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()
def clean(s):return re.sub(r'0x[0-9a-fA-F]+','<ADDRESS>',s.replace(str(WORK),'<WORKTREE>').replace(str(ROOT),'<A50G_OUTPUT>').replace(str(OLD),'<A47_READONLY>').replace('/home/huangrulin','<HOME>'))
def write(n,d):(PUB/n).write_text(clean(d if isinstance(d,str) else json.dumps(d,indent=2)+'\n'))
snap=read('old_asset_snapshot.json')
for x in snap['files']:
 p=pathlib.Path(x['path']);assert digest(p)==x['sha256'] and p.stat().st_mtime_ns==x['mtime_ns']
for x in snap['worktrees']:
 p='/home/huangrulin/workspace/worktrees/'+x['label'];assert subprocess.check_output(['git','-C',p,'rev-parse','HEAD'],text=True).strip()==x['head'];assert subprocess.check_output(['git','-C',p,'status','--porcelain'],text=True)==''
assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader'],text=True).strip()
obs=read('supervisor_receipt.json');build=read('build_observation.json');repair=read('packaging_repair.json');pre=read('preflight.json');assert all(build['fields']['assert_predicate_map'].values());assert not (ROOT/'glove.index').exists();assert obs['stages'][0]['returncode']==1
state='INDEX_RELOAD_OR_NUMERIC_NO_GO';cause='POST_BUILD_ENGINEERING_STOP_UNIQUE_BUILD_CONSUMED'
gates={'terminal_scientific_state':state,'precise_cause':cause,'not_a_numeric_or_recall_failure':True,'G0':'PASS_FROZEN_INPUT_ENV_QUERY_RESOURCE_CPU_SCRIPT_CHECKS','G1':{'full_base_build_API_calls':1,'build_returned_synchronized':True,'required_index_fields':'ALL_PASS','serialization':'NOT_RUN','reload':'NOT_RUN','numerical_canary':'NOT_RUN','reason':'Pinned-buffer NumPy view reshape exception before save; GPU child exited and in-memory index lost.'},'G2':'NOT_RUN_G1_BLOCKED','G3':'NOT_RUN_G1_BLOCKED','G4':'ARCHIVED_FOR_SINGLE_BRANCH_PUBLICATION','no_next_goal':True}
size=sum(p.stat().st_blocks*512 for root in [ROOT,WORK] for p in root.rglob('*') if p.is_file());free=shutil.disk_usage(ROOT).free;assert size<2*1024**3 and free>=64*1024**3
resource={'limits':{'GPU_lock_seconds':2700,'new_download_install':0,'new_disk_bytes':2*1024**3,'RAM_bytes':8*1024**3,'VRAM_bytes':12*1024**3,'CPU_workers':4,'prepare_seconds':1800,'free_FS_bytes':64*1024**3,'raw_summary_bytes':64*1024**2,'full_build_calls':1,'formal_points':4},'actual_GPU_lock_seconds':obs['GPU_lock_seconds_cumulative'],'peak_RSS_bytes_sampled':obs['peak_tree_RSS_bytes_sampled'],'peak_GPU_MiB_sampled':obs['peak_GPU_MiB_sampled'],'peak_disk_bytes_sampled':obs['peak_new_allocated_bytes_sampled'],'new_current_bytes':size,'free_FS_bytes':free,'CPU_preparation_seconds':pre['prepare_elapsed_seconds'],'CPU_affinity':[0,2,4,6],'OMP_limit':4,'OMP_BLAS_requested':1,'new_data_dependency_download_install':0,'GPU_children_ended':obs['all_own_GPU_children_ended'],'shared_lock_released':obs['shared_lock_released'],'observed_budget_violation':False,'watchdog_early_margin_policy':{'VRAM_stop_MiB':11520,'RAM_stop_GiB':7.5,'new_disk_stop_GiB':1.875,'deadline_margin_seconds':15},'sampling_caveat':obs['sampling_limits'],'supervision':obs,'old_SHA_mtime_reverified':len(snap['files']),'old_worktrees_clean':True}
write('GATES.json',gates);write('ENV_LOCK.json',json.loads((OLD/'resolved_env_lock.json').read_text()));write('DATA_AND_INDEX_IDENTITY.json',{'source_input':read('frozen_data_identity.json'),'frozen_query_identity':read('frozen_preregistration.json'),'actual_build':build,'actual_build_entry':read('full_build_enter.json'),'index_serialized_bytes':'NOT_CREATED','index_serialized_SHA256':'NOT_AVAILABLE','logical_graph_hash':'UNKNOWN_PUBLIC_VIEW_NOT_READ','graph_contents_qualified':False})
quality={'actual_search_calls':0,'functional_search_configurations_completed':0,'first_functional_configuration_constructed_but_search_not_entered':{'B':1,'arm':'AUTO'},'numerical_canary':'NOT_RUN','reload_canary':'NOT_RUN','calibration':'NOT_RUN','chosen_h':'NOT_SELECTED','report_recall':'NOT_RUN','formal_timing':[{'B':b,'arm':a,'status':'NOT_RUN','actual_samples':0} for b in [1,256] for a in ['AUTO','SINGLE_CTA_SMALL']],'scientific_performance_classification':'UNAVAILABLE_NO_SEARCH_DATA','do_not_infer_application_or_hardware_negative_result':True}
write('QUALITY_AND_TIMING.json',quality);write('RESOURCE_RECEIPT.json',resource);write('ENGINEERING_REPAIR.json',repair)
identity={'repository':'swayhrl/accel-sim-framework','branch':'hrl/aiarch-a50g-glove100-default-native-full-109-v1','fixed_start':'ea32eb190cf9697556f3560263b7a637563c69e7','client_date':'2026-10-15 Asia/Shanghai','preflight':pre,'device':read('device_identity.json'),'old_worktrees':snap['worktrees'],'executed_source':'tools/aiarch_a50g/native_executed.py','executed_native_SHA256':repair['executed_native_sha256'],'corrected_unexecuted_native_SHA256':repair['corrected_native_sha256'],'current_scripts':{str(p.relative_to(WORK)):digest(p) for p in sorted((WORK/'tools/aiarch_a50g').glob('*.py'))},'no_corrected_GPU_code_was_run':True}
write('RUN_IDENTITY.json',identity)
for p in (ROOT/'logs').glob('*.log'):write('raw/'+p.name,p.read_text())
for p in (ROOT/'raw').glob('*.jsonl'):write('raw/'+p.name,p.read_text())
for name in ['preflight.json','full_build_enter.json','build_observation.json','packaging_repair.json']:write('raw/'+name,read(name))
write('raw/old_asset_snapshot.json',snap)
nextstep={'status':'PROPOSAL_ONLY_NOT_STARTED','unique_minimum_recommendation':'Independent review of this avoidable packaging interruption and corrected transfer/save ordering; only if specifically authorized for one additional full build, repeat the default-only full protocol as one checkpointed Goal. No vendor/debug/driver changes warranted by current evidence.','new_evidence':'same real graph serialized before downstream helpers, reload+numerical+quality and4paired points still missing','necessary_before_any_new_full_build':['actual B1/B256 pinned-buffer shape/transfer checks under that future GPU lock, before build quota consumption','CPU rounded-buffer count tests already PASS','save/hash unique built index immediately after field qualification, before canary/measurement wrappers','preserve saved index for bounded load-only recovery; no automatic second build in the next task either'],'proposed_cap_envelope':{'new_download_install':0,'new_disk_GiB':2,'RAM_GiB':8,'VRAM_GiB':12,'CPU_workers':4,'GPU_lock_minutes':45,'CPU_prepare_minutes':30,'raw_summary_MiB':64,'full_build_calls':1,'formal_points':4,'functional_calibration_max_configs':8},'science_unchanged':'same frozen original inputs/query split/FP32/cosine/IVF-PQ64/128; h9/h11 only; recall>=.95 and same-B delta<=.005; default resources/streams only','STOP':['busy original lock/external GPU work','input/source/core/dtype/GT change','native failure or invalid required index fields','bad numeric/reload/recall or no common eligible h','any resource/cumulative deadline exceed, no quota reset','no performance gap or unstable gap ->legal negative; software wins are not hardware opportunity'],'not_authorized_in_this_goal':'another complete build; quota consumed and no checkpoint exists','no_automatic_future_task':True};write('NEXT_STEP_PROPOSAL.json',nextstep)
report=f'''# Round A50G | Full default-path build fields pass; downstream packaging STOP

**Terminal: {state}; precise cause POST_BUILD_ENGINEERING_STOP_UNIQUE_BUILD_CONSUMED.** The sole complete-base CAGRA build API was actually called, returned and synchronized. All five required index fields passed. A Python transfer-buffer view error then terminated the GPU child **before index serialization and before any search**. The live index object was lost on process exit. Rebuilding would violate this Goal's one-full-build hard limit; no second build or GPU retry was performed.

This is an avoidable execution-wrapper failure. It is **not** a detected numeric/recall failure, native SIGSEGV, hardware-resource failure or negative AUTO/SMALL result. The normative index/reload/numeric admission state is NO_GO because those downstream qualifications remain unperformed, not because bad numerical values were measured. No application or hardware conclusion can be drawn.

## Authority and isolation

Repository swayhrl/accel-sim-framework; independent branch `hrl/aiarch-a50g-glove100-default-native-full-109-v1`; fixed start `ea32eb190cf9697556f3560263b7a637563c69e7`, user-approved A50G contract. A50 review, A47/R1/R2 fixed evidence, original preregistration/data/env/quality and executed-source identities were read. Protocol bytes matched the previously read accepted version. All{len(snap['files'])} original A47/R1/R2 SHA+mtime checks and their HEAD/clean states were reverified after exit. Old env/data/cache/raw/worktrees were not changed; no coordinator merge or CURRENT_STATE edits.

## Actual gates and fields

| Gate | Actual outcome |
|---|---|
| G0 | PASS: frozen official env/wheels/libs/input/query identities, resources, dtype/formatter and script AST/compile checks |
| G1 complete-base build API | called once, returned, synchronized, all required fields PASS |
| G1 index save/load/numeric canary | NOT_RUN: pinned-buffer view exception before save; no serialized file |
| G2 calibration/report recall | NOT_RUN; h not selected |
| G3 four formal points | NOT_RUN; every point has0samples |
| G4 | evidence/corrected code/CPU verification/publication and STOP |

| Actual field | Value | Predicate |
|---|---|---|
| trained |true|true|
| size |1183514|true|
| dim |100|true|
| graph_degree |64|true|
| dtype_repr / normalized |class numpy.float32 / float32|true via np.dtype comparison|

The new-dataset100/old-index0 attach warning was retained and not misclassified; final observed dimension is100. Graph edge contents were not read/hash-validated. Native API/index metadata PASS does not stand in for serialized index, correct graph contents, search/recall or scientific timing.

Complete frozen FP32 base(1183514x100) was uploaded in the default CuPy stream and synchronized. `Resources()` and observed default RMM CudaMemoryResource/default CuPy None.malloc were used; no nondefault stream, explicit RMM pool or allocator setter. Build cosine/ivf_pq/degree64/intermediate128 stayed fixed; actual random seed for native build is UNKNOWN/not exposed. Actual RTX4080/76SM/CC8.9, Driver API13000/runtime12090 and cuVS26.10 source24ee1bf1cb17cad0ac611e39643af39ee1870124 were recorded.

## Input/query identity and unavailable scientific results

Original official HDF5485413888bytes SHA256 `544af1d5e84e112cd4749571dcfd8ca109818a572f850af75a3a09e093a953c4`, original normalized FP32 base/query and original GT all remain read-only. No base truncation, random substitute, FP16, metric or quality alteration. Source/derived-file hashes are in DATA_AND_INDEX_IDENTITY.

Frozen calibration2000/report8000 sets are disjoint; timing2048report queries are distinct. Split SHA `0fb3e14cd9b4b9c97397235c5dddcd73b1a53bb5979b04ac5e3762f8c559c650`, timing-list SHA `f7ebf0825b6ba7e351df18c20f8e0cb559b37fdbf0775142d989161df7baafea` verified. No selection looked at new report performance; there are no search outputs at all.

| Formal point | Recall | Paired/native timing samples |
|---|---|---:|
| B1 AUTO |NOT_RUN|0|
| B1 SMALL |NOT_RUN, h not chosen|0|
| B256 AUTO |NOT_RUN|0|
| B256 SMALL |NOT_RUN, h not chosen|0|

Original canary atol1e-5/rtol1e-4, GTkth10+.001 tie rule and recall>=.95/same-B delta<=.005 were preserved but not actually tested against a CAGRA result. Frozen prior CPU oracle remains historical identity evidence only. Neither synchronized resident-query service nor complete CPU/H2D/search/D2H wall was collected. Build/supervision elapsed values are resource bookkeeping, not search-performance samples.

## Exact wrapper error and bounded repair

After build, the first B1/AUTO functional preparation constructed Buffers(1). CuPy pinned allocations may expose an **alignment-rounded underlying buffer**: requested400bytes for100float32 values exposed512bytes/128elements. `np.frombuffer(pinned,dtype=float32).reshape(1,100)` therefore raised **ValueError: cannot reshape array of size128 into shape(1,100)**. Search had not been called. Process exit1 released the unsaved in-memory index; no index file or recoverable checkpoint exists. This should have been prevented by preallocation checks and save-first ordering.

Within this same Goal, the deterministic engineering repair was made concrete and CPU-verified:

- Every pinned view now passes an explicit element count (query Bx100, ID/distance Bx10; calibration/timing views likewise).
- B1/B256 buffer shapes are checked before a future unique full-build call.
- Corrected runner saves and hashes the built index immediately after required-field PASS, before any downstream buffer/search helper.
- CPU tests with512-byte-rounded buffers passed B1/B256 shape, dtype and contiguous-view checks. No GPU reconstruction/test was run after the stop; this CPU test is not proof that downstream native phases pass.

`tools/aiarch_a50g/native_executed.py` preserves the exact executed source; `native.py` is the corrected **unexecuted** code, distinct SHA identities in ENGINEERING_REPAIR/RUN_IDENTITY. Original failure/phase logs and build entry/fields were not discarded or overwritten. The one-build scientific limit prevents an apparently simple process restart from repairing the missing checkpoint in this authorization.

## Resources and safety

GPU original shared lock acquired nonblocking and released after the own child ended. Cumulative hold **{obs['GPU_lock_seconds_cumulative']:.6f}s**, sampled process-tree RSS **{obs['peak_tree_RSS_bytes_sampled']}bytes** ({obs['peak_tree_RSS_bytes_sampled']/1024**3:.3f}GiB), sampled GPU **{obs['peak_GPU_MiB_sampled']}MiB**. Early watchdog margins were11.25GiBVRAM/7.5GiBRAM/1.875GiBnewdisk with15sdeadline reserve; no limit violation was observed. Sampling is not an exact instantaneous peak proof.

CPU preparation{pre['prepare_elapsed_seconds']:.3f}s below30min, effective affinity0,2,4,6; OpenMP cap4 and BLAS requested1. New worktree/output allocated{size}bytes ({size/1024**2:.3f}MiB), free FS{free}bytes (>64GiB). Data/dependency download, installation, core compilation, system/driver changes=0. Runtime caches/bytecode policy isolated. Final CPU metadata confirmed no compute process. No NCU/NSYS/NVBit, simulator, training, second dataset, parameter scan or new mechanism.

## Unique smallest next recommendation — proposal only

First independently review this engineering interruption and the corrected buffer/save ordering. **Only if separately authorized for one additional full build**, execute one checkpointed default-only continuation protocol as a new bounded contract. Do not reinterpret this run's unused45min as another build permission, and do not spend another round debugging nondefault streams or changing vendors/drivers: the current blocker was our wrapper after native field success.

Concrete future sequence: reuse all current frozen source/data/query/GT and env; new independent output/ledger; under the original nonblocking lock, validate actual B1/B256 pinned-buffer shapes and host/device transfer completion **before** the sole full build. Build once, record all index fields, then immediately save/hash before any functional helper. Preserve that checkpoint and allow only load-based bounded wrapper recovery thereafter. Reload with precreated Index/Dataset and live owner;32-query full-base numeric/ID canary, fixed6calibration candidates plus<=2functional configs, common h9/h11 at unchangedrecall>=.95/delta<=.005,8000report quality,3fresh processes x10ABBA/BAAB paired blocks at four points, then raw/remote readback/STOP. No broadening of parameters or source changes.

Proposed resource ceiling remains original: new downloads/install0, newdisk<=2GiB/freeFS>=64GiB, RAM<=8GiB/VRAM<=12GiB,CPU<=4, preparation<=30min, shared-lock<=45min, raw<=64MiB, **one newly and explicitly authorized full build**. These are proposed caps, not measured minimum full-scale requirements. Busy lock/other GPU work, identity/precision change, native failure/invalid fields, canary/reload/quality failure or resource/deadline exceed ->STOP; no repeated build. AUTO sufficient/no stable complete-wall gap is a legitimate negative; SMALL advantage first means existing software configuration, not hardware headroom. The proposal is not executed or automatically authorized.

## Publication / hard STOP

Only the independent A50G branch adds this report, actual fields/error/raw/asset/resource receipts, SHA index and minimal executed/corrected scripts. HDF5/env stay private; no full serialized index was produced, and no data/index was copied164 or committed. One commit/push/fetch-back checks exact enclosing commit/tree/all new blobs and SHA,clean; final receipt is separate to avoid self-reference. **STOP, no next GPU Goal.**
'''
write('FINAL_REPORT.md',report)
files=sorted([p for p in PUB.rglob('*') if p.is_file()]+list((WORK/'tools/aiarch_a50g').glob('*.py')));(PUB/'SHA256SUMS').write_text(''.join(digest(p)+'  '+str(p.relative_to(WORK))+'\n' for p in files))
for p in PUB.rglob('*.json'):json.loads(p.read_text())
assert sum(p.stat().st_size for p in PUB.rglob('*') if p.is_file())<64*1024**2;print('A50G_ARCHIVE_READY',len(files)+1,state,cause,'OLD_UNCHANGED',len(snap['files']))
