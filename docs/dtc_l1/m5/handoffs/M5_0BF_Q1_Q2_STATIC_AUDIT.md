# M5.0BF Q1/Q2 static source and platform-lineage audit

Status: **Q1 SOURCE PATH PLAUSIBLE; PILOT INPUT/EXECUTION ENVIRONMENT NOT
YET ADMISSIBLE. Q2 STATIC LINEAGE COMPLETE.**

This is an M5.0BF evidence checkpoint, not a `TRACE_FORMAL_PATH_VALID`, an
`EXECUTION_DRIVEN_REQUIRED`, a frozen platform decision, or M5.0BF PASS. It
was produced in isolated M5.0BF worktrees and does not interact with the five
live M5.0B execution-driven processes.

| item | identity |
| --- | --- |
| Framework source | `08dad4c3be06efe2dfd61f50606ac84110b7fd83` |
| Core source | `120978646e4c8bae2707ddfc6b31512a4a0c76c8` |
| formal Base config | `configs/dtc_l1/m5/PAPER_BASE_16KB.config`, SHA-256 `993513296458bf014cfa33ff047e1ed7391a1fee990e3b4a2d9d738cab0ff366` |
| host snapshot | 512 logical CPUs; load `58.54/59.14/59.42`; 149 GiB MemAvailable; `vmstat` si/so `0/0`; no active swap thrashing; 69 GiB free on `/tmp`/output filesystem; root overlay is nevertheless 98% used |

## Q1 — static common-path result

The trace frontend does not introduce an alternate LD/ST timing unit. A trace
instruction is a `warp_inst_t`, and a trace shader core is a
`shader_core_ctx`; after trace parsing, it invokes the base shader issue path.
The DTC decision points below are consequently reached through the same
`ldst_unit` implementation used by execution-driven mode, subject to the
trace record satisfying the semantic contract.

| lifecycle point | source-backed path |
| --- | --- |
| Trace record and dynamic warp representation | Framework `gpu-simulator/trace-parser/trace_parser.h:81-113` defines `inst_trace_t` (CTA, PC, mask, opcode, registers, per-instruction memory record). `trace_driven.h:65-93` makes `trace_warp_inst_t` a `warp_inst_t`. |
| Parse active lanes, opcode, address and memory semantics | `trace_parser.cc:150-326` decodes PC, 32-bit active mask, opcode and per-active-lane addresses (including list/stride/delta encodings). `trace_driven.cc:253-455` copies mask and lane addresses, identifies LD/ST/atomic opcode classes, selects global/local/shared space, and preserves `CACHE_ALL` versus source-marked `CACHE_GLOBAL` bypass. |
| Trace core to normal timing issue | `trace_driven.h:222-260` derives `trace_shader_core_ctx` from `shader_core_ctx`; `trace_driven.cc:1142-1155` generates normal memory accesses and `:1158-1165` calls `shader_core_ctx::issue_warp`. |
| Common coalesced access queue and mode selection | Core `src/gpgpu-sim/shader.cc:3715-3825`, `ldst_unit::memory_cycle`, consumes `warp_inst_t::accessq`; it determines cache bypass from `cache_op` and routes cacheable loads to IO (`:3762-3765`) or OO (`:3766-3769`). |
| Base PIB and Tag arbitration | `shader.cc:3452-3479` admits/retire Base UIDs and calls `paper_frontend::try_serve_tag`; the conventional Base L1 access point calls `dtc_l1_try_tag` at `:2511-2557`. |
| IO/OO PIB, Tag, physical allocation and merge/lower ownership | IO: `shader.cc:2929-3043` calls `io_frontend::admit`, `try_serve_tag`, and `access`, then owns a lower request only after `dtc_l1_try_acquire_lower_request`. OO: `:3180-3314` analogously calls `oo_frontend::admit`, `try_serve_tag`, `access`, and the same global-credit acquisition. The typed frontend implementations are in `src/gpgpu-sim/dtc-l1-common.h:105-230` (IO) and `:374-510` (OO). |
| Fill/wakeup and IO/OO retirement | IO response identity/complete path is `shader.cc:3045-3121`; OO is `:3315-3385`. Both complete the physical record, release one lower credit, close dependencies, call `warp_inst_complete`, and retire their frontend entry. |
| Pending writes and scoreboard | Issue records cardinality in `shader.cc:4219-4270`. IO close asserts/removes the exact pending count and releases the scoreboard at `:3085-3121`; OO does the same, including zero-after-close assertion, at `:3351-3385`. Trace warp completion also requires `!m_scoreboard->pendingWrites(warp_id)` in Framework `trace_driven.cc:1042-1056`. |

### Trace semantic-contract audit

| required information | result | source |
| --- | --- | --- |
| dynamic instruction grouping and warp/CTA identity | preserved | `inst_trace_t` CTA/cluster fields; per-warp stream construction in `trace_driven.cc:1066-1113` |
| active mask | preserved | parser mask at `trace_parser.cc:184-186`; `set_active` at `trace_driven.cc:263-265` |
| opcode and load/store class | preserved for supported SASS opcode map | opcode parse `trace_driven.cc:293-317`; LD/ST mapping `:387-421` |
| global/local/shared space | preserved for explicit supported opcodes | `trace_driven.cc:387-454` |
| per-lane addresses and access width | preserved, including compressed encodings | parser `trace_parser.cc:280-326`; copied at `trace_driven.cc:367-372` |
| read/write and cache/bypass semantics | preserved for `LDG`/`STG` and source `STRONG.GPU`/`BYPASS`; atomics deliberately route `CACHE_GLOBAL` | `trace_driven.cc:387-430`; Core bypass/DTC eligibility `shader.cc:3738-3769` |

