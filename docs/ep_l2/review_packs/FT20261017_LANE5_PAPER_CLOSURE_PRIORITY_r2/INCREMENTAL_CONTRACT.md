# EP-L2：性能证据、RTL成本与最小验证的并行收敛计划

本文件是EN-v10审稿修订后的增量任务合同。用户要求性能结果与分析优先；新增一条按模拟器协议实现RTL、先开源综合、后由作者用DC重跑的成本线。发布本文件不表示Codex已收到任务或远端运行已启动。

## 0. 起点与不变边界

- 当前写作母稿：本对话附件 `EP_L2_EN_v10_REVIEW_FIX_SOURCE.zip`，不是远端Lane6旧EN-v8。母稿未取得时不得臆造远端路径或重建正文；先交付结果表和独立段落，后续再接收附件。
- Lane1发行索引：Framework `72ac64f2a29a162667e8304e8d39a763a015cac6`，`docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane1/PARALLEL_RUNTIME_RELEASE_INDEX_R1.json`。局部Ideal、S64、U_CAP16、P2、ALL_DATA已经有producer发行，不重复开发。
- 已知联合发行：Core `9bd30ed913c5058b5d952fbeb2e67cb5e4644b3f` / Framework `8ab6013ea90755fdc74819e92090c2de50f4f199` / binary `fb67448d08818bc8cbe72961580e8340f0e6f337a4df95e7c8ee9468472953f7`。正式应用支持范围以Lane5实际独立资格为准；RTL只能对应其中有限WB路径，不能实现Ideal来获取低成本。
- 本次读到Lane5 HEAD `8fcb42872ac8be66c54f3a11501b70ec3b1a4ca6`。其STATUS报告继续运行和I_META待发布快照；staged V2不自动等于当前接受。实际开始前读取最新STATUS、current pointer、撤回状态、run registry及source assignment，保留已在途任务。
- 原H0数据身份Core7b8 / Framework9bd / binary2309保持。已接受数值不因改文稿、RTL开发或无关账本追加自动重跑；跨binary比较按已有同源锚点规则。
- 仍使用唯一中央registry；完整应用仅Lane5启动。4长期sim / 8 CPU / 32GiB预约、workspace48GiB / Share40GiB / available RAM64GiB保护线保持。结果保留总额12GiB及既有每运行上限保持；EDA产物不得借新目录绕过资源计账。代码仓库小文件与构建产物按实际规则分类，不重复计账，也不把未计账临时产物当免费空间。
- 原R19 cap24、T0与期限，新potential cap72、T0与期限全部不变。过期不新起应用、不换campaign逃避限制。本文件不授权新一轮大规模仿真。

## 1. 三条工作线与交付目标

| 线 | Owner | 立即动作 | 完成证据 |
|---|---|---|---|
| 强静态/有限配置/Ideal应用 | Lane5，原Goal增量CONTINUE | 完成已准入运行，轮转既有矩阵；优先使Conv/FWT四种组织及局部/全数据Ideal形成可比较组 | 完整配对、绝对cycles、同源对照、目标资源实际触发和解除情况 |
| 机理解释及最小正确性补证 | Lane3，新短Goal | 优先消费已有raw/定向测试，不新增全应用；定位最有解释力案例并形成论文图表 | 有限因果结论、差异分解、已有证据复用与剩余缺口 |
| RTL实现成本和DC交接 | Lane2，新独立Goal | 将有限WB协议落实为可综合的单slice改动路径；B16/S64/U三种参数化构建，先开源工具 | 经基本功能检查的RTL、同约束综合/STA报告、明确SRAM范围、DC脚本 |

Lane1/4原发行任务不重启。只有确需修复或增加受控时序模型接口时，向Lane1交付最小问题/补丁请求。Lane6在新配对或成本报告可接收时做短增量写作，不为每个中间状态重编译全文、不等完整矩阵结束。

## 2. Lane5：强静态与性能潜力，增量CONTINUE

### 2.1 先得到能裁决贡献的配对

不取消在途运行；在既有矩阵及总预算内，让以下端点优先构成完整可比较组：

1. Conv/FWT同系统条件、同正式binary下的B16、S64、U_CAP16、Unified。B16锚点可合法复用，不因新文稿重跑。S64仍满时报告绑定资源，不能称其最优静态；需要再扩大静态配额时先交明确请求，不默默新增全sweep。
2. 已就绪的I_WB、I_META、联合I_WB_META、I_READ_HIT及I_MEM_ALL_DATA，与各自同源有限锚点比较。一个模式未就绪不阻塞其余模式；source37dc既有Vector端点继续保留，不能拼成sourcefb的同源锚点。
3. 既有ROP/ICNT/WAD/L1及下游有限条件，保持B/U同等变化。新增较好条件要在该相同条件检查强静态和必要消融，不能用H0的S64证明另一个环境的竞争力。

