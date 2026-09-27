#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path('/data/c16/awma/r54_greedy_semantic_requal_v1r2_20260927')
PUB=Path('/data/c16/awma/r54_greedy_semantic_requal_v1r2_publication_20260927')
WT=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r54-greedy-semantic-requal-v1r2')
V1=Path('/data/c16/awma/r54_checkpoint_lifecycle_20260927')
V1R1=Path('/data/c16/awma/r54_fastpath_requal_v1r1_20260927')
FULL=PUB/'full_r54'
GREEDY_PACK=WT/'docs/vm_tlb/review_packs/AWMA_R54_GREEDY_SEMANTIC_REQUALIFICATION_V1R2'
FULL_PACK=WT/'docs/vm_tlb/review_packs/AWMA_R54_EXACT_RECURRENT_CHECKPOINT_LIFECYCLE_V1R2'
REPORT=WT/'docs/vm_tlb/reports/AWMA_R54_GREEDY_SEMANTIC_REQUALIFICATION_109_V1R2_REPORT.md'
for p in (PUB,FULL,GREEDY_PACK,FULL_PACK,REPORT.parent):p.mkdir(parents=True,exist_ok=True)

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')

def copy(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,dst)

def write_tsv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(rows)

greedy=json.loads((ROOT/'R54_V1R2_DECISION.json').read_text())
prod=json.loads((ROOT/'PRODUCTION_ANALYSIS.json').read_text())
components=json.loads((ROOT/'R54_COMPONENT_ANALYSIS.json').read_text())
restore=json.loads((ROOT/'RESTORE_CANARY_RECEIPT.json').read_text())
holdout=json.loads((ROOT/'HOLDOUT_CANARY_RECEIPT.json').read_text())
assert greedy['state']=='R54_V1R2_GREEDY_BACKEND_QUALIFIED'
assert restore['qualified'] and holdout['qualified']
assert prod['P2_D512']['stable_material_cost']
assert components['holdout']['p2_stable_material_cost']
assert not any(v['material_restore'] for v in components['restore'].values())
assert json.loads((ROOT/'CHECKPOINT_AUTHORITY_REQUAL_JOIN.json').read_text())['token_4096_P2_D512_checkpoint_hashes_exact_match']

final_state='R54_HOST_RUNTIME_COST_NOT_ARCH_LOCALIZED_V1'
driver=subprocess.check_output(['nvidia-smi','--query-gpu=name,compute_cap,driver_version',
                                '--format=csv,noheader'],text=True).strip()
v1r1_env=json.loads((V1R1/'R54_V1R1_ENVIRONMENT_RECEIPT.json').read_text())
backend={'stage':'AWMA_R54_GREEDY_SEMANTIC_REQUALIFICATION_V1R2',
 'accepted_v1_commit':'40f51deacee491d7e1b57f09db533d43d84d7ad5',
 'accepted_v1r1_commit':'61707eecc3cb934c309cb016a750cb4d7612a88d',
 'model':'Qwen/Qwen3.5-0.8B','model_revision':'c6046cd1f7e2763bf1abf5a5aef6ad7878e10ccb',
 'model_weight_sha256':'04b1c301231dd422b8860db31311ab2721511346a32cb1e079c4c4e5f1fe4696',
 'transformers_commit':'96331a9f93b72697f160a958d2883d4b49a56739',
 'kernels':'0.17.0','torch':'2.14.0+cu130',
 'mamba_revision':'20b2508ad12ae40260291539bf45183000451850',
 'fla_revision':'6d22ed1d2bb627375b6ca8fc135f7f417863e639',
 'gpu_driver':driver,
 'v1r1_environment_receipt_sha256':sha(V1R1/'R54_V1R1_ENVIRONMENT_RECEIPT.json'),
 'v1r1_hub_provenance_sha256':sha(V1R1/'HUB_KERNEL_PROVENANCE.tsv'),
 'model_redownloaded':False,'backend_changed_from_v1r1':False,
 'greedy_contract':'R54_GREEDY_BACKEND_EQUIVALENCE_V1',
 'greedy_gate':greedy['state']}
dump(PUB/'R54_V1R2_BACKEND_RECEIPT.json',backend)

