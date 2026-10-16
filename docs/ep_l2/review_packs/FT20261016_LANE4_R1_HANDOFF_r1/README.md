# Lane 4 review_r2 continuation: R1 integration delivery

R0 production qualification and B16/U_WB16 main experiments belong to Lane5
and proceed without ideals, TVD or RO. Nothing in this pack requires a new
R0 binary. The immutable R0 content and file identity are verified unchanged.

CORE_MINIMAL.patch is the previously reviewed r2 patch against exact Core
126394be. PATCH_REPLAY.json proves a fresh private-index replay produces the
entire b8b3d55b candidate tree. No normal index or worktree was altered. Lane1
can apply this exact patch to a separate R1 integration worktree, freeze its
actual new source/binary identity, and send R1 to Lane5 for independent gates.
The existing candidate binary is offered as evidence, not a Lane1 R1 release.

R1_INTEGRATION_CONTRACT.json specifies the runner interface. Lane5 owns its
qualified release and B16 baseline specs. The per-mode ideal_gates entry is
R1-only metadata recording the already required independent mode validation;
only the requested mode needs qualification. R0 normal qualification needs no
ideal flags/gates. The adapter binds the qualification bytes, recomputes the
derived config hash, rejects mixed R0/R1 source/binary/trace/epoch, and records
the exact matched baseline key. The 19 new tests use synthetic non-executable
files and establish validation behavior only, never qualification/performance.

Prior audit, 12 production C++ invocations, six illegal configurations,
16 parser tests, and three complete legacy applications are reused, not rerun.
R1_CEILING_RESULTS.csv has 18 explicitly unrun cells with blank metrics and
identities. No old 1.721x result is inserted. Actual Lane1 common R1 release,
Lane5 independent mode qualification and same-binary B16 specs are pending.
Future per-cell results will be published as they complete, preserving the
first-wave four workloads and convolution/FWT-only I_WB_META combinations.