每个结果保留绝对cycles、S=C_B/C_U和分母身份；分别报告copy、真实bank工作、WB-data/WAD、命中/写回流量、压力变化。性能方向不作为接受条件。未触发目标限制、解除后无收益、尚未合格和实际失败分别记录。

### 2.2 避免无效扩张

本文件不扩大50 seed cells/72 starts。有限联合仍最多两组，按原合同保留00/10/01/11及匹配B/U，启动前登记依据和预算。只因两个单项收益小，不得直接断言组合无效；也不因某点好看就扫描全部参数。

有一个候选成为论文性能主张后，从既有未参与该候选选择的输入中做一个B/U验证配对；同条件强静态若仍是主张关键，也需对应比较。已有输入不称从未见过。没有额外预算时保留适用范围限制，不绕过上限。不要扩展新AI模型、抓新大型trace、做现代GPU平台复现或重复确定性样本来凑误差棒。

### 2.3 接受与输出

依旧按真实mode/scope做独立资格和终态检查。已验证且内容不变的文件复用hash/proof；仅因全局generation上升不重跑全trace hash。异常实际影响哪个source/profile就隔离哪个，不牵连无关已接受结果。当前Goal执行至原边界；需新额度/期限时交接，不自动续期。

给Lane3/6发布不可变配对输入与精确源身份，收到分析请求只提供现成日志定位；没有必要不改运行observer、不重编译在途runtime。

## 3. Lane3：机理解释与最小验证，新短Goal

在原Lane3基础上使用独立分析目录和正常非force提交。保留原RO及参数候选。不得自行启动完整应用或改变Lane5 ledger。

### 3.1 先分析现成结果，不先加观测系统

读取当前接受结果及已有raw、每kernel/窗口计数、请求时间戳和定向测试。固定问题：

- S64是否已消除静态WB数据配额限制？S64与Unified之间还剩什么差异？
- Unified相对U_CAP16的变化是否支持额外本地WB并发的作用？U_CAP16/B16包含组织、落点和复制差异，不命名pure-copy。
- 局部Ideal小而ALL_DATA大，支持哪一级机会；局部和全数据都小，在哪个输入/定义范围内可收窄结论？不能将ALL_DATA写成EP-L2 speedup或任意调度下严格数学上界。
- 正例或退化中，frontend pending/HOL、same-line WAD等待、payload bank落点及下游服务哪个解释有证据？

每个案例按“观察→竞争性解释→受控对照→结论及范围”写。优先完整展示Conv/FWT；另保留CFD负例或实际最相关退化，不能只选最优点。相同业务事件才比较时间区间；旧B/U staging起点不同不能直接对比。拒绝重试计数与操作等待不相加为执行时间。

已有kernel shared-delta必须核对overlap，不把重叠窗口相加为独占周期。先看shared normal path瓶颈，不能凭计数最大就称关键路径。若缺少决定性观测，只提出一项最小定向实验或默认关闭的观测补丁，经Lane1/5进入原预算；不先建新的critical-path框架。

### 3.2 最小正确性补证，嵌入本Goal

先列已有检查的真实覆盖，复用不变源码上的合格证明。只补会改变结果可信度的缺口，目标为6类、约8–12个短定向case，不是再跑完整benchmark：

1. 同sector不同字节的32/64-bit合法写，byte mask保留与未覆盖字节不被误覆盖。
2. 同line部分写后读、不同producer相邻字节与被延迟响应snapshot。
3. dirty数据lower accept前后、本地槽复用但WAD未完成时的same-line顺序。
4. bank冲突与victim固定、多周期重试不重复reserve或commit。
5. response/lower背压、合法rollback、容量边界和exact-once释放。
6. payload复用及晚到事件不污染新incarnation，有限generation方案的约束由RTL线提供。

共享最小stimulus与独立byte reference供Lane2 RTL测试复用。模拟器的symbolic接口只能比较其实际可观测范围：mask、sector版本、request/snapshot/lifecycle；不能把独立reference自测PASS或原始trace文件字节hash称作byte-merge生产正确性。能用已有生产驱动已知字节fixture闭合就复用；只有symbolic证据时明确保留范围，不伪造完整数值等价。

若发现真实输入会触发的错误，标明影响source/profile，提交最小复现并通知Lane1/5；错误不能通过删除检查或仅加论文限制规避。未证明广泛语义不自动撤销有限范围正确证据，但必须确保论文性能范围与被证明输入范围一致。

### 3.3 输入适用性只做必要补齐

从现有manifest/原capture材料整理suite、版本标签、literal命令、输入大小、kernel数和计时边界，没依据的内容写未披露。先定位已有捕获来源，不开展无尽考古，不因缺少外围历史机器信息阻塞独立可复核的当前范围。完整commandlist不自动等于完整源码默认循环。是否有新验证样本交Lane5在原预算内安排，不另开全套泛化实验。

