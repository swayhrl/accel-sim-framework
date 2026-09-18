# AWMA Current State

Date: 2026-09-18

## Coordination stage

`AWMA_Q05_CONTEXTUAL_WARM_PREFIX_REPLAY_V1`

Mainline priority remains frozen: node174-new now owns the active scientific mainline. Node109 RTX4080 is currently released by mainline and may run only explicitly authorized, preemptible side work that cannot delay the contextual replay.

Execution-efficiency policy remains frozen: correctness-neutral micro-fixes with an obvious safe resolution are folded into the next substantive handoff instead of creating standalone Codex rounds.

## 109 contiguous-context result — ACCEPTED

Execution:

```text
hrl/awma-q05-prefix-ldc-recovery-109-v1
c6733012c13099c6a86f506fd8c61e351791159e
```

Status:

`AWMA_Q05_PREFIX_LDC_U8_SEMANTIC_RECOVERY_V1_COMPLETE_WITH_SCOPE`

### LDC semantic recovery

The strict validator now accepts only exact base opcode `LDC` in the frozen width-zero/no-dynamic-address representation.

Boundaries:

- no raw/traceg rewrite;
- no producer change;
- no trace-parser change;
- no trace-driven change;
- no simulator-config change;
- no fabricated width/address;
- `ULDC` and other `LD*` are not covered;
- frozen simulator still uses its existing `OP_LDC data_size=4` constant-load approximation.

22 compiled consumer/grammar tests passed.

### Formal same-run context bundle

Existing P34 raw was promoted without recapture.

```text
35 / 35 members PASS
launches 0..34
same CUDA context = ctx_0x5b5ba0bd1a60
terminal drop=0 / overflow=0 for every member
```

Formal durable bundle:

```text
run_id =
C16R_qwen-qwen2-5-0-5b-instruct_s2-text_prefill_awma-route-b-nvbit1771-sim-native-contiguous-prefix_q05-contiguous-prefix_20260918T022749Z_1fea2d955d1c

durable path =
/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_prefill_awma-route-b-nvbit1771-sim-native-contiguous-prefix_q05-contiguous-prefix_20260918T022749Z_1fea2d955d1c

manifest SHA256 =
5dc4f8d3fc802e6af66ab76f33adfeb31b335d44511ec792404c7210ca04d64e

file_count = 114
total_bytes = 390072942
producer-side destination verification/ACK = PASS
```

## Producer page-overlap evidence

Broad same-run trace-address overlap reported by node109:

### 4 KiB

```text
P1   24.724%
P2   49.448%
P4   49.448%
P8   98.896%
P16  99.227%
P34  99.338%
```

### 64 KiB

```text
P1   24.670%
P2   49.339%
P4   49.339%
P8   98.678%
P16  99.119%
P34  99.559%
```

This is already strong evidence that most Q05 address-page overlap is created by a very recent predecessor window, especially by P8.

However, these producer tables remain **broad trace-address overlap**, not final translation-relevant overlap. The predecessor-distance table contains low pages such as `0x0`, so the 174 contextual replay must recompute overlap using the accepted simulator's real VM-entry address-space semantics before using it to explain TLB behavior.

Do not call these percentages hardware TLB residency.

## 174 current state

Accepted waiting parent:

```text
hrl/awma-q05-warm-prefix-replay-174new-v1
5b9d708087e8ff485f03fd561a15e08baea8ad3a
AWMA_Q05_WARM_PREFIX_REPLAY_174NEW_V1_WAITING_FOR_CONTEXT_BUNDLE
```

The required formal context bundle is now available.

174 resumes as:

`AWMA_Q05_CONTEXTUAL_WARM_PREFIX_REPLAY_174NEW_V1`

Execute:

`CODEX_RESUME_174NEW_Q05_CONTEXTUAL_WARM_PREFIX_REPLAY_V1.md`

## Contextual replay matrix

Each row starts from a fresh simulator process:

```text
ISOLATED_Q05 = accepted historical anchor
P1  = member 33 -> Q05
P2  = members 32..33 -> Q05
P4  = members 30..33 -> Q05
P8  = members 26..33 -> Q05
P16 = members 18..33 -> Q05
P34 = members 0..33  -> Q05
```

Within a row, accepted F0 state persists naturally across predecessor dispatches. Q05-only metrics are before/after counter deltas; no target-entry reset is allowed.

P4/P16/P34 remain scientifically useful even where page coverage barely changes because extra non-overlapping predecessors can perturb/evict existing warm state.

## Frozen workload

```text
Qwen/Qwen2.5-0.5B-Instruct
revision 7ae557604adf67be50417f59c2c2f167def9a775
S2_TEXT / B1 / Prefill2048 / Decode32 / FP16 / SDPA
Q05_PREFILL_ATTN_FLASH
function occurrence 0
```

Historical isolated Q05 SIM_INPUT/SIM_BASELINE/SIM_RUN/SIM_EVIDENCE remain immutable.

## Storage

164 remains durable authority.

109 may retain active-model replicas for capture convenience.

174 must not retain model-weight replicas or large context/simulation raw locally; large replay output belongs on node164.

## STOP boundary

No new TLB/PTW/cache mechanism, latency/capacity/page-size/walker/Segment experiment starts automatically from contextual replay. Return the completed contextual results to ChatGPT for scientific review.
