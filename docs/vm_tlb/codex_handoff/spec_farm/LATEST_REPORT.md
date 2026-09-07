# Window B：SPECULATIVE EXPERIMENT FARM B6 closeout

状态：`SPECULATIVE_DIAGNOSTIC`；低资源机会式模式下的透明 partial closeout。没有将任何结果合入或传播到 Window A。

## 隔离与来源

- Framework：`hrl/vm-spec-farm-v0`，起点 `eb18c43c516bdcd52c164969df10d97b895f45f1`。
- Core：`hrl/vm-spec-farm-v0`，起点 `0d92e6aa8fd8bc885ffdf081a559bc616aaa85fd`。
- B 专属 worktree：`/workspace/worktrees/{accel-sim-vm-spec-farm,gpgpu-sim-vm-spec-farm}`；B 专属 scratch：`/workspace/vm-spec-farm/`。
- 独立 binary SHA-256：`2d6f825faf71e4aa9acc8d62e98186c9d7c1a92ecd2c41cbfd108e918de44915`。
- Window A touched：**NO**。

## B0 与当前资源门控

- 主机为 512 逻辑 CPU、256 物理核心、2 socket/NUMA。B0 校准的吞吐膝点为 `FARM_CONCURRENCY_V1=32`；该值没有恢复使用。
- 当前有效并发固定为 **1**，只曾运行有成功先例且已校准的 decode1 smoke。
- B2 smoke 的已观测内存画像：prefill `n=16`，中位/P95/最大 RSS 均为 `626688 KiB`；decode1 `n=24`，中位/P95/最大 RSS 均为 `204800 KiB`。
- 最近 20 秒资源窗口：`MemAvailable` 最低 `26572528 KiB`，SwapFree `32 KiB`，出现 `2` 次 swap-in。尽管 iowait 为 `0.014%`，swap 是硬保护信号；因此 **不启动新的 B worker**。
- cgroup v2 存在，但 B 不能安全写入委派子树；未修改宿主 cgroup。B worker 仅使用 B 自身的 `taskset`、`nice` 和 `ionice`。

## 已完成的 speculative 产物

- B1 原子 partial 完整性：prefill `134/692`、decode1 `96/740`，均保留且有审计清单；全局 reducer、phase union、重用距离和 cross-kernel 指标没有在低内存下伪造。
- B2 smoke 语义完成 `37/54`，尚缺 `17/54`。本轮低资源模式安全追加了 `walkers=32/decode1` 和 `PWC-off/decode1` 两项；所有已完成 B2 行仍为 `SPECULATIVE_DIAGNOSTIC`。
- B3：20 个 smoke 的 **planned** 几何数值预检全部通过；没有声称为 realized 或运行时 cache 结果。
- B4：BFS、Hotspot、SRAD 三类 immutable conventional traces 的清单/格式静态检查完成；12 个 smoke 和 12 个 full 回放均未启动，因为此工作负载类没有独立的 RSS 校准。
- B5：18 个 smoke grid 行的 **planned** 几何数值预检全部通过；未运行 TLB×L2 grid，因为 B2/B3 的运行时基线和资源健康条件均不满足。

## 明确缺口与恢复条件

- B1：剩余 prefill 558、decode1 644 个 kernel partial；在恢复前先以单 worker 记录 miner/reducer peak RSS。
- B2：17 个 smoke，以及所有连续 full ROI，均待资源恢复后从语义去重 retry list 继续；不得把 stateful ROI 切成每 kernel 一个 simulator。
- B3/B4/B5：仅计划/静态验证，所有真实回放 deferred。
- 恢复前须满足：对候选 job class 有实测峰值、有效并发仍为 1、启动前窗口无持续 swap、iowait 可接受、并且 `MemAvailable > max(4×peak, 最近波动+2×peak)`。常规模式的原始 `20% + 4 GiB` 恢复线保持不变。

## B6 审查包

完整入口在 [VM_SPECULATIVE_EXPERIMENT_FARM](../../review_packs/VM_SPECULATIVE_EXPERIMENT_FARM/)。其中包含 B0 校准、B1 覆盖账本、B2 结果账本、B3/B5 planned 几何、B4 deferred 矩阵、失败/替代记录、原始日志路径索引及本次 resource gate。日志全量 SHA-256 在低资源 I/O 保护下标为 deferred，而非遗漏或伪造。

本报告及审查包内所有结果均为 `SPECULATIVE_DIAGNOSTIC`；没有 `FORMAL` 结论。

## B7 analysis-only 后续

已完成纯离线 B7 synthesis，且没有恢复 worker。详见 [B7_PARTIAL_FARM_EVIDENCE_SYNTHESIS.md](B7_PARTIAL_FARM_EVIDENCE_SYNTHESIS.md) 与 [B7 审查包](../../review_packs/VM_SPECULATIVE_EXPERIMENT_FARM/B7_PARTIAL_FARM_EVIDENCE_SYNTHESIS/B7_SYNTHESIS.md)。
