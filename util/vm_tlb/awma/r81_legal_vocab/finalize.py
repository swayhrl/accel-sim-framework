#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,importlib.metadata,json,shutil,subprocess,sys
from pathlib import Path

ROOT=Path('/data/c16/awma/r81_legal_vocab_20260927')
PUB=Path('/data/c16/awma/r81_legal_vocab_publication_20260927')
WT=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r81-legal-vocab-v1')
SOURCE=WT/'util/vm_tlb/awma/r81_legal_vocab'
PACK=WT/'docs/vm_tlb/review_packs/AWMA_R81_LEGAL_VOCAB_EXPLORATION_V1'
REPORT=WT/'docs/vm_tlb/reports/AWMA_R81_LEGAL_VOCAB_EXPLORATION_109_V1_REPORT.md'
for p in [PUB,PACK,REPORT.parent]:p.mkdir(parents=True,exist_ok=True)

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def copy(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,dst)

def dump(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')

def write_tsv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(rows)

decision=json.loads((ROOT/'DECISION_RECEIPT.json').read_text())
assert decision['final_state']=='R81_SOFTWARE_OPPORTUNITY_NO_ARCH_CLAIM'
assert decision['all_12_requests_schema_valid'] and decision['all_arms_exact_generated_ids_and_stop']
assert not decision['A3_complete_generation_reliable_improvement']
runtime=json.loads((ROOT/'INPUT_RUNTIME_BINDINGS.json').read_text())
assert runtime['dtype']=='torch.bfloat16'
assert runtime['model_config_vocab_size']==151936
assert runtime['xgrammar_version']=='0.2.8'
lock_check=subprocess.run(['flock','-n','/data/c16/locks/c16_gpu_campaign.lock','-c','true'],capture_output=True)
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=name,compute_cap,driver_version',
                             '--format=csv,noheader'],text=True).strip()
pip_freeze=subprocess.check_output([str(ROOT/'env/bin/python'),'-m','pip','freeze'],text=True)
(PUB/'environment_lock.txt').write_text(pip_freeze)
env_receipt={'stage':'AWMA_R81_LEGAL_VOCAB_EXPLORATION_V1',
 'node':'109','gpu':gpu,'environment_path':str(ROOT/'env'),
 'framework_execution_base_sha':'785a6c0651a1a4fbc6ed11c829be29d514a13f74',
 'simulator_core_sha':'NOT_USED_NATIVE_GPU_ONLY',
 'python':sys.version.replace('\n',' '),
 'torch':runtime['torch'],'torch_cuda':runtime['torch_cuda'],
 'transformers':runtime['transformers'],'triton':runtime['triton'],
 'xgrammar':runtime['xgrammar_version'],
 'xgrammar_wheel_sha256':runtime['xgrammar_wheel_sha256'],
 'apache_tvm_ffi':importlib.metadata.version('apache-tvm-ffi'),
 'pydantic':importlib.metadata.version('pydantic'),
 'isolated_paths':{'worktree':str(WT),'env':str(ROOT/'env'),
   'raw':str(ROOT/'raw'),'hf_cache':str(ROOT/'cache/hf'),
   'triton_cache':str(ROOT/'cache/triton'),
   'cuda_cache':str(ROOT/'cache/cuda'),
   'tmpdir':str(ROOT/'tmp')},
 'accepted_model_read_only':True,'system_cuda_driver_changed':False,
 'pip_freeze_sha256':sha(PUB/'environment_lock.txt')}
dump(PUB/'ENVIRONMENT_RECEIPT.json',env_receipt)

for name in ['PREREGISTRATION.json','INPUT_RUNTIME_BINDINGS.json','HEAD_WEIGHT_IDENTITY.json',
             'HOLDOUT_PREREGISTRATION.json','MASK_WORK_SUMMARY.tsv','MASK_WORK_AGGREGATE.json',
             'SEMANTIC_RESULTS.tsv','TIMING_RESULTS.tsv','TIMING_SUMMARY.tsv',
             'GRAMMAR_COMPILE_COST.tsv','GRAMMAR_VALIDITY.tsv','LEGAL_LOGIT_VALIDATION.json',
             'CONTROL_STRATIFICATION_RUNS.tsv','CONTROL_STRATIFICATION_SUMMARY.tsv',
             'DISCOVERY_ANALYSIS.json','NSYS_CANARY_SUMMARY.tsv','NSYS_TOP_KERNEL_STRATA.tsv',
             'DECISION_RECEIPT.json']:
    copy(ROOT/name,PUB/name)
