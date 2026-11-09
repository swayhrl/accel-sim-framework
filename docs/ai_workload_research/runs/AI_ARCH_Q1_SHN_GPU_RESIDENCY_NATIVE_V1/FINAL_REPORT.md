# AI-ARCH Q1 shN GPU 驻留与原生反事实 V1：执行报告

Goal：`AI_ARCH_Q1_SHN_GPU_RESIDENCY_NATIVE_V1`。独立分支：`hrl/aiarch-q1-shn-gpu-residency-109-v1`。执行基线为已接受 Q1 `5787826ca21f7af958e6e1c1f828d62fd58a1ec4`，本轮候选及冻结计划的事前提交为 `8e8c15472b5ab211d1108d97672c43757cfbc891`。本报告是新候选执行证据，待独立科学审查，不修改协调层已接受结论。

## 结论

在 109 RTX 4080、GS-Scale/Mill19 Rubble 的两个原生晚期 50 目标 camera 加 closure 窗口，`shN` 参数、梯度与两份 moments 改由 GPU 驻留和更新，**没有改善完整 Host 窗口**。发现窗 5 对有 4 对 ON 慢，独立验证窗 5 对全部 ON 慢。验证窗 OFF 中位数 9.254 秒、ON 16.792 秒，ON 的中位数相对 OFF 增加约 81.5%。冻结的 5 对配对 `OFF/ON−1` 中位数分别为发现 −21.26%、验证 −43.72%；该量不是训练质量或严格同工速度证明。

本轮完成执行与有边界的短窗采样数值资格；正式时延是**描述性退化**。可见数和更新数有 1 至数个 Gaussian 的微小波动，连 OFF/OFF 预热也出现，故不宣称逐项完全相同的轨迹或工作量。没有晋升 GPU 驻留硬件候选，也没有启动下一机制、第二场景或长程训练。

## 身份、方法与数值

- ON 为明确 opt-in `shn_resident=true`；默认 OFF 走冻结 Q1 的原训练变换。原 means/scales/quats GPU 路径、opacities/sh0 CPU 路径、CPU 上的 `U`/counter、Adam 规则、FP32、deferred pending 与自然 camera 顺序保持。原 trainer 与 CPUAdam C++ SHA-256 及本轮工具哈希见 [SOURCE_FREEZE.json](SOURCE_FREEZE.json)。
- 从只读 canonical `C_D(next15140)` 与 `C_FINAL(next15301)` 恢复。两次四步 OFF/ON 资格均满足事前固定的 `max_abs <= 2e-6 + 2e-4×reference_max_abs`：各 20 项采样字段检查全 PASS，最大绝对差均 `7.4505806e-9`。范围仅为 512 行确定性 `shN` 采样及下一 camera 前 128 行，不能证明全状态、逐 bit 或 200000 步质量等价。原始 [发现窗审计](NUMERIC_AND_FRONTIER_AUDIT.json)与 [C_FINAL 审计](NUMERIC_AND_FRONTIER_AUDIT_C_FINAL.json)保留。
- `C_FINAL` 的 bundle/sidecar 校验、语义指纹和恢复 frontier 成立；恢复时 pending15300、prepared15301 存在，实际自然续行到末端 pending15361、prepared15362。旧格式 `legacy_equal=false` 保留，不改写成字节级轨迹等价。四项验证预热的 51 个 camera ID 完全一致，与原 Q1 发现/验证目标样本均零重叠；[预正式核查](PRE_FORMAL_VALIDATION_AUDIT.json)记录了序列和微小工作量波动。
- 正式 OFF 不安装逐操作 observer。每个完整样本都记录了 50 目标 camera 加一个自然 closure、实际 step/camera、`N`/visible/updated 和末端 frontier；任何不完整样本均不得补造。实际 20 个正式样本、8 个预热、4 个独立诊断均完成。计划、顺序和随机种子在观察结果前冻结；完整 [样本表](FORMAL_SAMPLES.tsv)与 [复算](FORMAL_ANALYSIS.json)记录全部区组。

## 完整窗口性能

