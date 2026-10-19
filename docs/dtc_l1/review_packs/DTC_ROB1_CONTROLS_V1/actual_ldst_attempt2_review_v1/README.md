# Independent review of closed ROB1 actual LDST attempt2

Conclusion: the inspected closed inner receipts and actual byte streams support
`PASS_SIX_ACTUAL_LDST_CPU_CASES_ONLY`. This review performed no imports, tests,
builds, process/resource sampling, signals or launches. It read only the
parent-authorized closed inner evidence and immutable Git sources, then wrote
this ROB1 pack. It does not certify the outer controller's still-separate
publication/final readback or current live resource/authority state.

## Evidence identity

Raw root: `/workspace/dtc-evidence-closure-20261019-v1/rob1/fixture-runtime-v1/attempt2/`.
`RESULT.json` SHA256 is
`6641a7994f4420af767cad4f695fc8c4a38a5aeadbcc125de52289e11640fdb7`.
`CLOSED_INNER_SHA256.txt` binds the reviewed result, start/child/terminal,
admission, runtime/final resource and byte-stream files; it contains no copied
trace, ELF, library or source payload.

Immutable parent preregistration: Framework
`1c33ff7990fb6b75dedca470b9352d1d5af44081`,
`docs/dtc_l1/iscas2027/evidence_closure_20261019_v1/execution/ROB1_FIXTURE_RUNTIME_REGISTRATION_ATTEMPT2.json`,
SHA256 `dd4a61be152dc56ee7ae36a2659f92ce115d1e9bc48f191dc66a6ea436b48897`.
The closed cohort START records that exact registration SHA and Core
`b1077667f7a2bcc72260733f88f5798f167346d1`.
The registered/inspected inner source remains SHA256
`c73f30cd91a66f688c97de9177845eee88084a883124ff8cc6a88c5126cc95a9`;
classifier remains
`d5428e9114bbd3e6cf02670f1c1d664cc134bad572e42dd26ec928f75a70fcd2`.
Both were independently hashed from immutable Git, not imported. Each case
START binds static-freeze SHA
`05a100bfa7fa2be0181fe32aeb59a68614501902c8db1fb20cff70317778dac7`.
This is the previously frozen assertion-enabled b107 fixture/whole-library
tuple, not an original-c809 reference or a new trace frontend build.

## Actual cases, independently joined to source

| Case | Final three argv | Width | ready/start/done/retire | Actual exit | Root PID@start_ticks |
|---|---|---|---|---|---|
| omitted | omitted,3,1 | 4 | 11/12/12/14 | 0 | 1117629@918253784 |
| explicit_zero | 0,3,1 | 4 | 11/12/12/14 | 0 | 1118111@918254860 |
| quota_one | 1,3,1 | 1 | 11/12/14/16 | 0 | 1118442@918255932 |
| bad_width | 2,3,1 | rejected | not reached | 1 | 1118469@918257002 |
| bad_mode | 1,2,1 | rejected | not reached | 1 | 1118707@918258076 |
| nonfinite | 1,3,0 | rejected | not reached | 1 | 1118858@918259152 |

The three positive stdout files were read as actual output, not inferred from
the classifier's returned dictionaries. Omitted and explicit0 are byte-identical
(SHA256 `06f889b8f5bd118311f6228fa42f70b5b96732e0d2c95b4b230f1cacda9e5fcc`);
quota1 is `2ce519d7f9a6f1d7a5f0137ad9aa5ba23fee431e9a4f12aaaae40f1378aff89c`.
All three print the exact one ROB1 completion record, requested sectors3,
WB-denied1, finalRef0, ledger-closed1, kernels0, GPU-cycle-calls0 and threads0.
All positive stderr files are empty. The width1 change delays collection by
two absolute core cycles and retirement by two; no sector/Ref loss is hidden.

At immutable b107 `tests/dtc_l1_rob1_collector_ldst_test.cc`, the printed record
follows enabled assertions on actual parser/LDST construction and response
consumption: four32B returns in0/2/1/3 order, three requested sectors, ready11
without same-cycle consumption, first collection12, repeated LDST calls not
refilling a shared absolute-cycle quota, conservation and Ref1 through
collection. It reserves the real operand collector's RF bank with a competing
instruction at done+1, checks WB-blocked1 with pending-write/Ref retained, then
checks retirement at done+2, activeRefs0, pending-write removal, dependency
closed1, retired1, lower-outstanding0 and empty inflight. It does not assert
final scoreboard emptiness. These actual source assertions delimit the claim;
the printed constants alone would be insufficient without their source/build
binding.

