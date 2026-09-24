# Source and telemetry anchors

- Phase A accepted BICG telemetry and trigger: `docs/dtc_l1/iscas2027/granularity/sg3/SG3_BICG_DOWNSTREAM_TELEMETRY_HEADROOM_TABLE_V1.tsv` and `SG3_BICG_DOWNSTREAM_HEADROOM_INTERPRETATION_V1.md`.
- C0 source map: `docs/dtc_l1/iscas2027/granularity/sg3/SG3_MEMORY_SIDE_SOURCE_MAP_V1.tsv`.
- C0 BICG memory-side telemetry: `docs/dtc_l1/iscas2027/granularity/sg3/SG3_BICG_MEMORY_SIDE_TELEMETRY_V1.tsv`.
- C0 selection and exclusions: `docs/dtc_l1/iscas2027/granularity/sg3/SG3_MEMORY_SERVICE_KNOB_SELECTION_V1.md`.
- C1/C2 registry: `docs/dtc_l1/iscas2027/granularity/sg3/SG3_BUFFERING_MEMORY_SERVICE_EXECUTION_PLAN_V1.tsv`.

The selected option is registered at Core `src/gpgpu-sim/gpu-sim.cc:299-300`.  It sets `busW`; `dram_atom_size = BL * busW * gpu_n_mem_per_ctrlr` is derived in `gpu-sim.h:437-438`; detailed DRAM advances a request's data transmission/return by that atom in `dram.cc:298-301,570-592`.  Address-map initialization uses channel/subpartition/shader configuration separately (`gpu-sim.h:451-452`).  Per-DRAM `busW`, `bw_util`, `dram_eff`, and `mrqq` are printed by `dram.cc:691-720`; global latency counters are emitted by `mem_latency_stat.cc:352-365`.

The source map rejects scheduler, partition, and return queues as memory-service knobs because they alter buffering/admission; it rejects timing-string sweeps and the fixed `dram_latency` delay for the bounded question.  No mechanism or Core source was changed.
