# DTC-L1 configuration knob map

Status: `M1_IN_PROGRESS`; this is an evidence map, not a declaration that all
listed modes are implemented.

## Current Core option surface

| Option | Default | Current status | M0 role |
| --- | ---: | --- | --- |
| `-gpgpu_dtc_l1_mode` | `0` | implemented: `0=LEGACY`, `1=PAPER_BASE`; modes 2–4 reserved | variant selection |
| `-gpgpu_dtc_l1_pib_entries` | `8` | implemented for Paper Base admission | Baseline PIB depth |
| `-gpgpu_dtc_l1_mshr_entries` | `32` | implemented: overrides only Paper Base's traditional L1 MSHR capacity | Baseline MSHR depth |
| `-gpgpu_dtc_l1_lower_outstanding_cap` | `256` | implemented: global Paper Base token cap, acquired on L1 new-miss commit and released on final L1 fill | 8-SM lower outstanding cap |
| `-gpgpu_dtc_l1_tag_banks` | `4` | implemented for Paper Base Tag arbitration | Tag-bank count |
| `-gpgpu_dtc_l1_tag_req_per_bank` | `1` | implemented for Paper Base Tag arbitration | per-bank throughput |
| `-gpgpu_dtc_l1_tag_req_per_cycle` | `4` | implemented for Paper Base Tag arbitration | aggregate Tag throughput |
| `-gpgpu_dtc_l1_logical_sets` | `32` | implemented for `logical_set % tag_banks` mapping | 16KB/4-way logical Tag geometry |

These options are registered by
`src/gpgpu-sim/gpu-sim.cc:shader_core_config::reg_options` and consumed by
`src/gpgpu-sim/shader.cc:ldst_unit`.  With mode `0`, the DTC frontend is
disabled and no DTC admission, Tag arbitration, or DTC stats path is active.

## Existing baseline options retained unchanged

The project deliberately keeps the existing Core controls as the source of
truth for conventional cache behavior: `-gpgpu_cache:dl1`,
`-gpgpu_l1_banks`, `-gpgpu_l1_latency`, and
`-gpgpu_gmem_skip_L1D`.  PAPER_BASE alone applies its dedicated 32-entry
default to the existing traditional L1 MSHR; this is not an IO/OO DTC merge
capacity and LEGACY leaves the configured L1D MSHR untouched.

## Required later additions

The following frozen parameters remain unimplemented and must be added before
their corresponding stage can pass: physical capacity/allocation width and
policy, IO/OO PIB and retirement controls, lower-request issue width,
Ref Count width/checker, sector mode/count/size, debug-event filtering, and
no-progress watchdog controls.

Do not infer a paper result from the currently implemented M1 controls alone.
