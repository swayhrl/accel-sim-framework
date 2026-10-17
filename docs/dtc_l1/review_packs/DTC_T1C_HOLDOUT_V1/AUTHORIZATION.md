
Goal: DTC_T1C_HOLDOUT_174_V1

你在原174账户/容器执行，不是174-new。请完成DTC-L1 / ISCAS2027的T1-C固定配置独立holdout验证。用户已于2026-10-17明确批准本Goal的两个新模拟点。

采用solve-and-continue方式：普通工程、包装和Git传输问题在科学合同内自行修复并继续；只有科学身份、输入、机制、资源安全或比较合同无法保持时STOP交审。

一、首先确认冻结状态

Framework:
https://github.com/swayhrl/accel-sim-framework

Lane A:
hrl/iscas2027-dtc-service-closure-174-v1
f5c37d6edcce832a72cb0830021bffa78df6cc13

Lane M:
hrl/iscas2027-dtc-mechanism-consumer-174-v1
d723784a8b897566b63113f95972f7a8d12a01ce

Lane T:
hrl/iscas2027-dtc-tag-pilot-174-v1
f520a445436b57c0a0f2494fb858a1636f04d2bc

先fetch并核对实际远端HEAD，读取Lane T的LATEST_REPORT、FULL_MATRIX、FINAL_IDENTITY_AUDIT、PRE_REGISTRATION、strict及wrapper_repair_v2。

Lane A、M、T均已完成。不得重启、reset、改写其任何Goal、运行目录、原raw、控制身份或锁。

原44行41 PASS、3旧Hotspot HOLD，保持不变。

二、建立全新独立执行lineage

建议分支：
hrl/iscas2027-dtc-t1c-holdout-174-v1

独立worktree：
/workspace/worktrees/accel-sim-iscas2027-dtc-t1c-holdout-174-v1

独立raw：
/workspace/dtc-t1c-holdout-174-v1

新证据目录：
docs/dtc_l1/review_packs/DTC_T1C_HOLDOUT_V1/

从已核实的Lane T源与工具建立新lineage。不得复用其attempt UUID、runner进程或写目录。若存在同名活动工作区，先检查归属，不得强制覆盖。

三、固定科学合同

只验证T1-C：
logical_sets=64
logical_ways=8
logical mappings=512
logical coverage=64KiB

保持：
- OO模式，PIB=128
- physical pool=640×128B=80KiB
- ordinary side=16KiB
- shared=96KiB
- 4 Tag banks，原bank/lookup配额
- 现有finite service全部限制
- global lower cap=32768
- 64SM、原调度和时钟配置
- 原128B整行、4 distinct sectors返回合同
- 原source、binary、parser、runtime及其余全部有效选项

唯一允许的有效选项变化是相对原OO128：
-gpgpu_dtc_l1_logical_sets: 32→64
-gpgpu_dtc_l1_logical_ways: 4→8

冻结身份：
Framework build:
18a68dcccd795f1b6cda75504e9450d00c9cee02

Finite Core:
6fba0136f8465b59fe5858a950fa39efb265f654

Finite binary SHA256:
fe2d2737ebaed01680ebfc2346f727306c8db58ee0ca20b1e1f038056e99833b

运行前必须在原174现场重新核SHA和完整有效配置。不可只核选项文件中的显式参数而忽略默认值。

不得修改Core、parser、trace、有限服务实现或延迟模型。若配置不能合法工作，STOP，不为让结果通过而调整机制。

四、恰好两个预先指定的holdout

H-U1：DWT2D，原冻结完整输入

accepted original OO128：
UUID 95fd9a17-4e88-4063-998e-5713316ec3a1
cycles 237887

accepted C+：
UUID 5f69ab62-9525-4a7c-8853-ad93455479ab
cycles 247588

H-U2：BICG，原冻结完整输入

accepted original OO128：
UUID 8a5da6ac-ef65-4ca0-b1de-15a69d6ba613
cycles 47533116

accepted C+：
UUID f91d33da-730a-4047-998c-566c4fc416c0
cycles 25353488

旧cycles和UUID仅用于定位与交叉核验。必须从Lane A accepted原始记录中核完整stdout、config、input/list、ordered kernels及strict身份。

只允许新运行：
T1-C OO128 × DWT2D
T1-C OO128 × BICG

不允许重新运行旧OO/C+、T1-A/B或扩展第三个负载。DWT2D和BICG都是未参与T1-C选型的输入，但其旧baseline并非未知；不可称完全未见过的程序。