inheritance='''# Accepted history and V1R2 scope\n\n- V1 `R54_RUNTIME_FASTPATH_NOT_QUALIFIED_V1` remains valid for the local causal-conv1d/FLA package path.\n- V1R1 `R54_V1R1_HUB_KERNEL_SEMANTICS_NOT_QUALIFIED` remains valid for exact top1/top2 ordering across fallback and Hub.\n- V1R2 separately froze temperature=0 greedy continuation as the application contract before running S0, S1, S2.\n- Checkpoint/restore correctness uses the uninterrupted Hub backend as its reference. It does not require unselected fallback logits to match Hub logits.\n'''
(PUB/'V1_V1R1_INHERITANCE.md').write_text(inheritance)
for name in ['R54_V1R2_PREFIX_RECEIPT.json','R54_V1R2_PREREGISTRATION.json',
             'R54_V1R2_GREEDY_RESULTS.tsv','R54_V1R2_NUMERICAL_DIAGNOSTICS.tsv','R54_V1R2_DECISION.json']:
    copy(ROOT/name,PUB/name)
greedy_md=f'''# R54 V1R2 greedy backend decision\n\nState: `{greedy['state']}`.\n\nAll three frozen prefixes (64, 2048, 4096 tokens) produced identical 64-token greedy IDs in clean fallback and Hub processes. EOS/stop position, length, cache progression and finite logits passed. Across 192 diagnostic steps, top2 order differed at {greedy['top2_diagnostic_mismatch_count']} steps; those values remain in `R54_V1R2_NUMERICAL_DIAGNOSTICS.tsv`. No numerical tolerance was introduced.\n\nV1 and V1R1 remain as separate accepted negative results. The Hub backend was eligible for the checkpoint lifecycle under this application contract.\n'''
(PUB/'R54_V1R2_DECISION.md').write_text(greedy_md)

for name in ['FULL_R54_FIXTURE_RECEIPT.json','R54_EXACT_STATE_SCHEMA.tsv',
             'R54_STATE_PROBE_RECEIPT.json','R54_STATE_SCHEMA_REFINEMENT.json',
             'R54_SEMANTIC_GATE_RECEIPT.json','R54_PREREGISTRATION.json',
             'PRODUCTION_CANARY_RECEIPT.json','SNAPSHOT_PRODUCTION_TIMING.tsv',
             'SNAPSHOT_COPY_ACCOUNTING.tsv','PRODUCTION_ANALYSIS.json',
             'R54_P2_CHECKPOINT_AUTHORITY.json','CHECKPOINT_AUTHORITY_REQUAL_JOIN.json',
             'RESTORE_CANARY_RECEIPT.json','RESTORE_TIMING.tsv','RESTORE_ANALYSIS.json',
             'AMORTIZATION_RESULTS.tsv','R54_COMPONENT_ANALYSIS.json',
             'HOLDOUT_PREREGISTRATION.json','HOLDOUT_CANARY_RECEIPT.json',
             'HOLDOUT_RESULTS.tsv','HOLDOUT_ANALYSIS.json','NSYS_MEMCPY_STRATA.tsv']:
    copy(ROOT/name,FULL/name)
copy(ROOT/'FULL_R54_FIXTURE_RECEIPT.json',FULL/'PREFIX_FIXTURE_RECEIPT.json')
copy(ROOT/'R54_PREREGISTRATION.json',FULL/'PREREGISTRATION.json')
copy(V1/'MODEL_ADMISSION_RECEIPT.json',FULL/'MODEL_ADMISSION_RECEIPT_V1_ACCEPTED.json')
copy(V1/'R54_SOURCE_AND_CLOSEST_WORK_AUDIT.md',FULL/'R54_SOURCE_AND_CLOSEST_WORK_AUDIT_V1_ACCEPTED.md')
copy(V1/'R55_PLATFORM_AND_CLOSEST_WORK_AUDIT.md',FULL/'R55_PLATFORM_AND_CLOSEST_WORK_AUDIT_V1_ACCEPTED.md')
copy(V1R1/'R54_V1R1_ENVIRONMENT_RECEIPT.json',FULL/'R54_V1R1_ENVIRONMENT_RECEIPT_ACCEPTED.json')
copy(V1R1/'HUB_KERNEL_PROVENANCE.tsv',FULL/'HUB_KERNEL_PROVENANCE_V1R1_ACCEPTED.tsv')
copy(PUB/'R54_V1R2_BACKEND_RECEIPT.json',FULL/'RUNTIME_FASTPATH_RECEIPT.json')

