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
| `configs/dtc_l1/m5/LEGACY_16KB.config` | 0 | `462703a8c083f8442da1b67bc74a92ad3441aefac9953b8b69f784e9238702cc` |
| `configs/dtc_l1/m5/PAPER_BASE_16KB.config` | 1 | `96621d2899d26d939afbf4eb8a9f0f303629263adf1c42c65743f60cda90b634` |
| `configs/dtc_l1/m5/PAPER_IO_16KB.config` | 2 | `10d3da49675afdc90ed142f190cdd6de0cef3acca57afac9741e4eef8b09e8e8` |
| `configs/dtc_l1/m5/PAPER_OO_16KB.config` | 3 | `0005c35015730e50de5af6933ef7f9f88763e47cf838043ab8c6901dc0d026dc` |

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
  global-memory L1 bypass disabled. The inherited SM7
  `-gpgpu_l1_cache_write_ratio 25` remains frozen; it is source-reachable
  conventional-L1 dirty-victim behavior, not a DTC knob. M5-T005 records a
  16 KiB/4-way deadlock caused by that policy and requires a researcher
  decision rather than a silent tuning change.
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
