# G2-4 — stall/replay correctness (running)

Core checkpoint: `c1431e01f593719f9201d4ad4d7666bebead8a4f`.

`vm_m2_g2_4_test PASS` covers pending translation, walker completion, same-UID replay, exactly-one modeled store/atomic effect, and cross-page boundary. G2-1 through G2-3 regressions and standard build pass.

This is not G2-4 acceptance. QV100 and RTX3070 VM-mode LUD smoke attempts ended without statistics after abnormal memory growth; QV100 exited 137 and RTX was terminated near 64 GiB RSS. The host had swap exhaustion and unrelated TLS jobs. No actual cache-path replay claim is made. Raw logs: `/tmp/g2-4-qv-functional.log` and `/tmp/g2-4-rtx-functional.log`.
