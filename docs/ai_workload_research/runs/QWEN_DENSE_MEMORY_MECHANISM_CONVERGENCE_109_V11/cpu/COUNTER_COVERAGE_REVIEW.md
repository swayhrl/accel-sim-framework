# Counter coverage CPU review

Prefer six new counter nodes total: layer0 O/gate_up/down in each of B1/B2. Reuse V10 QKV counters.

The previous regex `.*(gemv|gemm|cutlass).*` also matches FlashAttention names containing cutlass::bfloat16_t. On each existing first decode it matches 217 kernels, including 72 non-dense kernels. CPU replay of `(internal::gemvx::kernel<|cutlass::Kernel2<.*gemm)` matches 145 Dense kernels with no false positives/negatives:144 inside the graph plus one external lm_head.

Use `--graph-profiling node --replay-mode kernel --profile-from-start no --nvtx --nvtx-include decodeGraph/ --filter-mode global --kernel-name-base demangled --rename-kernels off --kernel-name 'regex:(internal::gemvx::kernel<|cutlass::Kernel2<.*gemm)' --launch-skip 1 --launch-count 3 --kill no --clock-control none --cache-control none --disable-extra-suffixes --metrics dram__bytes_read.sum,gpu__time_duration.sum`. Worker must explicitly start/stop profiling around the first warmed decode graph. This command template was not executed.

launch-skip/count operate on matching launches. launch-skip-before-match counts all launches. kernel-id invocation is counted per ctx/stream/name/grid/block/shared identity, not one combined Dense sequence. per-launch-config changes ordinal semantics. Historical graphNodeId is not an NCU kernel-id selector.

Compiled layer0 order is QKV,O,gate_up,down. Skip1/count3 selects O/gate_up/down; count6/8 would cross another QKV. If 6/8 nodes per mode are required, separate profiler domains can select skip1/count3, skip5/count3, and optionally skip10/count2. These repeated runs cost initialization budget. The smallest plan is 3 nodes per mode, 6 total.

B1 targets have grids 512, 5504, 512; down has block 32x4 versus O/gate 16x4. B2 O and down share name,grid 8x16,block 32x1 and shared 16896:order plus compiled contract is necessary. Source-consistent attribution is not raw matrix-argument capture.

Every result must independently show one pass. Multiple selected kernels do not inherently enlarge the metric set per kernel, but actual pass counts remain unproven until executed. A missing backup counter remains null: V10 one-pass evidence plus the installed guide supports no-save/restore inference, not measured zero bytes.

The old V10 CSV audit reads only its first data row. Multi-node audit must inspect every row, expected total/order, exact identities, metric units/finite values and per-row passes. Any later multi-pass row must fail. Keep native timing/numeric/resource checks independent.

JSON records source SHA/line anchors, full target maps, CPU filter replay, historical evidence and measured CPU-process RSS. No GPU/CUDA/NVML initialization, profiler/query, model import or model-weight reading occurred.

## Supplemental DOWN clock/tensor pilot review

CPU streaming of the existing V9 metric query confirmed all four exact names and the retained SHA256, without a new GPU query. Candidate A is read+duration+SM elapsed cycles+tensor active; candidate B removes tensor active; fallback is the V10 verified read+duration pair. Actual pilot pass count decides the native plan. The original tensor-active metric is present but deprecated in favor of its v2 base name; do not silently change candidates.

`sm__cycles_elapsed.avg / gpu__time_duration.sum_ns * 1e9` is only a profiled-kernel elapsed-SM-cycle-rate proxy. The cycle count averages SM instances; duration may use measured_user or wallclock. It is not direct clock telemetry or stable-frequency proof.

Call the tensor metric tensor-pipe activity percentage. It measures active-cycle rate relative to peak sustained elapsed rate; it does not alone prove a compute bottleneck, FLOP throughput, occupancy or whole-model compute-bound behavior. Low B1 tensor activity may reflect its GEMV implementation rather than a limiting resource. Every native selected row still needs an independent one-pass audit after pilot success.
