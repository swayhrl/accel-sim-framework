# Lane O 初步论文 Observation 草案

以下均从访存/资源数据出发。当前数字取自已验收 reference 端点；不是按加速排名挑选。精确输入 SHA、模式、bundle、代码和验收身份见 [证据报告](EVIDENCE_REPORT.md) 及其链接。一个机制可处理某种现象，不等于已证明性能收益。

## 论文正文建议收敛为四个主观察（V1R1）

O1–O8继续保留为可核查的**具体证据条目**，不作为八个并列的论文贡献。以下四条是论文叙事候选；它们是否能支撑某个机制的**性能收益**，需另有同背景对照证明。

| 主观察候选 | 从程序和参考系统出发的事实 | 机制侧已观测结果与仍缺的证据 |
|---|---|---|
| **W：写回造成数据搬移与等待，负载间差别很大** | S的脏替换copy、WB_DATA_SPACE和同址WB独立受阻请求均有正负样本；Scan是重要正例 | 还需统一起点的WB阶段寿命、同址R/W/A×WB年龄；不能把retry算成GPU独占停顿 |
| **V：淘汰后仍可能发生读取，但时间复用并不等于空间sector连续触达** | 历史reuse/post-eviction已有独立证据，精确输入映射尚待核验 | F/WV有真实Victim响应与零响应端点；缺首次重访时间、复用距离、服务对象年龄及容量适配 |
| **M：同址读请求重叠与不同地址并发消耗不同资源** | S中有Line-MSHR满与每地址合并上限两类压力；不同输入差异显著 | F有RO事务合并，但严格fill前重访和普通+RO独立地址并集仍未知；live merge不能代替这两个分布 |
| **T：Tag占用寿命与新请求进入需求可能错配，机会必须同Set同刻联合观察** | S的Conv出现真实前端满路新地址需求，负例同样存在 | F已有Vector、Conv缩容实际detach；缺直接三重联合和同背景F−T/F，不能把触发当净加速 |

**用S作为访存需求与参考资源压力的首选观察背景；用F/WV描述Victim、RO和T的实际行为。** 同Source同配置的消融比较才解释单项机制收益；S中RO运行时不存在是NOT_APPLICABLE，不是程序没有RO资格。

## 已证实的证据条目 O1–O8（不是八条并列的论文主观察）

| 草案 | 数据与适用域 | 对结构设计的含义 |
|---|---|---|
| O1 脏替换引入可观的额外数据搬移，但程度依负载而变 | Source78参考S，Conv/scan/srad/stencil的copy read+write约占独立payload RAM操作的11–14%；Conv有720,834次WB及同数copy read、copy write。25个S端点中10个WB=0 | W的就地角色转换针对已发生的copy；优先研究高copy样本，并保留零WB控制。不能将操作占比当GPU停顿占比 |
| O2 写回依赖的重复等待可以集中在很少的独立请求上 | Conv SAME_ADDRESS_WB为16,791个独立首次受阻请求、3,736,508次检查；占5,239,872个requester的0.32045%。scan为390个、215,979次，占42,763,048个的0.000912%。scan另有1,737,618个WB_DATA_SPACE受阻请求，WBUF峰16、时间均值10.661 | 写回地址依赖与WB数据空间是不同问题。W/V可能缩短或服务这些等待，必须先区分R/W/A和WB阶段。大retry不能证明广泛影响 |
| O3 部分被替换数据确实继续服务读取，保留收益具有选择性 | 当前23个F reference端点中10个V读响应>0、13个为0。stencil4,930,616、3MM1,147,507、GEMM586,844；Vector4M/6M、2DCONV/3DCONV、sgemm为0，尽管都有安装 | V有真实服务见证；安装量不能预测服务价值。还不能由响应数确定所需容量、复用距离、避免的lower请求数或独立性能收益 |
| O4 读取与mandatory写回生命周期在部分真实负载中交叠 | 当前accepted FWT WV有3,312次dirty-forward，scan F有296次，3MM F75次、stencil F20次；均为实际response commit | W/V可以复用仍在WB状态的权威数据。非dirty-forward响应也可能来自WB_COMPLETE，不能全部当clean victim |
| O5 RO资格与低短期重复性是两个独立维度 | 当前Vector4M的1,000,000个RO requester中749,913个merge；SGEMM的1,135,915个中1,054,333个merge。它们合并到尚存活RO事务，可能包括ready/draining | M可绕开普通line-MSHR，但descriptor和合并价值仍存在；T的reuse_seen保护有实际适用背景。严格fill前重复比例仍未证实，不能称这些RO“无复用” |
| O6 独立地址容量与同地址合并限制出现在不同负载 | 既有44个reference端点中，Conv S line-MSHR峰128、6,499次full检查对应696个独立受阻UID；SGEMM S每地址32上限的1,738次检查对应55个UID；D512 full在此44端点中均0。Vector S峰110但line-full为0 | M的目标须区分全局独立line数与同址chain上限；普通MSHR占用不能代表全部RO并发。是否值得绕过或扩容需结合流量/等待，不从峰或性能推断 |
| O7 Tag释放机会取决于目标Set的新需求与瞬时保留状态 | 同Source78的已接受timeline，Conv首次NEW-at-R8为289/1,503,281，对应42,717次preview Tag失败；CFD诊断1/171,765和11次。Vector32×8 NEW-at-R8为0。actual-access TagFAIL均可为0，因为preview已拒绝 | T必须在同一NEW、同一Set、同一时刻测量结构可释放RO，不能把满路与RO边际拼接。CFD仅限5-kernel诊断，不升级为主42完整输入 |
| O8 有限way配置中已发生真实detach，触发事实与净收益分属不同证据层 | Source78的Vector4M 32×4有27次detach（F75,583、S75,484 cycles）；**Conv 16×8有237次**（F367,152、S360,380），**Conv 32×4有1,141次**（F425,074、S395,820）。均为同输入/同几何合法S/F接受点，但尚无同背景F−T/F | Detach在实际输入中发生且随配置改变；三例F均慢于S，不证明T单独负贡献；也不能由detach次数判定加速。4way可选寿命/Tag联合人口未补齐；不为追非零继续缩Tag |

