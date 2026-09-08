# C5 execution preflight — blocked before execution

Status: `NOT_EXECUTABLE`; this document is a preflight result, not C5
authorization. No C5 workload has been launched.

## Validated runtime identity

| Item | Frozen identity |
| --- | --- |
| Framework | `b092650350ea0ddc9ce7c97a5fd79cdfcb67381c` |
| Core | `5b4094931910cd3bb9b30df47a552eb0ae596983` |
| binary SHA-256 | `74307f3a9b975300e469a7768be1324444c927498e3b19d40d39dc326df31345` |
| runtime binding | external `GPGPUSIM_ROOT=/workspace/worktrees/gpgpu-sim-vm-m4b-speculative` |
| bounded decode1 trace-list SHA-256 | `4cbb1b9e9a25cf3e933b7bcfee6fed689cac0566ae799e7e874b185eba4d0e8a` |
| decode1 V2 registration SHA-256 | `690ad04b2935e01c7bf98922fa51d6b291cd6dcfa7c7882a65ae3d4ce8deafce` |
| bounded decode1 F8 config SHA-256 | `d8c61e734e8bc7191e3a6586d669db63875c2d9a2d18f6fcef55b345bfaecf85` |

The bounded decoder configuration and registration prove current C10 runtime
plumbing only. They are not a formal C5 result and may not be numerically
mixed with C4 or Window-A evidence.

## Frozen C9 arm matrix for a later C5 authorization

The minimum fair matrix is `F0`, `F1`, `F2`, `F5`, `F7`, `F8`, and `F9`.
`F1` and `F8` retain `REFERENCE_APPROX_SUBENTRY_16`; `F7` and `F8` retain
`SPECULATIVE_CANDIDATE`. `F7`/`F8` must each use every frozen `Lseg=5,10,20`
point. F3 is only an explicitly charged sweep after a point is selected; F4
and F6 are diagnostics and cannot be presented as equal-cost controls; H0 is
permanently rejected. Historical 768-group C2/C4 inputs are excluded.

For each authorized ROI, each arm must record arm ID, charged bits, page
class, exact/group/PWC geometry, Segment replica count, `Lseg`, source heads,
binary hash, config hash, registration hash, trace-list hash, telemetry schema
and parser version. It must also retain Segment/lower-path/requester/PTE/L1D/
L2/queue/DRAM observables and exact-once/conservation checks.

## Required resource/resume discipline

Use `C10B_AGGRESSIVE_PARALLEL_V3`: `MemAvailable >= 32 GiB`, memory full
`<=1%`, I/O full `<=2%`, iowait `<=10%`, and swap-in/out `<=4 MiB/s` over the
10-second preflight. Acquire `/workspace/vm_tlb_post_terminal_heavy_slot.lock`
once for each C batch, record `/usr/bin/time -v`, bind only the declared C
physical-core pool, and release the lock at batch completion. A resumed run
must preserve the same immutable trace/config/registration/binary hashes.

## Blocking missing inputs

No exact prefill C5 command can be written honestly. The only C-side prefill
file is an identity-like V1 map; there is also no immutable C-side prefill
trace-list. Neither is legal input for a C10 Segment arm. The template below
is deliberately non-executable until both fields are supplied; substituting a
V1 map, object map, decode1 descriptor or guessed PA base is prohibited.

```text
REQUIRED BEFORE ANY C5 COMMAND:
  PREFILL_TRACE_LIST_SHA256=<immutable supplied artifact>
  PREFILL_C10_V2_REGISTRATION_SHA256=<driver-owned nonidentity PA artifact>
  PREFILL_ARM_CONFIG_SHA256=<C5-approved fair-arm config>

ONLY AFTER A SEPARATE C5 AUTHORIZATION AND A GREEN V3 PRECHECK:
  accel-sim.out -config <immutable C5 arm config> -trace <immutable ROI list>
```

Because those required values are absent, this preflight establishes
`C10B_HARD_BLOCKER_WITH_EVIDENCE`, not
`C10B_READY_FOR_C5_RESOURCE_GATED_REPLAY`.
