# Isolated Core preparation after AG4 terminal

Prepared Core commit: `b1077667f7a2bcc72260733f88f5798f167346d1`.
Tree: `0a462efb9a48409064259735108b88dad127a53c`.
Parent: `c8090115bd57512b1b23fca7d925301fa620c751`.
Branch/worktree: `hrl/iscas2027-dtc-rob1-core-174-v1`, `/workspace/worktrees/gpgpu-sim-iscas2027-dtc-rob1-core-174-v1`.
Publication: [immutable Core source](https://github.com/swayhrl/gpgpu-sim/commit/b1077667f7a2bcc72260733f88f5798f167346d1).

The previously prepared patch applied cleanly to the new worktree with Git; production c8090115 and all AG4 files remain untouched. Four production files contain only29 additions. Existing selection, return, collection loop, WB, retirement, Ref/fence and arbitration bodies are unchanged. The override is default0 and only accepts1 for finite PAPER_OO; this source statement is not a measured OFF-equivalence result. `git diff --check` passed; no compiler, CPU script/test or simulator ran. No engineering execution failure occurred in this source-only step.

The coordinator consumed AG4 terminal `d8d0401dab0a1d9cb949302bcc05148328421cc2`: STOP due to prelaunch qualification gap,2/5 starts, no optimization result. The current candidate is therefore `PROVISIONAL_O_WITH_INCOMPLETE_OPT_SCREEN`, K0/OO128/Tag64x8/AE0/AD0. Current R requests are only GEMM/BICG collector4->1. Initial AE/AD conditional requests remain preserved in `CONTROL_REQUESTS_INITIAL.tsv` as superseded preparation; no C+ hash implementation was created.

## Actual integration fixture prepared, uncompiled

`tests/dtc_l1_rob1_collector_ldst_test.cc` adapts the accepted linked `dtc_l1_progressive_ldst_test.cc` fixture pattern. It uses the real option parser, GPU/cluster/core/LDST construction, actual four32B lower responses, production LDST cycle/selector and collection, **real operand-collector bank reservation to deny WB**, ledger completion and Ref drain. Setup uses synthetic instructions and -fno-access-control, as the accepted fixture does; it is a component test, not an application/native payload proof. No `gpu->cycle()`, kernel, replay, CUDA launch or simulation thread is requested.

It requests3 sectors from a whole line: quota4 should collect all at12 and retire14 after one actual RF denial; quota1 should collect at12/13/14 and retire16 after the same denial. At ready11 collection must not advance; repeat LDST calls in one absolute cycle must not refill quota; completed data must survive denial with Ref1/pending register/ledger intact. Both modes must collect exactly3 sectors, close one ledger dependency and drain Ref/credit. These are **expected assertions**, not observed results.

Arguments are exactly `CONFIG omitted|0|1 WIDTH_MODE FINITE`, with normal mode3/finite1. `ROB1_ORIGINAL_CORE=1` permits compiling the same source against original c8090115 headers and its accepted library, with only omitted width. Its stable `ROB1_COLLECTION_TRACE` line allows an actual original/default0/explicit0 differential without requiring production source changes. New diagnostic headers must never be linked to the old unpatched library: the new shader-config scalar changes a shared C++ type and requires a matching dependency-closed diagnostic library. The linked fixture therefore remains blocked by **heavy build admission/disk**, not disguised as a tiny helper. Parser width2, quota1/mode2 and quota1/nonfinite cases are planned actual-constructor negatives. The external-cache overload still has a source rejection guard; this fixture does not claim runtime coverage of that overload.

## Exact first CPU role request

`CPU_ROLE_REQUEST.json` contains exact compiler path/hash, source SHA, cwd/argv, bounded stdout/stderr and output paths. The first requested scope is only the small standalone actual-quota/service_entry helper. One compiler and one helper run are sequential, with64MiB planned output ceiling; no CMake, Core library build, linked LDST, simulator or input scan is included. Core dumps are explicitly disabled before the helper's seven aborting negative children. Compilation output SHA must be registered before runtime admission.

At preparation, filesystem free space was4.7GiB, below the10GiB full-simulation/input-scan R2 gate. No build or test was started. CPU authority/role registration and resource admission remain coordinator decisions. A successful helper alone cannot authorize full sensitivity points.
