# A65｜IGB-small GraphSAGE同batch编译更新数字资格最小诊断（109）

**科学状态：PREPARED_AWAITING_EXPLICIT_USER_DISPATCH / DO_NOT_LAUNCH_YET。** Goal发布不是GPU执行授权。只有用户向109 Lane M新的Codex Goal窗口实际发送包含本Goal branch/HEAD与明确批准有限资源的指令后，才执行。不得再次启动A61。

## 0. 身份与唯一问题

- Repository：swayhrl/accel-sim-framework；执行branch：hrl/aiarch-a65-igb-small-compiled-numeric-109-v1；科学父commit：A61真实STOP 37120f98186b83a946f4812755523f5d73245491（tree d13b446ca4824cb3ad7ffae25b5ce91c023b75a1）。
- 必读：原A61 Goal、其FINAL_REPORT、COMPILED_QUALIFICATION_FAILURE.json、raw/native_attempt0_compile.log、tools/aiarch_a61/native.py与native_utils.py；另读独立A64审查，固定文件在协调分支review commit 326dcac6227d1c1af6b38e4f76d21566525f35aa。
- **唯一目标**：在相同一份新自然B1024采样batch、输入和bitwise相同初始模型/optimizer状态下，分别执行eagerA、eagerB与torch.compile(train_step,dynamic=True)的compiledC，判定旧复合谓词是否真正对应更新数值不一致，若是定位至loss、gradient或optimizer更新阶段。不能将新样本的PASS追溯改写旧A61的STOP。
- 严格保留官方IGB-small同一SHA、1024 FP32特征与13,070,502自环后的有向CSC、原label/20261015 split、3层mean PyG GraphSAGE hidden256、fanout10/10/10、B1024、FP32 highest、TF32关闭、Adam lr.003/weightdecay0/defaultbetas/eps1e-8、原Torch2.2.0+cu121/DGL2.4.0+cu121/PyG2.6.1、原编译入口/原数值阈值。只允许数值观察和比较方法的修正，禁止改变训练模型或结果要求。

## 1. 资源与隔离硬合同（本Goal单独累计）

- Node109唯一RTX4080，必须先在既有/data/c16/locks/c16_gpu_campaign.lock上非阻塞flock独占；忙则GPU_LOCK_DEFERRED/STOP不轮询，不kill其它任务，不创建替代锁。由父supervisor持锁覆盖所有本Goal GPU子进程、CUDA初始化、cold compile及清理；累计持锁≤180s，计时临界有早停余量。清理自身子进程后释放。
- CPU有效workers≤4；任务进程树RSS≤12GiB；任务GPU显存≤12GiB（同时保留原allocator fraction .70）；新代码、worktree增量、raw、tmp、编译cache及输出合计≤128MiB，新数据盘空间仍保留≥64GiB；累计下载/依赖安装0B；新增正式训练0步。此处128MiB是硬上限，先CPU预估缓存与结果能否放下，不能通过写旧共享cache或扩大预算挽救。
- 实际optimizer updates≤3（各A/B/C一次），仅可预留最多1次因中断导致原受控对照未成形的工程retry；不可为了找到PASS反复重抽batch。GPU任务不存在默认授权时不能通过发起branch强行启动。
- 原A61私有科学源资产/data/c16/aiarch_a61_igb_small_gnn_native_109_v1、venv与所有既有raw/cache/日志只读；结果独立保存至全新的A65私有目录和Git的 docs/ai_workload_research/runs/AI_ARCH_A65_IGB_SMALL_COMPILED_NUMERIC_109_V1/；禁止将原A61数据搬到164、重下4.06GiB或改写原STOP。
- **危险的工具复用边界**：原 tools/aiarch_a61/common.py 把R硬编码成A61私有根目录，原gpu_supervisor.py也向A61/gpu_ledger写。不得直接运行或import它们完成新任务；必须用A65独立的read_only_input_root与output_root、自有supervisor、环境/cache与账本。可以审计后只读复用算法函数或复制改适配到A65新脚本，但不得在A61根写入任何文件，也不准执行原native.py（其后半段会尝试正式训练）。

## 2. G0｜锁外CPU-only：来源、比较器与启动资格

