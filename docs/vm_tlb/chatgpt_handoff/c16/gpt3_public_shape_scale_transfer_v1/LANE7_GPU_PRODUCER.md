# Lane 7 — GPT-3公开尺寸Native规模外推 Producer

执行节点：109  
Lane：7  
角色：唯一RTX4080 native producer  
GPU：RTX4080 / SM89  
GPU lock：必须；所有CUDA动作都在锁内  
GPU lock path：`/data/c16/locks/c16_gpu_campaign.lock`  
允许并行：Lane8 CPU prep、Lane6 consumer scaffold、Lane4原任务

任务：`C16_GPT3_PUBLIC_SHAPE_SCALE_TRANSFER_109_V1`

## 1. CPU-only bootstrap可以立即开始

先读取coordination：
- `MASTER_PIPELINE.md`
- 本文件
- 旧A/B与split-state packs

在不初始化CUDA的前提下可以：
- 建独立worktree；
- 核Git与old pack SHA；
- 核accepted A/B binary文件是否存在（只做普通文件SHA，不import extension）；
- 准备输出目录；
- 检查ncu/nsys命令版本；
- 阅读Lane8 prep branch状态。

禁止：
- import torch CUDA extension导致context建立；
- nvidia-smi之外任何CUDA动作；
- 获取GPU lock后长时间做可提前完成的CPU工作。

## 2. 与Lane8流水衔接

Lane8 branch：
`hrl/c16-gpt3-public-shape-prep-174new-v1`

可每120秒fetch一次，最长90分钟。

看到`PRE_GPU_CONTRACT_FROZEN.json`后：
- 可以继续CPU-only核对runner/source；
- 不得GPU执行。

只有看到`PRE_GPU_READY.json`，且：
- branch HEAD/tree与READY一致；
- unit tests PASS；
- memory budget合法；
- expected A/B binary SHA与本机文件相符；
- synthetic formula/version一致；

才进入GPU阶段。

超时则发布`WAITING_FOR_LANE8_PREP`并STOP，不自行补合同。

## 3. Producer branch

以Lane8最终READY commit为base，新建：

`hrl/c16-gpt3-public-shape-scale-transfer-109-v1`

不要修改Lane8 prep历史。

## 4. 单次GPU campaign

所有CUDA工作使用一个外层nonblocking/合法flock acquisition。锁被占用就等待，不偷锁、不删锁、不杀进程。

锁内顺序应最小化峰值和重复初始化：

1. GPU identity / L2 / free memory gate；
2. import accepted A/B extension；
3. 分配一次256MiB conditioner，保留到campaign结束；
4. 依次做EXPAND，再做CONTRACT；
5. 每个operator按“Dense anchor -> W4 correctness/launch -> W4 timing”完成；
6. 限定NCU如需独立进程，仍必须由同一锁wrapper串行调用；不要释放锁让别的GPU任务插入后再继续；
7. 完成后同步、记录nvidia-smi post，释放锁；
8. CPU分析与Git发布全部在锁外。

如果ncu必须为每个profile拉起新进程，可由持锁shell wrapper保持fd锁，并在子进程内运行。

## 5. Track A — FP16 Dense shape anchor

四点：
- EXPAND_M1 [1,12288]×[12288,49152]
- EXPAND_M256 [256,12288]×[12288,49152]
- CONTRACT_M1 [1,49152]×[49152,12288]
- CONTRACT_M256 [256,49152]×[49152,12288]

要求：
- exact Lane8 synthetic formula；
- FP16；
- 每次只保留当前operator的大weight，避免两块1.125GiB同时常驻；
- 10 warmups + 50 CUDA-event samples；
- launch inventory；
- output shape/all-finite；
- 同进程重复执行数值稳定性receipt；
- M256两个方向各1个NCU profile。

Dense基线没有split arm，也没有EVICT条件。它只锚定GPT-3公开尺寸在4080上的真实Dense kernel/traffic规模。

## 6. Track B — W4 split/state proxy

四point × A/B × W/E，共16 cells。

A：
- accepted split8
- 8-plane scratch + reduction