Each negative has empty stdout, exactly one
`DTC_COLLECTION_QUOTA_UNSUPPORTED_STOP`, one
`=== CRASH: SIGABRT (signal 6) ===`, a real multi-frame Backtrace ending with
`=== END BACKTRACE ===`, and actual exit1. Actual backtraces include the
matching whole libcudart path and real `ldst_unit` constructor frames. b107
gpu-sim.cc installs this handler and calls `_exit(1)`, so exit1 is the intended
rejection; raw -6 is not required. These are three distinct registered invalid
argv vectors, not three copies of one case. No completion/retirement claim is
made for the negatives. Backtrace paths are not a full loaded-library mapper
observation; no per-negative mapping/dladdr proof is promoted.

## Six new admissions and closed lifecycle

Every case has its own FIRST and SECOND sample and all-true complete
ADMISSION.json. The monotonic pair gaps, in the case order above, are
10.218446454, 10.215026416, 10.213065656, 10.203534372, 10.223257504 and
10.223488588 seconds. They are disjoint new samples, not a reused build or
preceding-case pair. Recorded UTC bounds are
2026-10-19T17:22:36.272185+00:00 through
2026-10-19T17:23:40.162033+00:00. UTC dates here come from the receipts;
review date/host timezone is not substituted for their recorded UTC.

All twelve admission samples record original host huangrulin-174; host and
cgroup memory headroom exceed32GiB; both memory full avg10 are0.00; maximum
host IO full avg10 is7.99 and cgroup is1.42, below25. Disk remains above
44,618,000,000 bytes, exceeding strict5GiB plus the registered32MiB output
and128MiB reserve. Device156 is bound as the output filesystem. Host oom_kill366,
cgroup oom0/oom_kill17 stay unchanged across all pairs and final/runtime
receipts. Each recorded authority check reports the exact registered parent
runtime role1117053@918252240, no pending quarantine and no unknown dispatch
authority; CPU-only resource roles grant no simulation permission. This review
examines those historical observations, not a new global authority audit.

Every case START follows its own SECOND by milliseconds, well within5s, uses
the exact ELF/config/three-argument vector and own output cwd, clean environment
and own library/TMPDIR. Its CHILD records the corresponding actual Popen,
boot identity and current exact exe/cwd/argv with live observation available.
Every case has one runtime resource observation plus final resource receipt;
all recorded checks pass with unchanged OOM counters. Positive and expected
negative exits therefore have no recorded resource/cleanup error masking them.

All six terminal receipts record reaped=true, reason=null, cleanup=null and
empty own-group instances after reap. The immutable launcher source performs
inspect-only group checks after reap and calls cleanup/signals only for an
unreaped root; these six natural completions required no cleanup call. No
post-reap signal or live-absence probe was performed by this reviewer. The
result contains six starts, zero retries and zero simulator starts, and its
case entries agree with the individual terminal identities and stream hashes.
The identical ADMISSION.json hashes reflect its identical boolean-summary
schema; distinct FIRST/SECOND files and timestamps, not that hash alone,
establish six fresh pairs.

## Scope and effect on the earlier R plan

This advances actual parser/constructor/collector/real RF-denial/Ref-retirement
CPU component evidence from the earlier immutable snapshot's NOT_EXECUTED to
the six actual limited PASS observations above. It does not rewrite or
retroactively pass attempt1, resource refusals, or earlier preparation records.
The earlier R6 plan's snapshot qualification remains historically accurate;
this review is the later evidence to consume.

The original c809 matching fixture remains unexecuted in this review.
Omitted=explicit0 within b107 is observed local component equivalence; c809
vs b107 whole-binary default/OFF equivalence remains NOT_PROVEN. The fixture
forces AE0/AD0 and executes no trace/kernel/GPU-cycle loop. Native values,
selected AE/AD interactions, full trace ELF/runtime closure, application
performance and formal R denominators remain separate. F remains provisional;
these six CPU starts do not spend or replenish AG6/BA simulation slots and
provide no new formal dispatch permission.
