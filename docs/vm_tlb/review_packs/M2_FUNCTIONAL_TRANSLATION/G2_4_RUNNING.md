# G2-4 — stall/replay correctness (running)

Core checkpoint: `c1431e01f593719f9201d4ad4d7666bebead8a4f`.

`vm_m2_g2_4_test PASS` covers pending translation, walker completion, same-UID replay, exactly-one modeled store/atomic effect, and cross-page boundary. G2-1 through G2-3 regressions and standard build pass.

This is not G2-4 acceptance. QV100 and RTX3070 VM-mode LUD smoke attempts ended without statistics after abnormal memory growth; QV100 exited 137 and RTX was terminated near 64 GiB RSS. The host had swap exhaustion and unrelated TLS jobs. No actual cache-path replay claim is made. Raw logs: `/tmp/g2-4-qv-functional.log` and `/tmp/g2-4-rtx-functional.log`.

A third diagnostic used only the existing 54 KiB `kernel-8.traceg` through a
temporary one-kernel list. It again grew to about 65 GiB RSS in roughly 41 s,
so the failure is not explained by full trace-list preload. The process was
terminated; raw log: `/tmp/g2-4-one-kernel.log`.

Final bounded reproduction: `ulimit -v 10485760` produces deterministic
`std::bad_alloc` immediately after the memory-subpartition initialization
banner, before trace replay. GDB itself could not start an inferior under this
limit because its debug mapping needed more virtual memory. Raw logs:
`/tmp/g2-4-one-kernel-vmem10g.log` and `/tmp/g2-4-badalloc-gdb.log`.
