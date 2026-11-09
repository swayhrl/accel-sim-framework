# AI-ARCH Q1 shN V1 实现独立审查（174，CPU-only）

固定执行对象：`swayhrl/accel-sim-framework@2838e93cfc129183d7d727e80eccc1b2f577a82d`；原Q1 authority `5787826ca21f7af958e6e1c1f828d62fd58a1ec4`；174接班接受 `c68aaf6e3fa503ae36719352f9ba73d7aee7b29e`。本报告只评估shN V1实现和既有关闭证据，不重做20行统计验收。109执行已STOP；描述性退化已接受，硬件候选未晋升。

## 出口：B，先缺一个具体观测

V1的分块、逐元素Torch更新/预测是**明确且可消除的实现组织限制**，但现有证据不能判定它是否是完整Host窗口退化的主要来源，亦不能据此承诺融合实现会转正。需要的一项决策观测是：在**同一冻结V1**的完整51-camera闭合窗口，分别量到ON `_rows(update)`、`_rows(forward)`、下一camera首次消费及其关键等待的Host区间与对应实际CUDA stream事件，并同时保留未插桩闭合Host时延作扰动检查。记录各调用实际U/visible、chunk数和stream身份；设备事件只在同一时钟域相互比较，Host区间只在Host域比较，不能相减。该观测属于将来的独立授权任务，本轮没有运行GPU。

判据：若这些新增调用及关键等待覆盖ON相对OFF的主要额外Host区间，并且插桩不显著改变未插桩闭合时延，才有依据建议一个保留deferred语义的融合软件实现；若新增成本不足以解释差额，应停止当前软件反事实或另立有界问题。若插桩扰动或stream因果边界无法闭合，仍为unknown，不能把缺口写成正收益。当前范围的正式结论保持V1负结果及STOP。

## 实现和语义核对

- OFF由原 `source_transform.install` 生成；ON先安装原hook，再以原 `transform_train(source, diagnostic=False)` 为基底改3处shN语句、替换CPU optimizer调用。补丁按源码行号和AST字符串匹配，冻结trainer SHA校验可避免悄悄漂移，但没有结构化assert证明每个预期节点恰好匹配一次。不能仅凭补丁文件证明生成函数与期望完全同构。
- 原恢复语义指纹通过后，`shN` 参数、梯度、两份moments迁往`cuda:0`，CPU optimizer字典仍持有该参数及step；CPU `U`、int8 counter、opacity/sh0的CPU Adam更新不变。`_rows(update)`使用当前step，更新U的参数与moments；随后CPU counter更新，再对`valid`清零。`_rows(forward)`以step+1和更新后的counter对下一camera可见ID作非写入预测；重复visible ID保留重复输出。此顺序与deferred意图一致。
- 更新计算在源码中使用旧 `w,m0,v0,g`，先恢复 `w-c*m0/(sqrt(v0)+eps)`，再计算年龄幂修正的 `m,v` 和新参数。系数按FP32存表，Torch逐元素表达式和C++的求值/融合顺序可能不同；极小浮点差属允许的顺序变化，不能直接判作语义错误。冻结C++原件并未入固定Git，只有SHA及执行时校验入口；因此对C++逐项数学和运行时版本的独立核查只能到此边界。原工具的小型CPU语义测试依赖该原始二进制，固定Git中的测试源码并非本轮重新运行结果。
- `cpu_optimizer_parallel`在可能的子线程中发GPU更新和GPU梯度清零；Python线程`join`只证明Host函数返回，不自动证明异步GPU work在下一camera的消费者stream完成。原trainer在GPU forward/backward、join及下一camera消费处的完整顺序和具体stream关系未随Git发布。若都在有序同一stream或有正确事件/同步，顺序合法；若跨stream而无依赖，则存在竞争风险。现有短窗采样PASS及正式N/visible/U近同不能排除此条件性风险，不能称已发现实际错误。`colorsN_cpu_grad.copy_`被替换为`colorsN_grad.detach()`，属于共享底层存储而非CPU快照；更新/清零前后的生命周期也须按实际stream和原trainer语句确认。
- ON诊断时旧GPU forward/backward wrapper仍包原方法；新增 `_rows` 在train函数内。COST_LEDGER显示OFF每51 step有153次`synchronize`，ON仅51次；AST替换删除了原CPU forwarding分支中的同步。这提示比较的是两种不同组织路径，不证明少掉的同步本身产生净收益，也不证明GPU工作已在Host窗口之外完成。

## 工作与诊断边界

详细公式和两个代表样本见 [WORK_LEDGER.md](WORK_LEDGER.md)，脚本读固定Git `FORMAL_SAMPLES.tsv`，不导入Torch。验证窗ON每闭合样本约48.61M U行加41.89M预测行；仅四份状态gather的源码级操作数约65.16GB，预测cat输出复制约7.54GB；ID/年龄上传操作数约1.45GB。每样本分块迭代界2,763–2,863，另有每块CPU年龄检查、更新块unique、3次表gather、4次状态gather、逐元素中间张量和更新块3次scatter。这些不是实测流量、kernel数或时间。OFF的CPU Adam 3.439/3.510秒和所有CPU参数forwarding 2.920/2.871秒也不是shN专属可回收预算；ON的新增GPU工作和等待为unknown。原`gpu_forward_backward` event不得当作它们的计时，Host减CUDA span不得用作因果分解。

## 数值门的实际覆盖

事前阈值为每字段 `2e-6+2e-4×reference_max_abs`。发现和C_FINAL各4步、每步5字段的20项采样检查均PASS，最大绝对差7.45e-9；这支持短窗采样资格。每步参数/梯度/moments仅512行×45元素，约为6,720,398行的0.00762%；下一camera只取首128行×45元素。C_FINAL中moment2参考最大值约9e-12而阈值约2e-6，梯度与moment1也常处于阈值绝对地板量级：门对这些小字段的**相对**错误不敏感。20项按字段/step计，并非20次独立全状态试验。完整ID集合、逐行U集合、全量状态及长期质量未记录，不能补造；正式窗口已有1至3行量级的可见/更新波动，OFF/OFF也存在。C_FINAL已经用于V1判断，任何后续修改候选不得称其为全新holdout。

## 来源与最小缺件

已读固定Git的 `FINAL_REPORT.md`、`FORMAL_SAMPLES.tsv`、`COST_LEDGER.json`、两份`NUMERIC_AND_FRONTIER_AUDIT*.json`、`PREFROZEN_CONTRACT.md`、`SOURCE_FREEZE.json`、`PRE_FORMAL_VALIDATION_AUDIT.json`、`FORMAL_ANALYSIS.json`、候选/worker/原AST变换和小型CPU测试源码。`SOURCE_FREEZE`固定trainer SHA `17e70b64...`、CPUAdam C++ SHA `f3f32bc0...`，但两份原文不在该Git树中。若要把上面的条件性顺序核对升级为确定性源码结论，最小请求是这两份与SHA相符的小型只读原件及执行时生成的ON AST dump/stream依赖记录；本轮未取109/164资产。该缺件不影响工作账、诊断缺口和出口B。

本轮无GPU、模型、Profiler、模拟器、RTL或环境安装；不修改原实验和109上下文。后续实验须另行授权。结束本审查后STOP。
