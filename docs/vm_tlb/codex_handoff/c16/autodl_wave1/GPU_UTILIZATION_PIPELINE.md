# C16 Wave-1 GPU Utilization and Local-Offload Pipeline

This addendum refines the RTX3090 execution handoff. It does **not** change scientific identities, scenarios, sampling policy, model revisions, or evidence boundaries.

## Goal

Maximize useful paid GPU-instance time without contaminating formal measurements.

The target is **high wall-clock productivity**, not artificially forcing the GPU utilization graph to 100%. Short LLM kernels and profiler serialization can legitimately produce bursty utilization. Never run concurrent scientific GPU jobs merely to increase utilization.

## Two-stage pipeline

### Stage R — AutoDL remote executor

AutoDL should do only work that requires, or is tightly coupled to, the real GPU:

- native inference / correctness / peak-VRAM / timing;
- Nsight Systems capture;
- bounded NCU target measurement;
- bounded NVBit capture;
- minimal artifact closure: terminal state, identity receipt, file size, SHA-256, RAW_INDEX row;
- only small control/runtime fixes that must match the real instance.

Do **not** spend paid GPU-instance time on large SQLite/TSV export, catalog reconstruction, semantic joining, compression, long hash rescans, plotting, or general analysis when those can run on the local server.

### Stage L — local postprocess executor

The local server should consume hash-closed remote artifacts and do, whenever possible:

- `nsys export` from `.nsys-rep` to SQLite;
- SQLite queries and launch/catalog extraction;
- `KERNEL_CATALOG`, runtime join, semantic map, coverage, heavy-tail tables;
- compression and Git-size reduction;
- C schema sanity / sampling preparation;
- H trace parsing and page/cache-line fingerprint work;
- long SHA verification of transferred copies;
- plots, summaries, cross-run comparison.

Local work may run while AutoDL executes the **next** formal GPU run, because it is on a different machine.

## Remote measurement exclusivity

Formal baseline/profile/capture windows remain exclusive on the AutoDL host.

Create a remote marker such as:

`/root/autodl-tmp/c16/control/MEASUREMENT_ACTIVE`

while a formal baseline, nsys, NCU, or NVBit scientific run is active.

While this marker exists, do not start on the AutoDL host:

- large rsync/scp transfers;
- large SHA scans;
- SQLite export;
- gzip/xz compression of large artifacts;
- model downloads/transfers;
- another GPU scientific job.

Small receipt writes and lightweight telemetry are allowed.

The marker is a hygiene guard, not scientific evidence by itself; each formal run still needs its own immutable run receipt.

## Preferred Nsight Systems flow

For each formal nsys run:

1. Remote GPU creates the `.nsys-rep`.
2. Remote performs only bounded validation:
   - nonzero report size;
   - run/package identity;
   - exact SHA-256;
   - terminal status;
   - source receipt.
3. Remove the formal measurement marker.
4. Transfer the **smallest sufficient raw artifact first**, normally the `.nsys-rep`, to the local server using resumable transfer.
5. Verify destination SHA-256.
6. Once the local copy is verified, local processing may begin while AutoDL starts the next formal GPU run.
7. Local server performs `nsys export -> SQLite -> catalog`.

Avoid generating a ~100+ MB launch TSV on AutoDL when the `.nsys-rep` is substantially smaller and can be exported locally.

### Local nsys qualification

Before making local export the standard path:

- install or otherwise provide a compatible `nsys` CLI on the local server;
- prefer the same Nsight Systems version as AutoDL;
- perform one paired remote-vs-local export of the same frozen `.nsys-rep`;
- compare schema, kernel/activity row counts, CUDA-correlation coverage, NVTX range coverage, and key identity fields;
- if the local export is not equivalent enough for the intended catalog, keep remote export as fallback and record the reason.

Do not require byte-identical SQLite files; compare the scientific fields/row relationships that are actually consumed.

## GPU run-ahead queue

Once G0/G1 are qualified, keep at least the next two **already-authorized** GPU jobs staged in a local queue so the GPU does not wait for postprocessing.

Recommended order for currently available assets:

1. Finish Llama S1/S2 formal G1 capture/closure.
2. While local server exports/parses S1/S2, AutoDL may run the next frozen Llama native scenarios (including remaining approved S3/S4 baseline/census if resource-admitted by the frozen matrix) without waiting for local catalog construction.
3. Between formal measurement groups, transfer/verify P1 (Qwen2.5-0.5B).
4. Run Qwen0.5 G0 then native baselines/census while local server continues Llama catalog/semantic work.
5. Consume P2/P3 immediately when A publishes them; do not wait for the other package if one is already immutable and accepted.

Do not invent new scenarios to fill idle time. Only use frozen C16 scenarios and approved capability canaries.

## Resident-model optimization

Repeated model load/unload is not useful scientific GPU work.

A resident-model runner/session may be introduced **only** if:

- weights stay resident on the same GPU;
- every scenario uses the exact frozen token receipt;
- KV/cache state is explicitly reset between scenarios;
- output/correctness and timing semantics match the standalone runner;
- one frozen scenario is run both standalone and resident as an equivalence check;
- no cross-scenario KV/prefix-cache reuse is introduced unless that behavior is explicitly the scenario under study.

If equivalence passes, use resident execution to reduce paid idle/setup time for repeated scenarios. If uncertain, keep the standalone runner.

## NCU / NVBit scheduling

G2/G3 remain nonblocking for G0/G1.

While local server processes a completed nsys report, AutoDL may use the GPU for G2/G3 **only when an exact target identity has already been fixed**. Do not select targets from guessed kernel names.

NVBit raw files can be large. Do not transfer multi-GiB raw traces concurrently with a formal measurement unless a separately validated interference experiment later authorizes it. Default policy: measurement -> capture closeout -> transfer gap -> next measurement.

After destination SHA verification, H may parse the local copy while AutoDL performs a different approved GPU run.

## Remote storage policy

Keep AutoDL as a rolling working set, not an archive.

For any raw artifact eligible for removal:

remote completed file
-> remote SHA-256
-> local resumable transfer
-> local SHA-256 == remote SHA-256
-> transfer receipt
-> only then remote cleanup

Never remove the only verified copy.

## Git artifact policy

Do not commit oversized raw profiler outputs or 100+ MB uncompressed launch tables.

Prefer:

- raw artifact outside Git + path/size/SHA/retention receipt;
- compact TSV summaries;
- deterministic `.tsv.gz` when full launch-level rows are required and the compressed file remains repository-safe;
- manifest binding to the uncompressed logical schema and source raw SHA.

Do not reduce scientific rows merely to satisfy Git size limits; use compression or external raw indexing.

## Progress policy

During paid AutoDL time, whenever the GPU is idle for more than a short bounded setup gap, ask in this order:

1. Is there an already-authorized G0/G1 native run ready?
2. Is there an already-fixed G2/G3 canary/target ready?
3. Is the next immutable A package ready to transfer between measurements?
4. Is remote-only setup actually required, or can it be moved local?

Do not answer low utilization by launching simultaneous scientific jobs or by modifying batch/context beyond the frozen scenario.

## Evidence boundaries

- Low instantaneous GPU utilization is not itself a scientific failure.
- The objective is reduced **paid idle wall time** while keeping formal measurement windows uncontaminated.
- Remote capture and local postprocess are separate evidence stages; preserve exact raw SHA and producer/runtime identity across the handoff.
- Local processing must not silently change semantic/operator labels; unsupported mappings remain `UNKNOWN`.
