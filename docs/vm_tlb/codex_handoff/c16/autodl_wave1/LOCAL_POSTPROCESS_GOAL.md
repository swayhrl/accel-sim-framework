# C16-P Local Native Postprocess Goal

Goal name: `C16_P_NATIVE_POSTPROCESS`

Purpose: keep paid AutoDL focused on GPU-required work by moving deterministic profiler export, catalog construction, semantic joining, compression, and local validation to the existing local server.

This lane is a companion to G-runtime. It does not own GPU execution and must not modify G's runtime branch/worktree.

## Inputs

Consume only hash-closed artifacts published or transferred by G-runtime. Each input must bind:

- remote G producer/runtime commit or explicit work-in-progress receipt;
- run UUID;
- A package ID/commit/manifest SHA;
- GPU UUID + driver/runtime identity;
- raw artifact path, size, SHA-256;
- transfer receipt and verified local copy path.

For provisional pipeline debugging, a transferred raw artifact may be processed before G publishes the final scientific checkpoint only if it is clearly labelled `PIPELINE_DIAGNOSTIC_ONLY`; such output cannot enter C/H scientific conclusions until the corresponding G manifest is committed.

## Primary work

1. Qualify local `nsys export` using one paired frozen report:
   - same/compatible Nsight Systems version;
   - compare SQLite schema and relevant row counts;
   - compare CUDA kernel/activity rows, stream IDs, CUDA-correlation coverage, and NVTX phase/range coverage;
   - publish `LOCAL_NSYS_EXPORT_QUALIFICATION.md`.

2. Once qualified, for each incoming `.nsys-rep`:
   - verify input SHA;
   - export locally to SQLite;
   - generate launch-level catalog without requiring AutoDL CPU time;
   - build compact deterministic summaries;
   - preserve unsupported semantic mappings as `UNKNOWN`.

3. Produce or assist G with:
   - `KERNEL_CATALOG.tsv[.gz]`
   - `KERNEL_SEMANTIC_MAP.tsv`
   - `SEMANTIC_COVERAGE.tsv`
   - `NATIVE_BASELINE.tsv` integration joins when baseline receipts are available
   - `RUNTIME_IMPLEMENTATION_AUDIT.tsv`
   - `HEAVY_TAIL_KERNELS.tsv`
   - row-count/schema/identity receipts.

4. For large launch tables:
   - never drop valid rows merely to fit GitHub limits;
   - prefer deterministic gzip or raw-outside-Git + hash-index policy;
   - record compressed and logical uncompressed row counts/schema.

5. When G transfers a tiny NVBit trace canary, provide the hash-closed local copy to H or run only the transport/schema sanity checks authorized by the H contract. Do not duplicate H's scientific fingerprint logic.

## Concurrency rule

This lane is intentionally local and may run at full CPU/disk utilization while AutoDL executes the next GPU scientific run, subject only to local-server contention with Lane A download/finalization.

Do not starve Lane A's active downloads/hash finalizer. Use bounded CPU/I/O priority for large export/compression jobs when necessary.

## Git ownership

Recommended execution branch/worktree:

- branch: `hrl/vm-c16-p-native-postprocess-v0`
- worktree: `/workspace/worktrees/accel-sim-vm-c16-p`

Own only new C16-P utility/tests/review-pack paths unless a fixed cross-lane interface explicitly authorizes otherwise.

Never edit:

- G runtime worktree;
- A asset worktree;
- C selector worktree;
- H fingerprint worktree;
- C12-C15 scientific artifacts.

## Early output

As soon as one real Llama `.nsys-rep` is transferred and hash-verified:

1. qualify local export;
2. build a provisional `REAL_NATIVE_SCHEMA_SANITY` pack;
3. check that the columns/join keys expected by Lane C can be produced;
4. report gaps back to G before G spends more GPU hours.

Do **not** freeze Lane C's prospective selector from this provisional pack.

## Final publication boundary

Scientific postprocess output becomes consumable cross-lane only after:

- G has a committed raw/native checkpoint or exact hash-bound producer receipt;
- all consumed input hashes verify;
- postprocess code/version is bound;
- output manifest hashes every published payload.

Otherwise label it diagnostic/provisional.