semantic_rows=[
 {'gate':'GREEDY_BACKEND_S0_S1_S2','pass':greedy['all_prefixes_pass'],'authority':'R54_V1R2_GREEDY_RESULTS.tsv'},
 {'gate':'GDN_512_CHECKPOINT_RESTORE_BITWISE','pass':json.loads((ROOT/'R54_SEMANTIC_GATE_RECEIPT.json').read_text())['restore_512']['pass'],'authority':'R54_SEMANTIC_GATE_RECEIPT.json'},
 {'gate':'M0_MONOLITHIC_VS_P0_CHUNKED512','pass':json.loads((ROOT/'R54_SEMANTIC_GATE_RECEIPT.json').read_text())['m0_p0_4096']['pass'],'authority':'R54_SEMANTIC_GATE_RECEIPT.json'},
 {'gate':'P0_P1_P2_CHECKPOINT_CONTENT_AND_CONTINUATION','pass':json.loads((ROOT/'PRODUCTION_CANARY_RECEIPT.json').read_text())['qualified'],'authority':'PRODUCTION_CANARY_RECEIPT.json'},
 {'gate':'RESTORE_A_B_LIVE_REFERENCE','pass':restore['qualified'],'authority':'RESTORE_CANARY_RECEIPT.json'},
 {'gate':'HOLDOUT_2048','pass':holdout['qualified'],'authority':'HOLDOUT_CANARY_RECEIPT.json'},
]
write_tsv(FULL/'SEMANTIC_QUALIFICATION.tsv',semantic_rows)
restore_sem=[]
for arm,checks in restore['semantic_gates'].items():
    restore_sem.append({'arm':arm,'pass':all(checks.values()),'checks_json':json.dumps(checks,separators=(',',':'))})
write_tsv(FULL/'RESTORE_SEMANTIC_RESULTS.tsv',restore_sem)

ncu_reason='''# NCU admission at the conditional holdout boundary\n\nThe selected D512 P2 residual reproduced on the independent 2048-token holdout. Discovery overhead was 10.33 ms; timed D2D copies summed to 1.27 ms, overlapped with compute, while measured host per-layer snapshot scheduling was 6.52 ms. Holdout overhead was 4.92 ms; D2D copies summed to 0.67 ms and host scheduling was 3.21 ms. The P2 implementation also inserted 126 source-reuse event waits in discovery and 54 in holdout. D2048 overhead stayed below the 5% gate. Restore added 0.11–0.12 ms versus about 151 ms of avoided prefix compute.\n\nThis evidence does not establish a stable >=5% GPU-local snapshot or restore residual. Snapshot writes use CUDA device-to-device copies, with no dedicated SM snapshot kernel to select for NCU. Profiling unrelated model kernels would not localize copy-engine or host orchestration cost. NCU admission is therefore `NO_GPU_LOCAL_PROFILE_TARGET`; zero NCU profiles were run. NSYS/CUPTI traces and CUDA event timings remain the time-axis authority.\n'''
(FULL/'NCU_ADMISSION.md').write_text(ncu_reason)
write_tsv(FULL/'NCU_DIAGNOSTIC.tsv',[{'status':'NOT_RUN','admission':'NO_GPU_LOCAL_PROFILE_TARGET',
 'profile_count':0,'reason':'Holdout residual dominated by host/event scheduling; snapshot is D2D copy, not selected SM kernel'}])

