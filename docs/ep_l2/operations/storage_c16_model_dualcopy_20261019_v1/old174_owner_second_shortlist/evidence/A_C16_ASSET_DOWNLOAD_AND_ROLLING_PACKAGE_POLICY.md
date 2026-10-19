# C16 A asset-download and rolling-package policy

Lane A is limited to local asset download/verification, immutable rolling
packages, and fixed-commit package handoff to G-runtime.  It does not rent or
operate AutoDL/GPU hardware and performs no model load, profiler, NVBit,
simulator, SASS, or full-ROI action.

## Priority and recovery

The five existing Qwen2.5-7B raw/AWQ `curl` streams are Wave-1 highest
priority.  Their command, protocol, concurrency, and partial files are not
changed by A.  Qwen3-30B-A3B is one low-priority worker at immutable revision
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`; it starts only at real filesystem
availability of at least 85 GiB and pauses only its own worker below 15 GiB.
No deletion is an admission or recovery action.

`/workspace/c16_assets/c16-a/download_logs/DOWNLOAD_PROGRESS.tsv` is local
telemetry, not a cross-lane input.  It records per active worker expected and
current bytes, elapsed time, retry evidence, recent throughput, and last growth
time.  A worker is eligible for a single resume/range recovery only when its
process is inactive **and** telemetry proves no byte growth for about 15
minutes.  The monitor never initiates that recovery itself.

After both P2 and P3 close, Qwen3-30B may be trialed at two and then at most
three workers.  Each trial must record aggregate throughput before and after;
if it does not clearly improve total throughput, concurrency returns to the
lower level.  It remains a Wave-2 asset and is not for RTX3090, P0--P3, or CPU
offload.

## Hash closure and packages

An admitted checkpoint follows fixed revision URL, complete byte count, frozen
expected size, one whole-file SHA-256, then an `IMMUTABLE_VERIFIED` receipt.
Temporary `.curl.download`, `.partial`, and `.incomplete` files are never
assets.  The Wave-1 finalizer is I/O idle-priority and consumes a prior receipt
plus current byte count after admission instead of rescanning an accepted large
file.  P2 is reserved for `c16_qwen25_7b_raw_reference`; P3 is reserved for
`c16_qwen25_7b_awq`.  They publish independently in whichever order closes.

Each P2/P3 handoff to G-runtime names A's fixed commit, package ID, package
manifest SHA-256, local model root, total bytes, and model/tokenizer revision.
P0/P1/P2/P3 directories are immutable: no correction modifies an existing
package identity.

The already-running 30B worker predates this policy update and remains
untouched to preserve its active transfer.  Its live progress is not an
immutable receipt; no 30B shard is claimed verified until an eligible receipt
exists.  Future worker invocations use the single-hash receipt protocol.
