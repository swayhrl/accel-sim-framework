# CODEX GOAL — node109 SIM_COMPAT_CAPTURE_V1 Producer Qualification

## Activation rule

Run this Goal on **node109 / RTX4080** only after the GPU is genuinely available for this work.

Do **not** interrupt or preempt another active node109 task. Do not bypass, delete, or steal:

```text
/data/c16/locks/c16_gpu_campaign.lock
```

If node109 is still occupied when this handoff is read, do not start the formal GPU stages. It is acceptable to defer the entire Goal until node109 is free.

Use a fresh worktree/branch.

Suggested branch:

```text
hrl/awma-sim-compat-capture-109-v1
```

## Goal

Build/requalify a simulator-native capture path on RTX4080/SM89 and close the first formal current-model `SIM_COMPAT_CAPTURE_V1` producer bundle for the exact accepted Qwen2.5-0.5B S2_TEXT Prefill Attention target.

Preferred final state:

```text
SIM_COMPAT_CAPTURE_V1_PRODUCER_PASS
```

This Goal ends at a READY/hash-closed producer bundle transferred through the accepted pipeline. It does not run Accel-Sim mechanism experiments and it does not create the formal consumer `SIM_INPUT_ID` itself.

## Accepted upstream authority

The consumer side is already prepared and stopped at:

```text
174NEW_SIM_CONSUMER_READY_FOR_INPUT_V1
```

Accepted consumer-preparation commit:

```text
25aa29862239a408099639ae9d5f1a0ea4fee1e1
```

Frozen consumer baseline:

```text
SIM_BASELINE_6305c065f2c4913448b0cb61a85d5003030c5917cd37d6a346fd3f42939d5964
NEW_SIM_BASELINE_V1_QUALIFIED
scope = HASH_BOUND_FIXED_WINDOW_10000
```

The consumer validator already has real traceg parser/grammar admission, fail-closed negative tests, immutable catalog schemas and a prepared 10k-cycle replay wrapper. Do not redesign the consumer contract from scratch on node109.

## Exact first target authority

The first producer bundle must match the consumer's frozen expected input:

```text
model_id: Qwen/Qwen2.5-0.5B-Instruct
model_revision: 7ae557604adf67be50417f59c2c2f167def9a775
scenario_id: S2_TEXT
input_class: TEXT
phase: PREFILL
batch: 1
prefill_tokens: 2048
decode_tokens: 32
backend: sdpa
dtype: float16
python: 3.10.12
torch: 2.5.1+cu124
transformers: 4.46.3

target_id: Q05_PREFILL_ATTN_FLASH
target_function_occurrence: 0
```

Target function authority:

```text
_ZN13pytorch_flash16flash_fwd_kernelINS_23Flash_fwd_kernel_traitsILi64ELi128ELi128ELi4ELb0ELb0EN7cutlass6half_tENS_19Flash_kernel_traitsILi64ELi128ELi128ELi4ES3_EEEELb0ELb1ELb0ELb0ELb1ELb1ELb0EEEvNS_16Flash_fwd_paramsE
```

Identity hashes already frozen by the consumer:

```text
input receipt SHA256:
3076a96415e22aa05bac1fe649a5ebc795e338c558d216ff71a989d9c3b61b1a

token semantic SHA256:
0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9

V2 authority SHA256:
fa6bf70b799e661878e9a4ba22bba69166e09f83fbdd054d3063a5bb1a8742e0

native catalog entry SHA256:
252e9e3d4a5d05b18addf8aad069cd93890012ee9f5a084cc18917a3f7dc43ad

native run manifest SHA256:
40d80a3b7fb46d398e4b3ff34878d813ea66a1830ffa9e1c95b5c805b516cbf3

native static map SHA256:
3e8ed36aa257ceb0c0eafe6e78ca6877ab1e4ba08e359269e1e03e3f30a1d47b

libtorch_cuda SHA256:
761b14acafb8b02011e32d11bd437b63cca3fe882b9c4a02c89fd01d738ccb6a
```

Use these only to bind workload/target identity. Existing Native trace bytes are not simulator input.

