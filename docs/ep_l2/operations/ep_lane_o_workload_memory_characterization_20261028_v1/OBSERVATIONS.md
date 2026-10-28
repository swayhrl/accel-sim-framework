# Lane O 初步论文 Observation 草案

以下均从访存/资源数据出发。当前数字取自已验收 reference 端点；不是按加速排名挑选。精确输入 SHA、模式、bundle、代码和验收身份见 [证据报告](EVIDENCE_REPORT.md) 及其链接。一个机制可处理某种现象，不等于已证明性能收益。

## 已证实的现象

| 草案 | 数据与适用域 | 对结构设计的含义 |
|---|---|---|
| O1 脏替换引入可观的额外数据搬移，但程度依负载而变 | Source78参考S，Conv/scan/srad/stencil的copy read+write约占独立payload RAM操作的11–14%；Conv有720,834次WB及同数copy read、copy write。25个S端点中10个WB=0 | W的就地角色转换针对已发生的copy；优先研究高copy样本，并保留零WB控制。不能将操作占比当GPU停顿占比 |
| O2 写回依赖的重复等待可以集中在很少的独立请求上 | Conv SAME_ADDRESS_WB为16,791个独立首次受阻请求、3,736,508次检查；占5,239,872个requester的0.32045%。scan为390个、215,979次，占42,763,048个的0.000912%。scan另有1,737,618个WB_DATA_SPACE受阻请求，WBUF峰16、时间均值10.661 | 写回地址依赖与WB数据空间是不同问题。W/V可能缩短或服务这些等待，必须先区分R/W/A和WB阶段。大retry不能证明广泛影响 |
| O3 部分被替换数据确实继续服务读取，保留收益具有选择性 | 当前23个F reference端点中10个V读响应>0、13个为0。stencil4,930,616、3MM1,147,507、GEMM586,844；Vector4M/6M、2DCONV/3DCONV、sgemm为0，尽管都有安装 | V有真实服务见证；安装量不能预测服务价值。还不能由响应数确定所需容量、复用距离、避免的lower请求数或独立性能收益 |
| O4 读取与mandatory写回生命周期在部分真实负载中交叠 | 当前accepted FWT WV有3,312次dirty-forward，scan F有296次，3MM F75次、stencil F20次；均为实际response commit | W/V可以复用仍在WB状态的权威数据。非dirty-forward响应也可能来自WB_COMPLETE，不能全部当clean victim |
| O5 RO资格与低短期重复性是两个独立维度 | 当前Vector4M的1,000,000个RO requester中749,913个merge；SGEMM的1,135,915个中1,054,333个merge。它们合并到尚存活RO事务，可能包括ready/draining | M可绕开普通line-MSHR，但descriptor和合并价值仍存在；T的reuse_seen保护有实际适用背景。严格fill前重复比例仍未证实，不能称这些RO“无复用” |
| O6 独立地址容量与同地址合并限制出现在不同负载 | 既有44个reference端点中，Conv S line-MSHR峰128、6,499次full检查对应696个独立受阻UID；SGEMM S每地址32上限的1,738次检查对应55个UID；D512 full在此44端点中均0。Vector S峰110但line-full为0 | M的目标须区分全局独立line数与同址chain上限；普通MSHR占用不能代表全部RO并发。是否值得绕过或扩容需结合流量/等待，不从峰或性能推断 |
| O7 Tag释放机会取决于目标Set的新需求与瞬时保留状态 | 同Source78的已接受timeline，Conv首次NEW-at-R8为289/1,503,281，对应42,717次preview Tag失败；CFD诊断1/171,765和11次。Vector32×8 NEW-at-R8为0。actual-access TagFAIL均可为0，因为preview已拒绝 | T必须在同一NEW、同一Set、同一时刻测量结构可释放RO，不能把满路与RO边际拼接。CFD仅限5-kernel诊断，不升级为主42完整输入 |
| O8 有限way配置中已发生真实detach，触发事实与净收益分属不同证据层 | Vector4M Source78的32×4已接受F端点detach27；32×8和16×8分别0。该32×4 F为75,583cycles、匹配S为75,484，但没有同背景F−T/F对照 | 不再沿用“真实负载从不detach”的概括。既不能由27次证明T加速，也不能由完整F慢于S证明T无益；本轮不新增缩Tag搜索 |

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

后续正式Observation应优先围绕O2/O3/O5/O7的异质性组织：写回等待的覆盖范围、淘汰后仍有读价值、RO的合并价值、Tag瞬时联合机会。W/V/M/T作为对这些现象的候选响应，在同一张证据表中另列，不提前写成必然收益链。
