# G3-0 M2 regression freeze

Status: `PASS`.

At Core `e7999554200760b31b4efe16d98e050370e1ea71`, the compact directed
entry commands were rerun:

```text
vm_core_m1_test PASS
vm_m2_g2_1_test PASS
vm_m2_g2_2_test PASS
vm_m2_g2_3_test PASS
vm_m2_g2_4_test PASS
```

The tests compiled against the current Core source and
`src/gpgpu-sim/vm_translation.cc` with `-std=c++11 -Wall -Wextra`.  Existing
formal raw captures for the same source state are indexed by the M2 pack's
`RAW_LOG_INDEX.tsv`; this rerun is the compact M3-entry guard, not a substitute
for the M2 formal replay evidence.

The completed M2 source and Framework evidence anchors are, respectively,
`e7999554200760b31b4efe16d98e050370e1ea71` and
`a7020e603d6081f1f16f26b5ad1ead5ca17d7756`.  Both worktrees were clean at the
time the M3 entry material was read.  No M3 Core source modification occurred
before this result.