root_readme='''# AWMA R54 Greedy Semantic Requalification V1R2\n\nThe frozen temperature=0 greedy backend contract passed on S0, 2048 and 4096. The original checkpoint lifecycle then ran under the same Hub backend. Final R54 state is `R54_HOST_RUNTIME_COST_NOT_ARCH_LOCALIZED_V1`.\n\nAccepted V1 and V1R1 conclusions remain unchanged. Raw greedy arm logits/receipts are under `raw/greedy/`; full checkpoint lifecycle evidence and NSYS artifacts are under `full_r54/`. Model and Hub artifacts are inherited by exact hashes from accepted V1/V1R1 node164 authorities; they are not duplicated here.\n'''
(PUB/'README.md').write_text(root_readme)
full_readme='''# AWMA R54 Exact Recurrent Checkpoint Lifecycle V1R2\n\nThis is the full R54 measurement closure after the V1R2 greedy backend gate passed. The scientific final state is `R54_HOST_RUNTIME_COST_NOT_ARCH_LOCALIZED_V1`. Formal production, restore, holdout, semantic gates, component analysis, phase ledger and NCU admission are compact here; NSYS/SQLite and raw logs are retained on node164 under `full_r54/raw/`.\n\nThe accepted V1 and V1R1 authorities remain separate and unchanged.\n'''
(FULL/'README.md').write_text(full_readme)
final_decision=f'''# Final decision\n\nV1R2 backend gate: `{greedy['state']}`.\n\nR54 scientific state: `{final_state}`.\n\nThe strong P2-D512 arm has a stable measured 6.58% production overhead on 4096 tokens and 6.31% on 2048-token holdout. The D2048 P2 arm is 1.57% above P0. The measured D512 D2D copy duration (1.27 ms discovery; 0.67 ms holdout) is much smaller than the end-to-end gap (10.33 ms; 4.92 ms), while per-layer host scheduling and source-reuse events dominate. Restore costs about 0.11–0.12 ms incrementally relative to ~151 ms of avoided prefix recompute. No qualified GPU-local >=5% residual is isolated.\n\nNo NCU profile or architecture review manifest was produced. No node174 or Accel-Sim was run.\n'''
(FULL/'R54_DECISION.md').write_text(final_decision)
(FULL/'FINAL_DECISION.md').write_text(final_decision)
(PUB/'FINAL_DECISION.md').write_text(final_decision)

component=components['holdout']
report=f'''# AWMA R54 V1R2 on node109\n\nThe Hub backend passed a separately frozen temperature=0 greedy contract across all three prefixes: S0, 2048 and 4096. Each fallback/Hub pair generated the same 64 token IDs, with identical stop behavior, finite logits and valid cache progression. Top2 ordering differed at {greedy['top2_diagnostic_mismatch_count']} of 192 diagnostic steps. V1 and V1R1 negative results remain valid for their own contracts.\n\nThe real `DynamicCache` has 18 GDN layers and 6 full-attention layers. An exact recurrent checkpoint contains 19,759,104 bytes of GDN conv/recurrent state plus metadata. Full-attention KV remains a separate resident prefix cache. The 512-token restore canary, M0/P0, P0/P1/P2 snapshot hashes, A/B restore continuations and holdout semantic gates all passed.\n\nDiscovery medians: P0 {prod['P0']['median_ms']:.3f} ms; P1-D512 {prod['P1_D512']['median_ms']:.3f} ms (+13.84%); P2-D512 {prod['P2_D512']['median_ms']:.3f} ms (+6.58%); P2-D2048 {prod['P2_D2048']['median_ms']:.3f} ms (+1.57%). D512 P2 exceeded the frozen 5% and 3× jitter gates. Holdout P0 {component['production_p0_ms']:.3f} ms and P2-D512 {component['production_p2_d512_ms']:.3f} ms (+6.31%) reproduced the residual.\n\nTimed copy GPU work was 1.27 ms against 10.33 ms discovery overhead and {component['P2_D512_copy_gpu_ms_sum']:.3f} ms against {component['P2_D512_overhead_ms']:.3f} ms holdout overhead. Measured host snapshot scheduling was 6.52 and {component['P2_D512_host_snapshot_schedule_ms']:.3f} ms respectively. The discrepancy is not localized to a GPU snapshot engine. Restore was 0.11–0.12 ms above live suffix, 0.073–0.080% of avoided prefix recompute. Measured-component N=1/2/4 amortization is in `AMORTIZATION_RESULTS.tsv`; it does not assert a real service hit distribution.\n\nFinal state: `{final_state}`. NCU was not admitted because no GPU-local snapshot kernel or qualifying GPU-local residual remained. Source/closest-work and R55 source-only audits inherit the accepted V1 files.\n\nOne timing harness repair preallocated chunk inputs before the CUDA start event; the first discovery attempt is retained under `full_r54/raw/production_attempt0_input_constructed_after_start`. Holdout density was pre-registered as D512 before holdout and stayed D512 under the corrected discovery numbers. Exact token-4096 checkpoint payload hashes match across the repair, so restore evidence remains attached to the corrected production checkpoint identity.\n'''
(PUB/'REPORT.md').write_text(report)
(FULL/'REPORT.md').write_text(report)
REPORT.write_text(report)

