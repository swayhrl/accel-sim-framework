# ROB1 source preparation after AG4 terminal

Status: **PREPARED_NOT_TESTED / WAIT_COORDINATOR_CPU_ROLE_ADMISSION**.

AG4 terminal d8d0401dab0a1d9cb949302bcc05148328421cc2 was consumed by the coordinator: STOP prelaunch qualification gap,2/5 starts, no optimization result. Candidate is now PROVISIONAL_O K0/OO128/Tag64x8/AE0/AD0. R is restricted to GEMM/BICG collector4->1. No C+ hash or AD performance work is active.

Core source patch and two CPU fixture sources are published at [b1077667f7a2bcc72260733f88f5798f167346d1](https://github.com/swayhrl/gpgpu-sim/commit/b1077667f7a2bcc72260733f88f5798f167346d1), new isolated branch/worktree derived from c8090115. Four production files add29 lines only; no production/AG4 worktree changed. A new linked fixture prepares actual parser/constructor/real RF-bank WB-denial/retirement coverage using the accepted harness pattern. It is not compiled or executed, and requires a matching diagnostic library; old library/new headers cannot establish equivalence.

`CORE_SOURCE_PREP.md` describes exact source scope and expected tests; `CORE_SOURCE_SHA256.tsv` binds all six Core files. `CPU_ROLE_REQUEST.json` requests only a bounded standalone actual quota/service_entry helper compile/run first, with exact compiler/hash/argv/source/output footprint. The coordinator must admit compilation, then register the produced ELF before admitting execution. No scripts, compiles, CPU tests, simulators, locks, background jobs or heavy builds were started in ROB1. No error was discarded. OFF equivalence remains NOT_TESTED.

At source preparation free disk was4.7GiB, below the10GiB full-run/input-scan gate. Remaining work: exact CPU admission; helper execution; disk/build admission and matching diagnostic library; real linked fixture and original/default0/explicit0 differential; qualified controls/inputs and coordinator-only full-run registration. Initial gate-closed prep remains preserved at e37b0920b957c162c6640230ee7ce3a9c391e556 and initial conditional requests at CONTROL_REQUESTS_INITIAL.tsv. No full-run slots or UUIDs are allocated by this handoff.

Core publication was independently fetched to refs/dtc-closure-readback/rob1-core, exact commit/tree matched, diff empty and worktree clean. Framework publication uses refs/dtc-closure-readback/rob1, independent of shared FETCH_HEAD. All testing statuses describe observed execution, not source assertions.
