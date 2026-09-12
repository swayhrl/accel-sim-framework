# C16 Lane G — AutoDL Native Execution and Bounded Capture

Goal: `C16_G_AUTODL_NATIVE_EXECUTION`。

Branch target: `hrl/vm-c16-g-native-gpu-v0`。

Lane G 是唯一默认允许 C16 使用租赁 GPU 的执行窗口。其职责是“真实运行 + 轻量 census + 少量计数/trace”，不是 simulator 窗口。

## 负责阶段

预租期：C16-0.3、0.4、0.9 协作。
GPU期：C16-1.1~1.6、C16-2.1~2.6、C16-4.1~4.3。

## G0 — 租GPU前准备

在本地服务器完成：
- `bootstrap_autodl.sh`，可重复执行；
- exact wheel/package lock；
- `run_model.py` + model adapters；
- scenario driver；
- NVTX ranges；
- nsys/ncu/nvbit wrappers；
- receipt schemas；
- no-GPU/mock tests；
- target selection second-pass identity guard。

禁止把“到AutoDL再现场写runner”当正常流程。只有与目标driver/GPU相关的必要编译允许在GPU实例上做。

## G1 — C16-1 inline qualification

### G0 native

用 Qwen2.5-0.5B S0：B1/T128/Decode4。
必须确认：GPU device、dtype、attention backend、output checksum、peak memory、no CPU fallback。
通过后立即开始该deployment的 unprofiled baseline。

### G1 nsys/NVTX

同一canary确认：完整 launch activity、stream、kernel name、correlation/NVTX linkage、profile region。
记录profile wall overhead；如果>10%，先缩减采集字段/范围并复测。仍高则时长字段标 `PROFILE_PERTURBED`，语义目录仍可保留。

### G2 NCU

先 `--query-metrics`/等价查询，冻结 C16 可用 metric set。只对一个小目标做 bounded test，记录 replay/cache-control。不可用的counter写 `COUNTER_UNAVAILABLE`；不要换名字相近的指标冒充。

### G3 NVBit

先小CUDA fixture，再单个模型kernel。实际验证 `DYNAMIC_KERNEL_RANGE`/目标过滤，不只读README。证明 target-in、target-out、terminal trace、stats/kernel identity closure、size/time guard。

G2/G3失败不阻塞G1 census。

## G2 — C16-2 native census

### Baseline

每scenario：2 warmup + 3 unprofiled measured。同步边界固定。保存median/min/max/CV和output checksum；CV超工程门限最多补到5次，所有run保留。

### Census

另一次 nsys pass 获取完整但轻量的 kernel catalog，不生成 full SASS。
至少输出：launch identity、device/context/stream/correlation、kernel name、grid/block、start/end/duration。

### Runtime implementation audit

通过直接runtime/backend证据记录：
- attention backend；
- KV representation/layout；
- raw/AWQ quant/dequant/repack；
- MoE router/expert/dispatch；
- CUDA graph/compile state；
- logits policy。

架构上的 MLA 与运行时真正缓存的对象必须分开。

### Semantic map

利用 NVTX/module hook/runtime metadata 关联 operator/layer/shape/dtype。名字启发只能作为弱证据，不允许覆盖 UNKNOWN。目标是累计GPU time >=95%有可审语义或复合语义；达不到则保留coverage gap。

### Wave-1先发布

完成 Llama3.2-1B、Qwen2.5-0.5B、Qwen2.5-7B raw、Qwen2.5-7B AWQ 的可用部分后，先commit/push小型目录和manifest，让C/H开始；GPU继续Wave-2。

## G3 — certainty-unit协作

基于未profile baseline + census时长，按冻结规则标certainty候选：
- 单launch >= phase GPU time 1%；
- E/O、KV management、MoE router/dispatch、rare implementation；
- stratum size<=2。

G只提供事实表，最终采样权重由C实现。

## G4 — C16-4 NCU/NVBit

### NCU先行

只跑C冻结的representative target。每个结果带target semantic/shape/grid/block identity、metric names、tool version、replay/cache-control scope。

### NVBit target freeze

读取C/H/A已提交的 `NVBIT_TARGET_PLAN.tsv`。第一轮通常4~6窗口/deployment，不要求跑满。第二次运行必须重新核对target identity，不能裸kernel ordinal直接join。

### Capture budget

每窗口：4GiB或20min先到即停；首轮raw总量<=64GiB；一张GPU同时一个capture process。超过即 `BOUNDED_PARTIAL`。

raw不提交Git；保存到AutoDL本地盘并尽快rsync回本地，Git只提交 `TRACE_MANIFEST.tsv/TRACE_STATUS.tsv/RAW_INDEX.tsv`。

## AutoDL专用纪律

- 不在租赁时下载本可本地准备的大模型，除非本地资产确实缺失且用户重新授权。
- 不在GPU空闲时扩大模型/场景/trace矩阵。
- 不运行Accel-Sim/GPGPU-Sim长仿真。
- 每个新deployment先baseline再profile；profile结果不能替代unprofiled timing。
- 任何自动回退CPU、dtype/backend变化都使该run无效，除非作为新的deployment identity重新登记。

## G终态

理想：`C16_G_NATIVE_CENSUS_AND_BOUNDED_CAPTURE_READY_FOR_REVIEW`。
若G1有真实census但G2/G3能力受限，可仍READY并明确counter/trace gap；若连真实census都不足，则 `PARTIAL_READY_FOR_REVIEW`。