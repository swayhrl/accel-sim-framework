# Validation

`VALIDATION.json`: PASS,30 meaningful evidence consistency checks.12 fixed programs/629 ordered members; preregistration byte-identical to before results; measured diagnostic/LayerNorm source unchanged;15 cases ?7 independent processes ?10 samples; all native command exits zero;15 complete-ROI profiles;10 trace members/all CTAs and warps; actual cubin versions and explicit LayerNorm non-admission; measured binary/library/input SHA closure; capture input/output SHA equal native; independent164 archive and all285 payload-file SHA checks.

Producer-format audit recomputes declared instruction counts for every warp, unique grid/warp coverage, dynamic opcode/width counts and per-file hashes. All10 complete files end each warp with EXIT. It does not restore skipped CALL instructions or prove simulator support. Full-operator kernel counts/resources were independently compared with nsys CUDA activity. Numerical correctness: Parboil source predicate + rejected corruption; LayerNorm all elements against FP64 reference. No correctness failure was bypassed.

Python compile checks, shell syntax and `git diff --check` pass. GPU native/capture phases used the existing exclusive nonblocking cooperative lock, no compute process present at acquisition; all locks released. Final GPU/lock probe found no compute job and free lock. No other task was terminated. No simulator, full LLM or extra family/shape sweep.

Archive transfer used rsync without owner/group/perms preservation to accommodate mapped SSHFS ownership. Initial no-payload/load failures and loader diagnostics remain. Destination verification streams the archive read-only and matches every indexed byte SHA independently; extraction was not required.
