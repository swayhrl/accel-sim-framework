<!-- DTC_PERIODIC_CURRENT_START -->
# DTC L2 MLP full-workload exploration V1

Latest read-only snapshot: [2026-10-29T03:14:59.107394+00:00](periodic/20261029T031458Z_191687a7/README.md) · [323/350 primary accepted cells](periodic/20261029T031458Z_191687a7/dashboard.html). [Machine-readable report](periodic/20261029T031458Z_191687a7/report.json) · [Snapshot member hashes](periodic/20261029T031458Z_191687a7/MEMBER_MANIFEST.json).

Coverage is partial until all valid planned cells are accepted. Original negatives remain visible; independent R2 is supplemental and never replaces a primary negative. CH non-P0 controls may be absent; available-subset GMs are not final suite winners. Sources are coherent per file, not one global transaction. The old BATCH_STATE .88 label is historical, not evidence of the active admission policy. English v0.23 is unchanged.

The root MEMBER_MANIFEST.json and historical checkpoint manifests describe their original snapshots; they are not manifests for later appended files. Use each snapshot MEMBER_MANIFEST.json.
<!-- DTC_PERIODIC_CURRENT_END -->

<details><summary>Historical root README, preserved in full</summary>

# DTC L2 MLP full-workload exploration V1

**Latest current-progress review:** [ChatGPT review checkpoint,2026-10-27 20:22 main snapshot plus20:29 resource supplement](checkpoints/CURRENT_PROGRESS_REVIEW_V1/README.md). It includes350 cells,145 accepted,80 confirmed live at the main snapshot,125 pending; newer79-live admission observation is separately labelled. [Ready-to-send review prompt](checkpoints/CURRENT_PROGRESS_REVIEW_V1/CHATGPT_REVIEW_PROMPT.md). The campaign continues.

Latest counter coverage: [129 closed-log sidecar and baseline CH/DH table](agents/D/raw_reason_v1/README.md). The prior unparsed-versus-unprinted distinction is now verified across129 accepted logs, with no raw or strict rewrite. [Supplementary search V2 review](SUPPLEMENTARY_SEARCH_V2_REVIEW.md) records the coordinator-approved boundary and best-uniform-CH rules before their separate runtime activation.

Latest completed read-only analysis: [three-agent current results](CURRENT_RESULTS_ANALYSIS_V1.md). This is a time-labelled partial snapshot, not a final candidate selection. [Counter clarification](COUNTER_CLARIFICATION_V1.md) distinguishes unparsed reason fields from absent raw counters.

Operational follow-up: the same owner now uses provider-consistent resource reservations and a four-task pre-execution window while retaining384 model capacity. Actual native models increased41→51 in two30-second observations with zero fresh-HOLD events, versus46 HOLD events in the preceding two intervals. A qualified durable registry journal protects future extension commits and prevents scientific completion while recovery is unresolved. The85-case actual-source qualification and production ACK are preserved; installation granted no starts and changed no frozen source or old budget.

This is the initial execution checkpoint, not the final scientific result. The active Goal continues in the single existing native epoch2 owner. No manuscript changes are made; English v0.23 remains the last user-confirmed master.

The frozen population contains all 35 ordinary representative inputs: 9 PolyBench, 7 Parboil, 9 CUDA Samples, and 10 Rodinia. Seven scientifically unresolved programs remain unresolved. Historical 72-input data, derived b+tree/hotspot, fraction/trim inputs, old failures, and repair-validation identities are not promoted into this new population. See agents/C/INPUT_COVERAGE_README.md and contract/SCOPE.json.

The initial matrix has 350 cells: CH P0 and DH P0 plus eight DH single-factor variants for every input. Six exactly matched downstream18 P0 results are references; 344 independent new starts are registered. All 18 old downstream points were closed naturally before this request. New factor-family extensions add exact new identities and credits, without resetting old requests or imposing a small total-start ceiling.

Core is 9eedb3131937748f0492fa83aad37d3691118d70; Framework is 02775fd795cde5aae1480d81cee6eb481d0a08f4. Binary SHA256 is 02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d. The fixed 850 MHz DRAM, other clocks, 10 MiB L2 sets/ways/mapping, DTC structures, Hash and completion service are preserved. Base L2 is S:128:128:16,L:B:m:L:L,A:192:4,32:0,32.

