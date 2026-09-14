# CM1 — TC80 canonical configuration lock

Status: **PASS — one primary configuration is locked before TC80 execution**

The only new primary configuration is
[`config/TC80_CAPACITY_MATCHED_OVERLAY.config`](config/TC80_CAPACITY_MATCHED_OVERLAY.config).
It is applied *after*, never instead of, frozen
`configs/dtc_l1/fast64/FAST64_BASE.config`, and before the frozen
`SM7_QV100/trace.config`.  The runtime command is therefore:

```text
<formal-runtime> -trace <frozen-kernelslist.g> \
  -config configs/dtc_l1/fast64/FAST64_BASE.config \
  -config docs/dtc_l1/iscas2027/tc80/config/TC80_CAPACITY_MATCHED_OVERLAY.config \
  -config gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config
```

The overlay makes exactly four resolved changes, enumerated in
[`CM1_B16_VS_TC80_RESOLVED_CONFIG_DIFF.tsv`](CM1_B16_VS_TC80_RESOLVED_CONFIG_DIFF.tsv).
Three change the possible L1D preference strings from 32×4 to 32×20; the
fourth changes `-gpgpu_unified_l1d_size` to the required divisible 80 KiB.
Every change is capacity geometry or mechanically derived from it.  No
alternative TC80 geometry or configuration is authorized.

The static frozen-field audit is
[`CM1_FROZEN_FIELD_AUDIT.tsv`](CM1_FROZEN_FIELD_AUDIT.tsv).  In particular,
the effective conventional MSHR remains 32 because PAPER_BASE explicitly
overrides the `-gpgpu_cache:dl1` parser's `A:512` value with the inherited
`-gpgpu_dtc_l1_mshr_entries 32`; the Base PIB remains 8; L1 latency remains
20 cycles; the four banks and 32-B data-port width remain unchanged.

The command's startup configuration echo and the final `DTC_L1_mode =
PAPER_BASE` report are mandatory CM2/CM3 evidence.  The validator computes
the complete geometry from the echoed tuple and rejects a run unless it is
exactly `32 × 20 × 128 = 640 lines = 81,920 B`.  It also rejects an IO/OO
mode/counter family, so an inherited physical-pool option cannot become
scientifically active by accident.

The canonical static final-option map is
[`config/TC80_RESOLVED_EFFECTIVE_CONFIG.tsv`](config/TC80_RESOLVED_EFFECTIVE_CONFIG.tsv).
Its SHA-256, the overlay SHA-256, parent/config parser SHA-256s, and the
launch-controller SHA-256 are recorded in
[`CM1_CONFIG_SHA256.tsv`](CM1_CONFIG_SHA256.tsv).  The runtime echo remains
the mandatory dynamic confirmation in CM2/CM3.

No Core source, observer, simulator build, trace, FAST64 result, Lane-E
artifact, or accepted scientific input was changed by CM1.
