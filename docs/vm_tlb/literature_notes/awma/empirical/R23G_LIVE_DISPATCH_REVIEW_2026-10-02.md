# R23G真实在线分派审阅与软件结果记录

日期：2026-10-02。

## 1. 审阅结论

按原冻结Goal接受：

`R23G_R81_LIVE_DISPATCH_LOCAL_RESPONSE_PRESENT`

固定RULE_U01在本轮公开来源、预先冻结的三个B4批次中，计入CPU union、分派以及真实A0/A3切换后，仍有稳定的净LIVE_HEAD收益；完整生成安全退化门未触发。这是有范围的软件执行组织正结果，不是新硬件结果，也不是已证明稳定的端到端加速。

R23G任务完成后按原合同STOP。本记录不授权新GPU任务、换样、去重重跑、阈值/union算法调优、profile或硬件工作。

## 2. Exact authority与实际核查范围

Repository：`swayhrl/accel-sim-framework`。

- Execution branch：`hrl/awma-r23g-r81-live-dispatch-109-v1`。
- Starting commit：`f981039d9289368cc32f761d6e5a79f91a775266`。
- Result commit：`99d05f0ad221a1d44dd11bac0ed83965bb2c0942`。
- Result tree：`b3bcf21e81e1bc34a3281d41b570d6021d8a1edd`。
- Result commit的唯一parent为上述starting commit。GitHub compare显示新增结果与runner文件，原Goal没有修改。
- R81 runtime parent：`69e74fe74e18d1f3a71bfac0d097ce49234327a9`。
- R22G audit parent：`296263043f4949467b33c6c99a695ac5c139104d`。

原Goal：
`docs/vm_tlb/chatgpt_handoff/awma/r23g_r81_live_dispatch_v1/LANE_G_R23G_R81_LIVE_DISPATCH_109_GOAL.md`

本轮结果根目录：
`docs/vm_tlb/review_packs/AWMA_R23G_R81_LIVE_DISPATCH_109_V1/`

ChatGPT实际通过GitHub connector读取分支ref、Git commit/tree、原START_HERE与完整Goal、结果报告、输入authority与cohort、qualification/semantic表、完整两张90行formal计时表、group summary、parent/union contract、run receipt和raw manifest，并阅读两个新增Python文件。随后在ChatGPT本地CPU对两张formal计时表中的全部数值逐组重算median/MAD；与发布的九组summary一致，没有删去异常值或追加测量。

这不是SSH节点检查，也不是重跑模型、重算node164全量raw/tensor SHA或独立逐token重放。语义、旧fixture canary及节点释放/归档属于发布证据与执行receipt支持的结论；没有把这些描述成ChatGPT亲自在节点重验。

## 3. 输入资格与必须补充的覆盖率限定

- Dataset：`korotkov/glaive-function-calling-v2-parsed`，`test`。
- Revision：`b5b1a23f1a88b180d512789ab0a77bf0764dc774`。
- JSON bytes：37,743,768。
- JSON SHA256：`eb796aacc2d775f52f8e7bb3edaa4dddfb52044e2e5b8e13f0226bbba482b516`。
- 下载方式为pinned JSON；未使用datasets-library cache，已发布authority没有split fingerprint。原Goal对fingerprint的要求为if available，不据此新增资格门。

12,553条来源记录中，5,350条通过固定结构/XGrammar编译筛选；canonical hash排序取前24条。`QUALIFICATION_RESULTS.tsv`的24条B0检查全部合格，最终12条正好是前12条，并连续组成V0/V1/V2。源码先写入冻结12条与authority，再执行旧canary、新M1语义资格及formal；没有按union、性能或输出长度重新排序。

**覆盖率补充（本次根据VALIDATION_COHORT.tsv核出）：**

- 12个source-row identity并不等于12个内容独立的输入。
- validation rank 1、2、4、5拥有相同prompt SHA和schema SHA，分布于V0/V1；都是同一个generate_password输入组合。
- 12条记录实际对应9种不同的(prompt SHA, schema SHA)组合、8种schema SHA。
- 这符合原本包含original row index的canonical身份和不去重的固定选样合同，不构成性能选样违规，也不在结果出来后重新去重、分组或补样。
- 论文/结果库应写“12条来源记录、三个B4批次，含内容重复”，不能写成“12个独立任务”。90次formal是重复测量，不是90个独立workload。