### 3.4 交付与停点

第一份分析以2小时为交付检查点（不是性能仿真deadline变更）：已有数据派生CSV/脚本、图表草稿、case结论、6类检查复用/新增/缺失表、最小缺口请求。未到新数据时正常结束，后续事件再续；不建常驻轮询器。不要把文献或输入全面调研作为本Goal前置。新颖性仅形成选定最近相关工作的能力对照，最终科学贡献由实际结果裁决。

## 4. Lane2：可综合RTL、开源成本及DC交接，新Goal

### 4.1 实现方式与范围

把模拟器已明确的有限协议、资源组织、并发和流水边界作为功能/周期规格，编写可综合Verilog/SystemVerilog。不是将std::map/vector、C++对象布局或全部模拟器直接HLS；日志、历史统计、符号版本sidecar不是物理数据阵列，不能算作硬件payload。

用独立worktree/目录，建议任务分支 `hrl/ep-l2-rtl-cost-v1`。先核本地已有RTL/开源工具/库，保留任何已有成果。源入口从发行索引解析：普通B16/Unified基于正式有限路径，S64使用Lane1集成版本的实际实现；列出与论文source7b8及将用于新性能结果source的有限路径差异，不把Ideal也综合进去。

实现“单slice中受EP-L2改动影响的完整控制和数据访问路径”：Tag-to-payload映射、bank-compatible allocation、role/owner/pin与必要sector状态、pending replacement、copy latch/原位转权、bank仲裁、WB数据交接和WAD生命周期接口。明确哪些传统Tag/MSHR控制复用或在边界外；被排除的部分不能计成0成本。如果只能完成控制器子模块，就准确标controller-only，不称整L2综合。

同一套参数化RTL分别elaborate B16、S64、Unified；模式为综合时常量，不为每种实现都综合所有模式mux。最低完整比较为B16/U，S64通过参数化随后加入。U_CAP16是消融，P2是额外端口资源诊断；除非其有限实现成为论文最终主张，不为它们重开额外RTL体系。若最终采用P2等，必须补真实匹配资源成本。

### 4.2 硬件语义不得在翻译中改变

- 容量、4banks×292slots、128B line/32B sectors、真实bank grant和已知配额均保持；地址、句柄、generation、计数器位宽须有依据。无法证明可缩小时先保守保留参数，并列成本敏感性；不凭经验选小G掩盖回绕风险。
- pins/refcounts、pending reservation、同line WAD等待、lower_accept与set_done分离、跨周期victim绑定和rollback均需真实RTL状态。
- byte enable、1024-bit数据通路和公共copy latch真实存在；不能拿sector版本整数替代数据宽度。
- 源码循环搜索不能无代价变成同拍无限带宽。明确硬件的组合选择、有限端口、优先级与拍边界。若可综合实现需要额外pipeline/不同吞吐，发布SIM_RTL_TIMING_GAP，不能默改RTL后继续引用原模拟器性能。
- 分别检查hit-data、allocation/replacement、WB出队三类关键路径。只在allocator上需要新增周期，不等于给所有命中统一加一拍；默认160-cycle ROP也不是自动可用的内部时序余量。

### 4.3 最小RTL功能检查

先lint/编译，再使用Lane3共享或同规格的8–12个短case和小范围随机ready/valid背压，比较独立byte-address参考与实际RTL输出、mask、请求完成及资源终态。模拟器输出只在真实可观测范围比对。B16/S64/U分别检查，保留失败并修复；至少证明copy路径真的活跃而U原位路径工作，综合报告没有把待测逻辑优化没。

不要求完整GPU数值仿真、全系统形式化、所有atomic/RO/TVD或硅后验证。小容量参数可用于边界case，但成本综合使用论文完整容量；关键宽度/寻址边界补全尺寸检查。缩小fixture不能冒充全尺寸PPA。

### 4.4 第一层：Yosys＋Liberty＋OpenSTA

优先已有可用工具和库；缺失时只做本地隔离安装/使用合规现成发行，不进行大规模系统升级、全量ORFS源码构建或无限库搜索。先用一个极小设计验证工具链。库若暂不可用，继续交RTL/测试和明确阻塞，不伪造面积。

首先完成完整容量B16/S64/U在同一开放库、PVT、相同约束下的标准单元映射与门级STA。可优先使用本地已有Nangate45/其他合法库；它是开放库评价条件，不能称目标芯片工艺，也不拿其绝对频率直接证明1132MHz目标已满足。