测量是同一资源窗口中从同一 canonical 状态独立恢复的 Host monotonic 闭合窗口，目标 camera 区间分别为 `[15150,15200)` 与 `[15311,15361)`，对应 closure 为 15200/15361。下表 median/MAD 单位为秒，均为每策略 5 个正式样本。百分比为 5 个配对 `100×(OFF/ON−1)` 的中位数，负值表示 ON 更慢。

| 窗口 | OFF median / MAD | ON median / MAD | ON−OFF 配对差中位数 | 配对速度变化中位数 | ON 较慢的对数 |
|---|---:|---:|---:|---:|---:|
| 发现 C_D | 9.243 / 0.193 | 11.988 / 1.217 | +2.548 | −21.26% | 4/5 |
| 验证 C_FINAL | 9.254 / 0.039 | 16.792 / 3.076 | +7.342 | −43.72% | 5/5 |

同 phase camera、总 N 和闭合 frontier 一致。相对首个预热，正式与预热的可见数总和最大偏差 3、更新数总和最大偏差 1；配对差见复算文件。两次 OFF 预热本身也有这种量级的波动，不能把它全部归给 ON。该幅度远小于观测的秒级退化，但它阻止严格“逐项同工”表述。新 OFF 同期采样是本轮比较基线；旧 Q1 T16 数值只作历史参照，不替代本轮 OFF。

## 容量、资源与诊断

静态唯一 storage 推导为 `shN` 参数加两份 moments 3.379784 GiB，若 dense gradient 同活为 4.506378 GiB。正式 ON worker 的 Torch allocated/reserved 最大为 7.260/7.918 GiB（OFF 为 2.751/3.045 GiB）；第二窗口自身 NVML 峰值 7.992 GiB。上述指标含不同层次且可能重叠，不能相加为显存需求。采样 Host RSS 峰值 18.694 GiB、独立 session charged 峰值 10.683 GiB；末端 OS reap 期间 RSS 未连续采样，charged 峰值保留。详情见 [LIVE_STORAGE_PEAK.json](LIVE_STORAGE_PEAK.json)。

两次顺序 GPU 窗口持锁 274.806 与 2753.311 秒，累计 3028.117/5400 秒。34 个第二窗口 worker 均以 0 退出；共同锁、预约和自身 GPU 上下文均已释放，NVML 已关闭。第二窗口 1740 个资源样本无监测缺口；私有盘最大新增 364,739,271 字节，MemAvailable 最低 47,544,807,424 字节。共享桌面 per-process 活动归因仍不可用，因此不称独占环境。见 [RECEIPT.json](RECEIPT.json)及完整 [RESOURCE_RECEIPT.json](RESOURCE_RECEIPT.json)。

分离的 OFF 诊断中，51-camera 窗口的 CPU Adam Host 区间合计为发现/验证 3.439/3.510 秒，全部 CPU 参数 forwarding 区间为 2.920/2.871 秒；这些不是 `shN` 专属可回收关键路径。OFF 逻辑 copy operand bytes 和 Host 调用区间见 [COST_LEDGER.json](COST_LEDGER.json)，不等于 PCIe/DRAM 物理流量。ON 的正式和诊断路径没有逐操作 transfer/region observer，因此 ON 新 GPU 更新、索引和版本协调成本没有逐项闭合；CUDA event span 含 launch 间隙，且不能跨未校准时钟与 Host 区间相减。当前证据支持“该具体实现净退化”，不能唯一归因为某一 kernel、PCIe 或 overlap 因素。强软件基线仍为原 T16 OFF。

## 合同偏差与科学边界

第一 GPU 窗口将私有 `TORCH_HOME` 指向空缓存后，原 runner 自动下载 244,408,911 字节（约 233 MiB）AlexNet 权重，**违反本 Goal 的“不下载模型”限制**。下载已结束，第二窗口使用该缓存；下载时段不属于正式性能样本。这一偏差不被事后抹除，执行收据标为 `COMPLETE_WITH_DISCLOSED_DEVIATION`。

本结果不证明完整训练质量等价、全状态逐 bit 等价、GPU 硬件因果或 PPA。候选短窗数值门通过，但完整窗口有微小状态/工作量抖动；容量在本次窗口可运行，而局部 CPU 工作减少未转化为净收益。维持 `NO_HARDWARE_CANDIDATE_PROMOTED`，本 Goal 已 STOP。