Paper-10's simple cacheable global loads/stores are therefore a plausible
contract match. Atomics, unsupported ordering, and unsupported cache-control
encodings are not silently eligible: they must be checked per trace and are
explicitly not a reason to generalize a pilot result.

### Why no Q1 simulation was admitted

No exact, provenance-compatible trace for completed BICG, canonical SpMV,
GESUMMV, or 2DConv was found in the local trace inventory. The only relevant
PolyBench trace material found is a fractional ATAX artifact whose manifest
names `polybench/11.0/polybench-atax`, but selects one CTA from a `(16,1,1)`
grid and has no frozen M5 source/input identity. ATAX is also one of the five
currently live M5.0B jobs. It is inadmissible as an M5.0BF formal-pilot
substitute and was not replayed.

The existing `/tmp/dtc-l1-framework-build/accel-sim.out` was built from the
M1--M4 Framework/Core worktrees, not either M5.0BF source SHA, and was not
used. CUDA 11.8 is installed, but this host has neither `nvidia-smi` nor a
visible `/dev/nvidia*` device, so a fresh NVBit trace cannot be generated here.
Accel-Sim's own tracer requires an NVBit-equipped GPU execution to emit the
trace (`util/tracer_nvbit/README.md` and `run_hw_trace.py`).

The Framework checkout does not carry `gpu-simulator/extern/pybind11` in its
tree or a `.gitmodules` entry. The isolated build therefore uses an ignored
read-only symlink to the already-present local pybind11 checkout at
`d87cf0b873e42f0e541a4be9b29ea4b2681148ed` (pybind11 3.1.0); this auxiliary
binding dependency does not alter Core, config, trace, or simulator semantics.
The missing local zstd development link was built from the already-present
zstd 1.4.8 source in `/tmp`; the resulting executable dynamically resolves the
host's same-version `libzstd.so.1`.

The isolated CMake cache proves the requested Framework/Core sources
(`08dad4c3...` / `12097864...`) were selected. The build completed successfully
at `/tmp/dtc-l1-m5-0bf-build/accel-sim.out` (SHA-256
`5b26b8a1e6390596eb449ddcefc4c5a2fbad0ddd1bb85b8396bf90b3ae2fb2c6`). Its
startup banner identifies Core `12097864`; invoking unsupported `--help`
exited before any simulation and produced no trace/result artifact. This CMake
configuration registers zero CTests, so that fact is recorded as build
inventory rather than a passing test claim. The binary is ready only for an
admissible isolated trace pilot.

Thus Q1 remains **PILOT-BLOCKED BY MISSING ADMISSIBLE TRACE INPUT / GPU TRACE
EXECUTION**, rather than falsely declaring either formal trace validity or a
source-semantic failure. The next admissible Q1 action is an isolated build
and Base/IO/OO replay of an exact completed Paper-10 trace with frozen
source/input/tracer/parser/config identities. Q3 is correspondingly not
started: it is Base-only, but the authorization requires it to follow trace
path viability.

## Q2 — 80-SM platform lineage

The M5 Base config was added by Framework commit
`a5b1084520a8d06ef032469e538a545c8c6f8fe4` (2026-09-03). A byte-level diff
shows it is the Core's `configs/tested-cfgs/SM7_QV100/gpgpusim.config` with
the M5 frozen-L1/DTC edits: adaptive cache disabled, 16 KiB L1 variants,
ratio-zero policy, and DTC mode. It retains the SM7 platform's
`-gpgpu_n_clusters 80`, `-gpgpu_n_cores_per_cluster 1`, 32 MCs and two
subpartitions/MC. Core blame traces the 80-cluster value through `SM7_V100`
commit `fe6506a14` (2019-05-06); the source config labels it a Volta Quadro
V100 model.

This establishes why 80 SM entered M5: **it is an inherited modern-SM7
platform setting, not a DTC or thesis-platform derivation.** The researcher
has authorized it as the primary formal candidate but that authorization does
not freeze it until Q3's Base-only lower-cap evidence closes.

| dimension | 80-SM inherited platform consequence |
| --- | --- |
| occupancy and wall time | CTA distribution, scheduler population, and simulator work scale with `n_simt_clusters`; source creates/iterates that many core clusters in `src/gpgpu-sim/gpu-sim.cc:1054-1068` and throughout simulation scheduling. |
| aggregate lower pressure | the current DTC lower cap is global (`gpu-sim.cc:1328-1362`), so `80 SM + 256` gives only 3.2 credits/SM and is diagnostic-only `CURRENT_INVALID_SUSPECT`. |
| proportional researcher rule | thesis platform = 2 SM; 256 / 2 = 128 credits/SM. Therefore primary `80 SM + 10240`, sensitivity `64 SM + 8192`, and thesis anchor `2 SM + 256` are the only stated proportional combinations. |
| native downstream provisioning | retained SM7 values are 32 MC x 2 subpartitions, 6 MiB L2 (`S:32:128:24`), L2 queue tuple `64:64:64:64`, ICNT buffers 512, DRAM schedule queue 64 and return queue 192. These bounded queues must be observed in Q3 rather than replaced by the synthetic cap. |
| comparability | existing 80-SM/cap-256 M5.0B results remain execution-driven mechanism/provenance anchors only. Their counters are not reusable formal results under a newly frozen cap or SM count. |

## Required continuation and join status

M5.0B remains independently active. M5.0BF has not started a simulation and
has no new correctness, deadlock, pending-write, or scoreboard failure. The
M5.0C join remains closed until both M5.0B natural-terminal/provenance closure
and an accepted M5.0BF terminal path/platform decision are present.