No retokenization, model substitute, backend fallback, dtype change, context shortening, target-function substitution, or occurrence change is allowed for FORMAL evidence.

## Scientific boundary

Current `C16WARP1` / MREF-sharded captures are Native evidence and remain `NOT_PROVEN_LOSSLESS` as simulator inputs.

Never:

- concatenate C16WARP1 shards into traceg;
- synthesize missing global ordering;
- infer missing opcode/width/access/sync/control semantics;
- relabel a Native capture as simulator-native trace;
- silently truncate a formal target while keeping the same target identity.

The producer must generate a new simulator-native trace from a fresh execution of the exact accepted workload/target.

## Required simulator-input semantics

The formal bundle must preserve/provide at least:

```text
kernel launch order
stream/context identity
grid/block geometry
static instruction identity / PC
opcode
READ / WRITE / ATOMIC access kind
memory space
byte width
warp ID
CTA ID
active mask
per-lane addresses
instruction/event ordering
sync/control semantics
terminal completeness
```

Address/context sidecars must include, when required by the admitted scope:

```text
ASID / epoch
VA width
page policy
address/object context
```

The producer must also provide the fields currently pending in the consumer contract:

```text
producer_bundle_hash_root
trace_member_hash_root
kernelslist_sha256
producer_terminal_receipt_sha256
producer_source_sha256
producer_binary_sha256
tracer_version
tracer_build_sha256
trace_grammar_version
address_context_sha256
stream_context
grid
block
asid_epoch
va_width
page_policy
```

## Phase A — CPU-only tracer archaeology and build

Before taking the GPU lock:

1. inspect existing Accel-Sim/NVBit tracer code and historical trace-capture entrypoints;
2. identify the shortest semantics-preserving path to native `kernelslist.g + *.traceg.xz` on SM89;
3. compare tracer NVBit/CUDA/API assumptions with node109's actual working environment;
4. prefer the existing simulator-native tracer over inventing a new format;
5. build only in user-owned/isolated paths;
6. root-cause SM89/CUDA/NVBit compatibility problems rather than immediately declaring BLOCKED;
7. make only narrow compatibility patches whose trace semantics remain unchanged;
8. freeze source, build and binary hashes;
9. prepare exact workload/target manifest from the frozen authority above;
10. prepare output-size/disk guards and local parser/list/hash validation before GPU use.

A new intermediate format is allowed only if the native tracer is genuinely unsuitable and a formally specified, tested lossless converter to the consumer grammar is provided. Do not create one merely for convenience.

## Phase B — GPU admission and micro-canary

Acquire the formal GPU lock. Never kill or restart another owner to obtain it.

Run the smallest useful CUDA canary and prove:

1. tracer injection/load works on RTX4080 CC8.9;
2. kernelslist and trace payload are produced;
3. actual traceg grammar parses, not merely xz readability;
4. required instruction semantics are present, including sync/control;
5. terminal/completeness evidence exists;
6. drop_count = 0;
7. overflow_count = 0;
8. repeated local reads/hashes are stable.

If the tracer's native terminal mechanism differs from the AWMA manifest vocabulary, create a semantics-preserving adapter/receipt. Do not invent COMPLETE evidence.

## Phase C — Exact Qwen target binding check

Before the target canary and again before formal capture, independently verify all frozen identity fields and hashes.

The launch selector must resolve:

```text
Q05_PREFILL_ATTN_FLASH
function occurrence = 0
```

to the exact frozen mangled function.

If the implementation dispatches differently from the accepted Native authority, classify the attempt as identity mismatch/diagnostic. Do not silently accept another attention kernel.

## Phase D — Target canary and volume qualification

Run the exact workload with a bounded diagnostic capture sufficient to prove:

- selector matches the intended launch;
- capture starts/stops on the intended scientific target;
- ordering and required semantics are intact;
- estimated formal output size is safe;
- filesystem capacity is sufficient;
- terminal/drop/overflow logic works for this target.

