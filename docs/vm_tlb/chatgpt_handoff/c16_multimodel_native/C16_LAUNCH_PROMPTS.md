# C16 Goal-mode launch prompts

Run four independent Codex Goal windows. Each window must use its own non-detached worktree/branch and must read `START_HERE.md` first.

## Lane A — local prep / coordination / integration

```text
用 Goal 模式启动 C16_A_LOCAL_PREP_AND_INTEGRATION。

仓库：swayhrl/accel-sim-framework
执行分支：hrl/vm-c16-a-static-coord-v0
建议 worktree：/workspace/worktrees/accel-sim-vm-c16-a

先 fetch 分支并确认 non-detached clean worktree。完整阅读：
docs/vm_tlb/chatgpt_handoff/c16_multimodel_native/START_HERE.md
然后按其中顺序读取 MASTER、STAGE_ACCEPTANCE、DATA/PROVENANCE、RESOURCE/BUDGET、C16_LANE_A_GOAL.md 和 MODEL_SCENARIO_MATRIX。

主要负责：C16-0.0~0.2、0.6、0.7、0.9，C16-5.4，C16-6.2~6.4。
第一件事先完成 C15-A metadata/provenance closeout，但不得重新跑科学实验或改 C15 数值；随后冻结 C16 A/B/C 输入。

租 GPU 前尽可能完成模型资产、逐文件 SHA、tokenizer/input/scenario、GPU package/transfer manifest。不要在 A 窗口启动 GPU profiler、NVBit、Accel-Sim 新回放。

普通工程问题主动解决并继续；缺失模型/metadata保留 gap，不用猜测补齐。所有跨lane输入只读取固定commit+manifest/hash，不读取live partial。最终只push A分支。
```

## Lane G — AutoDL native execution

```text
用 Goal 模式启动 C16_G_AUTODL_NATIVE_EXECUTION。

仓库：swayhrl/accel-sim-framework
执行分支：hrl/vm-c16-g-native-gpu-v0
建议本地 worktree：/workspace/worktrees/accel-sim-vm-c16-g

先完整阅读 START_HERE、MASTER、STAGE_ACCEPTANCE、DATA/PROVENANCE、RESOURCE/BUDGET、C16_LANE_G_GOAL.md 和 MODEL_SCENARIO_MATRIX。

本地阶段先完成 C16-0.3/0.4/0.9：AutoDL bootstrap、env/wheel lock、统一native runner、nsys/ncu/nvbit wrapper、receipt schema、mock/dry-run。不要等租GPU后再现场开发这些基础设施。

当用户提供/确认 AutoDL SSH 后，执行 C16-1 inline qualification：G0/G1/G2/G3边验证边放行，不单独长时间资格测试。G0通过立刻做native baseline；G1通过立刻做完整轻量kernel census；G2/G3失败不阻塞G1。

Wave-1：Llama3.2-1B、Qwen2.5-0.5B、Qwen2.5-7B raw、Qwen2.5-7B AWQ。先发布Wave-1 catalog再继续Wave-2。

GPU只用于真实运行、nsys、有限NCU、有限NVBit。不要在租赁GPU上跑Accel-Sim长模拟，也不要因GPU空闲扩大实验矩阵。

NVBit每窗口硬限制4GiB或20min先到即停，首轮raw总量<=64GiB。大文件不commit，只写manifest/hash/index并及时rsync回本地。只push G分支。
```

## Lane C — Sampling V2

```text
用 Goal 模式启动 C16_C_STRATIFIED_SAMPLING_V2。

仓库：swayhrl/accel-sim-framework
执行分支：hrl/vm-c16-c-sampling-v2-v0
建议 worktree：/workspace/worktrees/accel-sim-vm-c16-c

完整阅读 START_HERE、MASTER、STAGE_ACCEPTANCE、DATA/PROVENANCE、RESOURCE/BUDGET、C16_LANE_C_GOAL.md。

不等待GPU。立即在本地完成C16-0.8与C16-3基础设施：真正的strata-specific estimator、certainty unit、Selector-R probability sampling、Selector-M medoid、zero-sampling conservation、ratio numerator/denominator重构、预算12/24/48和freeze协议。

C12/C13仅作RETROSPECTIVE_ORACLE_CALIBRATION；旧C13 mode=1永远排除。不得使用candidate speedup/miss结果选择样本，不得挑最好seed或修改阈值凑PASS。

G发布Wave-1 committed catalog后只读消费固定commit，先冻结selector code/seed/strata/tuning-vs-holdout，再读取holdout target metrics。尽早向G/H发布冻结sample/target plans。

逐指标资格，不用一个总PASS覆盖duration/counter/page/cache/机制响应。只push C分支，不启动新simulator replay。
```

## Lane H — object/page/cache-line fingerprint

```text
用 Goal 模式启动 C16_H_MEMORY_FINGERPRINT。

仓库：swayhrl/accel-sim-framework
执行分支：hrl/vm-c16-h-memory-fingerprint-v0
建议 worktree：/workspace/worktrees/accel-sim-vm-c16-h

完整阅读 START_HERE、MASTER、STAGE_ACCEPTANCE、DATA/PROVENANCE、RESOURCE/BUDGET、C16_LANE_H_GOAL.md。

不等待GPU。先完成 C16-0.5/0.8：Runtime Object Map V2 schema/observer fixtures、NVBit address parser、active mask+width、4K/64K page、128B line、set overlap、partial trace、UNKNOWN object边界测试。评估memory-only observer，但只有与full tracer tiny fixture等价才GO；否则NO_GO并保留full tracer fallback。

G有真实committed capture后，只读/通过exchange manifest+SHA消费。完成C16-4.5/4.6和C16-5.1~5.3/5.5。Observed GPU VA bucket不是hardware TLB miss，CTA-group file order不是global L2 order，UNKNOWN不得补Activation。

跨模型结论必须保留metric/evidence/domain/lineage边界。只push H分支，不启动AutoDL正式任务或新full-ROI simulator。
```
