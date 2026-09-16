# CODEX ACTIVATION — node109 SIM_COMPAT_CAPTURE_V1 NOW

## Execution context

You are starting a **new Codex window on node109 / RTX4080**. Assume **no prior chat context**.

This is the active AWMA Simulation Analysis producer stage. The upstream 174-new consumer is already prepared and stopped cleanly at a consumer-ready checkpoint. Your task is to produce the first formal simulator-native current-model trace bundle on node109, validate it, and transfer it through the accepted data pipeline.

Do not redesign the overall project. Do not mix Native Characterization and Simulation Analysis evidence.

## Repository / branch bootstrap

Fetch/pull the coordination branch:

```text
hrl/awma-sim-compat-producer-109-v1-coordination
```

Create a **fresh worktree and execution branch**. Suggested branch:

```text
hrl/awma-sim-compat-capture-109-v1
```

Do not perform this Goal in an unrelated active Native/Qwen worktree.

## Required read order

Read these files completely before formal GPU work:

```text
docs/vm_tlb/chatgpt_handoff/awma/sim_compat_capture_v1/CODEX_GOAL_109_SIM_COMPAT_CAPTURE_V1.md
docs/vm_tlb/chatgpt_handoff/awma/sim_compat_capture_v1/PRODUCER_CAPTURE_CONTRACT.md
docs/vm_tlb/chatgpt_handoff/awma/sim_compat_capture_v1/ACCEPTANCE_REQUIREMENTS.md
docs/vm_tlb/chatgpt_handoff/awma/sim_compat_capture_v1/BASELINE_REVIEW_AND_COMPATIBILITY_NOTES.md
```

Also consume the accepted consumer-preparation authority:

```text
commit:
25aa29862239a408099639ae9d5f1a0ea4fee1e1

review pack:
docs/vm_tlb/review_packs/AWMA_SIM_CONSUMER_PREP_174NEW_V1/

report:
docs/vm_tlb/codex_handoff/awma/SIM_CONSUMER_PREP_174NEW_REPORT.md
```

## Accepted upstream state

Treat the following as already accepted, not as tasks to redo:

```text
174NEW_SIM_CONSUMER_READY_FOR_INPUT_V1

NEW_SIM_BASELINE_V1_QUALIFIED
scope = HASH_BOUND_FIXED_WINDOW_10000

SIM_BASELINE_ID =
SIM_BASELINE_6305c065f2c4913448b0cb61a85d5003030c5917cd37d6a346fd3f42939d5964
```

Consumer-side parser admission, negative tests, catalog schema and 10k replay wrapper are already prepared. Do not rerun historical C12 merely to reconfirm this state.

## Exact first formal current-model identity

Resolve this identity from accepted authority files and verify it independently before formal capture:

```text
model_id = Qwen/Qwen2.5-0.5B-Instruct
model_revision = 7ae557604adf67be50417f59c2c2f167def9a775
scenario_id = S2_TEXT
input_class = TEXT
phase = PREFILL
batch = 1
prefill_tokens = 2048
decode_tokens = 32
backend = sdpa
dtype = float16
python = 3.10.12
torch = 2.5.1+cu124
transformers = 4.46.3

target_id = Q05_PREFILL_ATTN_FLASH
target_function_occurrence = 0
```

Frozen target function:

```text
_ZN13pytorch_flash16flash_fwd_kernelINS_23Flash_fwd_kernel_traitsILi64ELi128ELi128ELi4ELb0ELb0EN7cutlass6half_tENS_19Flash_kernel_traitsILi64ELi128ELi128ELi4ES3_EEEELb0ELb1ELb0ELb0ELb1ELb1ELb0EEEvNS_16Flash_fwd_paramsE
```

Relevant accepted identity hashes are frozen in the Goal and in:

```text
docs/vm_tlb/review_packs/AWMA_SIM_CONSUMER_PREP_174NEW_V1/EXPECTED_FIRST_CURRENT_MODEL_INPUT.json
```