本数据仍是解析衍生集而非独立生产到达分布。预注册的B0正确性筛选范围、B4、128-token上限及重复输入均保留为适用边界。

## 4. 身份、union与真实执行边界

PARENT_AUTHORITY绑定原`Qwen/Qwen2.5-0.5B-Instruct`，model revision `7ae557604adf67be50417f59c2c2f167def9a775`，BF16，XGrammar 0.2.8。A0/A3共用的原head source SHA256为`e6f457b95be5f87cffed040cd3b0c218d6f39b73da441afb8ba59f3d1c33b872`；此为parent/runtime receipt，不冒充本次重hash运行节点文件。

新增runner从原R81 source导入HeadArms；没有新增或修改head kernel。B0始终A0，不算union；M1才调用固定classify。两者复用相同mask、backbone与head内部工作路径。

源码核查的union路径：active CPU int32 mask按uint32解释；NumPy OR/reduce写入persistent uint32[4748]；固定uint8[256] LUT在byte view上popcount，uint64求和；除以151936后严格应用`<0.01 -> A3; else A0`。151936正好等于4748×32，无尾部padding bits。

`head_start`位于classify之前，结束时间位于head.select与CUDA同步之后。active-row索引、union、branch、原head内部必要工作以及真实切换都包含在M1实际测得的LIVE_HEAD中。没有从净时间扣掉union，也没有用post-head ledger拼装hybrid。原union contract文字对total起点描述略简略；源码实际还计入active-row索引等前置开销，README已明确说明，没有少计候选成本。

执行发布的旧C1 canary为72步exact union/arm/token检查通过；新semantic表的三个批次均记录token、stop、schema、无截断与matcher终止通过。Formal两张表包含90次完整生成，45次/arm，全部记录语义通过。

## 5. 必要配套净成本与实际覆盖

下表union数据来自发布的UNION成本汇总/README；每步median与每generation合计的median是不同统计量，不能强行相乘或相加。

| Batch | OR每步median (us) | Popcount每步median (us) | Branch每步median (us) | 总union+dispatch每步median (us) | 每generation总成本median (ms) | A0/A3步数 | 切换次数 |
|---|---:|---:|---:|---:|---:|---|---:|
| V0 | 6.665 | 44.135 | 0.533 | 75.711 | 2.244045 | 6 / 23 | 4 |
| V1 | 5.556 | 43.200 | 0.417 | 73.022 | 7.079472 | 23 / 71 | 8 |
| V2 | 8.052 | 50.839 | 0.498 | 89.197 | 2.371240 | 10 / 17 | 6 |

总成本还包括索引、view/LUT临时结果、计时和标量处理，不能只相加三个小分项来替代。A3调用比例分别为79.31%、75.53%、62.96%；这是step覆盖，不是耗时占比，也不能直接外推生产工作负载。

## 6. 全部formal计时的CPU复算

下表均为同组五次formal/arm的中位数。耗时减少为(B0−M1)/B0；不是speedup百分比。

| Batch/group | B0 LIVE_HEAD (ms) | M1 LIVE_HEAD (ms) | 净head耗时减少 | 3×较大arm MAD (ms) | 完整生成耗时减少 |
|---|---:|---:|---:|---:|---:|
| V0/0 | 20.404641 | 15.475335 | 24.1578% | 0.704421 | 5.0991% |
| V0/1 | 20.407967 | 15.413076 | 24.4752% | 0.123858 | 2.8166% |
| V0/2 | 20.395597 | 15.504236 | 23.9824% | 0.127632 | 3.1931% |
| V1/0 | 66.210230 | 45.471509 | 31.3225% | 2.972328 | 1.9786% |
| V1/1 | 66.091538 | 45.663809 | 30.9082% | 0.997344 | 0.2418% |
| V1/2 | 71.509643 | 47.336098 | 33.8046% | 0.527298 | 14.6980% |
| V2/0 | 20.910157 | 17.623771 | 15.7167% | 0.211539 | 4.1923% |
| V2/1 | 20.885978 | 17.644671 | 15.5191% | 0.052929 | 4.0052% |
| V2/2 | 20.930657 | 17.682612 | 15.5181% | 0.315162 | -1.1215% |

