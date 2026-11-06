# Independent actual-review watch CPU preparation

This package is inert until an exact Main release and independent source review.
No actual reviewer child has been launched during preparation. Tests use fake
identities; actual Gate2 is never produced from mocks.

The existing A image closes strict/archive/native restore/RESULT but contains no
original R3 review queue. This CPU worker consumes those naturally accepted
results, validates/reuses the four existing qualifier receipts, then invokes the
unchanged frozen original reviewer with `--mode` only when the mode's fixed8 and
same-build OFF8 all have real accepted results. Missing/HOLD/negative rows remain
excluded from acceptance, not replaced. Performance never determines readiness.

Source chain:

- Original runner12608931a0c7b904722360b751f2aa10a15219e1d5a5eafd8076969638c5341d
- Independent reviewer2446f7db384b4df2977decface1fb49fe42af1939b3cbb091112f6cb1809edc7
- Resources3f20a6bb18d401825a84eb5445c00d0771c449fa5766ddd434d9f284b7ff4b7f
- Engine5f978c77586f3be030ca0295adb6eec09d8152254df1f88f85becb45588850d9
- Fixed original32 plan6bb3876db0fe5dc7ef4544e7a0a03f822a53da73129daed9bce5bc9d822c53b0
- Fixed matrix658fc5f35827d3c516b8d3eba06501b33e0d55dc1d546a4ae832ef9819e7b81a

The sole watch instance holds ORACLE_INDEPENDENT_ACTUAL_REVIEW_WATCH.lock. Each
actual CPU reviewer child shares the exact job-lock OFD with the watch parent;
B's actual review queue uses the same job lock. Thus no duplicate canonical
review writer is introduced, including if a watch parent exits while its child
continues. No lock is borrowed from the scientific owner, no science registry EX
is held, and no resource safety loop is blocked by true164 reads.

Existing receipts are only read and checked by the frozen resource gate against
the original UUID, strict/RESULT/source/binary and true164 proof. They are not
rerun or overwritten. The original runner creates its own PASS or separately
named HOLD receipt with exclusive writes; this worker cannot manufacture PASS.
Absent/partial result files are waited for. Every actual CPU child gets a
separate BEGIN/END engineering event. It is never a scientific model or UUID.
No child/model signal, timeout kill, dispatcher, model prepare/run, scientific
register, budget update, source change or publication watcher change exists.

Default invocation prints PREPARATION_ONLY. Main may later use:

`python3 -B oracle_actual_review_watch.py --run --release ACTUAL_RELEASE.json --release-sha EXACT_SHA`

The release must bind this exact worker source, independent review scope
INDEPENDENT_CPU_ONLY_ACTUAL_REVIEW_WATCH and an independent engineering output
directory. Do not use the working publisher output directory. A stop marker
STOP_NEW_REVIEWS.json admits no further review children, allowing the current
CPU review to finish naturally. The worker exits after all three actual mode
Gate2 receipts pass. scan/OFF is required in every mode's shared OFF8 set.

This is CPU postprocessing of existing scientific evidence. Actual launch awaits
D's small source review and Main release. B still consumes only real receipts;
no science can start by running this helper alone. No paper changes occur.
