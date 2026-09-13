# POST-FAST64 paper results analysis

## 范围与证据边界

本分析的主性能结果严格来自冻结的 FAST64 提交 `18a68dcccd795f1b6cda75504e9450d00c9cee02`。后 FAST64 的 Lane-D 观察者数据是诊断证据，绝不进入 FAST12 几何平均。所有数字和图均由随包的紧凑快照重建；没有启动仿真、采集 trace 或改动 Core。

## 主性能

用 12 个未四舍五入的整数周期比值重算，IO 的 GM 为 **1.326143376x**，OO 的 GM 为 **1.592062402x**。这一聚合不能掩盖反例：ATAX、BICG、GESUMMV 的 IO 分别为 0.993065x、0.942017x、0.925562x；OO 仍在这些工作负载中恢复到更快状态。Gaussian 的约 1.108x 收益应表述为温和收益，而非“无收益”。

## 结构压力与 IO→OO 证据

PIB 满、真实 cacheline/all-lines-reserved、Tag-bank 冲突、MSHR entry/merge 满和下游队列事件均为非互斥的累计计数，不能堆叠成 100% 因果分解。IO HOL 使用 `hol_ready_younger_cycles/(64×IO cycles)`，OO 乱序退休使用 `ooo_retires/retire_count`；二者保留精确分母，提供机制相关证据而非唯一因果归因。

## 容量敏感性与观察者诊断

逻辑 Tag、物理池和 PIB 三类 Stage6 曲线仅使用接受的单元，并采用同模式归一化。BICG/GESUMMV 的 16.5-KiB 是非数值资源死锁边界；Btree 16.5-KiB 是保留的数值结果，二者不可混同。D4 对 24/32/48 KiB 的容量做了控制改变，因此它支持“容量改变会产生工作负载相关的端到端敏感性”。它不单独识别 occupancy→inflight→L2→pending lifetime→pending Tag eviction→duplicate→performance 的内部中介箭头。

在 BICG/GESUMMV 中，48 KiB 时 physical-full 的活跃 SM 周期暴露可大幅下降；但 IO 的 no-free/instruction 以及端到端周期未必随之改善。这与解除前端容量约束后出现瓶颈迁移相一致，但不证明 L2 是主导瓶颈。observer_sample_sm_cycles 与 `64×global cycles` 不是同一量，故未互换。

## 重复下游请求

Lane-C 源码语义证明：IO duplicate-after-eviction 只在仍 pending 的线失去 Tag、同一线在旧响应完成前再次成功分配并创建新 lower 请求时递增；响应后的再访问不计数。每个事件对应一个 128-B lower-request payload；它不能称为 DRAM、总内存或总链路流量，也不能被转换成可回收性能。

FAST12 的完整分布反驳了无条件“局部性使重复请求罕见”的说法：LUD、GEMM、2DConvolution、Gaussian 分别超过 5%，其中 2DConvolution 为 42.220%，Gaussian 为 50.200%。展示分箱只是呈现手段，不是“罕见”的科学定义。OO 的精确计数来自限定的 Lane-D 观察者：7 个工作负载的 OO share 更低、3 个更高、2 个均为零；因此 OO 的性能优势不能归结为普遍消除重复请求。

## 局限与开放问题

Tag eviction 总数与 pending-hit 总数都不足以单独解释高重复请求；相关不等于因果。物理池的 D4 控制敏感性仅覆盖 BICG、GESUMMV、Btree，不能外推到其他九项工作负载。当前证据不足以证明 L2 为主导瓶颈，或证明 duplicate traffic 是较大物理池变慢的次级反馈。

## 12 workload explanations

下表的逐工作负载字段和证据范围见 `WORKLOAD_EXPLANATIONS.tsv`；它包含恰好 12 行并保留每项性能、HOL/退休、IO/OO duplicate 及边界。
