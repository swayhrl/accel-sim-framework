# M5 formal platform/config knob map

Status: `M5.0C_PRELIMINARY_SOURCE_AUDIT`.  This map is current for Core
`ddb9aac59cd1f6c80d7990b8bb9ec173d4819680`; it is preparation evidence, not
an M5.0C PASS declaration.  The M5.0B corrected Base batch must finish before
the platform handoff can close.

## Committed formal configuration family

All four files derive from the same SM7 platform configuration.  They differ
only in `-gpgpu_dtc_l1_mode`; every other byte is identical.

| Configuration | Mode | SHA-256 |
| --- | ---: | --- |
| `configs/dtc_l1/m5/LEGACY_16KB.config` | 0 | `e49453b37d2bc430abf9bc56caf1f1a10e7d665cd5b9d24f7f919fd65f1f1970` |
| `configs/dtc_l1/m5/PAPER_BASE_16KB.config` | 1 | `993513296458bf014cfa33ff047e1ed7391a1fee990e3b4a2d9d738cab0ff366` |
| `configs/dtc_l1/m5/PAPER_IO_16KB.config` | 2 | `5efe4113415732a83366949d5aaaf4863848d5f7f2f606d4a4e36e1246ad87a5` |
| `configs/dtc_l1/m5/PAPER_OO_16KB.config` | 3 | `9fdad38d8bba8967b177596858761580f7fde50ec15dbc68df3495fdb7cf42ea` |

The old temporary config `5ca33d...` is not formal: its adaptive path emitted
`Reconfigure L1 cache to 128KB`.  M5-T004 records the root cause and
invalidation.  The four new files set `-gpgpu_adaptive_cache_config 0` and
`-gpgpu_cache:dl1 S:32:128:4,...`; the cache parser computes capacity as
`sets * line_bytes * associativity`, hence 32 × 128 × 4 = 16 KiB. The
`dl1PrefL1` and `dl1PrefShared` variants duplicate that exact geometry so a
CUDA per-function cache preference cannot silently select `none` or another
capacity. The fresh LEGACY/Base/IO/OO VecAdd checks all PASS without a resize
message.

## Frozen DTC values and source path

The config files deliberately leave DTC dimensions at the Core's M5 defaults.
`shader_core_config::reg_options` in `src/gpgpu-sim/gpu-sim.cc` registers
these values; `ldst_unit::init` in `src/gpgpu-sim/shader.cc` transfers them to
the selected paper frontend.

| Knob / behavior | Base | IO | OO | Evidence |
| --- | ---: | ---: | ---: | --- |
| Conventional L1D | 16 KiB, 32×128B×4-way | identical unrelated L1D config | identical unrelated L1D config | formal config family; adaptive resize disabled |
| Base PIB / L1 MSHR | 8 / 32 | n/a / not DTC capacity | n/a / not DTC capacity | defaults in `gpu-sim.cc`; Base-only `override_mshr_entries` in `shader.h` |
| DTC PIB | n/a | 256 | 128 | `dtc_l1_io_pib_entries`, `dtc_l1_oo_pib_entries` defaults |
| Logical Tag geometry | n/a | 32 sets × 4 ways × 128B = 16 KiB | same | `dtc_l1_logical_sets=32`, `logical_ways=4` |
| Physical cacheline pool | n/a | 640 × 128B = 80 KiB | same | `dtc_l1_physical_lines=640` |
| Physical allocation width | n/a | 4/cycle | 4/cycle | `dtc_l1_allocation_width=4` |
| Tag service | 4 banks, 1/bank/cycle, 4 total/cycle | same | same | defaults plus all three `try_serve_tag` implementations in `dtc-l1-common.h` |
| Global DTC lower cap | 256 | 256 | 256 | `gpgpu_sim::dtc_l1_try_acquire_lower_request` |
| Lower issue width | conventional cache path | 1 request/SM/cycle | 1 request/SM/cycle | one-front-item issue block in `dtc_l1_io_issue_lower_requests` / `dtc_l1_oo_issue_lower_requests` |
| Retire width | conventional path | FIFO head, 1/cycle | oldest ready, 1/cycle | DTC frontend and LD/ST retirement source |
| Ref count width | n/a | n/a | 13 bits | `dtc_l1_ref_count_bits=13` |

`MODERN_OO_SECTOR` is not represented in this family and is excluded from
paper-mode M5 figures.

## Common platform and downstream model

These values are byte-identical across the four formal configs:

- 80 clusters × 1 core (`-gpgpu_n_clusters 80`,
  `-gpgpu_n_cores_per_cluster 1`), four L1 banks, L1 latency 20 cycles, and
  global-memory L1 bypass disabled. The paper-facing conventional-L1 policy
  explicitly sets `-gpgpu_l1_cache_write_ratio 0` in all four files. This is
  the researcher-approved M5-T005 correction: it preserves the frozen
  16 KiB/4-way geometry and write-through/allocation semantics while removing
  the inherited SM7 25%-global-dirty retention heuristic. Ratio-25 controls
  remain diagnostic only.
- 32 memory controllers × 2 subpartitions, 6 MiB L2
  (`S:32:128:24` per subpartition), L2 queue tuple `64:64:64:64`, and
  FR-FCFS DRAM scheduling queue 64 / return queue 192.
- Interconnect in/out buffer limits 512, clock domains
  `1132:1132:1132:850`, and `-gpgpu_coalesce_arch 70`.

The global DTC cap is not the only lower bound.  In
`l2cache.cc`, a subpartition's shared credit limit is computed from the
configured DRAM scheduler and return queues: `64 + 192 - (2 - 1) = 255`.
The DRAM scheduler enforces its configured 64-entry queue and the return FIFO
is bounded to 192.  These are source-reachable downstream/platform limits;
they remain frozen rather than being tuned for a DTC result.

The DTC whole-line modes consume the already-coalesced access queue and group
128B references; they do not create lane transactions or use conventional L1D
MSHRs as DTC merge capacity (`dtc-l1-common.h::group_128b_references` and the
IO/OO LD/ST paths).  This distinguishes the upstream coalescer/transaction
geometry from the DTC logical Tag and physical-line model.

## Tag-bank equivalence finding

The Base `paper_frontend`, IO `io_frontend`, and OO `oo_frontend` each map
`(address / 128B) % logical_sets` to `set % tag_banks`, reset their per-cycle
service state, and reject a request at either the aggregate-four or
per-bank-one limit.  IO's source comment explicitly states the same frozen
contract as Base; OO uses the same arithmetic and predicates.  Therefore the
previous Base-vs-IO discrepancy in observed conflict counts is not treated as
different configured Tag-bank service.  It remains an M5.0E behavior question
about request timing/instrumentation, to be tested on a corrected workload
triplet; Tag-bank conflicts will remain diagnostic rather than a paper
Tag/cacheline-allocation stall.

## Required closure evidence before M5.0C PASS

1. Corrected M5.0B Base smoke must close for every recovered workload.
2. A corrected full-workload Base/IO/OO triplet must confirm identical
   unrelated platform identity and report the common service/invariant fields.
3. The M5.0C handoff must list this natural downstream-cap chain and any
   resulting platform limitation without changing it.
