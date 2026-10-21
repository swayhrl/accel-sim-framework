# E2 workload调查审查与当前勘误

**结论：调查方向可保留，但尚不能作为新实验启动清单。** 两份独立审查及root中央资格回读均未发现需要停止当前Conv ON的问题；本轮0应用、0native、0主binary构建、0trace正文扫描、0中央修改。历史r1报告保留，以下当前解释覆盖其过时/含混标签。

## 最重要的修正

1. **先选runtime与统计分母。** 原FWT准确main61资格`1d3af457…`仍为INDEPENDENTLY_QUALIFIED，S/F18门PASS，无当前Q HOLD；旧两端仍INCOMPLETE。若目标是补原MAIN，优先审查复用main61既有资格并单独提两次恢复；若选新93a9完整S/F，须补准确有限F资格和同binary新S锚点，作为独立cohort，不能填入旧main61原七GM。本轮不自动采用任一路线或替换当前五组新binary OFF/ON。
2. **冻结trace模型、源码再采集、数值应用复现分开。** 缺原GPU UUID、scaled源码、capture binary或数值payload限制复采/数值结论，但不自动撤销已有main61 FWT trace-model资格。SGEMM原探索登记也明确是固定trace模型范围；其完整runtime/输入/RO/profile资格仍未通过。不得擅自豁免新范围，也不得凭新增材料发明一套统一强制数值门。
3. **补机制覆盖，不按应用数凑齐。** FWT RO零覆盖与SGEMM低压力/未知复用有负对照价值，不能当Tag detach正触发样本。当前没有已经建立的detach-positive候选。BFS仅有条件性的间接访存/多kernel/host更新补充价值，实际S压力与资格仍未知；Hotspot已保存512/2/2仅1kernel，不补跨kernel迭代。8–10只是早期非约束目标，具体已选清单并不证明10个，更不证明机制完整。
4. **SGEMM已经登记。** 权威状态是`E2_EXP_SGEMM_MEDIUM_20261020_r1 / REGISTERED_EXPLORATORY_HOLD_NOT_LAUNCHABLE`，不是原七输入的第八格，不替换Btree。旧README/JSON的缺登记说法不再作为当前阻塞。
5. **静态映射不是运行PASS。** A2未发现必须增加opcode、机制或重建的已知不兼容；这是先复用producer的理由，不能保证后续正确性验证永不发现缺陷。文件stat齐全、保存的全输入grammar、当前内容身份及新runtime资格也分别列账，不重复大扫描来掩盖真正缺件。

## 建议的准备优先级

|顺序|候选|科学价值|当前最小下一步|另批后真实启动/结果提案|
|---|---|---|---|---|
|1|FWT 原main61恢复|补原登记缺失、W/V压力假设、RO零覆盖负背景|核复用原准确Q/输入/配置、当前durable exit和资源适用性，提出明确恢复方案；不重复已过native|2次/768MiB；旧S80–110min、F85–120min仅先验|
|2|SGEMM 独立探索|dense/低压力对照，保留负例|选定producer与冻结trace范围，自己的RO或明确普通fallback、精确S/F资格；现有HOLD登记不重复|2次/768MiB；walltime UNKNOWN|
|3|BFS 条件准备|不规则、20次声明kernel及host更新|先闭合graph/capture/完整host语义，再按原pipeline一次完整输入证明；不以F收益挑选|2次/768MiB；walltime UNKNOWN|
|备用|Hotspot512/2/2|单kernel stencil对照|不为凑数优先；若改迭代参数须作为新输入重新审查|未建议当前运行|

每对2×384MiB算术正确，但属于拟议端点上限，不是已分配预算；还需资格输出、collector/metadata和实际空间余量。新10GiB/总24GiB累计生成量保持，迁移不归零；数值/时间限制取消不自动批准新条件。任何未来方案均须明确source/binary、cohort、完整输入、固定profile、启动次数和原中央准入。旧INCOMPLETE/HOLD及原七GM UNKNOWN不被新增成功替换。

当前推荐先把FWT与SGEMM的上述准备闭合，再决定是否值得运行；BFS准备可并行，Hotspot备用。更广泛泛化或T-detach收益仍缺证，不能通过不断更换输入直到F变快来补。

## 依据

- [独立科学审查](INDEPENDENT_SCIENCE_REVIEW.md)
- [独立资格与成本审查](INDEPENDENT_ELIGIBILITY_COST_REVIEW.md)
- [准确身份、勘误和当前候选机器表](DECISION_REVIEW.json)

本轮也复核了一手源码：[Hotspot循环/参数](https://raw.githubusercontent.com/accel-sim/gpu-app-collection/dev/src/cuda/rodinia/3.1/cuda/hotspot/hotspot.cu)与[BFS间接访问](https://raw.githubusercontent.com/accel-sim/gpu-app-collection/dev/src/cuda/rodinia/3.1/cuda/bfs/kernel.cu)。公开参考不等于捕获源码身份；Hotspot单launch结论同时有D本地完整命令表记录支持。[官方v2.0.1发布说明](https://github.com/accel-sim/accel-sim-framework/releases/tag/v2.0.1)明确H200新tracez集合有省略kernel，不能直接作为本轮完整应用替代输入。
