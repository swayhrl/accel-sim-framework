# Lane 4 review_r7: host-prefill reference synchronization candidate

Coordination99e7515f81b0038ac49d274b73f774e8ea801e46, original science
6c136e2a56a008695f8c8b815723bf8f1a760db9. Continued the existing Lane4
branches, without a new Goal, disk waiter or production worker.

Core source candidate **8ff56eb0804a027f1e253e629dd2915b02bc03b5**, tree
1949be28284e3d9d1674ee21211eb5885e75a128. Framework tooling source
**705cd7b30d825cd1d9887e48427475a126d9bc83**. The exact target is Lane1 c9481845,
not the superseded62dc target. Its publication57e1c363 is tree-equivalent.
This source candidate is **not compiled or independently qualified**. No new
binary, simulator config identity, application trace identity or run key exists.

The candidate fixes I_READ_HIT reference initialization after an accepted
later clean/quiescent host prefill. It follows the producer's selected-sector
version-zero symbolic semantics, preserves unselected bytes and the producer
version clock, and does not restrict prefill to initial time. Failed prefill
does not reach the new hook. Bank operations and responses retain physical
time; Tag touches retain native memcpy-offset time.

Delivered patches:

- CORE_C948_IDEAL_CANDIDATE.patch: complete exact c948 integration, including
  corrected fixture extraction and new regression sources/config.
- CORE_RUNTIME_ONLY.patch: corresponding src delta.
- REFERENCE_SYNC_RUNTIME_ONLY.patch: minimal synchronization change, two src
  files, based on reference_patch_parent_tree in SOURCE_AUDIT.
- REFERENCE_SYNC_ONLY.patch: that synchronization plus regression inputs.
- TAG_TIMESTAMP_ONLY.patch: independent native Tag timestamp call fix.

Original replay had one real conflict in test_ft_wbuf.cc. Resolution preserves
all c948 test bodies and extracts its repaired fixture clock, adding only ideal
options. The obsolete getter patch was not reapplied; exactly one observer
remains. Producer FT implementation, both repair test sources and scope are
byte-identical to c948. The complete patch round-trip and candidate-tree identity
were verified after freezing the source/tooling commits.

Two C++ regressions and their exact invocation path are prepared, **NOT_RUN**;
see QUALIFICATION_PREPARATION and CORRECTNESS_REVIEW. Python syntax checked for
the two changed tools; no old passing66-test suite was rerun. No compiler,
CMake, resource lease or simulator was invoked. This is source validation,
not runtime repair PASS or an observed red/green C++ test.

R1_1_PREPARATION retains all18 original cells as NOT_RUN with null runtime
identities/metrics, four Lane5 OFF baselines and14 Lane4 ideal cells. The
unchanged fail-closed runner still requires current repair/ideal gates, both
OFF and ideal launch authorization and same-R1.1-binary B16 inputs. In this
continuation the loader refused a registry working-file/hash mismatch with the
shared client pointer; no fallback or registry fork was used. The publisher
must complete a coherent Lane5 contract update before launch validation.

Latest consumed remote producer receipt still has binary=null/runtime_ready=false;
no official R1.1 or matched baseline exists. Lane1 R0.1 and Lane5's first formal
pairs retain priority. No source Ops, migration, disk policy, DTC-L1/C16 process
or quota was changed. LIVE_CHECK records actual processes/resources and no
Lane4 waiter. Dependency continuation is through the existing coordinator event,
not an unaudited background process or repeated resource polling.

Five previous packs/112 indexed files were checksum-verified unchanged. Old
R0/R1 results remain scientifically withdrawn; old1.721x remains historical.
Large raw, binaries and traces were not rewritten or reexecuted.

Low-resource reproduction (new output path required):

```sh
python3 util/ep_l2/prepare_ft_lane4_r7_static.py --core /workspace/worktrees/gpgpu-sim-ep-l2-ft20261016-lane4-v1 --out /tmp/lane4-r7-new-static
```

This uses a private index and emits patches; it never checks out another source,
invokes the production build entry or launches a simulator. SHA256SUMS binds
pack bytes except itself. Regression source files are also committed in Core.
