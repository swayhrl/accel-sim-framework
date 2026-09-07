# FAST64.1 — Platform and Payload Lock

Status: **ACTIVE_TELEMETRY_RERUN_PENDING**

This is an active recovery checkpoint, not a FAST64.1 PASS artifact. No
FAST64.2 work may begin from it.

## Authority and reproducibility

| item | identity |
| --- | --- |
| prior stage | `FAST64_0_PIVOT_PASS` at Framework `c02ea2259e4bc6ee0ee026734aa60e561ea79724` |
| original Core anchor | `15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9` |
| current Core authority | `bbcbb5e7565417102087bc80b14c349b4e568c05` |
| Core change disposition | telemetry-only repair `FAST64-1-TELE-001`; source and NN regression in `FAST64_1_TELEMETRY_RESOLUTION.md` |
| current formal runtime | `/tmp/dtc-fast64-telemetry-build-sEWez4/accel-sim.out`, SHA `6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041` |
| observer | A1, `-gpgpu_runtime_stat 500000`; overlay SHA `2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e` |
| payload manifest | `generated/FAST64_PAYLOAD_MANIFEST.tsv` and `generated/FAST64_PAYLOAD_MEMBERS.tsv` |
| resolved config diff | `generated/FAST64_RESOLVED_CONFIG_DIFF.tsv`, exactly one Base/IO/OO difference: required mode selector |

Resolved 8192-cap config SHA-256 values:

| Base | IO | OO |
| --- | --- | --- |
| `1a016e3cac65376330a92dd3fcf037d5fdcab5e7d295920be568e04600dd1cde` | `d4a2d9d0088946b950370b922a8d8e34422bbca9bac26f109b3977fe02a7f621` | `546c68f96d47f4650703ccfbc925bd789f923501d5607a77e79ca4845f234caa` |

The non-binding high-cap overlays have SHA-256:

| Base | IO | OO |
| --- | --- | --- |
| `fcef53355c61dea6f141a8e0d3a2608c5a69cb1b37181d468e3022edfeafc12d` | `c0d169b83f4b30c2e19c77a83a67789e0733df20ea0da94525c37e194adc44ae` | `b9c8716bffb4c35dad31f568fd9288e2bb6cbda995997a9912ff2b3ddab5b6d6` |

Each high-cap config differs from its 8192 counterpart only at the terminal
lower-cap overlay line.

## Completed evidence

- The frozen FAST12 payload set was hashed before any accepted FAST64 IO/OO
  performance result: 12 workloads, 629 ordered trace members, 9,162,136,500
  bytes.
- Original-Core NN Base/IO/OO smoke rows naturally terminated and strict
  parsed; compact evidence is `generated/nn_smoke/`.
- New-Core NN Base/IO/OO telemetry regression naturally terminated, consumed
  the frozen NN trace exactly, strict parsed, and has compact raw-log bindings
  under `generated/telemetry_regression/`.
- New-Core equivalence is exact in cycles, instructions, and every old
  parser-visible DTC/cache/traffic field. The only new field is OO
  `DTC_L1_lower_cap_full_events = 0`.
- The platform shell is directly runtime-echoed as 64 clusters x 1 core, 20
  memory partitions, 16-KiB/4-way/128-B DTC Base, and no C2P peer/cache
  mechanism or 64-KiB/32-way L1 option is present.

## Live preservation and recovery state

Seven original-Core qualification rows are still live in
`/workspace/fast64-runs/`: BICG Base, IO/OO at 8192 and 1048576, plus GESUMMV
IO at 8192 and 1048576. They are
`PRE_REPAIR_TELEMETRY_INCOMPLETE_ANCHOR`, not failures; their processes and
raw namespaces remain untouched.

`util/dtc_l1/deferred_fast64_1_telemetry_rerun.sh` is an isolated,
fail-closed controller. It requires every old row to naturally exit zero, the
current Core SHA and runtime SHA to match this handoff, and all target
namespaces to be absent before dispatching exact new-Core replacements. It
contains no timeout, kill, overwrite, renice, debugger, or cleanup action.

## FAST64.1 HARD checklist

| HARD item | state |
| --- | --- |
| resolved Base/IO/OO configs build and launch | PASS (new-Core NN triplet) |
| NN and BICG smoke natural terminal in all modes | PENDING BICG new-Core replacements |
| no assertion/fatal/trace error/deadlock | PENDING terminal validation |
| terminal accounting drains | PASS for NN; PENDING BICG/GESUMMV replacements |
| 64x1 shell and frozen DTC geometry | PASS |
| no C2P 64-KiB/32-way or peer mechanism | PASS |
| machine-readable diff has no unrelated mode difference | PASS |
| all FAST12 payload identities frozen | PASS |
| 8192 non-binding versus high cap | PENDING new-Core BICG IO/OO and GESUMMV IO pairs |
| Core/runtime/config/observer provenance | PASS for completed rows; PENDING replacement rows |

## Next executable action

Allow the pre-repair anchors to finish naturally. The deferred controller will
then dispatch replacements under `bbcbb5e…`; validate them with the strict row
validator and close the lower-cap comparison before considering FAST64.1 PASS.
