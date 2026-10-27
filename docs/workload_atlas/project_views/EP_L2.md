# EP-L2 view - source/behavior atlas V1

The EP scientific roster is the actual frozen original seven inputs plus independent SGEMM exploration, as audited in [CROSS_PROJECT_MAPPING.md](../CROSS_PROJECT_MAPPING.md). It is not inferred from familiar benchmark names or from every later shared trace-library candidate. No experiment, capture, build, controller, active registry, or raw result was operated for this atlas.

Current authority was checked against the later18-variant asset inventory and accepted native Vector diagnostic; see [CURRENT_AUTHORITY_SCOPE_AUDIT.json](../contributions/ep_mapping/CURRENT_AUTHORITY_SCOPE_AUDIT.json). The18 variants retain8 current selections, legacy references and conditional named cases separately. Takeover asset draft labels are historical and do not establish present materialization or qualification.

## Frozen evidence and independent boundaries

Original MAIN has accepted pairs for convolutionSeparable, CFD097K, DWT1024, SAD default, Vector4M, and restored FWT7/21. Btree remains HOLD; original seven-input aggregate remains UNKNOWN. SGEMM is a distinct accepted exploratory pair. `EP_FROZEN_INPUT_MAPPING.json` preserves their exact pair/attempt IDs, input SHA and source/config/simulator identities. Its authority source files carry full SHA256 receipts.

The EP execution contract's `full_application` wording is preserved as a historical contract label. The atlas separately asks whether the captured list covers the source application. CFD's five-kernel trace is inconsistent with the standard iterative source; Conv's two-launch capture is not explained by the inspected fixed host source. Neither issue retroactively changes accepted numbers, identity or historical qualification.

Native main61 is Core `d010911e3174a3764791183cd108fe4664ba8731`, simulator SHA `61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5`. Observer r4 is Core `9243f769620653f2a9d4df5599e9581e9dae6067`, simulator SHA `d99ac88d60a596b123765009420a85eea1463c01e88807a8876ae946e380fd13`; observer r5 is Core `1093d2629e3d6a9130ba25b9dd119b6f3e16c092`, SHA `e511cce7d8bcd5a3ebbe6255f42ebe153547484a69c6857ab55f7a8835a2dc33`. Their runtime Framework is `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`. They must not be pooled or mistaken for capture application ELFs.

## Program-specific use

| Case | Source-backed behavior to reuse | EP-L2 question and limitation |
|---|---|---|
| convolutionSeparable3072^2 | [Rows/columns analysis](../programs/cuda_samples/convolutionSeparable.md): shared halo staging, two transposed access directions and intermediate image dependency. | Distinguish overlap of data objects between phases from actual L2 residency and RO admission. Host/ROI discrepancy remains open. |
| SGEMM medium | [Tiled column-major `mysgemmNT`](../programs/parboil/sgemm.md), single-kernel registered trace shared with DTC. | Input certificate is line/read-reference classification, not cache misses or transactions. EP accepted r4 SGEMM candidates were resident hits and production RO/relieve/detach zero; do not infer T benefit from certificate size. |
| SAD default | [Three SAD stages](../programs/parboil/sad.md), read-only reference reuse then output aggregation and stage dependencies. | Compare line sharing across search positions and output/intermediate traffic separately; static repeated requests do not establish simultaneous MSHR merge. |
| FWT7/21 | [FWT analysis](../programs/cuda_samples/fastWalshTransform.md), 19 launches with global radix-4 stages, shared terminal transform and modulation. | Global stages overwrite data that later stages reread. This creates data-version/residency questions, not a blanket immutable-line certificate. Do not substitute DTC selected11/19. |
| DWT1024^2 | [DWT analysis](../programs/rodinia/dwt2d.md), component split then three levels for each of three channels. | Explicitly use EP's192/128/64 thread specializations and larger RGB input. Observer r5's covered RESERVED occupancy reached3/16, with actual TagFAIL/relieve/detach zero in the accepted observation; source overlap does not make all16 RESERVED occur. |
| CFD097K | [Conditional CFD source scope](../programs/other/cfd.md); source pointer/neighbor and variable planes, but retained list only initializes/step/flux. | r5 observed RO transactions with covered maximum4/16 RESERVED and actual TagFAIL/relieve/detach zero. This pertains to the frozen five-kernel model, not the full2000-step application. |
| Vector4M | [VectorAdd analysis](../programs/cuda_samples/vectorAdd.md), one coalesced load/load/store stream with no inter-CTA reuse required by the algorithm. | Control/boundary case. It is the takeover's exact existing native `EP_VECTORADD_S` asset. Larger DTC6M changes footprint/CTA count. The later accepted native r5 Vector F diagnostic uses this same4M input: covered/new-tag RESERVED maximum3/16 and production TagFAIL/relieve/detach zero. It is one point, not a performance pair; historical Conv r5 remains unmeasured in the reviewed evidence. |
| Btree original | [Additional source audit](../contributions/ep_mapping/BTREE_SOURCE_SCOPE.md), dependent tree traversal and root-node sharing. | Original nonzero-mask address-scope HOLD remains. DTC derived trace is a different input. No performance or numerical claim is promoted. |

The r4/r5 observations above are retained historical accepted scope from EP-MAIN `CURRENT_SCIENTIFIC_STATE.md`, with Vector updated by `ep_main_vector_r5_20261023_v1/SCIENTIFIC_CAUSE_PROJECTION.json`, not measurements performed by this atlas and not an inference from source. Physical phase alone does not identify requester/victim kernel causality.

## Evidence dimensions

`SOURCE_VERIFIED` applies to the pinned, content-verified source analyses, with explicit capture-source applicability gaps. `INPUT_BOUND` applies to the frozen identities; seven cross-project links additionally pass independent member-set reconciliation. `BINARY_BOUND` for EP here refers to the named **simulator** lineage in accepted pair records, while the capture application ELF remains UNKNOWN. `TRACE_SCOPE_BOUND` means the exact frozen list/order and headers are known; original application completeness remains conditional for CFD/Conv. `RUNTIME_MEASURED` refers only to retained historical observations within their accepted contracts. These dimensions are not interchangeable.

## Architecture hypotheses requiring new evidence

EP-L2 questions should distinguish transaction type (read/write/atomic), directory state, physical data residence, write-buffer occupancy, and downstream response lifetime. A source read-after-write between kernels establishes a dependency, but does not prove the line is resident or inflight at the relevant moment. Read-only offline certification also does not prove a nonresident read is admitted, that Tag reservation is saturated, or that detachment occurs.

For shared Conv/SGEMM/SAD traces, DTC-L1's pending-tag and physical-line questions and EP-L2's directory/data/write-buffer questions can be compared at the same registered access stream. Compare within each exact simulator/config first; cross-layer conclusions require a measured bridge. No negative or near-flat result should be explained by a label derived from the performance outcome.