1. 以A61原commit+raw SHA核旧失败及执行代码，确认原来compile的是train_step函数而不是model对象；静态区分n==n2与allclose，识别潜在batch/optimizer/输入生存期风险。原值未记录的字段标UNKNOWN，不能编造旧差异。
2. 只读检查原始IGB/CSC/split/feature/venv/Torch DLL和模型输入权威实际存留及SHA；真实payload不存在且无同SHA accepted副本则ASSET_IDENTITY_NO_GO/STOP，不使用替代图/随机特征/重新下载。
3. 设计新独立A65 runner与GPU supervisor；静态单测命名、参数顺序/个数/shape/dtype、逐参数阈值与更新差分类器；对大数据使用已有只读映射，不复制4GiB特征。运行GPU前检查磁盘与estimated compilation cache是否满足128MiB；不足及时合法STOP。

## 3. G1｜持锁同输入三路，最多三次实际更新

1. 只在PINNED_CACHE_ON强图缓存和feature缓存原条件下，按原seed/自然官方ItemSampler从固定train split取**一份新自然B1024 minibatch**；冻结真实采样subgraphs CSC、原input-node IDs、其FP32 fetched features和labels在本次内的值/数据生存期。把可小型落盘的真实subgraph和IDs、hash保存，原始特征源仍只读引用；不要为了凑结果从graph cache多抽batch。采样子图、特征及label在三路执行前后必须保持相同hash/数值；如无法无损freeze则STOP。
2. 从唯一seed=20261015或其确定性CPU初态快照建立三个完全独立且bitwise相同的GraphSAGE模型和Adam optimizer初态。记录各模型参数完整name/dtype/shape、初态参数与optimizer state SHA，确认不共享可变parameter storage或optimizer buffer。每次train_step使用完全相同冻结mb对象内容。
3. 原始未修改数学调用：eagerA=train_step、eagerB=train_step、compiledC=torch.compile(train_step,dynamic=True)，三者都执行真实loss.backward和optimizer.step。不得替换成仅forward、短16seed子图、关闭torch.compile、改变PyG/GraphBolt API或降低精度。
4. 在每次step后、执行下一路前观察输出loss、每参数grad与updated parameter。断言名称、shape、dtype的门与数值门分开；eagerA↔eagerB先评本平台相同batch的自然数值波动，然后eagerA↔compiledC。每参数保存至少max_abs、归一化tol余量、标量max_rel统计（说明零附近的诊断分母），非有限计数、失败元素个数、前若干坐标及对应ref/candidate数值；不要一个assert先停掉观察。输入/初态SHA必须单独闭合。
5. 原有更新阈值严格保持atol1e-6/rtol1e-4，前向loss门保持1e-5/1e-4；原gradient数值门仅在其原定义适用的比较中使用，不经观察临时放宽。compile cold timing/graph breaks仅作为资格metadata，不能充当性能对照；不收NCU/NSYS/NVBit、不新增正式step窗口。

## 4. 分类、STOP与交付

- EAGER_EAGER_NUMERIC_VARIABILITY：A/B在原更新门下就不一致；记录真实波动/源头，不把C差异归罪compiler，不自动调容差。
- COMPILED_PATH_NUMERIC_NONALIGNMENT：A/B通过、C在同名字/shape/初态/输入上越过原门；区分先梯度差异还是optimizer更新差异。此时仍不得无独立复现宣称Torch bug，严格STOP。
- COMPARATOR_OR_IDENTITY_DEFECT：names/参数数量、起始状态、输入生存期或比较器分支本身失败；须准确记录是数据身份还是观测缺陷，不凭旧日志补数字。
- SAME_BATCH_NUMERIC_CONTROL_PASS：A/B/C全部在原门PASS，成立的只是本次新受控batch资格，不抹除旧A61真实FAIL，不自动开始完整训练/弱基线/新模型或硬件机制。
- ASSET_IDENTITY_NO_GO、GPU_LOCK_DEFERRED、BUDGET_STOP、NUMERIC_INSTRUMENTATION_INCOMPLETE均合法STOP。一般CLI/日志/新脚本和路径工程问题由Codex在累计合同内solve-and-continue；科学输入、精度、阈值、软件版本或预算变化立即STOP。
- 一个新branch、独立raw和最小报告：按原Goal→final的可验证SHA/树/blob发布Git；记录所有尝试（含负值）、执行源diff、数据SHA、GPU锁/显存/RSS/新盘/下载、子进程退出与工作区clean。不可覆盖A61旧证据。完成后向用户回执，等待独立审查，不自动执行A61 G2。

**本Goal在用户明确派发前只属于提案。**
