# R0.1 isolated source candidate — not a repaired runtime release

Authority a41bfb55 review_r3; old R0/R1 application qualifications are superseded. Preserve old raw/config/CSV/trace/binary/receipts; this revision archives the earlier Lane1 receipt rather than rewriting history. Lane5 b134f76d acceptance is authoritative; original COMPLETE_VALID is an execution fact only.

Core62dc1d17 is a pure child of exact R0126394be. Its publication c93d900e retains the prior R1 history but has exactly the candidate tree, with no diagnostic/TVD/RO mixture. R0/R1 worktrees and binaries remain untouched. Source reverse-patch applicability and unchanged native Tag/old memcpy-loop checks pass; compilation and every new producer test remain NOT_RUN.

Imported Lane5 clock+warmup code was hardened after source review: dirty selected victims or dirty same-line host updates refuse without changing owner/data/Tag/offset; live hardware, pending sectors/references and held responses also refuse. Normal timed GPU WB remains required and tested by new source fixtures. Host full-width address and endpoint-sector repair binds actual high pointers; old non-FT behavior is unchanged. Unsupported dirty/concurrent host overwrite is an explicit fail-closed scope boundary, not free WB service.

Shared disk floor48GiB is unchanged, plus2GiB build growth reserve. Only owned inactive CMake .o/.a caches were removed after pinning source/executable hashes, compiler recipes and before/path/inode/block evidence. Actual free delta1,091,817,472bytes; frozen executables and every raw/config/CSV/trace are unchanged. Details in OWN_REBUILDABLE_CACHE_CLEANUP.json; compiler recipe backups remain in its indexed result root. This did not restore admission.

The real guarded driver is util/ep_l2/ft_lane1/build_r0_1.py. It writes a hold receipt and starts no compiler until admission and measured growth headroom permit. One Lane1 compile serves the official producer and Lane5's independent checks; R1.1 and other feature builds do not duplicate it. No daemon, implicit retry, fake binary hash or PASS exists.

CORE_R0_1_CANDIDATE.patch uses zero context: apply with git apply --unidiff-zero at exact126394be only. A source candidate is not a qualification.