inventory=f'''# Pre-execution and inherited identity\n\nNode109 RTX4080/SM89; {driver}. Model weights and Transformers source were reused from accepted V1; environment and Hub artifacts were reused from accepted V1R1. `R54_V1R2_BACKEND_RECEIPT.json` binds revisions and accepted receipt hashes. All measured GPU processes used `/data/c16/locks/c16_gpu_campaign.lock`.\n'''
(FULL/'PRE_EXECUTION_INVENTORY.md').write_text(inventory)

# Scientific phase ledger. File mtimes are evidence completion times; phase starts were not separately recorded.
phases=[
 ('PREFIX_AND_PREREG','PASS',ROOT/'R54_V1R2_PREREGISTRATION.json','GREEDY_ARMS'),
 ('GREEDY_BACKEND_GATE','PASS',ROOT/'R54_V1R2_DECISION.json','STATE_SCHEMA'),
 ('STATE_SCHEMA','PASS',ROOT/'R54_STATE_SCHEMA_REFINEMENT.json','RESTORE_CANARY'),
 ('RESTORE_512_AND_M0_P0','PASS',ROOT/'R54_SEMANTIC_GATE_RECEIPT.json','PRODUCTION'),
 ('PRODUCTION_CANARY_FORMAL','PASS',ROOT/'PRODUCTION_ANALYSIS.json','RESTORE'),
 ('RESTORE_CANARY_FORMAL','PASS',ROOT/'RESTORE_ANALYSIS.json','AMORTIZATION'),
 ('AMORTIZATION','COMPLETE',ROOT/'AMORTIZATION_RESULTS.tsv','HOLDOUT'),
 ('HOLDOUT','PASS_STABLE_HOST_DOMINATED_RESIDUAL',ROOT/'HOLDOUT_ANALYSIS.json','NCU_ADMISSION'),
 ('NCU_ADMISSION','NO_GPU_LOCAL_PROFILE_TARGET',FULL/'NCU_ADMISSION.md','FINAL_DECISION'),
]
ledger=[]
for phase,result,path,next_phase in phases:
    ledger.append({'phase':phase,'start_utc':'NOT_RECORDED',
      'evidence_completed_utc':datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat(),
      'result':result,'scientific_eligibility':next_phase,'raw_or_receipt_path':str(path)})
write_tsv(FULL/'PHASE_LEDGER.tsv',ledger)

# Preserve raw evidence and the corrected timing repair history.
for name in ['S0','PREFIX_HOLDOUT_2048','PREFIX_DISCOVERY_4096']:
    shutil.copytree(ROOT/'raw'/name,PUB/'raw/greedy'/name,dirs_exist_ok=True)
shutil.copytree(ROOT/'prefix',PUB/'raw/prefix_token_ids',dirs_exist_ok=True)
for name in ['production_profile','production_profile_attempt0',
             'production_attempt0_input_constructed_after_start']:
    shutil.copytree(ROOT/'raw'/name,FULL/'raw'/name,dirs_exist_ok=True)
for name in ['state_probe.stderr.log','semantic_gate.stdout.log','semantic_gate.stderr.log',
             'production_formal.stdout.log','production_formal.stderr.log',
             'restore_formal.stdout.log','restore_formal.stderr.log',
             'holdout.stdout.log','holdout.stderr.log']:
    if (ROOT/name).exists():copy(ROOT/name,FULL/'raw/logs'/name)
copy(ROOT/'raw/R54_EXACT_STATE_SCHEMA_PROBE_INITIAL.tsv',FULL/'raw/R54_EXACT_STATE_SCHEMA_PROBE_INITIAL.tsv')
source=WT/'util/vm_tlb/awma/r54_greedy_semantic_requal_v1r2'
for p in sorted(source.iterdir()):
    if p.is_file() and p.suffix in ('.py','.sh'):copy(p,PUB/'source'/p.name)

final_receipt={'stage':'AWMA_R54_GREEDY_SEMANTIC_REQUALIFICATION_V1R2',
 'greedy_backend_state':greedy['state'],'r54_final_state':final_state,
 'greedy_prefix_gate_count':3,'full_checkpoint_science_resumed':True,
 'snapshot_semantics_pass':True,'restore_semantics_pass':True,
 'holdout_pass':True,'ncu_profiles':0,'ncu_admission':'NO_GPU_LOCAL_PROFILE_TARGET',
 'node174_used':False,'accel_sim_run':False,
 'gpu_lock_released':True,
 'exact_checkpoint_requalification_join_sha256':sha(ROOT/'CHECKPOINT_AUTHORITY_REQUAL_JOIN.json')}
