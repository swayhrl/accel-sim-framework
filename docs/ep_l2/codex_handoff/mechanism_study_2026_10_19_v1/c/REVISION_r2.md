# C revision r2 handoff to A/E

Core source: b1d42152805e22b6a12774f37351926b6fcbeaf5.
Adapter A base: 44c940b748fceaec8f21fa2b443907d5afd2756b.
New patch: adapter_a44c_r2/CACHE_ALLOCATOR_ADAPTER.patch.
Historical r1 patch: adapter/CACHE_ALLOCATOR_ADAPTER.patch, unchanged.

A can cherry-pick the C additions since84359d4 (only standalone ep-l2-ro-* modules and tests), then review/apply the exact-A small public adapter in its own branch. Do not merge the old historical RO branch. Complete the explicitly remaining CLI, GPU/partition epoch hooks, final print and CMake before building. The common interface, diagnostics, atomics and all current repairs remain A-owned. Record a separate RO integrated source; no C qualification is inherited merely by cherry-picking.

Reproduce the source-only patch without modifying either worktree:

```
python3 util/ep_l2/mechanism_study_c/prepare_adapter.py --core /workspace/worktrees/gpgpu-sim-ep-l2-ms20261019-a-core-v1 --historical-core /workspace/worktrees/gpgpu-sim-ep-l2-ms20261019-c-ro-v1 --base 44c940b748fceaec8f21fa2b443907d5afd2756b --out NEW_EMPTY_OUTPUT
```

The two repositories have different object stores. --core supplies A's exact public preimages; --historical-core supplies the historical30c implementation, never an alternative current base. Git apply check against exact A passed. This is not a compiler check.

Native targets: transactions (module/reference payload), store-port (actual paid store/reference Tag), oracle parser, bank progress, production cache runtime, production partition. Distinguish these scopes. New allocator pin-refusal and independent-address witnesses are uncompiled/unrun. Future native four-mode witness01 has1 lower group/1 line,10 has2/2 and11 has3/2;00 has no RO runtime. The extra11 lower read is paid traffic, not useful independent work. Those are expected assertions, not observed numbers.

E acceptance still requires original174 admission, actual exact A-integrated build/binary/config/manifest/trace identities, affected native production tests and independent whole-epoch RO proof. Native64slice/request/WB/WAD/bank/drain gates stay applicable. Keep both positive and negative raw results. E alone launches full applications; C has consumed0 starts and no leases. Source and resource blockers affect C native qualification only, not A's independent diagnostic release. No autonomous build or resource exception is requested by this handoff.
