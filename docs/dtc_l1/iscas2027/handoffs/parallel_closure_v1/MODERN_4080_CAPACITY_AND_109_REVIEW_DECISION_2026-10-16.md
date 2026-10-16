# DTC 4080容量合同与109交付审查决定（2026-10-16）

性质：用户本轮明确要求在两种4080 DTC实现中选型，同时交付109报告。该文件是对174 V1容量STOP点的科学合同决定，不改变冻结FAST64／Lane-E／TC80／SG0／SG3及AWMA/C16。**174当前工作树／执行分支不得reset或重启**。核查执行分支当前状态并继续。

## 一、4080选择：选择原128KiB统一物理容量内的DTC组织（方案2）

**拒绝把独立80KiB物理DTC池加到已有128KiB L1/shared之外，并将208KiB拿来与128KiB现代基线声称公平加速。**额外80KiB只能在后续单独授权时作为明确“额外存储的理想上界”，不进入现代主论文比较，也不在本轮自动运行。

具体审计与实施约束：

1. 4080配置锚点：`8d1f14a32f5538660d74da86ccb03a2c504c5735` 的 `configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config` 包含 `-gpgpu_unified_l1d_size 128`（单位KiB）、`-gpgpu_adaptive_cache_config 1`、shared及L1独立配置与默认覆盖。必须按真实解析链和**每个kernel运行期的有效分配**审计，不能仅从配置字面声称所有kernel都可用128KiB L1。
2. 80KiB物理池是每SM **DTC数据行占用**（640×128B）；16KiB“逻辑Tag容量”是128个可搜索映射，不再额外分配16KiB数据阵列。Tag/PIB/掩码/事务控制是额外元数据成本，必须在逻辑/SRAM面积中单列，故“128KiB统一数据共享容量”不等于“所有模块总面积完全相等”。
3. 设有效L1物理数据份额为 `L_k`，shared实际物理占用预算为 `S_k`，DTC池占用为 `P_k`，其他仍实际存在的L1数据阵列/旁路路径需要的存储占用为 `C_k`。原则：`P_k+C_k <= L_k` 且其与 `S_k` 必须在同一统一容量预算内有合法分配；**原L1数据阵列和DTC池不能同时按全额容量实例化而只记账一次**。确切的容量公式必须与实际模型存储/端口共享方式一致。
4. 优先尝试在每个已准入kernel的有效L1预算内保留名义 `P_k=80KiB`，同时为写/原子/旁路等沿原路径的合法访问保留实际必需的 `C_k`；若无法共存，不得为赶结果默认删除原路径阵列、无证据改路由、把全额双数组称为共享、改变合法操作或偷偷缩小shared。不许可就保留4080 **baseline-only**，报告容量/服务实现缺口并停止现代DTC比较；主64-SM已授权实验仍可独立推进。
5. 若现有前端无法只用有限且不重叠的数据阵列表达该组织，先用**CPU-only**明确方案、容量/端口/路径影响、代码改动范围和现有正确性前提。涉及协议或合法容量模型变化的额外科学合同，在实际改动前STOP供用户审；不要为一张现代性能图无限重构模拟器。
6. 现代论文比较至少明确区分：原生/模拟 **现代baseline**，同粒度的结构性传统对照，以及共享同一物理预算的DTC；必须保持input/ROI、shared预算、有效L1及服务条件准确。一组配置中的DTC 80KiB与baseline 128KiB不构成数据容量匹配，但可以是同总数据预算下不同分配策略；不能写“等总面积”，元数据和端口仍需计价。
7. 原来R1的opt-in有限服务、correctness/OFF等价、失败保留、严格验收不变。禁止从208KiB结果推导原生硬件4080的DTC加速，不为取得收益选择容量参数。

**执行门槛：**只接受在同一128KiB物理数据/shared容量内合法、不双计、原路径语义保持且服务约束能够核查的现代DTC比较。若这需要大范围更改功能协议，尽早停在现代DTC容量边界，不拖累64-SM主稿。

## 二、109提交审查及消费边界

已核查 `890fb0be7e681a60419c49ca0a7aa85731d8c164` 分支结果中的：`README.md`、`NATIVE_FINDINGS.md`、`VALIDATION_SUMMARY.md`/`VALIDATION.json`、`TRACE_DELIVERY_AND_GAPS.md`、`OPEN_ISSUES.md`、`R0_ADDED_FAMILY_PATHS.tsv`、`TRACE_AUDIT.json`、`DURABLE_STORE_RECEIPT.json`。来源入口：
`docs/dtc_l1/review_packs/DTC_NATIVE_COVERAGE_109_V1/`

- **接受原生测量/实验源身份交付（按其证据范围）**：12项诊断＋SpMV/LayerNorm两族，总15 cases，每case七个独立进程×10次计时，保留profile、运行版本和计时噪声。30项是109生产/归档一致性验证，**非174 simulator strict验证**。
- **SpMV**：原生数值检查合格，四个完整SM89 cubin的`spmv_jds` kernel（3 warmup＋1 final），36 CTA；SpMV trace生产格式审计PASS，**模拟器opcode/trace/环境/服务准入仍由174判定**。输入`1138_bus`规模小，warm native DRAM读0，未填满4080；不能冒充大规模DRAM/并发压力验证。按固定small-resident样本保留，不能以无收益为由更换。
- **LayerNorm**：原生算子和计时有效，包括1024×1024主形状与8192×1024 native-only对照；**SASS trace NOT_ADMITTED**，实际编译的cubin为SM86且tracer跳过`CALL.REL.NOINC`。不能忽略CALL代价、将完整warp/grid审计当语义准入，也不能将其填入DTC仿真或GM。除非能证明语义完整且确有必要的轻量修复获授权，不启动独立重构/选替代算子。
- 164归档单次SHA `af5c6ec76179f881f689f486829c025055764bd9e564e598c0dc18560865f984`；109记录独立目的端285个payload SHA核验。**此决定复核了GitHub收据，未重复读取164原始压缩包每个字节**。
- 原12程序/629有序成员 **在109不可用**，不代表科学payload不可恢复。174优先依据自身现有接受轨迹及164既有资产查找，不要求109为了补元数据重跑冻结producer。必要时登记新获取的输入身份；不得从名称猜大小。
- 完整前序执行并不证明主机异步拷贝、分配器或初始缓存状态全被捕获。warm native vs cold simulator不得称完全配对。SpMV consumer先核对真实trace支持与完整范围。
- 不新增第3个程序族，不汇总GM14；不重启109完成的任务或抢占GPU。未经原主线授权不扩展AWMA平台资格。

## 三、174下一步交付

继续已通过的R1/64-SM实验和4080 baseline-only pilot；接收109 SpMV证据，单独做严格准入。对现代DTC优先输出 **容量布局审计表**，至少列每个kernel的shared实际预算、有效L1、DTC pool、剩余传统数据阵列与端口、L1/shared统一容量、是否可合法共存、与baseline的可比性、是否需要修改科学合同。容量gate PASS才允许现代DTC数据行滚动运行。进展/失败继续单槽验收、严格记录、推送远端，不提前创造通过标记。

R1之前已经修正的前端顺序问题及保留原始失败UUID/日志不得覆盖。本文件不要求重发Goal、重启或重跑任何已经完成的attempt。
