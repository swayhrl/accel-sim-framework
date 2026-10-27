# DTC L2 MLP full-workload exploration V1

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