copy(SOURCE/'SOURCE_CAPABILITY_MAP.md',PUB/'SOURCE_CAPABILITY_MAP.md')
copy(SOURCE/'SOURCE_AND_TESTS.md',PUB/'SOURCE_AND_TESTS.md')

source_rows=[]
for p in sorted(SOURCE.iterdir()):
    if p.is_file() and p.suffix in ('.py','.sh','.json','.md'):
        copy(p,PUB/'source'/p.name)
        source_rows.append({'source_file':p.name,'sha256':sha(p),'size_bytes':p.stat().st_size})
write_tsv(PUB/'SOURCE_HASHES.tsv',source_rows)
copy(ROOT/'wheels/xgrammar-0.2.8-cp310-cp310-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl',
     PUB/'raw/wheels/xgrammar-0.2.8-cp310-cp310-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl')
shutil.copytree(ROOT/'raw',PUB/'raw/measurements',dirs_exist_ok=True)
if (ROOT/'cache/triton').exists():
    shutil.copytree(ROOT/'cache/triton',PUB/'raw/jit_cache/triton',dirs_exist_ok=True)
if (ROOT/'logs').exists():
    shutil.copytree(ROOT/'logs',PUB/'raw/logs',dirs_exist_ok=True)

effects=decision['effects']
def pct(value):return 100*value
summary_lines=[]
for cohort,label in [('C0_SHARED_DISCOVERY','C0 shared'),('C1_HETEROGENEOUS_DISCOVERY','C1 heterogeneous'),
                     ('H0_HETEROGENEOUS_HOLDOUT','H0 holdout')]:
    e=effects[cohort]
    summary_lines.append(f'| {label} | {e["total_steps"]} | {e["broad_union_steps"]} | {e["a0_ms"]:.1f} | {e["a3_ms"]:.1f} | {pct(e["a3_fraction_vs_a0"]):+.2f}% |')
