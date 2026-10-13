# AWMA 下一阶段科研优先级审查（CPU）
日期：2026-10-13，Asia/Shanghai。Stage：`AWMA_CPU_RESEARCH_PRIORITY_REVIEW_174NEW_V1`。
入口：[最终科研判断](FINAL_RESEARCH_JUDGMENT.md) → [实际论文实验组](PAPER_EXPERIMENT_GROUPS.tsv) → [条件性最小设计](CANDIDATE_MINIMAL_TESTS.md)。

终态：`READY_FOR_INDEPENDENT_AWMA_REVIEW`；科学选择：`NO_QUALIFIED_CANDIDATE_YET`，**0 个立即值得启动的已资格化实验，0 个硬件候选**。数值线建议暂存；动态图线保留具体问题和条件性设计，但模型后端兼容与自然更新输入尚未闭合。完成一轮数值证据、原文实验组、源码兼容性和设计合并审查。

起点 commit `e32c47d4b54dac25bce94cc8020657e8932f3d26` / tree `8a5eb49d7de8ff2e3ec78f2f7caaac110d5ba947`。独立分支 `hrl/awma-cpu-research-priority-174new-v1`。只读协调版本 `4e5953c189792dd5a4ac5c13c33ba922b8c2a1e9`。

证据分层：`ACCEPTED_NATIVE` 为已接受的旧原生结果；`CPU_RECHECK` 只重新核 published 数值；`PAPER_AUTHOR` 为原论文特定组；`SOURCE_ONLY` 为固定源码/官方接口；`SIM_SCOPE` 为指定模型；`HYPOTHESIS/UNKNOWN` 未获得实测。表中有 5 个已核实际论文组，来自 Sobek/Kitsune/VTC 三个独立 primary 来源；ALCHEMI 一行是官方 API 案例，明确不计性能实验组。论文全文与临时截图均不进 Git。

没有 GPU/CUDA/JIT/profiler、模型计算、Accel-Sim、新性能实验、数据集/权重下载或大型 raw 复制。CPU 检查脚本只用标准库读取 Git 小文件。历史结果、协调分支、容差和输入均不改。
