# C16 Recovery V3 — Native Census and Target-Plan Handoff

## Purpose

For every authoritative deployment/scenario, produce the cheap real-native evidence needed to select bounded memory-trace windows before NVBit capture.

The order is:

```text
frozen identity/input
 -> no-profile runtime/baseline
 -> lightweight kernel census
 -> implementation/semantic audit
 -> frozen target plan
 -> NVBit
```

Do not jump directly from model name to a static instruction range.

## Native baseline

For each required deployment/scenario:

- warm up consistently;
- run unprofiled measured repeats under the frozen synchronization boundary;
- retain output/checksum correctness and device/backend evidence;
- record median/min/max/CV where timing is used;
- if CV exceeds the existing engineering threshold, extend only to the allowed repeat cap and retain all runs.

Profiled timings are not substitutes for native timings.

## Lightweight census

Use nsys/NVTX or the already-qualified lightweight mechanism; do not emit full SASS for every kernel.

At minimum record:

```text
run/scenario/phase
kernel launch identity
full kernel name
context/stream/correlation
NVTX or equivalent phase linkage
grid/block
start/end/duration when trustworthy
launch count
```

Keep prefill and decode distinct. Where decode steps are independently visible, preserve step identity.

## Runtime implementation audit

Record direct evidence for:

- attention backend;
- KV representation/layout;
- quant/dequant/repack for raw/AWQ;
- MoE router/expert/dispatch where applicable;
- compile/CUDA-graph state;
- logits policy;
- dtype/device/offload behavior.

If direct evidence is absent, use UNKNOWN rather than guessing from architecture.

## Semantic/shape mapping

Associate operator/layer/shape/dtype/implementation when directly supported by runtime metadata, NVTX, module hooks, or stable implementation evidence.

Name heuristics alone are weak evidence and may not overwrite UNKNOWN.

## Existing target plans

Before generating a new target plan, search current repo and relevant fixed branches/commits for:

```text
NVBIT_TARGET_PLAN.tsv
SAMPLE_PLANS.tsv
CERTAINTY_UNITS.tsv
```

A plan is reusable only if deployment identity, scenario, phase, implementation, and target validation contract match the current run.

## Recovery-v3 deterministic plan fallback

If no valid C-lane plan exists, generate `RECOVERY_V3_TARGET_PLAN` from the frozen census using the following pre-outcome rules. The plan must not inspect TLB/cache outcomes or candidate mechanism speedups.

Prioritize:

1. high native duration mass / heavy-tail launches;
2. special semantics: embedding/indexing, KV management, attention, quant/dequant metadata, MoE router/dispatch, rare implementation paths;
3. shape/implementation diversity;
4. both prefill and decode when both are active;
5. a small random audit reserve when budget allows.

Do not select solely by kernel ordinal.

## Target identity

Every target-plan row must use a stable second-pass identity such as:

```text
full mangled function / kernel identity
semantic key
phase
shape/grid/block when needed for disambiguation
module/library identity
```

Before every formal capture, revalidate this identity against the live launch.

## Phase-specific behavior

Llama proved that shape-dependent dispatch can change kernel implementations between prefill and decode. Therefore:

```text
PREFILL_TARGETS[]
DECODE_TARGETS[]
```

are first-class separate objects.

A prefill target with zero decode records is not a decode target.

## Frozen plan output

For every plan version publish:

- plan ID/version;
- code SHA;
- source census commit/SHA;
- rows with selection reason;
- estimated capture bytes/time;
- plan SHA256;
- freeze timestamp/receipt.

After the first formal NVBit capture, do not mutate the same plan version.

## Acceptance

R3 and R4 acceptance gates in `C16_FULL_AUTHORITY_RECOVERY_V3_STAGE_ACCEPTANCE.md` must pass before R5 begins.
