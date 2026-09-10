# FAST64 Sensitivity Configuration Preflight

Status: **FROZEN PLAN — MATERIALIZATION AND EXECUTION GATED BY
`FAST64_2_REPAIR_PASS`**

This is a pre-performance mapping, not a generated-config set and not a
permission to start a sensitivity simulation.  It instantiates the frozen
FAST64.6 roster (`bicg`, `gesummv`, `btree`) and points in
`FAST64_EXPERIMENT_MATRIX.md` using the source-backed DTC controls below.

## Source-backed controls

| experiment dimension | source control(s) | source meaning |
| --- | --- | --- |
| logical Tag capacity | `-gpgpu_dtc_l1_logical_sets`, with 4 ways and 128-B lines fixed | logical Tag geometry supplied to every paper frontend |
| Base logical control | the same logical-set control plus the three `-gpgpu_cache:dl1*` set fields | Base's DTC admission/tag geometry and conventional 128-B/4-way L1 must denote the same capacity |
| DTC physical capacity | `-gpgpu_dtc_l1_physical_lines` | whole-line IO/OO physical-pool entries |
| IO PIB | `-gpgpu_dtc_l1_io_pib_entries` | IO FIFO depth and the source-coupled IO lower-create candidate-queue bound |
| OO PIB | `-gpgpu_dtc_l1_oo_pib_entries` | OO random-access PIB depth and the source-coupled OO lower-create candidate-queue bound |

The control names and meanings are registered in Core
`src/gpgpu-sim/gpu-sim.cc`; the lower-create coupling is in
`src/gpgpu-sim/shader.cc`.  It is therefore explicit that the PIB sweep also
changes the mode's unavoidable candidate-queue headroom.  It must be described
as one mechanism capacity, never misreported as an independent queue-only
sweep.

## Frozen point mappings

### Logical capacity

| label | sets x ways x line | modeled bytes |
| --- | ---: | ---: |
| 16 KiB | 32 x 4 x 128 B | 16,384 |
| 32 KiB | 64 x 4 x 128 B | 32,768 |
| 64 KiB | 128 x 4 x 128 B | 65,536 |

PAPER_IO and PAPER_OO change only `logical_sets` at these points, with the
80-KiB/640-line pool, mode PIB, global lower cap, tag-bank service, and all
other formal controls held fixed.  The supplemental Base control mirrors the
same capacity in its `dl1`, `dl1PrefL1`, and `dl1PrefShared` set fields plus
`logical_sets`; this is one logical-capacity change represented in both source
paths, not independent tuning.

### Physical pool

| label | `physical_lines` | modeled bytes |
| --- | ---: | ---: |
| 16.5 KiB | 132 | 16,896 |
| 24 KiB | 192 | 24,576 |
| 32 KiB | 256 | 32,768 |
| 40 KiB | 320 | 40,960 |
| 48 KiB | 384 | 49,152 |

Apply each point identically to PAPER_IO and PAPER_OO.  Keep logical capacity
at 16 KiB, IO/OO PIB at their primary values, and all unrelated controls
frozen.  Base has no DTC physical pool and is not a physical-pool point.

### PIB capacity

Use the FAST64 frozen points `32, 64, 128, 192, 256`.  At each point set the
IO and OO mode-local PIB control to the *same* entry count; retain logical
capacity at 16 KiB and physical pool at 256 lines (32 KiB), with retirement
width, global cap, Tag service, and all unrelated controls unchanged.  The
IO/OO same-capacity rule is inherited from the frozen M5 sensitivity matrix;
the extra 256 point is explicitly retained by the FAST64 scope.

## Execution and identity rules

1. Do not materialize a sensitivity config or launch a sensitivity row until
   `handoffs/FAST64_2_REPAIR_QUALIFICATION.md` contains the exact canonical
   status header `Status: **FAST64_2_REPAIR_PASS**`.
   `util/dtc_l1/materialize_fast64_sensitivity_configs.sh` enforces this gate;
   its `--plan-only` mode is read-only mapping audit only.
2. Every generated config must have a one-dimensional resolved-config diff
   against its corresponding 16-KiB/640-line/primary-PIB mode identity.
3. Every new row uses formal repaired Core
   `95ccdb7a056f2d53f740d90869785cac6d4ee0f5`, runtime
   `462d105cf28efe98a8a20131fd671f3d28ad374a3e4b5448a597df702cc4dbc9`, A1
   observer, candidate cap 8192, frozen payload identity, and an isolated
   namespace. Historical bbcbb rows retain their literal identity and are not
   silently reused outside the zero-access transition map.
4. Rows retain `PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE` until the logical
   acceptance gates are satisfied.  They cannot alter FAST12 membership,
   primary platform choice, or the primary matrix.
5. Any deadlock is preserved as `EXPECTED_RESOURCE_DEADLOCK` only after
   source-backed no-progress/physical-pressure evidence; no timeout is a
   deadlock classifier.

## Materialized configuration set (2026-09-10)

`sensitivity_frozen_v2` is the sole materialized configuration set.  It
contains all 29 frozen resolved configurations (nine logical, ten physical,
and ten PIB).  Every file preserves lower cap `8192`; each was normalized
against its corresponding Base/IO/OO primary configuration and compared
byte-for-byte after removing only its declared family field(s).  The manifest
`generated/FAST64_SENSITIVITY_CONFIG_MANIFEST_V1.tsv` records the paths and
SHA-256 values.

An earlier `sensitivity_frozen_v1` attempt stopped at the stale standalone
PASS-text assertion before it wrote a configuration file.  It supplies no
configuration or result evidence.  The materializer now tests the canonical
FAST64.2 status header and accepts ordinary horizontal whitespace in the three
Base cache geometry lines.  This is an authority/format repair only: no
sensitivity simulator was launched, and the materialized files remain
`PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE` until their separate execution
and acceptance gates close.

## Authority reconciliation

The original M5 matrix supplies the exact set/line and same-capacity rules;
FAST64 narrows the workload roster to three pre-frozen workloads and includes
the explicit 256-entry PIB point.  The FAST64 plan governs this campaign where
that scope differs; it does not rewrite historical M5 results.
