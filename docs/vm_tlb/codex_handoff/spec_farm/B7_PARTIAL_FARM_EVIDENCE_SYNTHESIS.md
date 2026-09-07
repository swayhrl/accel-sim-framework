# B7：partial farm evidence synthesis

状态：`SPECULATIVE_DIAGNOSTIC`。本阶段只执行了现有 Window-B artifact 的 streaming/offline 分析；没有启动 accel-sim、生成 trace、重建、补跑任务或访问 Window A。

## 发布状态

- B6 提交 `04d269244db9ab9273c080ffbe8a04db521ae575` 已推送。
- 本地 `HEAD` 与 `origin/hrl/vm-spec-farm-v0` 在推送后均为该 SHA。

## 覆盖矩阵

106 个 workload/config/ROI 行分类如下：

- `REAL_PASS`：0
- `REAL_PARTIAL`：2（B1 prefill/decode1 的 atomic trace partial）
- `SMOKE_ONLY`：37（B2 单 kernel continuous replay）
- `PLANNED_ONLY`：38（B3 20、B5 18；仅 planned geometry）
- `STATIC_ONLY`：12（B4 BFS/Hotspot/SRAD × 4 config）
- `MISSING`：17（B2 尚未有 smoke）

因此没有任何配置具有完整 ROI 的真实通过证据。

## 已有 partial characterization

- B1 prefill：134/692 kernel partial（19.364%）；累计 9,853,745 条 memory instruction、304,904,196 lane reference、1,843,016,208 requested bytes。已覆盖部分的 exact-adjacent lane 比例为 47.567%。
- B1 decode1：96/740 kernel partial（12.973%）；累计 1,850,097 条 memory instruction、55,011,093 lane reference、324,547,612 requested bytes。已覆盖部分的 exact-adjacent lane 比例为 77.759%。
- prefill/decode1 的已覆盖对象 lane 比例分别为：WEIGHT 15.992%/4.914%，KV_CACHE 4.949%/4.121%，UNKNOWN 79.060%/90.964%。覆盖比例不同，不能将其解释为完整 phase 的对象组成差异。
- B2 的 TLB/PTW/MSHR/PWQ/PWC/PTE 与对象归因已从既有 log 流式抽取。522 项 B1/B2 提取守恒检查全部通过。

## 可观测差异与证据不足

- 唯一强 smoke 信号是 `b2-pwc-off/decode1`：PWC hit/miss 从 1/5 变为 0/0，PTE request 从 7 变为 8，IPC 相对基线为 -1.0583%。WEIGHT PTE request 为 3→4；UNKNOWN 仍为 4。
- `b2-l1tlb-e16/prefill` 仅有小差异：L2-TLB miss 815→808，IPC +0.0274%。
- 其它已完成 smoke 在选定 TLB/PTW/MSHR/PWQ/PWC 指标上没有检测到差异。
- 上述均为单 kernel smoke，不是 full-workload 性能、瓶颈或因果结论；full ROI、B1 phase union/reuse、B3 runtime cache、B4 non-LLM 和 B5 interaction 证据均仍缺失。

## A terminal 后的第一小批建议

前提始终是 clean no-swap gate、有效并发 1、且只在 Window A terminal 后执行。

1. B2 decode1：PWC finite-32、finite-512、ideal 三个 smoke。
2. B2 decode1：2MB diagnostic、VM-disabled、ideal-identity 三个 smoke。
3. 若以上稳定，依次做一次 B1 decode1/prefill trace-miner worker 的 peak-RSS 校准；校准通过后才恢复 B1 partial。

完整的 1,321 条恢复条目（1,319 个缺口加 2 个校准前置）按信息增益、资源成本和缺口排序于审查包中。B3/B4/B5 smoke 与所有 full ROI 均排在上述小批之后。

## 审查包

- [coverage matrix](../../review_packs/VM_SPECULATIVE_EXPERIMENT_FARM/B7_PARTIAL_FARM_EVIDENCE_SYNTHESIS/EXPERIMENT_COVERAGE_MATRIX.tsv)
- [B1 phase partial comparison](../../review_packs/VM_SPECULATIVE_EXPERIMENT_FARM/B7_PARTIAL_FARM_EVIDENCE_SYNTHESIS/B1_PHASE_PARTIAL_COMPARISON.tsv)
- [B2 observed differences](../../review_packs/VM_SPECULATIVE_EXPERIMENT_FARM/B7_PARTIAL_FARM_EVIDENCE_SYNTHESIS/OBSERVED_BEHAVIOR_DIFFERENCES.tsv)
- [resume priority](../../review_packs/VM_SPECULATIVE_EXPERIMENT_FARM/B7_PARTIAL_FARM_EVIDENCE_SYNTHESIS/RESUME_PRIORITY_V1.tsv)
- [provenance](../../review_packs/VM_SPECULATIVE_EXPERIMENT_FARM/B7_PARTIAL_FARM_EVIDENCE_SYNTHESIS/B7_INPUT_PROVENANCE.tsv)

所有 B7 文件均为 `SPECULATIVE_DIAGNOSTIC`，不可提升为 `FORMAL` 证据。