九组净head绝对gap全部超过各自3×MAD，三个批次均满足稳定局部positive，强于至少2/3批次的晋升要求。MAD只按原合同作为工程噪声判据，不声称某一统计置信水平。

完整生成没有任何一组构成超过2%的稳定退化，因此原“两批次稳定退化>2%”安全门不触发。另一方面，各批次都存在至少一组未形成噪声稳定的完整生成positive：V0/0、V1/0与V1/1噪声大；V2/2慢1.12%且不稳定。**不能把安全门通过写成各批次稳定端到端提速。**尤其不能把V1/2完整生成14.70%的全部差值归于head。

由各组B0中位数计算，LIVE_HEAD/COMPLETE_GENERATION约8.16%—9.32%。这只是已定义wall边界的描述性比值，不是关键路径/profile分解；不能由其推断其余kernel零副作用。非目标族逐一退化、一般生产覆盖率、task accuracy均未建立。

## 7. 四层评价及历史更新

1. 目标族/区域：本冻结runner的完整LIVE_HEAD工作集合稳定改善，不只挑一个A3 kernel。
2. 必要配套净成本：CPU union/分派及真实切换已进入主边界，局部positive仍成立。
3. 覆盖率/非目标：报告A0/A3调用、重复输入、计时边界比例；非目标族逐项中性仍UNKNOWN。
4. 完整边界：本轮完整生成安全门通过；稳定、可归因的普遍端到端收益尚未建立。

R22G“旧证据不足以证明真实在线分派净收益”作为历史审计仍正确；R23G用新实际执行填补其特定成本缺口，而不是改写旧标签。旧R81稀疏状态正结果保留，并新增本轮固定在线软件策略的范围化正结果。不要套用整应用5%一票否决，也不要从局部positive自动进入硬件。

## 8. 节点receipt与操作终点

RUN_RECEIPTS报告单persistent process、36次formal warmup、90次formal、无新NSYS/NCU/NVBit/SASS、无174计算/Accel-Sim。GPU锁获取/释放UTC为2026-10-02T06:48:25Z / 2026-10-02T06:50:29Z，进程退出且post-campaign GPU进程receipt为空。

Node164 publication：
`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r23g_r81_live_dispatch_109_v1_20261002`

Archive SHA256：
`2152aa7c5ce9a697bb87cd85b594a3a8b742867c48287b52e7c21e6dc28d7668`

这些是节点发布的closure/归档信息。本次直接核了GitHub exact commit/tree，没有SSH核当前进程或重hash归档，也不另外声称检查了节点worktree clean状态。

当前操作：G完成并STOP；F/R22F1 STOP；E/R22E STOP；R20 CLOSED；R21A/OEQ STOP；174/Accel-Sim无新任务。保留软件结果与覆盖率限制，不重发启动、reset、重启、merge或扩展矩阵。

## 9. 可复核来源

上述result commit下的review pack文件：FINAL_DECISION.md、README.md、PARENT_AUTHORITY.json、PUBLIC_INPUT_AUTHORITY.json、VALIDATION_COHORT.tsv、QUALIFICATION_RESULTS.tsv、SEMANTIC_QUALIFICATION.tsv、UNION_DISPATCH_CONTRACT.md、FORMAL_LIVE_HEAD_TIMING.tsv、FORMAL_COMPLETE_GENERATION_TIMING.tsv、GROUP_RESPONSE_SUMMARY.tsv、RUN_RECEIPTS.json、RAW_MANIFEST.tsv。

上述result commit下的源码：
- `util/vm_tlb/awma/r23g_r81_live_dispatch/prepare_public_input.py`
- `util/vm_tlb/awma/r23g_r81_live_dispatch/run_live_dispatch_campaign.py`

本记录是ChatGPT审阅/软件结果记录，不是新的execution receipt或实验授权。
