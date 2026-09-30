# Pass07 | bounded next-problem screen

Date: 2026-09-30

Decision: `NO_NEXT_CANDIDATE_QUALIFIED_PASS07`

Authorities re-read before screening:
- literature baseline `5ff0287ce45c3909d53ac44975f6fa488664b085`
- Round16 final closeout `31d585dc44f90eb70f83603c8b87a2d06efff01a`
- Round17 FlowANN closeout `8462768f6baf8d4130ee0076c4aee5ff7fd9d6c1`
- Round18/Pass06 `f7d3f445c03cca2e28072123fcf0e0d8410dffe9`

No earlier line is reopened.

## A. diffusion-language-model inference

Sources:
- Flash-dLLM, arXiv:2609.26796
- `VILA-Lab/Flash-dLLM@7437a550fd3d1a0752edcbf58bd015ad69083068`
- Beyond GEMM-Centric NPUs: Enabling Efficient Diffusion LLM Sampling, arXiv:2601.20706
- dLLM efficient-inference survey, arXiv:2607.12829

This family has real public workloads and is single-GPU testable in principle. It fails the novelty gate: Flash-dLLM already identifies GPU memory I/O as a dominant bottleneck in KV-cache-enabled dLLM inference and uses an I/O-aware fused cache kernel plus cache-driven draft/verify. A separate 2026 architecture paper directly targets diffusion sampling's vocabulary-wide logits, reductions, masked updates, SRAM pressure and irregular access. Generic dLLM cache/sampling memory claims are therefore directly covered.

State: `DLLM_MEMORY_IO_AND_SAMPLING_DIRECTLY_COVERED_NO_AWMA_ADMISSION`.

## B. adaptive-depth / looped-language-model execution

Sources:
- Continuous Depth Batching, arXiv:2608.09444
- `kschwethelm/continuous-depth-batching@9b96d920be3539da5cfe21d4b1221d57cfbfd268`
- `ThinkFlowLab/vllm-rlt@299bf14b117f42a38d15852886d673f89e123307`
- TIDE, arXiv:2603.21365
- FlexEE, arXiv:2609.17008

Variable per-token depth is a real execution shape and public looped models make a 109 experiment conceivable. But CDB already schedules at loop-iteration granularity, separates boundary stages from recurrent-core work, manages looped KV state, and prepares future batches asynchronously. It reports up to 99% of its estimated maximum adaptive-depth speedup. TIDE adds fused CUDA early-exit execution and FlexEE handles KV-correct early exit under weight offload. Literature does not expose a distinct residual that justifies a new AWMA card.

State: `ADAPTIVE_DEPTH_EXECUTION_STRONG_SOFTWARE_BASELINES_CLOSE_GENERIC_CLAIM`.

## C. agentic / tree-structured KV state

Sources:
- ArborKV, arXiv:2605.22106
- TokenDance, arXiv:2604.03143
- AgentKV, arXiv:2609.14872
- `LiuTaowen-Tony/agentkv@b5280b7c42bd90962712c19f8e0047c89ca40d6d`
- ActKV, arXiv:2609.31395
- ForkKV, arXiv:2604.06370

Branching/backtracking/multi-turn KV state has good real-workload authority, but the direct-neighbor space is already dense: tree-aware eviction and lazy rehydration, collective/sibling sharing, persistent multi-turn state plus online page compaction, action/phase-aware retention, and copy-on-write disaggregation are all directly attacked. Generic branch-KV sharing, eviction, compaction, or COW is not admitted.

State: `AGENTIC_BRANCH_KV_DIRECT_SYSTEM_COVERAGE_NO_AWMA_ADMISSION`.

## Final admission

None passes all four gates at once:
1. real public input/workload authority;
2. a narrow residual not directly targeted by strong recent work;
3. cheap semantically valid first falsification on 109/174;
4. clear nearest-neighbor boundary before mechanism design.

Final: `NO_NEXT_CANDIDATE_QUALIFIED_PASS07`.

R102 remains `R102_DORMANT_WAITING_FOR_REAL_UPDATE_AUTHORITY`.

No R19 problem card is created. No formal 109 GPU experiment, profiler run, 174 simulation, trace capture, synthetic scientific payload, contract change, or mechanism design is authorized by this note.
