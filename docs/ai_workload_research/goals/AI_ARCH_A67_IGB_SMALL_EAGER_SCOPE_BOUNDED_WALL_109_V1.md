# A67｜IGB-small GraphSAGE eager-scope三路径完整训练步供数Discovery

**状态：PREPARED_AWAITING_EXPLICIT_USER_DISPATCH / DO_NOT_LAUNCH。** 这份Goal是有意变更原A61 compiled强软件资格之后的**新、范围严格的eager-only科研合同**，不是重启A61、修改A65失败或“绕过原数值门”。只有用户将明确批准的精确Goal HEAD指令发给109 Lane M，才实际执行；发布文档自身不授权CUDA。

## 0. 来源、问题、不能偷换的边界

Repository: swayhrl/accel-sim-framework  
执行branch: hrl/aiarch-a67-igb-small-eager-scope-wall-109-v1  
固定科学父提交：A65 STOP `3cdf0489b0b3a2cbbb4081e6dd13044f7ec70f79`；A61前史STOP `37120f98186b83a946f4812755523f5d73245491`。  
先读A61与A65 FINAL_REPORT/GATES、A64和A66独立review、原A61 Goal与本文；然后审查现有`tools/aiarch_a61/native_utils.py`、`tools/aiarch_a61/native.py`及A65三路观察源与GPU监督来源。

**唯一科学问题：** 在相同真实IGB-small、PyG GraphSAGE自然B1024训练及**已经数值合格的eager软件执行范围内**，FULL_RESIDENT_GPU、PINNED_CACHE_ON与仅用于反证的PINNED_CACHE_OFF，是否表现出材料性不同的完整step wall/吞吐，支持或削弱“成熟软件之后还有暴露供数成本”这一假说？

- A65确认Compiled C对原更新门`atol1e-6,rtol1e-4`有1/665619元素失败，保留`COMPILED_PATH_NUMERIC_NONALIGNMENT`，不得修改阈值、假称compiler合格，也不得再次为了寻找PASS跑Compiled C。本实验**不使用torch.compile**，EAGER_SCOPE不能宣传为已穷尽所有强软件后端，更不能单凭正性能结果推出新硬件headroom。
- 核心软件身份不变：官方IGB small原数值图/1,000,000×1024 FP32 feature/19类及固定有向自环CSC13,070,502、原split seed20261015、执行种子20261015和20261016、3层mean PyG SAGE hidden256、fanout[10,10,10]、B1024、FP32 highest/TF32禁止、cross entropy、Adam lr.003/weight_decay0/defaultbetas/eps1e-8；Torch2.2.0+cu121、DGL2.4.0+cu121、PyG2.6.1等必须与A61/A65同一权威，不升级CUDA/driver。
- GraphBolt FULL路径原图与全部FP32 features真实GPU驻留；ON是feature cache128MiB＋graph cache1000000 edges、合法fallback与pinned/UVA/async；OFF采用相同数学语义和GraphBolt后端，关闭两类GPU cache，仅作软件敏感度诊断。不能用OFF当唯一软件对手。未获授权其它GPU图、dataset、后端、dtype、hotspot重排或自然train/val/test质量报告。
- 同seed固定相同train seed-node顺序；独立自然异步neighbor采样未保证逐边相同，**不能把各arm数据叫逐样本bitwise同源**。要保留节点seed/order SHA、真实采样统计和每种arm的数值门及完整wall；比较的是相同科学训练分布、固定配置与两个seed的有界现象，不能编造每步严格因果配对。
- 不能将本轮12-step短窗口冒充全epoch收敛或真实应用大规模部署趋势；也不能把软件命中率当性能结论。

## 1. 单Goal累计资源、隔离和用户授权条件

- Node109单RTX4080，所有GPU初始化/训练/clock计时持既有`/data/c16/locks/c16_gpu_campaign.lock`非阻塞LOCK_EX；锁占用/真实外部GPU PID即STOP，不轮询等待、不杀其它用户进程，不建替代锁。**新Goal GPU锁累计≤900秒**，含warmup、任何数值canary与清理；20s余量前主动STOP。
- 任务CPU有效workers≤4，RSS≤16GiB、VRAM≤12GiB（保留原torch allocator fraction .70），新增disk/worktree/env/cache/raw/日志≤256MiB，原文件系统可用≥64GiB；下载与依赖安装预算**0B**。全部日志/raw新增≤32MiB（不计已存在权威数据），CPU准备≤1小时。新增资源超标或缺本体scientific payload立即STOP，不挪用164大存储、不开109第2张GPU。
- 109当前较多闲置盘来自A65另行获批的首批清理；**本Goal没有任何新的删除授权**。A61/A65/164/A26GR1/C16/AWMA只读且保留原Git和Stop。只读复用原A61私有数据、CSC、split/order、官方Python wheel包绑定，不在其根目录写入、清cache或复刻全4GiB特征。
- 使用全新A67 output/worktree/tmp和isolated cache+runtime写保护，任何新runner禁止直接执行原A61 `native.py`或硬编码A61根目录的`common.py`/`gpu_supervisor.py`；依赖相同数学路径的审过代码可复制到A67独立工具目录，保留source/AST、原SHA与改动diff。
- 总计3 arms ×2 seeds ×每格2次自然warmup+12次连续正式更新：**12 warmup＋72 formal =84训练更新**，另允许G1的PINNED_CACHE_OFF最多1次真实更新资格canary，累计≤85；不做额外retry/额外模型训练。每个seed使用原冻结自然node-order的前2个batch warmup，后12个batch计时，不追加形状/seed/质量参数扫描。
- GPU child应在启动和完成时记录真实PID/PGID/NVML snapshots、每一个异常第三方PID及采集时刻和归属；CPU定向测试旧A65 child-exit false-positive边界，修正判据**只改善观测，不屏蔽真实未知PID**。如真实外部GPU竞争或排他归属无法证明，则正式performance不得PASS；不允许将旧`EXTERNAL_GPU_TASK_STOP`静默重标PASS。