这些草案说明现象异质且有正负样本。O1–O8是参考模型条件下的运行事实，不声称物理GPU必然相同。

## 已有历史观察与其验收边界

**H1 历史line局部性很短，但普通命中与victim机会必须分开。** Motivation的10程序审查接受了DATA/SEMANTICS，仍需packaging收尾：reuse-instance中distance≤32约68.8%–100%、≤128约86.2%–100%；post-eviction再访问率在CFD约27.2%、FWT约24.8%、scan约15.2%，而Vector4M/spmv/sad/gemm为zero/none。这支持历史配置下真实存在且高度异质的淘汰后再访，不能将普通reuse CDF变成K项victim捕获率。原小CSV与输入manifest本轮尚未核验，不将审查约数写成当前输入的新精确测量。[历史审查与谱系](agents/V.md)

**H2 高line重复可能来自空间触达。** Streaming prefinal方向审查中Vector4M/BlackScholes为line reuse0.75、sector temporal reuse0；相反，条件于真正sector时间复用，FWT的>1024尾约61.44%、Conv约39.27%。这是方向通过、final promotion未闭合的候选证据；同请求多sector的recency顺序证明和final delta仍需核实。它要求后续指标区分128B line空间延续与32B sector时间复用，不能推出“所有复用都很近”或“当前Vector6M已测无时间复用”。[历史边界](agents/V.md)

## 待验证的现象

| 问题 | 已有动机 | 真正缺少的证据 |
|---|---|---|
| WB持续时间是否使某类独立R/W/A频繁等待 | 现有独立同址阻塞和dirty-forward | WB年龄/阶段×请求类型联合分布；当前reason wait不是整段WB寿命 |
| 有限保留窗口能覆盖多少post-eviction读复用 | 历史再访和当前实际V服务 | 当前精确输入下的first-next-touch、对象年龄/删失、目录与payload联合约束；不能从响应数倒推容量 |
| RO在fill前是否几乎不再访问 | 现有live merge事实反对无条件低复用假设 | 首次独立requester到达与sector ready/fill的联合人口；ready-only drain另列 |
| 普通MSHR与RO事务的并发需求是否互补 | 普通MSHR及RO pending各自峰值已有 | 地址并集的时间分布；不能将各自峰相加 |
| 旧RO占Tag时是否正好有别址因满路等待 | Conv满路与历史/当前RO正人口分别已有 | 同NEW∧目标Set满路∧结构可detach的直接联合，structural与policy enabled分开 |
| 有机会的W/V/M/T能否改善服务或性能 | 已有结构事件 | 后续同Source/ELF/输入/背景的独立控制；不是本轮characterization启动条件 |

## 不成立或不能成立为论文结论的表述

- **被当前数据否定**：“所有真实负载没有Tag压力或detach”“所有保留对象都会再次读取”“RO事务不会发生同址合并”。上述正例直接否定这些全称判断。
- **统计含义错误**：“retry次数=独立受阻请求=GPU停顿周期”“WAD峰128意味着WBUF16满”“ordinary MSHR峰0意味着无访存并发”“actual-access TagFAIL0意味着无preview阻塞”。
- **缺乏证据，不能当作已否定机制**：“V响应0说明程序无复用”“F比S慢说明T无价值”“copy减少或detach27必然加速”。这些是未成立的推断，不是已证实的机制负结论。
- **粒度或人口混用**：“128B line重复就是真sector时间复用”“all-demand reuse CDF直接给出victim容量K”“历史tiny输入/不同Core/未接受快照可填当前全workload空格”。

后续正式论文以顶部四条主观察组织，O1–O8作为相应数据证据及正负例。W/V/M/T是针对这些现象的候选设计，必须在完整工作负载和公平S/F或合法消融控制中另证实际收益；不将四条观察写成四个已证实的加速因果链。