If the selected target is too large, explicitly define a narrower scientific ROI with a new target identity and stop for scientific review before calling it FORMAL. Do not truncate while preserving `Q05_PREFILL_ATTN_FLASH` identity.

## Phase E — Formal capture

Capture the exact accepted target with simulator-native ordering.

Required artifacts include:

```text
kernelslist.g
*.traceg.xz
producer manifest
address/context sidecar(s)
terminal/completeness receipt
source/build/binary/environment receipt
trace member manifest
SHA256 manifest
READY marker/receipt
```

Do not MREF-shard or post-hoc concatenate records if doing so loses global instruction/warp order.

## Phase F — Producer-side qualification

Before publication, perform all applicable checks:

- exact identity re-check;
- kernelslist syntax/list closure;
- all referenced trace members exist;
- full decompression/read pass;
- actual traceg parser/grammar smoke;
- semantics coverage check;
- terminal_status = COMPLETE;
- drop_count = 0;
- overflow_count = 0;
- repeated read/hash stability;
- source/build/binary/environment hash closure;
- sidecar/hash closure;
- no producer error hidden by wrapper exit status.

Create READY only after all formal gates pass.

## Phase G — Publish through accepted pipeline

Use the established 109 -> 174/node164 data pipeline. Do not bypass it with ad-hoc scp into an accepted consumer raw directory.

The producer handoff must state:

```text
producer capture/run ID
READY path
WORKLOAD_ID / target relation
kernelslist SHA256
trace-member hash root
sidecar hash root
bundle hash root
terminal receipt SHA256
source/build/binary identities
expected consumer target = 174NEW_SIM_CONSUMER_READY_FOR_INPUT_V1
```

The 174-new consumer will independently rehash, parse/admit and issue the formal `SIM_INPUT_ID` later.

## Optional second target

Do not broaden this Goal merely to increase coverage. Only after the first Prefill Attention bundle is fully closed may a second already-authoritative target be considered if cost is clearly bounded. The default is to stop after the first formal target.

## Solve-and-continue policy

Recoverable engineering problems must be solved inline:

```text
tracer compile/link portability
CUDA/NVBit include or library path
SM89 compatibility
stale helper paths
selector tooling bugs
packaging/manifest issues
parser invocation issues
transfer wrapper issues
```

Diagnose -> repair safely -> regression-test -> document -> continue.

Do not STOP merely because the first build or injection attempt fails.

Escalate only if the fix would change workload identity, trace semantics, simulator semantics, scientific scope, or require destructive operations.

## Required review pack

```text
docs/vm_tlb/review_packs/AWMA_SIM_COMPAT_CAPTURE_109_V1/
```

Minimum files:

```text
README.md
EXECUTION_CONTEXT.md
SOURCE_AUTHORITIES.md
TRACER_SOURCE_AND_BUILD_RECEIPT.md
SM89_COMPATIBILITY_CHANGES.md
MICRO_CANARY_RESULT.md
FORMAL_TARGET_BINDING.json
TARGET_VOLUME_QUALIFICATION.md
SIM_COMPAT_CAPTURE_MANIFEST.json
TRACE_MEMBER_MANIFEST.tsv
ADDRESS_CONTEXT_RECEIPT.md
TERMINAL_AND_COMPLETENESS.md
TRANSFER_RECEIPT.md
TEST_AND_REGRESSION_SUMMARY.md
CLAIM_BOUNDARY.md
OPEN_ISSUES.md
SHA256SUMS
```

Codex report:

```text
docs/vm_tlb/codex_handoff/awma/SIM_COMPAT_CAPTURE_109_REPORT.md
```

## STOP conditions

Preferred:

```text
SIM_COMPAT_CAPTURE_V1_PRODUCER_PASS
```

A non-PASS stop is acceptable only after bounded recovery genuinely proves one of:

- required simulator semantics cannot be preserved with the available tracer/toolchain on SM89;
- exact frozen workload/target authority cannot be reproduced;
- an external resource required for a semantics-preserving capture is unavailable.

State the exact blocker and evidence.

Do not start simulator mechanism experiments. Do not modify Native evidence or its scientific status.
