# 六项轻量审查清单：整合B/C独立画像，排序不读F结果

**高价值机制对象优先FWT、DWT2D、CFD；Conv保留既有控制锚点，vectorAdd保留独立负样本，SGEMM medium预留新增独立验证。** 这6项是审查/机制互补优先级，不是预测加速榜，也不是新增6个实验或启动授权。FWT已有E正在执行的原计划，不得重复；DWT/CFD须E绑定当前binary/input/config，Conv只保留原矩阵之后可能的控制。SGEMM未被E正式登记。

1. FWT：传统S WB/copy178569、WBfull890294、同址hazard276421；B保存模型131072读line均与store重合、41943040 lane-line读引用。是W压力和读写复用假说，非实际L2复用距离。原完整RO证明0覆盖，可与Conv区分传统跟踪压力背景；实际F指标只在E接受后分析。
2. DWT2D：旧B0 WAD-full74044、scheduler281249；B保存模型122880读line中98304也有store，5066286读引用落其上。E完整10kernel原字节/native输入证明保留，值得独立多阶段复用检验。旧B0预算1152/descriptor256不同于当前1168/512，不把旧计数当main61 S或WB流量。
3. CFD：传统S copy31123、WBfull仅5、同址hazard9841、bank等待观察102546；B模型15180读写line/2869330读引用。较低WB容量阻塞但存在同址相关性，有助区分容量、依赖与复用机会。实际evict→read距离/sector存活UNKNOWN。
4. Conv：S复制/WB空间/line-MSHR压力与已认证输入支持原先登记的控制锚点；不因目前可见F结果把它重选成新“盲选”样本。当前接受S/F无需重跑，remove-one尚需独立资格。
5. vectorAdd：传统S copy100568、WBfull440161，模型GPU读写line交集0；保留高写回但dirty读复用缺失的独立负样本。不能据此声称clean victim没有复用，也不能假定最终F零收益。属于原七输入，不冒称新增输入。
6. SGEMM medium：低跟踪压力稠密/计算复用独立验证样本。D完整2.216GB静态输入/非原子/byte闭合，旧B0 tag/MSHR/descriptor0、per-address1409。E仍未登记；RO证书UNKNOWN，未认证line须按固定合法F普通路径回退。保留负结果价值，不因预期加速挑选。

准确input composite、来源、逐项传统压力、模型计数类型及成本在CANDIDATE_SHORTLIST.csv、S_ONLY_CANDIDATE_FEATURES.json及冻结B原始画像。排序只消费传统S/旧B0背景、全输入无序访存模型、资格与成本字段。**未使用F cycles、F加速或F命中作为排序键**；B原始表中的current_actual_victim_read_responses等F字段仅留为原件，不导入S_ONLY_CANDIDATE_FEATURES。读写集合重合不代表先写后读，不代表短距离/淘汰后复用；真实L2顺序/寿命UNKNOWN。

## B/C独立接收

本轮第二次fetch获得B新提交 `78e69a54ee2834bb9c5fd838baa4ee695ce7f43a`，已完整阅读其screen REPORT、CANDIDATE_PROFILES及RANKED_CANDIDATES，并冻结源SHA。其提取只读保存统计/模型、不读trace正文、不启动应用，独立支持上述FWT/DWT/CFD假说及vector负对照。它也明确没有证明任何候选存在大量短距离淘汰后V复用。Conv当前F计数用于机制归因单独报告，未作为选择新输入的依据。

C新提交 `1eb8f5254c5e4bc12e4519476a997a6e11a97ec4` 已fetch并完整阅读REVIEW及逐应用T/M画像。C只读当前Conv S和原完整epoch模型，没有读F性能/计数；独立支持Conv的M机会（实际line峰128、1824个被阻塞请求），**不支持已知T瓶颈**（当前one-set reserved max7<16、Tag pending拒绝0；早期guard仍可能遮蔽）。这与B的W/V优先级是互补信息，不是投票或加速榜。

C模型RO读lane比例：Conv49.895%、vector100%、CFD36.532%、DWT13.437%、SAD2.295%、FWT0；这些分母是模型读lane引用，不是native准入概率/缓存miss/Tag脱离率。结合B，FWT是有W/V假说但零RO资格的T/M负对照；vector是高W、模型无dirty读复用、RO覆盖广却无已证明追踪瓶颈的交叉负样本。CFD/DWT提供较小RO子集与依赖/多阶段复用假说。SAD低压力小RO子集仍在原七输入中保留，六项提名上限内不额外重复提名。SGEMM继续作为新增、低跟踪压力验证样本，RO UNKNOWN、E待定。

B/C彼此没有完成真实evict→read/Tag拥塞/RO阻塞UID交集的独立测量；读写集合及RO覆盖并不能认证这种时间关系。两份独立画像均冻结原件/hash并按实际scope合并到S_ONLY_CANDIDATE_FEATURES，没有把F命中/加速导入排序。C保留的旧失败/未运行fixture不被D升级为当前native PASS；较新的E准确资格和接受配对仍为权威。
## 输入HOLD、探索集合与统计

Btree继续原七输入HOLD，不因旧oracle读写重合而排名，不修改trace/解析器。SpMV Dubcova3第80103行字段缺失、Scan kernel7非零mask/full32冲突继续HOLD；旧压力即使很强也不进入可运行推荐。它们的旧审查保留，既有失败不重扫。本轮没有凭空添加其它合法候选。

原七输入固定7、原32条件矩阵不变；FWT/DWT/CFD/Conv/vector都在原组。**新增探索组仅SGEMM为待E审查提名，正式登记及接受配对均0**，SpMV/Scan是未合格备选，绝不混入统计分母。原七主图目前main61为1/7，均值UNKNOWN；不得用各应用最佳子方案拼图。累计12/40来自E，非再加40；D启动0。所有walltime新版本预测UNKNOWN，CSV的旧cycles/字节/指令量仅成本代理，不跨年代用数值排总分。
