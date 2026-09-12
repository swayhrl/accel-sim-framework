# C16-P → G event/schema request

Status: `SCHEMA_REQUEST_FOR_FUTURE_EVENTS`, not a request to rerun the current clean S1/S2 census.

P found no missing Lane-C catalog or join-key column in the current S1/S2 population. The following future event closure is mandatory; otherwise P labels input `INPUT_NOT_HASH_CLOSED` and does not formally postprocess it.

## Every new G `.nsys-rep` (P1)

Provide producer G full commit SHA, producer manifest path/SHA, profile run identity, deployment/scenario/input identity, raw report path/byte size/SHA, G Nsight version, export command/config identity, terminal status, and a transfer receipt with both remote source and local destination path/size/SHA.

The current remote profile receipt has artifact output SHA `NA`; the available export-validation receipt closes the local raw SHA but is not an explicit dual-endpoint transfer receipt. Add the latter to every future producer checkpoint.

## Direct semantic diagnostic (P2)

Provide direct evidence only: `DIRECT_RUNTIME_NVTX` and/or `DIRECT_MODULE_ID`. Each candidate mapping must carry diagnostic report/run scope and enough structural fields to compare without kernel-name guessing: deployment/scenario/input identity, phase/decode bin where available, report-local device/context/stream/correlation/launch identity, kernel name, grid, block, dtype, layer ID, operator, evidence source, and explicit ambiguity status.

Current S1/S2 prove that stream IDs collide and 4,501 correlation IDs overlap across reports. Do not publish an unscoped correlation-only mapping. If a diagnostic cannot uniquely bind a clean launch, publish `UNKNOWN` rather than choosing a candidate.

## C-facing boundary

P can now provide complete physical launches, timing, profile indexes, and join validation as `REAL_NATIVE_SCHEMA_SANITY`. It cannot notify C to freeze a prospective selector until G's committed producer closure and a direct semantic map permit a non-ambiguous, evidence-bound semantic catalog.
