# Lightweight read-only Oracle result consumer

`snapshot(base_root, matrix_path, out_dir)` returns a dictionary and writes
`ORACLE_LIVE_RESULTS.json`, schema `DTC_ORACLE_LIVE_READONLY_SNAPSHOT_V1`.
CLI: `python3 -B oracle_live_consumer.py --base <native base> --matrix <frozen128>
--out <independent derived directory> [--watch --interval 60]`.

No engine imports, native science registration, model/GPU calls, dispatcher,
archive/restore repair, source mutation, ledger write or Git operation exists.
Inputs are frozen plans and naturally closed request-local results. Only the
specified derived output directory is written. Main enables any watcher.

All128 rows preserve status/classification/raw_status, result_path,
result_sha256, uuid, cycles, S_oracle, H, input/program/suite/mode/stage. Count of
rows with RESULT paths equals closed_result_count. The closed_fingerprint_sha256
uses only sorted original RESULT path/SHA/UUID/state, not timestamps or pending
changes. No closed result means no scientific data to publish. Historical DH-P0
cycles remain context only; matched OFF must share new Core/binary/cudart and
all270 non-Oracle options for the exact full input.
The runtime writes exclusive RESULT files in place. The watcher waits for valid
JSON, its final newline and stable size/mtime before pinning/counting a closed
result, so transient partial writes cannot crash the watch or create a false
immutable-result mutation. Postprocessing engineering events remain linked even
before a RESULT can close; they do not become accepted or fabricated negatives.

Accepted here means the actual immutable result reported acceptance from the
frozen strict/archive closer, with local DONE/natural exit/strict identity and
typed-archive report checked. This lightweight watcher does not rehash all164
archive chunks or replace D's independent scientific review. Independent final
review is explicitly NOT_YET_FINAL_INDEPENDENT_REVIEW until separately attached.
It never holds or releases a model gate. Runtime negative/HOLD results and
mutated/missing evidence remain visible and outside performance statistics.

Flat `KERNEL_FACTS.<RESULT_SHA>.json.gz` files retain actual original ordinals1..N,
kernel names (including repetitions), per-kernel cycles/active instructions and
cumulative CTA plus explicit CTA delta. `cycles` is strict gpu_sim_cycle for that
kernel; `total_cycles` is cumulative gpu_tot_sim_cycle. Cumulative cycles are
never used as the per-kernel comparison. Accepted kernel deltas sum to actual
application cycles; instruction and CTA work and order match same-build OFF.

`MATCHED_KERNEL_PAIRS.json.gz` contains kernel speedup/headroom, actual exposure
and selected retained-service counters with original strict/raw SHA/path refs.
Raw files are read once per immutable accepted RESULT into a bounded-by-source
derived cache. Counters are **as printed in each kernel stats block**: reset,
cumulative/delta and critical-path semantics are not invented. Missing counters
are null; M/L2 printed unit counts and sums remain explicit. Full raw data stays
in its existing164 archive/native source; no raw logs are copied into reports.
Terminal metrics, traffic and latency dictionaries are preserved as printed.

Mode/suite/fixed8/CORE32 coverage, signs and GM retain slowdowns/negative H. Direct
mode comparisons use a common accepted input intersection. There is no per-
program best-mode GM, mathematical bound, realizable DTC gain, equal-area or
additive headroom claim. Trace/per-warp semantics and ROI do not mean identical
global cross-warp issue order. Source-event checks do not certify original
HtoD/capture ELF or native application numerical correctness. v0.23 stays frozen.
