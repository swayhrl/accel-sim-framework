# START HERE — C12_OPERATOR_AWARE_CHARACTERIZATION

目标：在**不干扰正在运行的 C12** 的前提下，建立 Kernel/Operator-aware 的只读离线分析，并把现有“Prefill/Decode × Weight/KV”结果细化到 Attention/FFN/Other。

## 必须使用独立 worktree

推荐：

```bash
cd /workspace

git -C /workspace/accel-sim-framework fetch origin

git -C /workspace/accel-sim-framework worktree add \
  /workspace/worktrees/accel-sim-vm-m4b-operator-aware \
  origin/hrl/vm-m4b-operator-aware-v0

cd /workspace/worktrees/accel-sim-vm-m4b-operator-aware
```

如果本机 Framework 主仓库路径不同，先定位已连接 `swayhrl/accel-sim-framework` 的现有 clone，再建立等价独立 worktree。不要因为路径不同而停止。

## 进入 Goal mode 后先读

```text
1. docs/vm_tlb/chatgpt_handoff/operator_aware/C12_OPERATOR_AWARE_CHARACTERIZATION_GOAL.md
2. docs/vm_tlb/chatgpt_handoff/operator_aware/C12_OPERATOR_AWARE_ACCEPTANCE.md
3. docs/vm_tlb/chatgpt_handoff/operator_aware/C12_OPERATOR_AWARE_OPERATOR_TAXONOMY.md
4. docs/vm_tlb/chatgpt_handoff/operator_aware/C12_OPERATOR_AWARE_RESULT_SCHEMA.tsv
5. docs/vm_tlb/chatgpt_handoff/operator_aware/C12_OPERATOR_AWARE_REFERENCE_ANCHORS.md
```

然后按 Goal 文档连续执行 OA0→OA5，不要逐阶段等待用户确认。

## 关键执行约束

- C12 source branch `hrl/vm-m4b-speculative-v0` 只读；
- Core 只读；
- 不启动 simulator replay；
- 不向 C12 live worker/scheduler/finalizer 发 signal；
- 只消费 terminal PASS arm；
- semantic kernel name 必须读 embedded trace header；
- operator direct classification 优先使用 runtime `weight_layout` parameter range；
- `UNKNOWN` 保持 UNKNOWN；
- heuristic classification 与 formal direct evidence 隔离；
- 普通工程/路径/parser问题主动解决，不直接停止；
- 等待 C12 最后两个arm不是 hard blocker，先完成可做分析并定期 fetch source branch。

## 输出

Review pack：

`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C12_OPERATOR_AWARE_CHARACTERIZATION/`

Codex回报：

`docs/vm_tlb/codex_handoff/operator_aware/LATEST_REPORT.md`

最终 push：

`hrl/vm-m4b-operator-aware-v0`

禁止 `git add .` / `git add -A`；仅 stage 明确路径。
