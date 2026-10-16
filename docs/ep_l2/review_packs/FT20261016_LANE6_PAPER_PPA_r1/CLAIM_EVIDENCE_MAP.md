# Claim–evidence map

All paths below are relative to the named repository and exact source revision.
`CONTRACT_DEFINED` is a design choice; `HISTORICAL_MEASURED` and
`SHADOW_OBSERVATION` do not certify a new finite-WBUF implementation.

| ID | Exact claim / maturity | Implementation or design anchor | Directed test / validation anchor | CSV / manifest anchor | Permitted paper use and missing gate |
|---|---|---|---|---|---|
| C01 | C16/C8 data budgets 1168/1160; CONTRACT_DEFINED | FW coordination `6c136e2a`, COMMON_CONTRACT §0/3 | Lane-6 budget arithmetic; Lane-5 actual effective config still pending | FIGURE_INPUT_MANIFEST budget section; PPA_BITS.json | Design table only; not a runtime claim |
| C02 | Descriptors remain live until response commit; HISTORICAL_IMPLEMENTED | Core `1fc248aa`, `src/gpgpu-sim/gpu-cache.h/.cc`, mshr_table::commit_next_access | `tests/ep_l2/run_descriptor_mshr.sh`, `run_descriptor_mshr_integrated.sh`; source inspection only in Lane 6 | Historical C1_C3_IMPLEMENTATION_REPORT; source manifest | Explain lifecycle; new candidate regression still required |
| C03 | Pointer/global-ID static substrate preserves historical behavior; HISTORICAL_MEASURED | Core `955a50cb`, ep_l2_payload_store and tag sidecar | FW `c0a71e20`, M1 pack VALIDATION_SUMMARY and PARENT_EQUIVALENCE.csv: 10 pairs | Same pack: exact cycles/instructions and seven artifact families | Supports M1 only; not dynamic allocation or data correctness by itself |
| C04 | Descriptor relief need not accelerate the system; HISTORICAL_MEASURED | Core D256 formal `ece1a3a7` vs D512 `878f8086` | Provenance/config delta contracts and convergence validation | FW `aa44f9e8`, CALIBRATION_MATRIX_FINAL.csv, CALIBRATION_DELTAS_FINAL.csv, ANALYSIS_MANIFEST.json | Historical sensitivity figure, all 13 Banked workloads retained |
| C05 | MSHR full removal gives about 0.38% speedup on convolution; HISTORICAL_MEASURED | Core D512 `878f8086` vs controlled Line-MSHR capacity child; exact per-run identity in Lane-E pack | FW `b7dbdecb`, LINE_MSHR_CAUSALITY_r1 CONFIG_DIFF.csv and RUN_STATUS.csv | CONVOLUTION_2X2.csv: 292211→291108, full 931416→0 | One controlled sensitivity, not a non-binding ideal L2 |
| C06 | Line reuse and exact-sector temporal reuse differ; SHADOW_OBSERVATION | Core `ca3e7bc0`, sector telemetry; FW runtime `db1c9018` | Streaming prefinal VALIDATION_SUMMARY, SOURCE_MAP, FIELD_SEMANTICS | FW publication `cdab5765`, STREAMING_REUSE_PREFINAL_r1/line_vs_sector_reuse.csv | Workload motivation, 12 completed archival rows, scan excluded; no TVD hit inference |
| C07 | Old resident handle did not remain live for the observed dirty victims; SHADOW_OBSERVATION | Core `9907b7e6`, M0b generation/liveness producers | FW `7ad2b240`, M0B_OPPORTUNITY_PREFINAL_9OF10_r1/SOURCE_ANCHORS.md | DIRTY_VICTIM_TVD_PREMISE_9OF10.csv: 683333/0 live | Reject only the old-model early-release premise; not a conclusion about new TVD retention |
| C08 | WB staging ends at actual lower data accept; CONTRACT_DEFINED + HISTORICAL_HOOK | C0 §4; Core `ca3e7bc0` l2cache.h L2interface::push | New finite-WBUF production test must cover full queues, partial commit, sector data/version and release; PENDING | Lane-1 contract + Lane-5 run manifest PENDING | Lifecycle design; software packet is not free data RAM |
| C09 | U_WB16 borrows capacity with equal data/Bank budget; INTERFACE_DEFINED_RUNTIME_PENDING | Lane-1 V1 interface/baseline publication `cb7d92e4`; Core interface `4fb91f0a`; functional producer PENDING | Production rollback, Bank exhaustion, copy service, progress, reference data/version PENDING | BASELINE_CONTRACT_V1 runtime_ready=false; B16/U_WB16 result manifests PENDING | Published API is not a functional implementation-complete or performance claim |
| C10 | TVD avoids lower reads and forwards dirty inflight data; DESIGN_PENDING | Lane-2 TVD module + Lane-1 actual integration PENDING | Required-sector validity, dirty forward reachable before WAD gate, promotion atomicity, write/atomic wait PENDING | Lane-5 TVD hits/avoided reads/bytes/retention + complete manifest PENDING | Contract path only; +1 cycle is not STA |
| C11 | RO oracle can safely select whole-epoch line classes; ORACLE_DESIGN_PENDING | Lane-3 classifier/transaction module PENDING | Alias/store/atomic/write-allocate/external-write rejection; detached instances; stale fills; epoch drain PENDING | Oracle file/hash/coverage/exclusions + Lane-5 run manifest PENDING | Conditional oracle-assisted claim only, not hardware classification capability |
| C12 | I_WB/I_META/I_READ_HIT quantify ceilings; IDEAL_DIAGNOSTIC_PENDING | Lane-4 exact switch semantics and source PENDING | Prove targeted blocking non-binding; finite expansion without proof remains sensitivity | Lane-4 receipt, ideal vector and manifest PENDING | Diagnostic-only figure; cannot fill implementation bars |
| C13 | Shared data capacity is exact; total PPA is not yet known; BIT_ACCOUNTING | COMMON_CONTRACT; PPA_LEDGER field inventory | `build_figures.py` arithmetic and JSON consistency | PPA_BITS.json, PPA_STORAGE_SCENARIOS.csv | Raw bits only; metadata scenario is not measured area or percentage area overhead |
| C14 | Downstream masking requires interaction; METHOD_DEFINED | PERFORMANCE_HEADROOM_PLAN, C0 §6 | Separate H0/H comparisons, independently verified downstream relaxation | Four exact baseline/mechanism×H0/H manifests PENDING | Do not claim masking from headroom speedup alone |

## Evidence promotion

New results enter a later immutable pack revision only after a Lane-4/5 receipt
is bound by file hash and exact publication commit. The receipt must name its
producer manifests; a branch name, a chart, a mode label or a nonzero counter
alone is insufficient. Check runtime sources, binary, effective config,
trace/epoch identities, complete feature/ideal vectors, all terminal gates,
and explicit budget before promotion. A historical or shadow row cannot be
relabelled as B16_BANKED.

Historical test evidence is cited as historical: Lane 6 inspected source and
records and did not rerun these simulator tests. New production correctness
remains the responsibility of Lane 5's independent validation. Missing cells
remain missing, including unaccelerated workloads; no zero imputation.

The manifest records full revisions; shortened revisions in this table are
labels only. Current upstream contracts/results are indexed in
`DEPENDENCY_SNAPSHOT.json`, with null for unavailable publications.
