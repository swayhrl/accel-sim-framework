# AI family resource map

No cross-scenario arithmetic average is used.

## Prefill Flash versus prefill GEMM

T0 Flash is sensitive to the modeled L1 hit-path latency: 32 -> 16 cycles
improves runtime 8.145%. A 1-cycle upper bound improves only 5.076%, so the
response is non-monotonic and cannot be described as simple latency saturation.

T1 GEMM is exactly insensitive to both 2x and 4x L2 set count. Its dominant
observable is eligible-structural scheduling time. Tensor-unit count could not
be independently widened beyond the four-entry specialized issue register, so
the stage leaves the per-FU cause unresolved rather than changing two domains.

Thus prefill Flash and GEMM do not share one demonstrated resource limit.

## Decode GEMV versus attention

Qwen T2 GEMV responds to finite L1-MSHR capacity (+2.842%) and less to the DRAM
service diagnostic (+1.295%). Beyond 2x MSHR, the cycle response is flat while
dependency and DRAM pressure remain.

SPLITKV attention drops L2 reservation failures from 169,253 to 7,528, yet
improves only 0.611%; its DRAM 2x diagnostic regresses 5.828%. Llama L2 attention
similarly drops L2 reservation failures from 63,962 to 832 with a -0.064% cycle
response. Across these two attention targets, L2 reservation pressure is a
repeatable location but not a demonstrated dominant runtime limiter.

## Exact GEMV scale pair

L1 and M1 are the same implementation and have identical per-CTA instructions,
memory instructions, active references, and logical requests. Both respond to
L1-MSHR and DRAM interventions, but L1's aggregate scale produces materially
larger responses. This is a scale/context result, not a Llama-versus-OLMoE
family difference. See `CROSS_SCALE_ANALYSIS.md`.

## Low-demand control

M2 has one CTA, three admissions, zero cache reservation failures, and
negligible queues. It receives no scaling matrix and prevents interpreting all
decode kernels as memory-resource limited.

## Resource-balance answer

The suite supports resource-balance sensitivity rather than one absolute
capacity limit. In high-scale GEMV, both L1 outstanding capacity and DRAM
service produce similar bounded gains; increasing either one moves pressure to
the other hierarchy/scheduler locations. In attention, removing reservation
pressure barely changes cycles. In prefill, the demonstrated responses differ
between Flash and GEMM.
