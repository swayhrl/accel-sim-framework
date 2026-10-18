# Handoff to Lane AG

先消费`Core_SHA`、`SOURCE_AND_TOOLCHAIN.json`、`PUBLICATION_RECEIPT.json`和`SHA256SUMS`核固定父X2及AE source/blob/工具链/两个CPU ELF。实现分支：`hrl/iscas2027-dtc-lane-ae-tag-hash-core-174-v1`；审查分支：`hrl/iscas2027-dtc-lane-ae-tag-hash-174-v1`。只发布本AE包，不写AG或其他Lane工作树。

审查范围：固定单hash、bank与set各调用点一致、历史probe recency不变、negative收益保留、固定资源/延迟/quota、K1 old owner生命周期。`CPU_CASES.json`137项是CPU frontend资格；所有原始输出在AE独立external目录，仅约3MB，未提交。

未完成/不授权事项：完整Core/libcudart/trace构建及其实际动态绑定、完整LDST/SASS/NoC/DRAM、应用性能/值正确性/跨SM coherence、硬件面积/时序、C+对等hash实验。本轮仅两次CPU编译，完整sim/native应用/GPU运行均0；不应直接启动AA完整模拟或消费旧论文结果充当hash结果。

如仅需核收据，用Python/源码/Git read-back即可，无需再编译。`run_cpu.py`保留编译次数硬闩，本轮external lock已为2，不能在本Goal内重置以绕过限额。后续新增构建/运行应按AG自己的明确授权和预算处理。
