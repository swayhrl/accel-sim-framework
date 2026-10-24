# Bounded verification pipeline and complete archive inventory

This is an in-progress infrastructure checkpoint. The expanded user Goal also
includes complete RTX4080 collection, input identity, trims, and independent
consumer semantic qualification. None of those is declared complete here.

All four historical archive inventories completed V2 full decompressed EOF,
physical whole-archive SHA, strict nonzero-header checks, and gzip CRC/zstd EOF
checks. Their frozen union contains 125 exact asset bundles and 22,769 unique
content objects, including command lists and kernel members; these are not
benchmark-program counts. New archive content is 784,147,541,854 bytes in two
source-ordered batches (172,594,900,769 and 611,552,641,085 bytes). The latter
reads the exact already-verified polybench.tgz from true164 because another
authorized storage task retired its original Source copy. Provenance retains
the original path and explicit retirement; no fresh original-body read is claimed.

V8 engine SHA256 is
`c5fac7e8137adb389e9843d26d52c1035727e75a71f780d9603dac6517358a74`.
The frame receiver/source sender and production leases remain single. Two
workers independently hash distinct closed chunks, rename without replacement,
rehash the published chunks, and publish their range indexes. Three pending
chunks is the hard bound; offsets account for pending as well as completed
ranges. Only the receiver consumes frames. All futures complete before source
EOF/exit verification, whole-file assembly, closed-reopen whole-file SHA, and
COMMIT-last publication. Resources checks are serialized by an RLock.

The source ceiling remains 32 MiB/s; each verifier read ceiling is 30 MiB/s.
These are component ceilings, not a claimed 32 MiB/s aggregate NAS budget.
Actual local block busy/latency/queue determines whether high global I/O PSI is
local saturation or the task's own NAS/FUSE waiting. Unknown or busy local
block state retains conservative pressure throttling. The minimum local free
space is 5 GiB plus every other registered project reservation, 1 GiB other
project headroom, and 64 MiB controls. No foreign locks or jobs are modified.

Qualification used real SIGKILL after a durable chunk and before COMMIT, then
resumed through full current SHA checks. Three pending chunks were observed.
An actual corrupted durable chunk, wrong incoming SHA, duplicated offset,
wrong/missing file EOF, missing source completion, and nonzero sender exit
all refused COMMIT. Archive concatenation positives and CRC/truncation/invalid
header negatives still pass. The small test sender chunk is a subprocess-local
fixture setting; production frozen source frames remain 128 MiB.

Promotion waited for expanded batch 15 to close, for its V7 receiver and source
to exit, and for its immutable COMMIT to verify. Only then were our old paused
controller and supervisor ended. A production native-backend synthetic case
passed before atomically changing the finite controller. V7 and original engine
bytes remain unchanged; prior committed bundles retain their actual restore
engine SHA. Supervisor then continued batch 16 with V8. No simulator or GPU
was launched by this infrastructure change.

Five completed synthetic native qualification restores were retired only after
both the current native files and corresponding true164 files passed full SHA
and exact manifest checks. This freed 51,240,960 allocated native bytes; their
old ext4 restore receipts are historical, and the current native restore paths
are explicitly absent. No unique asset or original Source was deleted.
Four frozen plan controls were cold-placed with full SHA/reopen checks and
original-path symlinks, releasing a further 69,108,767 logical native bytes.
The current plans and qualification receipts remain readable from true164.

All original scientific lineages, failures, consumed engineering cases and
semantic HOLDs remain distinct. Infrastructure and byte-integrity PASS does
not establish numerical accuracy, ISA compatibility, EP acceptance, or RTX4080
timing calibration.