table='\n'.join(summary_lines)
decision_text=f'''# R81 decision\n\nState: `{decision['final_state']}`.\n\nThe strongest qualified known-capability baseline was A0, a BF16 vendor dense head with XGrammar masking and singleton support shortcut. A1 used a FlashSampling-style greedy fused tile adaptation; A2 used Kestrel-style indexed union gather; A3 was a fixed direct-index ragged prototype. All four arms selected exactly the same tokens and stop positions for every C0, C1 and H0 request; 12/12 authored outputs satisfied their JSON schemas.\n\n| Cohort | Steps retained | Union > half vocabulary | A0 full generation median (ms) | A3 median (ms) | A3 vs A0 |\n| --- | ---: | ---: | ---: | ---: | ---: |\n{table}\n\nThe median legal union was 147,068 of 151,936 rows (96.8%) in all three cohorts. On the pre-registered sparse stratum (union <1% vocabulary), A3's summed head-region time was 53.4%, 45.3% and 44.8% below A0 for C0, C1 and H0. On broad states (union >50%), A3 was 27.5%, 7.1% and 6.7% slower. All timesteps were retained. The local sparse response is real within the authored fixture; it did not yield a reliable complete-generation improvement. A2 indexed union regressed substantially because union often approached the full head and its gather/metadata remained on the path.\n\nThis identifies a bounded software opportunity to choose among already known dense and direct-index organizations from the current legal set. It does not establish an architectural need or deployment-wide gain. The authored B4 fixture is not a production distribution; task-answer accuracy and logprob-serving semantics were not evaluated. A1 is a greedy adaptation, not a reproduction or upper bound for the published FlashSampling kernel.\n\nC0's first formal complete-generation bundle had unexplained A0/A1 latency outliers and is retained in raw as `C0_ATTEMPT0_HIGH_VARIANCE`; one exact same-configuration paired repeat is the primary C0 timing. C1 and H0 were not rerun. Neither Kestrel's indexed head nor FlashSampling's fused-selection ability is claimed as new. No NCU profile was admitted because there was no remaining registered mechanism question that would change this software-first conclusion.\n'''
(PUB/'DECISION.md').write_text(decision_text)
readme='''# AWMA R81 legal vocabulary exploration V1\n\nRecommended entry for this review pack. Final state: `R81_SOFTWARE_OPPORTUNITY_NO_ARCH_CLAIM`. The bounded authored B4 Qwen2.5-0.5B BF16 experiment ran on node109 RTX4080/SM89. `DECISION.md` gives the scientific conclusion; `REPORT.md` gives the numbers and limits.\n\n## Source anchors and commit history\n\n- Coordination handoff and execution branch base: `785a6c0651a1a4fbc6ed11c829be29d514a13f74`; branch `hrl/awma-r81-legal-vocab-exploration-v1`. The R81 execution commit is the branch HEAD following this base; `git log` on that branch is the exact final history.\n- Round08 literature authority: `214b30039cc579c28457cb17bfbd7e9d88d00fcd`.\n- Read-only model `Qwen/Qwen2.5-0.5B-Instruct@7ae557604adf67be50417f59c2c2f167def9a775`; safetensors SHA256 `fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe`.\n- XGrammar `0.2.8` wheel SHA and all environment/tokenizer/schema bindings are in `INPUT_RUNTIME_BINDINGS.json` and `ENVIRONMENT_RECEIPT.json`. The prior indexed-head and fused-selection capabilities are mapped in `SOURCE_CAPABILITY_MAP.md`.\n\n## Changed files and validation\n\n- New implementation/tests/fixture: `util/vm_tlb/awma/r81_legal_vocab/`. New compact evidence: this review pack. New report: `docs/vm_tlb/reports/AWMA_R81_LEGAL_VOCAB_EXPLORATION_109_V1_REPORT.md`. No simulator or accepted baseline source was changed.\n- `VERIFIED_RUN`: two CPU mapping tests passed; all 480 active request-step dense legal logits were finite; C0/C1/H0 retained all 207 grammar timesteps; A0/A1/A2/A3 selected the same IDs and stop positions; 12/12 JSON outputs satisfied their schemas; one NSYS canary per qualified arm was accepted.\n- Formal: 2 warmups and 7 paired/interleaved repetitions per arm/cohort for head region and complete generation. C0's first high-variance full-generation bundle is retained as an attempt, and one exact-configuration repeat is primary.\n- `PAPER_SPEC` / `VERIFIED_CODE` boundaries and original versus ported software capability are in `SOURCE_CAPABILITY_MAP.md` and `SOURCE_AND_TESTS.md`.\n\n## Open issues and raw authority\n\nThe fixture is authored, not a production distribution. A1 is a bounded greedy adaptation of FlashSampling, and arbitrary dynamic-grammar support in FlashRec source remains unverified. Sparse-state A3 savings did not yield a stable complete-generation gain; software support-aware dispatch remains untested. No NCU or architecture admission followed.\n\nThe node164 authority is `/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/round08_20260927/R81/`. `RAW_DATA_INDEX.tsv` and `SHA256SUMS` bind all large hidden/mask tensors, compiled grammars, JIT artifacts, NSYS/SQLite and logs; model weights are inherited by hash and not duplicated.\n'''
(PUB/'README.md').write_text(readme)
report=f'''# AWMA R81 legal vocabulary exploration on node109\n\n**Result:** `{decision['final_state']}`. The fixed 12-request authored fixture produced 207 grammar timesteps. C0/C1/H0 each had a median legal union of 147,068 / 151,936 rows (96.8% of the model head); broad free-text states occupied 63/78, 63/72 and 47/57 timesteps. Exact legal masks, current hidden states, prompt token IDs, matcher histories, model/head weights and selected IDs are bound in the raw authority. All arms were semantically exact on all 12 requests, all JSON outputs were valid and none truncated at 128.\n\n{table}\n\nThe direct-index A3 prototype reduced head-region time 45–53% on the pre-registered sparse stratum, including independent H0 content. Broad states cost 6.7–27.5% more than A0. Therefore there was no stable complete-generation improvement. A2 indexed-union was slower because the union was usually near full vocabulary; NSYS's separate C1 canary recorded substantially more host-to-device index/mask traffic for A2. These profiler sums are not the formal latency metric. CPU grammar compile cost is separately reported.\n\nThe exact C0 paired repeat resolved a high-variance first run without changing inputs or code; both runs remain indexed. Kestrel already performs indexed weight selection, FlashSampling establishes tiled fused selection, XGrammar supplies the legal masks, and FlashRec documents restricted SID-range projection. `SOURCE_CAPABILITY_MAP.md` records their specific scope and the limits of R81's ports. The only concrete next direction is a separate software support-aware dispatch study; this Goal stops before any architecture claim.\n'''
(PUB/'REPORT.md').write_text(report)
REPORT.write_text(report)
write_tsv(PUB/'NOT_RUN_PHASES.tsv',[
 {'phase':'NCU','status':'NOT_RUN','reason':'no focused registered GPU mechanism question after exact full-generation and NSYS controls'},
 {'phase':'NVBIT_FULL_TRACE','status':'NOT_RUN','reason':'prohibited by R81 Goal'},
 {'phase':'ACCEL_SIM_OR_174_SIMULATION','status':'NOT_RUN','reason':'prohibited by R81 Goal'},
 {'phase':'R82','status':'NOT_RUN','reason':'independent window not in R81 scope'},
])
final_receipt={'stage':'AWMA_R81_LEGAL_VOCAB_EXPLORATION_V1',
 'final_state':decision['final_state'],
 'execution_branch':'hrl/awma-r81-legal-vocab-exploration-v1',
 'coordination_head':'785a6c0651a1a4fbc6ed11c829be29d514a13f74',
 'literature_commit':'214b30039cc579c28457cb17bfbd7e9d88d00fcd',
 'request_count':12,'discovery_configurations':8,'holdout_invocation_count':1,
 'all_arms_exact':True,'all_json_schema_valid':True,
 'model_redownloaded':False,'r81_gpu_subprocesses_exited':True,
 'gpu_lock_nonblocking_available_at_publication':lock_check.returncode==0,
 'ncu_profiles':0,'full_nvbit_traces':0,'accel_sim_runs':0,
 'node174_gpu_work':False,'r82_workspace_touched':False}