| Profile | Sole target change |
|---|---|
| E384 / E768 | MSHR entries 192 to 384 / 768 |
| M8 / M16 | Maximum merge 4 to 8 / 16 |
| Q64 / Q128 | L2 miss queue 32 to 64 / 128 |
| F128 / F256 | FR-FCFS queue 64 to 128 / 256 |

FR-FCFS also changes partition shared credits from F+191: 255 to 319 / 447. It is not an isolated change in L2 capacity. Resource counts and interpretation are in agents/A/PARAMETER_CONTRACT.md. These are simulator resource explorations, not equal-area claims.

Five actual subagents prepared A configuration, B resources, C input registration, D strict consumption and E adaptive search. The main coordinator alone registers, dispatches and publishes. Four matrix-native canaries covering the four factors passed natural completion, strict raw/config/binary/input checks, true164 archival and native restore. CPU-only native-prefix qualification passed 743 checks before production starts.

The new additive scheduler remains inside the existing owner PID 1498278, with no second controller. An independently CPU-qualified operational amendment expands only this new scheduler and its executor threads from inherited 32-CPU affinity to the actual 512-CPU cgroup set and 384 quota-equivalent executor capacity. The old main thread, old workers and already running model affinities are retained. The frozen scientific sources and registry are not changed by this amendment. Actual concurrency is dynamically limited by memory/CPU pressure and observed RSS, not by 384 as a promised simultaneous count. See operational_amendments/affinity_v1/ACK.json.

The owner lifetime is additionally protected by a qualified CPython 3.10 threading pre-join hook. When the old R20 main loop finishes naturally, this appended hook waits for the current L2 addon before the existing ThreadPool global shutdown runs. It does not intercept the old loop, remove previous hooks, reset shutdown flags, or alter registry/source identities. Twelve real subprocess checks include a failing unprotected control and successful post-main submission, executor expansion and natural closure. See operational_amendments/lifetime_v1/ACK.json and agents/B/OWNER_LIFETIME_AMENDMENT_CPU_QUALIFICATION.json. Post-affinity observations also confirm actual native models on CPUs above63 and three strict/archive/restore successes; no CPU throttle, new OOM or memory pressure was observed in that interval.

Admission uses an 88% conservative available-memory budget, same-input history, separate RSS/address-space envelopes, long/short filling and one CPU per model. Pressure pauses fresh admission without killing healthy models. Streaming compressed result logs are archived to true164; local free-space floor is 5 GiB. Inputs and binaries are reused read-only. Native controls and small state remain on174.

Results remain strict PASS, archived negative, pending, or engineering states; there are no automatic model retries or substitutions. Frozen BUILD_PROFILE.native_values=UNPROVEN is a pre-start declaration; subsequent actual-option checks validate configuration and whole declared trace completion, while they do not prove numerical application correctness. Missing counters are null, never zero. Early non-P0 cells without their matching DH P0 cannot establish DH self-speedup or suite GM. Three diagnostic P0 references alone are not a 35-program aggregate. See agents/D/first_results.md.

Adaptive selection waits for terminal single-factor results across the complete registered population. It uses one uniform configuration, never per-program best-of choices. Registered rules assess 1% total and marginal GM improvements, extend a still-improving factor boundary, search evidence-backed combinations without a full Cartesian product, and obtain CH/DH matching over all 35 inputs for proposed formal configurations. Missing/negative coverage remains explicit; formal complete coverage is not fabricated. See agents/E/ADAPTIVE_SEARCH_CONTRACT.md.

Live native root: /root/data/dtc_l2_mlp_exploration_20261027_v1

True164 archive: /root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1

This checkpoint includes immutable contracts, exact configs, execution/consumer/search code, CPU qualifications, input provenance and a time-labelled partial result snapshot. Large raw logs, traces, binaries and datasets remain outside Git. Snapshots are individually coherent closed records, not an atomic snapshot of all concurrent processes. Final workload tables, sensitivity plots, uniform moderate/high-resource candidates and CH/DH comparisons will follow natural completion of the scientific stage.

</details>
