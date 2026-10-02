# C16 Stage A：终态独立综合

## 1. 我们实际观察到了什么？

Stage A 先在成熟软件路径中获得了 MP01 BF16 prefill 和 MP05 AWQ control 的合法局部证据；旧 MP02/MP03 eager Graph-OFF 则因生成 token 正确性失败停点。后续把“关 CUDA Graph”和“关编译”拆开后，无 semantic observer 的 Mode A/B 自然生成正确性通过。对 MP02 B1，新的正式原生计时进一步形成一个同点 A/B 子结果：A 中位数 354.59820556640625 ms，B 为 361.45654296875 ms，A 相对 B 少用 1.8974168640064404% 时间。这个有限结果说明此冻结 B1 点对执行模式有可测响应，不说明 B4 或硬件机制。

## 2. 哪些证据真正有效？

本 consumer 从两组 164 durable raw 的 41 个 payload 逐项重算 size/SHA，直接解析 formal 样本与每个 token/logprob；原始 MP02 A/B 各 5 个 formal 请求和 32-token 正确性可用于 B1 同点比较。MP03_A 的 5 个 formal 数值仅是诊断。continuation MP03_B 的两次四行 warmup 输出正确且 compiled Qwen2Model 存在，但它们是 warmup，不是 formal timing。MP01/MP05 的既有合法线索仅在各自原 scope 内保留；MP05 不是 BF16 的一变量精度 A/B。

## 3. 为什么 MP02 有 B1 响应，MP03 没有 B4 pair？

MP02 两臂完成了冻结数量的 formal 请求并通过正确性和身份门槛。MP03_B 原版在旧 cache-path 门槛前停；surgical continuation 的预热前 AOT 身份、两次预热正确性和基本 compiled Mode B 配置均通过，但两次预热后仍在 `e3e9…` AOT root，未达到 PREEXEC 冻结的 `c975…/backbone` 最终路径。该合同的执行身份门槛遂失败，formal=0。MP03_A 不能单独形成 B4 的 A/B 比，也不能被挪来计算 B1→B4 throughput scale 或 Graph×batch interaction。

## 4. 编译路径归因为什么停在 LEVEL_0？

Python 模块 hooks 在 compiled Mode B 观测 warmup 给出 0/4608 范围，六次正式 ON/OFF 样本甚至尚未开始。对既有 compiler cache 的 CPU 产物审计虽然恢复了 FX node→模块/层的**静态**来源，但 Mode B runtime 名称中只有 1/96 个不同 kernel 名能直接、单一地接上语义 family；通用 GEMM/GEMV 无逐调用投影关联，MP03_B 缺 point-bound generated output code，融合边界不能任意拆分。因此既没有可靠的 family-level 时间归属，更没有每层、每 step 的 runtime 边界。无 observer 的 Mode B 正确性 PASS 与 Python-hook 不可见是两个不同事实。

## 5. 四个原始问题各缺什么？

- DQ1：MP01 局部组成仍有效，但 MP02/03 compiled decode 的 family 时间份额不可识别；成熟 Graph-ON whole-run 对应贡献也未闭合。
- DQ2：MP02 B1 同点 A/B 已有效；MP03 B4 缺合法 B formal arm，因而缺 batch/shape 阶梯和交互。
- DQ3：MP01/05 内存/布局线索保留；compiled decode 无可辩护的语义 family/service-time 对应，不能进入 Tier1 归因。
- DQ4a：MP01 有局部时序现象；compiled decode 缺无歧义的 runtime producer→consumer 边界，静态 FX DAG 不能替代。

四问终态分别仍是 `QUESTION_INCOMPLETE`。任何一个局部 PASS 都没有升级成完整 Tier0 surviving problem。

## 6. 为什么停止修 Observer/cache identity？

当前链条已连续尝试 Python hooks、现有 compiler artifacts 映射以及两轮 MP03_B cache 身份恢复。继续换 hook、放宽执行身份、增加 cache policy 或扫描参数，会改变被测 strong compiled path，或使恢复成本开始超过尚未成立的整请求科学 headroom。两次 warmup 正确性已排除“简单推理全错”的说法，却不能合法填补 formal 计时；第三种现场修复没有事前科学门槛。故本轮停止，而不是为了保持采集而再开一次 109。

## 7. 失败的是观测能力，不是被证伪的科学假设

现在**不能**说没有新的架构现象：关键 decode family 时间、B4 A/B、内存服务暴露和 compiled handoff 都未被完整合法观察。可说的是：当前 Stage A 测量/观测链没有形成可进入 Tier1 或 holdout 的完整问题。已有 MP01/MP05 局部线索及 MP02 B1 响应是真实、受限的结果；它们既不证明新机制，也不证明对应假设为假。

## 状态附录

项目分类：`C16_STAGEA_TIER0_TERMINAL_PARTIAL`。旧 MP02/03 MODE_C `STOP_POINT_CORRECTNESS` 不变；Mode A/B 无 observer 正确性 PASS 不变；Python-hook Observer V2 关闭；compiler-native attribution `LEVEL_0_UNRESOLVED`；DQ2 仅 B1 子结果恢复；四问全为 `QUESTION_INCOMPLETE`，formal Tier0 survivor=0。Stage A V2、Tier1、MP04/MP08 holdout 与机制 promotion 均不 ready；不输出 `NO_NEW_ARCHITECTURAL_PHENOMENON_FOUND`。