dump(PUB/'FINAL_RECEIPT.json',final_receipt)

compact=['README.md','DECISION.md','REPORT.md','SOURCE_CAPABILITY_MAP.md','SOURCE_AND_TESTS.md',
 'PREREGISTRATION.json','HOLDOUT_PREREGISTRATION.json','INPUT_RUNTIME_BINDINGS.json',
 'ENVIRONMENT_RECEIPT.json','HEAD_WEIGHT_IDENTITY.json','MASK_WORK_SUMMARY.tsv',
 'MASK_WORK_AGGREGATE.json','SEMANTIC_RESULTS.tsv','GRAMMAR_VALIDITY.tsv',
 'LEGAL_LOGIT_VALIDATION.json','TIMING_RESULTS.tsv','TIMING_SUMMARY.tsv',
 'CONTROL_STRATIFICATION_SUMMARY.tsv','GRAMMAR_COMPILE_COST.tsv',
 'DISCOVERY_ANALYSIS.json','NSYS_CANARY_SUMMARY.tsv','SOURCE_HASHES.tsv',
 'NOT_RUN_PHASES.tsv','FINAL_RECEIPT.json']
for name in compact:copy(PUB/name,PACK/name)

index=[]
for p in sorted(PUB.rglob('*')):
    if p.is_file() and p.name not in ('RAW_DATA_INDEX.tsv','SHA256SUMS'):
        index.append({'relative_path':str(p.relative_to(PUB)),
                      'size_bytes':p.stat().st_size,'sha256':sha(p)})
write_tsv(PUB/'RAW_DATA_INDEX.tsv',index)
with (PUB/'SHA256SUMS').open('w') as f:
    for p in sorted(PUB.rglob('*')):
        if p.is_file() and p.name!='SHA256SUMS':f.write(f'{sha(p)}  {p.relative_to(PUB)}\n')
copy(PUB/'RAW_DATA_INDEX.tsv',PACK/'RAW_DATA_INDEX.tsv')
with (PACK/'SHA256SUMS').open('w') as f:
    for p in sorted(PACK.iterdir()):
        if p.is_file() and p.name!='SHA256SUMS':f.write(f'{sha(p)}  {p.name}\n')
print(json.dumps({'final_state':decision['final_state'],'indexed_files':len(index),
 'publication_path':str(PUB),'raw_index_sha256':sha(PUB/'RAW_DATA_INDEX.tsv'),
 'sha256sums_sha256':sha(PUB/'SHA256SUMS'),
 'final_receipt_sha256':sha(PUB/'FINAL_RECEIPT.json')},indent=2))
