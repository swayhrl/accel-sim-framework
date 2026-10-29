# D01 engineering candidate V2: ordinary relief and diagnostic consistency

The known V1 diagnostic gap is closed in this private CPU candidate. The complete patch is ordinary_preview_relief_with_diagnostics.patch. No accepted source or old D V1 artifact was changed; old D manifest still235826fff40646e51090fbafba7c35ff8b3a51d8702af41cd1c265bd2a938382.

The production opportunity is unchanged from V1: when ordinary preview sees raw TagFAIL and an RO runtime exists, evaluate the same read-only detachable predicate used by ft_access. If eligible, virtualize MISS and keep normal MSHR/MissQ gates. This patch does not change can_detach, reuse_seen, attachment/generation, required-sector state, owner, pin, bank, directory or descriptor safety.

The diagnostic addition marks consulted whenever that existing predicate is actually evaluated, then records intermediate equal to the actual preview result. This deliberately includes T0/reuse cases as consulted-but-kept-fail, consistent with existing RO preview's consulted semantics at ep-l2-ro-runtime.inc:277-281. It does not claim an eligible victim exists in those cases. raw and production_raw retain the original RESERVATION_FAIL; the controller reads no diagnostic result.

## Executed CPU checks

The private executable uses actual Source78 production partition/ROP/frontend/RO/Tag/MSHR/Payload/return/response classes. No full simulator model or application ran. Five exact same-binary diagnostic OFF/ON pairs (10 executions) all completed and drained:

| Case | Pre-release decision and production evidence with diagnostic ON | Preserved constraint |
|---|---|---|
| READ | rawRF1, virtualMISS1, commitRF1, relieve1, detach1, after-detach-accept1 | Old RO returns and versions drain |
| WRITE | Same funnel as READ | Ordinary write resource/response path drains |
| T0 | rawRF62, keptFAIL62, commitRF0, relieve0, detach0 | T disabled cannot detach |
| REUSE | rawRF62, keptFAIL62, commitRF0, relieve0, detach0 | All8 merged histories remain ineligible |
| MSHR_FULL | rawRF62, virtualMISS62, rewritten-final-denied, commitRF0, relieve0, detach0 | Normal line128 capacity still blocks |

All five ON cases have pressure_relief_not_consulted0 and closure_errors0; partition accounting assertions pass. READ/WRITE specifically have eligible_rewrite_miss1 and trigger_accepted_after_detach1. These counts are the pre-release pressure window, before the fixture returns held memory packets. They do not describe permanent stalls or application rates.

Each case performs32 read-only snapshots/previews before admission. The original raw status is preserved, intermediate matches the virtual decision, consulted is set, and old Tag/Payload identity, bank grants/attempts and descriptors remain unchanged. When diagnostic is ON, the entire ledger is byte-identical across repeated previews. Only actual frontend callbacks charge counters.

CPU_DIAGNOSTIC_NI.json compares both semantic lines for every pair, including fixture cycles, ordered event/version identity digest, replies, lower packet/byte counts, bank grants/conflicts/attempts and full drain. All five pairs are exactly equal. This is CPU NI for this bounded fixture, not whole-application NI or a host-overhead benchmark. The existing fixture's ordered digest is not a complete waveform comparison.

## Resource, build and failure receipts

RESOURCE_ADMISSION.json records fresh host/cgroup/SSD evidence. One candidate source TU compiled with nice10, O1 and assertions enabled; compile elapsed8.27s and child maxRSS690224KiB. The private archive starts from exact acceptedSource78 lib SHA e5a743a2bb796d82f58109251f43d5c1997d5c1f7fdeac61213416da3835b697 and replaces only gpu-cache.cc.o. Member lists have no duplicates and match the original list. Full production source/archive hashes and old D manifest remain unchanged.

IDENTITY_AND_CLOSURE.json and BUILD_COMMANDS.json record exact source, patch, fixture, input references, object/archive/executable hashes and commands. This one-TU build is an explicit engineering identity, not a full newCore commit or qualified new modelELF. Assertions were not removed. Binary/archive files stay out of Git and should be retained true164 by Main's unified archive.

All attempts are retained. Attempt01 could not find /usr/bin/time and therefore never launched the compiler; Python child resource usage then supplied the compile measurement. Attempt02 fixture compilation failed because one auto declaration mixed uint64 and unsigned values; the failed source/log are preserved. Splitting that declaration and making printf casts explicit resolved the test harness compile issue. No protocol assertion failed in the10 final executions; no scientific retries/budgets were consumed.

## Boundaries and next decision

This closes the specific missing consulted/intermediate synchronization within the tested ordinary-relief CPU path. It does not close all known protocol gates: ready-only, descriptor-full, per-addressfull, MissQfull, directory/payload exhaustion and exhaustive cross-clock cases are not newly covered here. V1's existing sector/reorder/backpressure regressions are references, not rerun qualification of every new binary behavior.

Still pending: reviewed Core commit, full all-TU build, frozen Source/ELF/config identity, Host/native and per-mode eligibility, application NI, and actual sameSource F-minus-T/F performance. Existing S/F or WV/F results cannot fill those controls. No W/V/service policy or host-writeV3/MSHR64/Source92 code was bundled in. No collector, scientific dispatcher or new budget was created. Models started:0. Application incidence and speedup remain UNKNOWN.