## 2. 执行次序：一个连续Goal、常规工程自行解决

**G0 CPU-only：** 固定Git/原始数据和split/order SHA、环境 ABI/RECORD与必要python可用性；源/对照语义正确性审查、磁盘/内存预估；监督器PID采样边界静态单测；新旧输出根隔离审计。合法的路径、venv、API适配、临时日志小问题在本Goal预算内solve-and-continue，别为小问题开新Codex窗口。若无法以原身份获得3个对照的合法实现/原数据，科学STOP。

**G1最小数值资格：** 旧FULL和ON eager单batch/PyG CPU FP64小子图oracle的accepted结论保留作为历史资格，但本次新runner对G1实际自然输入要进行输入/梯度/更新finite与合法图采样审计。尤其首次补`PINNED_CACHE_OFF`一自然B1024 batch，对有效标签/feature、方向/fanout、同FP32/Adam含梯度与optimizer canary核验；原容差与语义不得修改。FULL重新判一个自然batch实际显存/缓存状态；无法维持VRAM或发生数值/强路径错误则STOP。G1数值canary仅有预算中允许的1次额外Adam更新，不要对FULL/ON重复旧canary更新。

**G2完整自然step短窗口：** 3 arms×2 seeds，每格前2自然batch warmup、紧接后12自然batch正式uninst wall；同一模型初始化规则/Adam、不跨arm继承训练权重。每窗口计时从创建正式iterator之前开始，覆盖采样→feature-ready→前向/反向→optimizer，**中途不做每step同步、loss.item、NVTX profiling、NCU、NVBit或别的测量侵入**，在第12次真实更新完成后一次GPU同步并停止wall。冷初始化、pin、上卡与warmup作为另账保留；如果某些路径预先复制全图的成本被排除出step时间，必须显式说明该steady-state范围，不能把准备成本当免费系统端到端加速。逐run保存wall、12个loss数值、实际完结updates、输入node-order SHA、图sampling计数、任务CPU/GPU峰、实验顺序，预先交叉安排两种seed的arm顺序降低顺序偏置。完整loss/梯度/权重finite，短窗不是最终accuracy。
   
**G3仅在有值得解释的方向时做少量独立诊断：** 首先结束并持久保存未插桩window raw。可使用已经存在的cache计数与输入信息说明方向；若必须运行同步诊断，**本Goal没有额外GPU更新预算**，只能在现有两个warmup之内做非侵入式元数据记录、不能改正式计时路径或额外重跑正式点。需要新同步/NCU/复杂归因则在本Goal中写为下一Proposal而非自行执行。

## 3. 结果裁决与关闭标准

必须按arm/seed列出完整wall、每自然seed batch的吞吐、离散度/次序限制、cache真实生效证据、是否full resident、全量输入身份、negative结果，不能将GPU锁时长或NSYS kernel占比冒充train-step wall。

- FULL与ON都无显著材料性差异／供数暴露不明显 → `SCOPED_EAGER_NO_MATERIAL_SUPPLY_COST_OBSERVED`，本IGB-small/4080 eager负发现，及时STOP而不是新Cache机制。注意2seed×12batch不支持精确小收益上界。
- PINNED ON/OFF差异明显，但FULL已经能承载自然训练，强软件可能通过驻留解决 → `SCOPED_FULL_RESIDENT_SOFTWARE_ALTERNATIVE`，不把ON/OFF差异当硬件headroom；不能在未验证完整eager+strong替代前宣称唯一强路径。
- FULL或ON仍存在稳定、材料性的自然wall等待候选 → `SCOPED_EAGER_SUSPICIOUS_RESIDUAL`，仅提出一个最小CPU/PCIe/GPU内存服务定位建议；compiled数值资格仍FAIL、当前未排除所有软件方案，不直接发机制/模拟器/PPA。
- 两seed方向相反、运行资源/排他监督未完整、OFF数字失败、完整wall窗口缺失/设备超预算 → 分别记录`NOISY_OR_INCOMPLETE`、`NUMERIC_NO_GO`、`GPU_EXCLUSIVITY_UNRESOLVED`或`BUDGET_STOP`，不能靠后视换batch/seed/阈值补正结果。

局部kernel-family、自然时间权重和完整wall的分母分别记录；不采用“端到端必须>=5%才有研究价值”的统一硬门，但本轮为低成本Discovery，少量差异不允许直接晋升硬件。

## 4. 交付与STOP

发布本A67独立执行branch的Goal+原运行source+完整原始每arm/seed loss/time/采样/资源+数值/监督/STOP/实验失败记录、SHA校验和、source AST/frozen scientific identity、代码差分、完整report。实际原始数据/图/4GiB features/venv不进入Git或164。Git commit/push/fetch-back和tree/blob核验，结束所有自身GPU子进程并释放原锁、worktree clean，报告精确git final commit/tree、阶段GATES、资源累计和NEXT_MINIMAL_RECOMMENDATION；然后STOP，不自动追加run、改A61/A65失败或启动其它AI-ARCH/C16/AWMA任务。

**用户必须明确选择并下发本Goal，任何仅准备/发布行为都不是执行授权。**