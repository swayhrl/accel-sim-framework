# Round A66｜A65真实IGB同batch编译更新数值／清理／监督独立审查

**2026-10-16；ChatGPT／AI-ARCH Discovery；科学裁决：A65_COMPILED_PATH_NUMERIC_NONALIGNMENT_ACCEPTED_WITH_SUPERVISOR_SCOPE。**

## 0. 权威与边界

- A65 Goal HEAD `afe42345c4b0c45b3e09f3cb32ce4e3e0de09989`；执行分支 `hrl/aiarch-a65-igb-small-compiled-numeric-109-v1`；完成commit `3cdf0489b0b3a2cbbb4081e6dd13044f7ec70f79`、Git tree `7a37e87cc063d03ee2a7b4a2212cad2a6da098eb`。
- 连接器独立核Goal→final ahead 3、final→远端branch HEAD identical；compare列113个新增文件。已读FINAL_REPORT、GATES、numeric_result、parameter_comparisons、failure_element_attribution、initial_identities、actual_minibatch_semantics、compiled metadata、资源/监督/存储cleanup收据。**本独立审查没有逐一复算113文件的raw SHA或解码所有NPZ数据，也没有实时SSH核109；113个blob/SHA fetch-back由109发布收据报告，不冒充本审查另一次硬件运行。**
- A61原`DATA_OR_NUMERIC_NO_GO`属于不同旧batch/旧复合断言，保持冻结；A65新受控输入不能追溯改写其FAIL。
- 本轮审查仅GitHub证据读取及协调记录，无109/174/164作业或新GPU授权。

## 1. 数据与数值证据

- 本轮B1024、同一真实GraphBolt采样结果、FP32 fetched features、graph和labels在A/B/C间冻结，三个独立GraphSAGE模型/Adam初始状态、全name/shape/dtype及逐参数SHA一致，独立参数storage与optimizer对象。A65输入节点349419、自然sample结构原样保存。符合受控数值比较；不是A61旧失败batch的逐字节恢复，也非独立泛化holdout。
- `eagerA/eagerB`两者loss相同，逐参数更新在原`atol=1e-6,rtol=1e-4`门全部PASS，但多数元素并非逐bit相等；不能将eager执行描述为完全确定。 `eagerA/compiledC`两个loss相差2.384185791015625e-7，原loss门PASS。共9个参数张量、665619元素，仅`layers.0.lin_r.weight[59,378]`一个更新元素超门（失败比率约0.0001502%），其余8张量均PASS。
- 失败点初值`0.0034851767122745514`；eagerA/compiledC梯度分别`3.1561739888275042e-9`/`3.1678837331128307e-9`，差`1.1709744285326451e-11`。更新后分别`0.0027654748409986496`/`0.0027634433936327696`，差`2.0314473658800125e-6`，原门允许量约`1.276344339363277e-6`，实际/门约`1.59161`。
- 对首次Adam、weight_decay0、lr0.003、eps1e-8，按`-lr*g/(abs(g)+eps)`独立代入观察梯度，预测更新差约`2.02779e-6`，与FP32实际更新`2.03145e-6`吻合。原收据的每路“使用自己观测梯度”的CPU Adam解析式PASS。因此**来源优先归于微小梯度差异经Adam敏感区间放大，不是已证不同optimizer语义**；更不能断言编译器错误或训练质量退化。
- 原数值门仍严格FAIL，`COMPILED_PATH_NUMERIC_NONALIGNMENT`接受；不能因为只有一个元素超门而改写为compiled qualified。A/B本身存在FP32数值离散，C是否为具体编译器defect尚未确认；原Dynamo存在graph breaks，不能宣传所有train_step完全融合。
- 全部为3次资格更新、正式train updates 0、wall诊断NOT_RUN。不能推出全驻留/缓存ON性能、供数关键路径、训练精度或新GPU硬件机制。

## 2. 资源和监督

- 独立读取`storage_cleanup/finished.json`与`space_accounting.json`：获批目标清理的去重分配字节`203394699264B=189.4261GiB`，实际目录项/硬链接去重；`df`空闲`67206217728→284689309696B`，净增202.55GiB，但明确含其它文件系统活动，不全部归功本任务。164核验9172项、本地核验9142项来自执行receipt；归档不变及A61/A26GR1不变来自已报告的清理和read-only收据，未由本ChatGPT直接重hash164。
- A65 GPU非阻塞锁实际32.530213秒，采样task-tree RSS 9.570GiB，GPU 6982MiB，真实下载/安装0，3资格更新，正式0。新盘实际/估算不同账口径保留：资源收据中`new_disk_conservative_final_bound_bytes=103428096B≈98.64MiB`；均低于128MiB，但不能不加口径复制其它96.55MiB数字作为完全同值。
- `EXTERNAL_GPU_TASK_STOP`在末次监督保留；进程返回码0、观测完成、退出后NVML空，但flag触发时未保存NVML/PID原始快照。CPU复现说明“自身child在边界退出造成误判”**可能**，不是本次已证实误报；保留`FULL_EXCLUSIVITY_UNRESOLVED`。对主要受输入/参数确定性控制的数值观察可接受带监督范围的结果，但不能声称全过程独占资格PASS，更不能把该运行当正式性能样本。

## 3. 下一科研决策：不要继续修一个FP32 epsilon元素

- **停止对本批Compiled C做参数阈值微调、编译器归罪或为了找到PASS无界反复执行。** 编译路径在原严格门下不合格；它仍是未解决的软件资格，不是GNN科学问题的性能负结果。
- 推荐以新科学合同**明确转为eager-scope bounded native discovery**（新Round A67提案），不是“旧A61绕过FAIL后继续”，也不声称compiled strong path已达到资格。只在同一GraphBolt/PyG eager模型、真实IGB、相同seed/split/fanout/FP32/Adam下，对比FULL_RESIDENT_GPU、PINNED_CACHE_ON和仅作诊断的PINNED_CACHE_OFF，自然完整train-step未插桩wall；保留强软件full GPU resident作为最关键反证。
- 先CPU-only修改自有supervisor：在external flag发生时落实际NVML PID集合、owned child与进程组身份、采样顺序与child终态；只有真实排除第三方GPU干扰才允许正式性能claim，不能仅清除标志。修复不单独开小工程Goal。
- 最小探索推荐3 arm × 2冻结seeds ×每arm/seed 12正式自然B1024 batches（72 updates），每arm/seed最多2 warmups（12），加cache-OFF数值canary最多1次；全部由预冻结累计hard cap、额外资源早停和完整wall测量门控制。不需要因A65 FAIL再申请另一轮编译数值诊断，也不使用历史A61的数据下载额度。
- 所得只支持`EAGER_SCOPE`：若全驻留已消除重要供数残余，可以对IGB-small当前目标及时止损；若PINNED_CACHE_ON仍有代价，先区分容量与PCIe/CPU、GPU采样、L2等原因，且不能在compiled路径未qualified时直接升级“最强软件后新硬件机会”。同seed seed-nodes相同并不保证邻域逐边相同，应当保存执行分布与单次wall/seed而不是伪称逐样本完全配对。
- 用户必须明确向109 Codex派发新Goal才执行；A61/A65原branch与raw永久冻结。Q-S、稀疏权重训练仍只读候补；C16/AWMA/ISCAS权限不受本审查影响。

**最终科学裁决：A65新受控numeric mismatch成立、范围严格；监督末次证据不闭合；不继续编译数值追逐；下一个有价值问题是eager强软件下的完整GNN训练供数能否被FULL_RESIDENT_GPU解决。**