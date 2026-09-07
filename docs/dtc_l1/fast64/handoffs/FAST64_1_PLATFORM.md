# FAST64.1 — Platform and Payload Lock

Status: **ACTIVE_HARD_EXECUTION_FAILURE; R1 QUALIFICATION NOT PROMOTABLE**

This is an active recovery checkpoint, not a FAST64.1 PASS artifact. No
FAST64.2 work may begin from it.

## Authority and reproducibility

| item | identity |
| --- | --- |
| prior stage | `FAST64_0_PIVOT_PASS` at Framework `c02ea2259e4bc6ee0ee026734aa60e561ea79724` |
| `MECHANISM_BEHAVIOR_ANCHOR` | `15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9` |
| `FAST64_FORMAL_INSTRUMENTED_CORE` | `bbcbb5e7565417102087bc80b14c349b4e568c05` |
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

The original-Core qualification set in `/workspace/fast64-runs/` remains
`PRE_REPAIR_TELEMETRY_INCOMPLETE_ANCHOR`, not formal FAST64.1 evidence.  At
the 2026-09-07T08:27:49Z review snapshot, BICG OO at both 8192 and 1048576
had naturally exited zero and five other original-Core rows remained live.
Both terminal OO anchors have correct payload/config identity, no scanned
assertion/fatal/deadlock/output error, and closed lower/dependency/drain
state, but cannot close the candidate-cap HARD gate because the old runtime
lacks the required OO lower-cap-full telemetry.  Their processes and raw
namespaces remain untouched.  The compact, reviewable inventory is
`handoffs/FAST64_1_PROGRESS_CHECKPOINT.md`.

`util/dtc_l1/deferred_fast64_1_telemetry_rerun.sh` remains a preserved
fail-closed historical controller. It waits for old rows and therefore is not
the active r1 scheduling authority. Resource-safe independent r1 dispatch is
performed by `util/dtc_l1/dispatch_fast64_1_telemetry_rerun_now.sh`, which
requires the formal Core/runtime identity and all target namespaces to be
absent before exact new-Core launch. Both paths fail closed on an existing
target; neither contains a timeout, kill, overwrite, renice, debugger, or
cleanup action.

### Controller metadata correction — `FAST64-1-CTRL-001`

The BICG Base/IO/OO 8192-cap replacement rows always invoke the corresponding
`FAST64_*.config`, whose resolved final lower-cap setting and recorded SHA
identify cap 8192.  Their detached controller's human-readable supervisor TSV
field was discovered to be initialized as `64`; that field is not an input to
the launch command and cannot alter the simulator/configuration.  The
checked-in controller now records `8192`.  The already-running controller is
deliberately not restarted while it preserves live pre-repair rows, so a later
`64` value in only that sidecar TSV must be treated as non-authoritative and
regenerated from `RUN_MANIFEST.tsv` plus the config SHA.  The strict validator
requires the latter identities and will reject any different configuration.

## FAST64.1 HARD checklist

Counter interpretation is stage-specific: FAST64.1's
`DTC_L1_lower_cap_full_events` is the global lower-outstanding-cap gate.
FAST64.2's `DTC_L1_io_lower_create_queue_full_stalls` and
`DTC_L1_oo_lower_create_queue_full_stalls` are bounded lower-create candidate
queue backpressure. Neither is a Tag-bank conflict solely because an internal
retry uses `BK_CONF`.

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
| 8192 non-binding versus high cap; global cap-full events zero on every 8192 candidate row | PENDING new-Core BICG Base plus BICG IO/OO and GESUMMV IO pairs |
| Core/runtime/config/observer provenance | PASS for completed rows; PENDING replacement rows |

## Next executable action

The pre-repair anchors remain live, untouched supporting evidence. Launch the
isolated r1 rows under `bbcbb5e…` when the dynamic resource gate passes;
validate them with the strict row validator and close the lower-cap comparison
before considering FAST64.1 PASS.

The dynamic resource gate passed and all seven r1 rows were dispatched at
`2026-09-07T08:49:18Z`; their exact source/runtime/config/payload manifests
and active PID inventory are recorded in `FAST64_1_PROGRESS_CHECKPOINT.md`.
This does not change the ACTIVE/PENDING gate state.

## r1 execution-path contamination (2026-09-07)

`fast64_1r1_bicg_oo_cap8192_a1` has two observed simulator execution epochs
in one exactly-once namespace.  It lacks the mandatory terminal status and
cannot participate in the BICG OO candidate/high comparison.  This is an
execution/controller failure, not a DTC mechanism result; the precise
read-only evidence and fail-closed recovery boundary are in
`FAST64_1_R1_EXECUTION_PATH_CONTAMINATION.md`.  No FAST64.1 PASS or FAST64.2
promotion is allowed while this HARD item remains unresolved.  Future recovery
dispatch uses the separately added atomic-namespace v2 runner; it does not
alter a currently mapped historical runner or launch a replacement row.
