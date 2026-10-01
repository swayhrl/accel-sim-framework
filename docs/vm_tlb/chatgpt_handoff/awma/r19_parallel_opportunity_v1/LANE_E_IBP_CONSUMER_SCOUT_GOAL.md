# Codex Goal — Lane E / node174-new CPU/source only
## R19 IBP decompression-to-consumer opportunity scout V1

Execution branch:
`hrl/awma-r19-ibp-consumer-scout-174new-v1`

CUDA=0. Accel-Sim=0. No GPU lock.

## Question

IBP already compresses host-side ML tensors and overlaps fetch+decompression. Does its published integration still require the full decompressed tensor to be materialized in GPU memory before the first real consumer, leaving a distinct decompression->consumer boundary that is not already covered by IBP or close prior work?

This is a novelty/source/input qualification task, not a performance experiment.

## E0 — source authority

Pin:
`AKKamath/InvariantBitPacking@b2f71003113defb4e387caf18843b241f6280ba9`

Audit:
- `decompress_fetch`
- output_tensor path
- device decompression helpers
- FlexGen / InfiniGen-IBP integration referenced by authors
- GNN/DLRM integrations if relevant.

Determine exactly:
- where compressed bytes live;
- where reconstructed bytes are written;
- whether consumer GEMM/embedding/message-passing reads a fully materialized dense buffer;
- whether decompression can already be invoked inside a consumer kernel/device function;
- whether author code has any fused decompress+consumer path.

Do not infer from API names only.

## E1 — nearest-neighbor search

Return to primary sources/repositories for:
- DFloat11 / ZipServ / other lossless compressed execution already in Round11/18;
- nvCOMP-style decompression integration where relevant;
- compressed GEMM / on-the-fly decode work that may already cover the same consumer fusion.

Separate:
- compression format innovation
- PCIe transfer overlap
- device decompression
- direct compressed execution / fused consumer.

## E2 — decision

If existing IBP or direct nearest-neighbor work already performs the relevant consumer fusion:
`R19_IBP_CONSUMER_BOUNDARY_ALREADY_COVERED`.

If the source proves a full dense materialization boundary remains and there is a real public workload path where that boundary is on the critical path, write one preparation card:
`docs/vm_tlb/literature_notes/awma/problem_cards/R19_IBP_DIRECT_CONSUMER_PREPARATION.md`

The card must contain:
- exact producer/consumer
- real public input
- strong software baseline
- numerical/lossless contract
- one bounded Native falsification on 109
- nearest prior work.

Then decision:
`R19_IBP_DIRECT_CONSUMER_CANDIDATE_QUALIFIED`.

If critical-path relevance cannot be established from source/literature:
`R19_IBP_CONSUMER_OPPORTUNITY_UNRESOLVED`.

Do not create an execution Goal automatically.

Also update the literature notes with the R53 correction if not already present.

Push/fetch-back verify and STOP.
