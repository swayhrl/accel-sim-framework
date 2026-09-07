# B_LOW_RESOURCE_OPPORTUNISTIC_MODE（`SPECULATIVE_DIAGNOSTIC`）

有效并发固定为 1。仅已校准的 decode1 smoke 类允许在无持续 swap、可接受 iowait、且 MemAvailable 大于 `max(4×peak, 最近波动+2×peak)` 时启动。

已观测 decode1 smoke 峰值 RSS=204800 KiB；prefill smoke 峰值 RSS=626688 KiB。发现快速内存下降后，停止新增高负载 B 作业；B1 reducer/miner、B3/B4/B5 实际回放均延后。
cgroup v2 存在但委派子树不可写，因此没有改变宿主 cgroup；B worker 使用 taskset、nice、ionice。