B：
- accepted split1 direct output
- no reduction

同point A/B使用bit-exact相同：
- input
- qweight
- qzeros
- scales

### correctness gate

每个point：
1. A/B shape/dtype一致；
2. all finite；
3. elementwise isclose `rtol=1e-2, atol=5e-2`；
4. 记录max_abs、mean_abs、relative_L2、changed count、SHA；
5. fail则该point不进入timing/NCU。

若任一点失败：
- 其他独立point可继续做correctness以判断scope；
- 禁止time/profile失败point；
- 最终以部分闭合结果STOP，不调容差。

### launch gate

动态验证：
- GEMM grid；
- reduction有无；
- scratch bytes；
- block shape；
- function identity。

必须与Lane8 expected table一致；否则相关point停止解释。

### timing

对每个point使用25 complete mirror blocks：

`A_W, B_W, A_E, B_E, B_E, A_E, B_W, A_W`

每cell最终50 samples。

每个sample前：
- 对目标arm做2次untimed same-arm warmups；
- E cell再完整遍历conditioner一次；
- conditioner在event外；
- 再测目标一次。

记录所有raw samples，不只median。

### NCU

只M256：
- EXPAND A_W/B_W/A_E/B_E
- CONTRACT A_W/B_W/A_E/B_E

8 profiles。

再加Dense EXPAND_M256/CONTRACT_M256两份，共10。

只收冻结指标：
- L1/TEX bytes
- L2 bytes
- DRAM bytes
- duration

A GEMM/reduction分列。
禁止根据counter猜具体tensor。

## 7. OOM和工程问题

正常工程问题solve-and-continue，但禁止改变科学变量。

若显存压力：
优先顺序：
1. 严格按operator串行，释放前一operator tensor；
2. analyzer/日志放CPU；
3. NCU profile独立进程；
4. 不降低M、K、N，不降低conditioner，不改split，不改dtype。

仍OOM则STOP为真实平台限制，不静默缩小问题。

## 8. 输出

Review pack：
`docs/vm_tlb/review_packs/C16_GPT3_PUBLIC_SHAPE_SCALE_TRANSFER_109_V1/`

至少：
- `SOURCE_AND_AUTHORITY.json`
- `GPU_LOCK_RECEIPT.json`
- `SYNTHETIC_TENSOR_RECEIPTS.tsv`
- `MEMORY_LIFECYCLE.json`
- `DENSE_TIMING_SAMPLES.tsv`
- `DENSE_TIMING_SUMMARY.tsv`
- `DENSE_LAUNCH_AUDIT.tsv`
- `W4_CORRECTNESS.tsv`
- `W4_LAUNCH_AUDIT.tsv`
- `W4_TIMING_SAMPLES.tsv`
- `W4_TIMING_SUMMARY.tsv`
- `W4_STATE_INTERACTION.tsv`
- `NCU_KERNEL_ROWS.tsv`
- `NCU_SUMMARY.json`
- `SCIENTIFIC_INTERPRETATION.md`
- `NEXT_174_CONSUMER_CONTRACT.md`
- `RAW_INDEX.tsv`
- `SHA256SUMS`

## 9. producer侧只做描述性解释

必须用中文写：
- 更大的N是否让M1的split1不再严重缺CTA；
- qweight从<L2变为>4×L2后，W/E差异如何变化；
- EXPAND/CONTRACT是否仍不同；
- Dense FP16只作为shape anchor。

不要把producer自己与旧Qwen比较写成最终跨实验结论；最终scale-transfer判断留给Lane6独立consumer。

## 10. Durable与发布

本实验raw不要求像完整模型trace那样大规模入164；但所有timing/NCU/raw CSV/manifest必须可重算并hash-close。

若采用164 durable目录：
- 独立RUN_ID；
- 不覆盖旧run；
- verify/admission/ACK闭合。

最终：
validate -> SHA256SUMS -> commit -> push -> fetch-back commit/tree -> clean -> STOP。

停止后Lane7窗口继续保留为109唯一GPU lane，不自动抓SASS或启动模拟器。
