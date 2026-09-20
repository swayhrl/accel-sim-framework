# CODEX NEXT STAGE — 174 Runtime Activation Forensics + Hit-Path Resume V4

Date: 2026-09-20

Mode:
`GOAL MODE / solve-and-continue`

Node:
`174-new`

Stage:
`AWMA_174_RUNTIME_ACTIVATION_FORENSICS_AND_HITPATH_V4`

Coordination:
`hrl/awma-174-runtime-load-forensics-handoff-v4`

Accepted parent:
`2ae0b7732881f29f5565d84ef1b76bae857a3501`

Suggested execution branch:
`hrl/awma-174-runtime-load-forensics-hitpath-v4`

Read:
1. `REVIEW_174_V3_RUNTIME_MISMATCH_2026-09-20.md`
2. V1 recovered patch/review pack
3. V3 runtime authority/review pack
4. this Goal

## 0. Fresh time authority

At actual launch:
- START_UTC = now
- DEADLINE_UTC = START + 12h
- NO_NEW_SCIENCE_AFTER = DEADLINE - 1h

Do not inherit older deadlines.

## 1. Do NOT run full P34 first

The first task is runtime-load proof.

The V3 result 871,835 + missing coverage marker means a new long run is forbidden until the loaded core image is proven.

## 2. Reconstruct exact launch chain

Recover the exact command/environment used by the accepted repaired requalification and by V3.

Record:
- launcher script;
- executable path;
- LD_LIBRARY_PATH;
- PATH;
- GPGPUSIM_CONFIG;
- CUDA_INSTALL_PATH / GPGPUSIM_ROOT / ACCELSIM_ROOT or equivalents;
- working directory;
- environment variables controlling coverage and target UID.

Produce:
`RUNTIME_LAUNCH_CHAIN.md`

## 3. Identify the real simulator core artifact

Use read-only tooling as appropriate:
- `ldd`
- `readelf -d`
- `readelf -Ws`
- `nm -D`
- `strings`
- `LD_DEBUG=libs`
- `strace -f -e trace=file,process`
- `/proc/<pid>/maps`

Answer:

> Which exact ELF/shared library/executable contains the compiled `shader.cc` / `vm_translation.cc` code used by the run?

Do not assume it is libcudart.

Freeze:
- path;
- SHA256;
- ELF SONAME/build-id;
- resolved load order.

Produce:
`LOADED_CORE_ARTIFACT_AUTHORITY.json`

## 4. Prove repair content exists in the loaded artifact

On the exact loaded core artifact, prove presence of repair content using non-semantic checks where possible:
- `AWMA_VM_COVERAGE` string;
- lookup-override symbol/string;
- relevant symbol evidence where available;
- binary/source build-id mapping.

If the loaded artifact lacks repair content:
this is an engineering failure, not scientific STOP.

Fix build/load path and continue.

## 5. Rebuild using the project-standard build path

The V3 manual partial relink is not sufficient unless proven equivalent.

Locate the normal build system used by this simulator/runtime.

Prefer the existing Makefile/CMake/build script/environment setup used by accepted historical runs.

Build the entire simulator core dependency graph required for the loaded artifact.

Do not manually relink only `shader.cc + vm_translation.cc` unless the build graph proves those are the only required changed objects and the resulting artifact is exactly the one loaded.

Record full build command/log.

Freeze:
- source patch SHA;
- all changed source file SHAs;
- actual core ELF SHA;
- libcudart SHA only as auxiliary evidence;
- config SHA.

Publish durable runtime bundle to node164.

## 6. Runtime-load canary before science

Run the smallest available existing simulator invocation that exercises the same runtime load chain.

This canary does not need scientific performance meaning.

Required runtime evidence:
- loaded core path/SHA matches frozen repaired core;
- coverage marker string exists in loaded core;
- target coverage env var is present;
- no fallback to legacy library path.

If runtime loading cannot be proven:
continue engineering diagnostics until resolved or deadline.

Do not close the whole Goal merely because the first artifact/load path is wrong.

## 7. P34 repaired qualification

Only after Sections 2–6 PASS.

Run full P34 repaired natural 10/80.

Require:
```text
Q05 cycles                 = 1,619,068
downstream admissions      = 3,090,304
translated admissions      = 3,090,304
untranslated               = 0
unobserved                 = 0
post-ready retranslation   = 0
coverage marker present
same target completion
```

If the exact repaired core is proven loaded yet this result mismatches:
then and only then use:

`STOP_SCIENTIFIC_REPAIRED_RUNTIME_BEHAVIOR_MISMATCH`

## 8. Hit-path matrix after qualification

Run:
- 0/80
- 0/0
- 10/0
- 5/80
- 2/80
- 10/40

All predecessors remain repaired natural 10/80.
Only Q05 gets override.

Independent runs may use max 2 parallel simulator processes after RAM/CPU/shared-state preflight.

## 9. Metrics

For each accepted point collect target-boundary deltas:
- cycles;
- L1/L2 launches/hits/misses;
- requester L1/L2 service;
- MSHR;
- walks;
- PWC/PTE;
- requester latency;
- L2/DRAM;
- coverage invariants.

Compute:
- TOTAL_I0_GAP
- L1_ENVELOPE
- L2_NATURAL_L1_EFFECT
- ZERO_LOOKUP_RESIDUAL

No RTX4080 latency claim.

## 10. Solve-and-continue

Engineering issues including wrong library path, stale LD_LIBRARY_PATH, wrong launcher, incomplete build, missing receipt:
solve and continue.

Do not end the Goal merely because the first rebuilt artifact is wrong.

Whole-goal scientific STOP only after:
- exact repaired core is proven loaded;
- P34 naturally completes;
- repaired behavior itself mismatches the accepted authority.

## 11. Deliverables

Report:
`docs/vm_tlb/codex_handoff/awma/RUNTIME_ACTIVATION_FORENSICS_HITPATH_174NEW_V4_REPORT.md`

Review pack:
`docs/vm_tlb/review_packs/AWMA_174_RUNTIME_ACTIVATION_FORENSICS_HITPATH_V4/`

Minimum:
- RUNTIME_LAUNCH_CHAIN.md
- LOADED_CORE_ARTIFACT_AUTHORITY.json
- BUILD_AUTHORITY.json
- RUNTIME_LOAD_CANARY.md
- P34_REPAIRED_QUALIFICATION.md
- REPAIRED_HIT_PATH_LATENCY_MATRIX_V4.tsv
- TARGET_DELTA_METRICS.tsv
- COVERAGE_INVARIANTS.tsv
- RUN_RECEIPTS.json
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Then node164 closure -> commit -> push -> remote verify -> clean -> STOP.