Do not retokenize, substitute the model, change backend/dtype/context, or silently select a different attention kernel.

## Scientific separation rule

Existing `C16WARP1` / MREF-sharded traces are Native evidence. They are **not** simulator input.

Forbidden:

```text
C16WARP1 -> traceg conversion
post-hoc shard concatenation to invent global order
inference of missing opcode/width/access/sync/control semantics
relabeling Native trace as simulator-native input
```

Generate a **new simulator-native trace from a new execution** of the exact accepted workload/target.

## Goal-mode execution policy

Run in solve-and-continue Goal mode.

For recoverable engineering problems:

```text
diagnose root cause
-> make the narrowest semantics-preserving repair
-> regression-test
-> record hashes/evidence
-> continue
```

Do not stop merely because of:

```text
first tracer build failure
CUDA/NVBit include/library path issue
SM89 compatibility error
stale helper path
parser invocation issue
manifest/packaging bug
transfer wrapper problem
user-space dependency issue
```

Escalate only if a proposed fix changes workload identity, trace semantics, simulator semantics, scientific target/scope/status, or requires destructive operations.

## GPU safety gate

The user reports node109 is free, but verify independently before formal GPU use.

Formal GPU stages must acquire:

```text
/data/c16/locks/c16_gpu_campaign.lock
```

Rules:

```text
never delete a valid live lock
never steal the lock
never kill another owner
never bypass the lock
```

Complete CPU-only archaeology/build/manifests/validators/size guards before expensive formal GPU capture when practical.

## Required execution sequence

Execute the full Goal, including at least:

```text
A. tracer archaeology + build
B. SM89 micro-canary
C. exact target identity/selector verification
D. target canary + volume/disk qualification
E. formal simulator-native capture
F. producer-side parser/semantics/completeness/hash qualification
G. accepted 109 -> 174/node164 transfer
H. review pack + report + commit/push
```

Prefer existing Accel-Sim/NVBit simulator-native tracer grammar:

```text
kernelslist.g
*.traceg.xz
```

Do not invent a new intermediate representation unless the native tracer is genuinely unsuitable and a formally lossless converter is demonstrated.

## Formal producer PASS requirements

Do not mark PASS until the formal target closes all applicable gates:

```text
exact workload/input/target identity
simulator-native ordered trace
actual traceg parser/grammar smoke
required instruction + sync/control semantics
all kernelslist members present
terminal COMPLETE or exact native equivalent
drop = 0
overflow = 0
stable repeated hashes/reads
sidecar closure
source/build/binary/environment closure
READY/hash-closed publication through accepted pipeline
```

The bundle must provide all producer fields expected by the consumer, including bundle/hash roots, kernelslist SHA, terminal receipt, tracer/source/build/binary identities, grammar/version/context and address/page-policy metadata.

## Required output

Review pack:

```text
docs/vm_tlb/review_packs/AWMA_SIM_COMPAT_CAPTURE_109_V1/
```

Codex report:

```text
docs/vm_tlb/codex_handoff/awma/SIM_COMPAT_CAPTURE_109_REPORT.md
```

Large raw traces remain outside Git. Git contains code, manifests, hashes, summaries, receipts and review material.

## Final stop

Preferred and expected stop:

```text
SIM_COMPAT_CAPTURE_V1_PRODUCER_PASS
```

At PASS, the report must give the exact READY path/run ID and all hash roots needed by 174-new.

After producer PASS, **STOP node109 work**. Do not start current-model simulation replay or mechanism experiments on node109. The next stage returns to 174-new for independent rehash/admission, formal `SIM_INPUT_ID`, 10k bounded replay, repeat/determinism, `SIM_RUN_ID` and Simulation Evidence catalog closure.

A non-PASS stop is acceptable only after bounded recovery proves an exact scientific/semantic or external blocker. Do not return a generic `BLOCKED` while a safe engineering recovery path remains.