所有模式共用规范SDC：周期、IO延迟/负载、clock uncertainty、fanout/transition限制、RAM接口和例外。目标周期与探索周期分开；若开源库无法满足目标，报告WNS/TNS/路径，不给U独自放松约束或通过虚假false/multicycle path过关。

输出总/组合/时序cell面积、分模块面积与cell数、关键路径类型和delay、WNS/TNS、约束覆盖、未映射cell、锁存器检查、blackbox清单、工具版本和library/corner/hash。有意义的B/U输出必须连接，不能把空壳/被优化消失的模块当低成本。

### 4.5 SRAM和时序范围是硬门槛

146KiB payload不能默认展开成海量DFF/mux后称SRAM-L2面积。使用统一参数化memory wrapper：仿真有真实byte-enable行为；综合用已有匹配宏或明确保留宏边界。无匹配宏时报告“实际综合的控制/访问逻辑＋单列SRAM容量/端口模型”，未知宏面积/时延为空而不是0。必要拆bank、byte-enable外围、mux/解码不能因容量相同全部抵消。

没有RAM时序模型时，OpenSTA只能证明标出的控制器/接口路径，不能推导完整L2 hit latency或整slice Fmax；需要RAM接口预算但未被数据支持时标假设。无SPEF的网表级STA不是post-layout。禁止声称“RTL代码生成或综合成功证明了数据正确性”。

### 4.6 第二层可选：OpenROAD布局后时序

仅在已有环境可直接用且第一层结果已经交付时，按相同floorplan/利用率/库和约束补placement/CTS及可用RC估计；明确是placement估计还是post-route SPEF。完整GDS不在必需路径。不要为追求完整物理流程拖住性能分析或DC交接。

功耗不是首轮必交。只有有匹配activity、RAM能量模型和完整成本范围时才给限定范围估计；默认toggle或只看copy减少不能宣称实际GPU节能。先把面积和时序做到可用。

### 4.7 DC ready同时交付

与开源版本使用同一RTL提交、top/参数、memory wrapper及规范约束，提供filelist、test入口、yosys脚本、OpenSTA脚本、可选OpenROAD配置、`run_dc.tcl`和最小调用说明。DC实际target/link library、宏库、corner等使用显式参数，缺少时快速报错，不填虚构路径；真实技术库不上传公开GitHub。

作者一两天后只需配置本地库/工艺并运行。DC尚未执行标UNRUN；DC综合不是硅测，也不自动等于signoff/布线后。若DC使用不同工艺库，与开源结果分别做各自库内B/S64/U比较，不把绝对mm2/MHz混为同一次工具对照。

首版以8小时为交付检查点：无论完整物理流程是否结束，先发布已完成RTL/测试/真实报告/剩余缺项；不是承诺8小时必定获得全PPA。普通工程问题自行解决，不为一个可选工具缺失整体停工。

## 5. 短文验证与适用范围的取舍

必须做的是“与实际主张对应的最小正确性”，不是堆测试页数。原资格复用，新增RTL做基本功能，实际发现错误立即处理。方法正文用一小段交代non-atomic范围、独立数据/状态检查、输入和计时边界；具体case进复现材料。

暂不做：全应用数值重放、全GPU死锁形式化、完整一致性/atomic/RO/TVD、全新AI模型与跨GPU平台、无边界capture考古、大量新benchmark。这些不作为本次投稿前置。

建议做一个既有未参与新配置选择的B/U验证点，前提是预算与时间允许；没有时相应收窄外推结论。不能因为篇幅短删掉已知会影响结果的正确性问题，但可以不建立论文没有声称的普适性。

## 6. 论文事件驱动交付

Lane6后续消费EN-v10附件和经过独立接受的新结果，更新强静态图、Ideal机会图、有限参数交互及限定范围成本表。不是重新写一篇论文。性能/正确性/PPA来源分别标明；不能将代码完成写成应用结果、将开源预布局值写成DC或实测硅数据。

性能第一优先；RTL并行，不等DC才成稿；最小验证嵌入分析/RTL任务，不再单开大验证项目。贡献仍由结果决定，任务目标不是保证跑出正收益。

## 7. 工具依据（用于执行时核对，版本仍以实际环境为准）

- Yosys官方：Liberty映射与综合流程，https://yosyshq.net/yosys/
- Yosys官方：memory默认映射及memory_libmap，https://yosyshq.readthedocs.io/projects/yosys/en/v0.56/using_yosys/synthesis/memory.html
- OpenSTA：Liberty/SDC/SPEF与无寄生范围，https://opensta.readthedocs.io/en/latest/Examples/
- OpenROAD Flow官方：Yosys、布局布线与平台，https://openroad-flow-scripts.readthedocs.io/en/latest/user/UserGuide.html
- Synopsys官方：Design Compiler RTL synthesis，https://www.synopsys.com/implementation-and-signoff/rtl-synthesis-test/design-compiler.html
