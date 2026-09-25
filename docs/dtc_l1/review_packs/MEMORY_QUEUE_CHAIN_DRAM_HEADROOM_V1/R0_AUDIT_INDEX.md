# R0 source and telemetry audit index

This review pack preserves the zero-simulation audit required before the
memory-side queue-chain/DRAM-service experiment.  The canonical, versioned
artifacts are retained in the SG3 granularity directory rather than copied or
rewritten here.

| Required audit item | Canonical artifact | Review use |
|---|---|---|
| Source-supported resource map | [`SG3_MEMORY_QUEUE_CHAIN_SOURCE_MAP_V2.tsv`](../../iscas2027/granularity/sg3/SG3_MEMORY_QUEUE_CHAIN_SOURCE_MAP_V2.tsv) | Parser ordering, queue ownership, shared-credit coupling, and DRAM clock semantics |
| Existing accepted BICG telemetry | [`SG3_BICG_MEMORY_QUEUE_CHAIN_TELEMETRY_V2.tsv`](../../iscas2027/granularity/sg3/SG3_BICG_MEMORY_QUEUE_CHAIN_TELEMETRY_V2.tsv) | Baseline pressure evidence and explicit `NOT_AVAILABLE` fields |
| bus-width diagnostic reclassification | [`SG3_BUSWIDTH_PROBE_RECLASSIFICATION_V1.md`](../../iscas2027/granularity/sg3/SG3_BUSWIDTH_PROBE_RECLASSIFICATION_V1.md) | Why the prior 16-to-32-B result is retained but not a discriminating service test |
| Registered R1/R3 gates | [`SG3_MEMORY_QUEUE_CHAIN_EXECUTION_PLAN_V1.tsv`](../../iscas2027/granularity/sg3/SG3_MEMORY_QUEUE_CHAIN_EXECUTION_PLAN_V1.tsv) | Six BICG configurations, GESUMMV priority order, and conditional gates |
| Registered all-headroom ceiling | [`SG3_MEMORY_QUEUE_CHAIN_R4_REGISTRATION_V1.tsv`](../../iscas2027/granularity/sg3/SG3_MEMORY_QUEUE_CHAIN_R4_REGISTRATION_V1.tsv) | Conditional BICG 20-MiB L2 ceiling definition |

All listed artifacts were registered before their corresponding simulations.
The current study retains the accepted `queue=128` evidence and treats the
older detailed-DRAM `busW 16 -> 32 B` rows solely as diagnostic/non-
discriminating provenance.
