# FAST64.1 — Platform and Payload Lock

Status: **FAST64_1_PLATFORM_PASS**

This is the formal FAST64.1 PASS artifact. Historical r1 evidence remains
superseded/nonformal; the immutable R2 full wave below is the sole
execution-path acceptance evidence.

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
| NN and BICG smoke natural terminal in all modes | PASS |
| no assertion/fatal/trace error/deadlock | PASS |
| terminal accounting drains | PASS |
| 64x1 shell and frozen DTC geometry | PASS |
| no C2P 64-KiB/32-way or peer mechanism | PASS |
| machine-readable diff has no unrelated mode difference | PASS |
| all FAST12 payload identities frozen | PASS |
| 8192 non-binding versus high cap; global cap-full events zero on every 8192 candidate row | PASS |
| Core/runtime/config/observer provenance | PASS |

## Immutable R2 closeout (2026-09-10)

The full seven-row immutable R2 wave is the formal FAST64.1 execution-path
evidence. Every row naturally exited `0`, has one atomic immutable attempt
UUID and one natural-exit epoch, and binds formal Core
`bbcbb5e7565417102087bc80b14c349b4e568c05`, runtime
`6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041`,
A1 observer `2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e`,
scientific Framework snapshot `037f008b330eb230353b60edf126d6be9f45afdc`,
the frozen payload manifest, and the resolved configuration SHA recorded in
its compact JSON. The normal error scan and all required lower/dependency/drain
closures pass.

The three R2-vs-R2 candidate/high comparisons are exact metric matches:
BICG/IO, BICG/OO, and GESUMMV/IO. Every required 8192 candidate has
`DTC_L1_lower_cap_full_events = 0`, establishing that cap 8192 is non-binding
for FAST64.1; platform, payload, and the 64x1 DTC configuration lock are
unchanged.

The frozen closeout controller is retained as negative controller evidence,
not a scientific disqualification. Its unmodified validator counts the normal
`perf_counter.csv.gz` symlink alias as a second stream and fail-closes on
"single-epoch proof requires one perf stream, found 2". The future-only
alias-v2 reader verifies the optional alias resolves exactly to one canonical
timestamped perf stream; it does not relax single-epoch validation or change
simulator mechanism, runtime, config, payload, or results. The compact evidence
and SHA manifest are under `generated/qualification_r2_full_wave_alias_v2/`.
The obsolete frozen monitor was then stopped after its final retained log was
secured (`/workspace/fast64-runs/fast64_1_r2_closeout.log`, SHA-256
`f3c1cd810d4d86d6a62274655b855967e6994abb84b850d1f84e65f7ba545ea2`).

## Next executable action

Enter FAST64.2. Reuse exact-identity R2 normal-triplet evidence only where the
contract permits. The existing coupled positive-stress attempts remain strict
negative pressure evidence; inspect the source path and construct the smallest
source-correct immutable diagnostic that can observe the required binding
lower-cap/create-queue pressure without changing DTC mechanism semantics.

## r1 execution-path contamination (2026-09-07)

Both BICG OO r1 cap rows have two observed execution epochs and are
`INVALID_EXECUTION_PATH_CONTAMINATED`; the remaining r1 rows are
`LEGACY_R1_EXECUTION_PATH_AT_RISK`.  This is an execution/controller failure,
not a DTC mechanism result.  The precise evidence and immutable dynamic-r2
boundary are in `FAST64_1_R1_EXECUTION_PATH_CONTAMINATION.md`.  No FAST64.1
PASS or FAST64.2 promotion is allowed until the complete r2 wave passes.