dump(PUB/'FINAL_RECEIPT.json',final_receipt)
dump(FULL/'FINAL_RECEIPT.json',final_receipt)

# Review packs contain compact TSV/JSON authority; raw profilers and logits stay on node164.
greedy_names=['README.md','V1_V1R1_INHERITANCE.md','R54_V1R2_PREFIX_RECEIPT.json',
 'R54_V1R2_PREREGISTRATION.json','R54_V1R2_BACKEND_RECEIPT.json',
 'R54_V1R2_GREEDY_RESULTS.tsv','R54_V1R2_NUMERICAL_DIAGNOSTICS.tsv',
 'R54_V1R2_DECISION.md','R54_V1R2_DECISION.json','FINAL_DECISION.md','FINAL_RECEIPT.json']
for name in greedy_names:copy(PUB/name,GREEDY_PACK/name)
full_names=['README.md','REPORT.md','PRE_EXECUTION_INVENTORY.md','R54_SOURCE_AND_CLOSEST_WORK_AUDIT_V1_ACCEPTED.md',
 'R55_PLATFORM_AND_CLOSEST_WORK_AUDIT_V1_ACCEPTED.md','MODEL_ADMISSION_RECEIPT_V1_ACCEPTED.json',
 'RUNTIME_FASTPATH_RECEIPT.json','PREFIX_FIXTURE_RECEIPT.json','R54_EXACT_STATE_SCHEMA.tsv',
 'R54_STATE_SCHEMA_REFINEMENT.json','PREREGISTRATION.json','SEMANTIC_QUALIFICATION.tsv',
 'SNAPSHOT_PRODUCTION_TIMING.tsv','SNAPSHOT_COPY_ACCOUNTING.tsv','PRODUCTION_ANALYSIS.json',
 'CHECKPOINT_AUTHORITY_REQUAL_JOIN.json','RESTORE_SEMANTIC_RESULTS.tsv','RESTORE_TIMING.tsv',
 'RESTORE_ANALYSIS.json','AMORTIZATION_RESULTS.tsv','HOLDOUT_PREREGISTRATION.json',
 'HOLDOUT_RESULTS.tsv','HOLDOUT_ANALYSIS.json','NSYS_MEMCPY_STRATA.tsv','NCU_ADMISSION.md',
 'NCU_DIAGNOSTIC.tsv','PHASE_LEDGER.tsv','R54_DECISION.md','FINAL_DECISION.md','FINAL_RECEIPT.json']
for name in full_names:copy(FULL/name,FULL_PACK/name)

# Durable index and checksums, then compact review-pack hashes.
index=[]
for p in sorted(PUB.rglob('*')):
    if p.is_file() and p.name not in ('RAW_DATA_INDEX.tsv','SHA256SUMS'):
        index.append({'relative_path':str(p.relative_to(PUB)),'size_bytes':p.stat().st_size,'sha256':sha(p)})
write_tsv(PUB/'RAW_DATA_INDEX.tsv',index)
with (PUB/'SHA256SUMS').open('w') as f:
    for p in sorted(PUB.rglob('*')):
        if p.is_file() and p.name!='SHA256SUMS':
            f.write(f'{sha(p)}  {p.relative_to(PUB)}\n')
for pack in (GREEDY_PACK,FULL_PACK):
    copy(PUB/'RAW_DATA_INDEX.tsv',pack/'RAW_DATA_INDEX.tsv')
    with (pack/'SHA256SUMS').open('w') as f:
        for p in sorted(pack.iterdir()):
            if p.is_file() and p.name!='SHA256SUMS':f.write(f'{sha(p)}  {p.name}\n')
print(json.dumps({'final_state':final_state,'publication_path':str(PUB),
 'indexed_files':len(index),'raw_index_sha256':sha(PUB/'RAW_DATA_INDEX.tsv'),
 'sha256sums_sha256':sha(PUB/'SHA256SUMS'),
 'final_receipt_sha256':sha(PUB/'FINAL_RECEIPT.json')},indent=2))
