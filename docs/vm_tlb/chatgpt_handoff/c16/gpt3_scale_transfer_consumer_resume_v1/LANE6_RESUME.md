# Lane 6 Resume — GPT-3公开尺寸规模外推正式独立消费

日期：2026-09-28

执行节点：174-new  
Lane：6  
角色：CPU-only independent consumer / cross-experiment comparator  
GPU：禁止  
GPU lock：禁止  
允许并行：Lane4、Lane7、Lane8

任务：继续原 `C16_GPT3_PUBLIC_SHAPE_SCALE_TRANSFER_CONSUMER_174NEW_V1`，**不要重做准备阶段**。

## 1. 已完成的consumer准备

Consumer prep branch：
`hrl/c16-gpt3-public-shape-scale-transfer-consumer-174new-v1`

Prep commit：
`117c9e994ea08d8307e349f75e2852d239635a15`

Tree：
`74d52c8f296afbb8b1e7a6c986a5d7e7ff6e1505`

已完成：
- 旧Qwen 800条timing独立重算；
- GPT-3公开尺寸静态数学；
- 比较公式和输出schema；
- 新结果表仅表头；
- no GPU/no Lane4 partial。

直接在现有worktree/branch上继续，不要重新生成旧Qwen基线。

## 2. Lane8 READY authority

Prep branch：
`hrl/c16-gpt3-public-shape-prep-174new-v1`

Final HEAD：
`55cfac5f3edd346d8c6083bdd399a206cc463d0d`

Validated prep：
`e1caa0d03843744bd2e2093731a032e201e73f80`

Validated tree：
`4901debe8aae27e055dcac34bba738d0e42255dd`

`PRE_GPU_READY.json` Git blob：
`72aa5bfc62c1d0193cb1b2c63962fe453e039fa6`

## 3. Producer authority — 消费gate现已满足

Producer branch：
`hrl/c16-gpt3-public-shape-scale-transfer-109-v1`

GPU source commit：
`eebcc63b3ae9f84f8ee8f2be0c008eabc85794c0`

Science-result commit：
`4cd1a7c5826560189814b677b8a7762e6b871db1`

Final HEAD：
`1544018d967003c2825eb69f56440f641f5f5581`

Final tree：
`08cffe7ff0e5c4981aef0c6626950a6632d5dc73`

Review pack：
`docs/vm_tlb/review_packs/C16_GPT3_PUBLIC_SHAPE_SCALE_TRANSFER_109_V1/`

RUN_ID：
`C16R_gpt3-public-shape-scale-transfer-v1_20260928T123239Z`

GPU lock：
`2026-09-28T12:43:44Z -> 12:44:31Z`
状态：正常释放。

Producer pack明确绑定Lane8 READY：
- lane8_ready_head = `55cfac5f3edd346d8c6083bdd399a206cc463d0d`
- validated_prep_head/tree均一致
- accepted binary hashes verified
- Lane4 partial未读取

## 4. 正式消费必须从原始样本/基础表重算

不要使用producer `SCIENTIFIC_INTERPRETATION.md` 或其derived gain作为计算authority。

优先读取并验证：
- `SOURCE_AND_AUTHORITY.json`
- `GPU_LOCK_RECEIPT.json`
- `W4_CORRECTNESS.tsv`
- `W4_LAUNCH_AUDIT.tsv`
- `DENSE_LAUNCH_AUDIT.tsv`
- `DENSE_TIMING_SAMPLES.tsv`
- `W4_TIMING_SAMPLES.tsv`
- `NCU_KERNEL_ROWS.tsv`
- `RAW_INDEX.tsv`
- `SHA256SUMS`

然后独立生成：
- Dense summary
- W4 cell summary
- gain_W/gain_E/state interaction
- complete mirror-block bootstrap，seed 20260928，1000次
- NCU summary
- 与旧Qwen的scale-transfer comparison

## 5. 本轮重点审查的四个变化

### A. EXPAND_M1
旧Qwen：
- split1 grid 148
- warm gain约 -41.3%

新GPT-3公开尺寸proxy：
- split1 grid 384
- producer观察 warm gain约 +24.1%

独立确认是否存在策略方向翻转。若成立，只能说与更高CTA供给一致，不得仅凭grid证明原因。

### B. EXPAND_M256
旧Qwen：
- warm split1 gain约 +30.0%
- disturbed约 +26.9%

新proxy producer观察：
- warm约 -71.0%
- disturbed约 -73.6%

这是最强scale-transfer候选。
重点结合新M256 NCU：
- split8 A_W DRAM约0.945GB
- split1 B_W DRAM约2.993GB

独立重算这些计数，并判断是否形成“更大权重工作集下split1失去旧Qwen优势”的证据。
不得做tensor级归因，也不得唯一归因L2。

### C. CONTRACT_M1
旧Qwen split1极慢（约-413%）。
新proxy producer观察仍慢，但约-64%。

判断更大N带来的CTA供给是否显著缩小退化，而不是简单宣称问题消失。

### D. M256 state sensitivity
旧Qwen qweight/L2≈0.506。
新proxy qweight/L2=4.5。

独立比较：
- EXPAND M256 state interaction
- CONTRACT M256 state interaction
- W/E DRAM变化

重点回答：工作集远大于L2后，显式conditioner对相对策略收益是否变得较弱/混合，而不是假定统一增强。

## 6. 允许的项目级结论

用中文主结论，不能用机器标签代替。

如果独立重算确认producer结果，可以讨论：

1. **规模改变确实能改变split策略方向**，至少EXPAND_M1和EXPAND_M256可能形成一正一反的强scale crossover。
2. 单纯固定split值在不同M/K/N和工作集尺度下不可靠。
3. 并行度供给与访存工作集/驻留状态需要共同考虑。
4. GPT-3公开尺寸W4只是机制代理，不是GPT-3量化模型。
5. FP16 Dense只是大Dense shape anchor，不用于证明W4机制原因。

不得推出：
- 原始GPT-3 checkpoint性能；
- 完整96层收益；
- GPT-3自然激活；
- 唯一L2/cache因果；
- 多GPU系统结论。

## 7. 是否建议SASS/模拟

只有consumer确认以下至少一项后，才在最终报告中**建议**后续paired trace：
- EXPAND_M1策略方向相对旧Qwen翻转；
- EXPAND_M256策略方向相对旧Qwen翻转；
- 且correctness/launch/离散度/NCU均闭合。

若满足，推荐优先：
- 旧Qwen UP_M256
- GPT3 proxy EXPAND_M256

作为第一paired mechanism target。

M1可作为第二候选，但不要一次抓四点。

本consumer不能自动启动SASS/Accel-Sim。

## 8. 输出与完成

继续更新已有review pack：
`docs/vm_tlb/review_packs/C16_GPT3_PUBLIC_SHAPE_SCALE_TRANSFER_CONSUMER_174NEW_V1/`

补全：
- NEW_DENSE_RECOMPUTE.tsv
- NEW_W4_RECOMPUTE.tsv
- SCALE_TRANSFER_COMPARISON.tsv
- GRID_AND_WORKSET_INTERPRETATION.md
- NCU_COMPARISON.json
- SCIENTIFIC_INTERPRETATION.md
- FINAL_DECISION.json
- OPEN_ISSUES.md
- SHA256SUMS

然后：
tests -> deterministic rerun -> diff-check -> commit -> push -> fetch-back exact commit/tree -> clean -> STOP。

汇报重点：
- 哪些方向真的翻转；
- 哪些只是幅度变化；
- qweight从0.506×L2到4.5×L2后，state sensitivity如何变化；
- 是否值得做1组paired SASS/模拟。