五、任何新性能前必须完成预注册

创建并冻结：
- 两个全新UUID与完整spec
- 原完整trace/list及成员SHA
- ordered kernel、CTA、active-thread instruction预期
- source/Core/binary/parser/runtime身份
- effective config及只允许的两项差异
- 原OO和C+对照UUID及SHA
- 一次启动规则、timeout和资源准入规则
- strict验收规则与失败保留规则

将预注册文件及runner脚本SHA commit、push、fetch-back核验。

上述步骤完成以前，不启动任何新模拟、不消费任何新candidate部分周期。

六、执行与资源安全

先检查真实PID/start_ticks、DTC authority/lock、其它项目进程及cgroup/host内存、swap、PSI、磁盘和IO压力。

沿用Lane T已经验证的资源保护策略及V2项目指纹区分逻辑，不把明确独立的EP-L2进程误判为DTC执行权冲突；但所有项目实际资源占用必须计入统一压力门槛。未知归属的DTC运行或有效冲突锁必须STOP。

默认DWT2D先运行，合格后再运行BICG。最多一个新DTC simulator同时运行，以降低混合项目压力。

必要时等待资源恢复，不准终止其它项目进程，不准借移除旧锁获取执行权。资源安全停止时只处理本Goal确实拥有的进程组。

新attempt最多2次实际启动，每个输入一次。失败、timeout和deadlock都保留原始收据；不得因性能不好重试。包装故障只允许在原身份和原timeout范围内确定性修复，不产生第二个实际attempt。

七、严格验收

必须检查：
- natural exit0与完整terminal
- 完整原输入及全部ordered kernels
- CTA/active-thread instructions逐kernel一致
- Core/binary/parser/runtime/config实际生效身份
- 64SM、pool、PIB、Tag sets/ways、bank、cap
- credit、dependency、lower及ordinary路径守恒
- PIB、inflight、partial、active Ref排空
- physical allocation/reclaim守恒
- 合法Tag-visible retained数据不误判为未排空
- 11项finite service统计
- stdout、原文件和收据SHA
- 资源与运行时间

严格检查沿用Lane T已核语义，不凭空添加模拟器未输出的字段。数值load正确性、独立sector返回、内部MSHR占用等未提供的证据应标UNAVAILABLE。

任何不完整点不能产生正式speedup结论。

八、输出与科学解释

对每个新点独立报告：

R_OO = accepted original OO cycles / new T1-C cycles

R_CPLUS = accepted original C+ cycles / new T1-C cycles

同时报告cycles增减百分比。

完整对照：
- DWT2D原OO、原C+、新T1-C
- BICG原OO、原C+、新T1-C

原T1探索的GEMM/Gaussian两点及A/B/C全矩阵仅作为既有发现证据，不参与新选型。

对于有效同路径字段，比较：
ready/pending/new reference outcomes、
lower created、
physical/PIB residency、
ready-to-collect、
collection、
fully-ready-to-complete、
L2/DRAM可比量。

只使用定义一致的计数器，不把credit转换成DRAM字节，不把条件均值差解释成可加的整机周期贡献。

两个holdout无论正负都报告；不施加未经本合同批准的新硬性能门槛，不按结果改变选点规则。

本Goal仅验证固定配置的外推表现，不授予T1-C自动成为论文主配置的权力；不改原44行、原GM12或v0.11-VI主图。

九、交付与STOP

在DTC_T1C_HOLDOUT_V1目录中至少交付：

PRE_REGISTRATION.tsv
SOURCE_INPUT_IDENTITY.json
CONTROLLED_DELTA.tsv
FULL_MATRIX.tsv
TERMINAL_MECHANISM_COMPARISON.tsv
STRICT_AUDIT.json
EXECUTION_RESOURCES.tsv
SCIENTIFIC_SCOPE.md
LATEST_REPORT.md
FILES_SHA256.tsv
run_receipts/与strict/逐UUID文件

大raw保留原174独立目录。Git只提交小型审查文件、脚本、配置及SHA，不推大stdout、trace、binary或build。

最终push并fetch-back核HEAD/tree、文件SHA和worktree clean。外部最终commit回执可放独立raw root，避免自引用hash循环。

两个点自然收口或合法STOP后结束Goal，向ChatGPT提交科学审查包。

禁止自动开启T2、新observer、physical pool调参、新Tag候选、modern DTC、SpMV/LayerNorm、Hotspot/Btree/2D/LUD扩展、任何新Core或论文主设计替换。
