# W/V Observation-Guided Optimization：候选与公平对照

本交付仅复用Lane O V1R2与Main已接受小汇总，并核对有限生产源码。没有正式仿真、Trace/raw正文扫描、编译、Core/registry/Git修改。数据为引用分析的as-of快照，不替代后台长尾实时状态。

优先建议先闭合W-only并做少量模式分解，再决定是否实现service-aware optional reclaim。当前证据不足以支持继续扩队列或直接增加WB/WAD资源。

## 已证实的机会与抵消

|输入|现有结果|W/V现象|解释边界|
|---|---|---|---|
|Stencil bd0309df|S 5,242,939；F 4,769,712，约1.0992×|V实际响应4,930,616；S copy占独立bank ops约11.13%；WAD峰7，WB空间阻塞0|强V见证、W有操作可省；没有扩WAD/WBUF依据，不能归因T或单独V|
|3MM f9f80028|S 1,696,618；F 1,669,413，约1.0163×|V 1,147,507；S copy约0.070%；WAD峰32、WB空间阻塞0|V比大WB预算更值得优先验证；事件本身不是独立净收益|
|GEMM 140f6ed3|S 558,588；WV 550,642；F 552,065|WV V服务609,858；F586,844；S WB仅3,241|WV真实正例；不是SGEMM，不默认大量WB收益；WV→F为M/T组合差异|
|FWT fc3a9062|S181,827；合法WV178,951|WV V88,069，dirty-forward3,312；S WB_DATA_SPACE独立head8,736|W/V交叠适合作W-only分解；WV不得擅自变RO-F|
|Scan cf8d1c4d|S2,162,540；F2,224,142，F慢约2.85%|WB_DATA_SPACE独立head1,737,618→0、copy→0；V仅5,584；同址WB独立head390→1,913，WAD_FULL35→257|有W机会但收益被抵消或不在关键路径；原因待W/WV控制，不能把queue/query计数当独占损失|
|Conv 438eefd6|S331,234；F335,088，F慢约1.16%|WB_DATA_SPACE49,161→0；同址WB16,791→16,396仍在；WAD_FULL1,004→959；V44,974|多个约束共同存在；不支持仅扩WAD或继续缩Tag|

逐输入精确SHA、Source、接受point/spec/bundle和原始同人口数见JSON/CSV。S/F写回数不同，不能逐包相减解释copy收益。MS head条件人口与FT tracked requester并不相同，不作未经证明发生率；原因不求和作GPU独占stall。V服务、query、install是不同人口，不算虚假hit rate。

## 少量候选，按证据与成本排序

1. **D0：W-only/WV分解先行。** Source78模式flags已有明确实现候选，但正式Host/CPU/sole-entry资格尚未闭合。首选6个拟议点：Stencil W/WV、GEMM W、FWT W、Scan W/WV；旧精确S/F/WV只有Main闭合身份/配置资格才复用。可后选3MM和Conv各W/WV，非自动再加4点。W_ONLY→WV是整个V包的净差，包括目录与dirty-forward，不能将其直接拆成单次lookup开销。S→W是unified W-only组织差，不能称纯copy-free消融。正式授权当前为0。
2. **C1：service-aware optional reclaim。** 当前reclaim固定先CLEAN后WB_COMPLETE；准备一个默认关闭的有限策略：reclaimable的CLEAN/WB_COMPLETE中，未成功服务过读取者先回收，随后按已有age，保留bank颜色限制。一entry一service_seen位随incarnation清零、只在实际response_commit置位；全GPU逻辑1024B未计padding，硬件比较/时序/PPA仍UNKNOWN。它可能保护GEMM/Stencil有用保留对象，减少Scan无用对象；也可能损害未来复用。**HYPOTHESIS**，未写生产代码、未有性能结果。最小新ELF公平控制可选Scan/GEMM每个S、WV原策略、WV候选，共6点；任何新ELF必须有本ELF基准，不能拿旧ELF补性能反事实。
3. **C2：optional completed-retention cap，仅条件备选。** 只有D0显示V包有净代价且新小观察证实optional压力后考虑。物理128 directory与1168 payload均保持；只限制CLEAN+WB_COMPLETE可选保留，单候选64对原128。64是代表性有界半限而非数据推导最优，**NOT_FROZEN**；不得改mandatory/pin。现有mandatory reclaim已经优先，额外限制收益UNKNOWN。选C1或C2之一，不自动构造两维扫描。

不优先：重复ICNT1024/MissQ256/更宽组合、直接扩大WAD/WB、无代价目录skip或Native-hit shortcut。三组固定8输入验证S/F GM分别0.9969868679、0.9990639069、0.9999769608，均未显示总体EP净收益。Source92 P2仅Vector独立资格，不能移植为其他程序已证实更高bank吞吐。

## 公平资源与协议

固定64slice、32set×8way、32DRAM channel、128B/4sector、4bank/P1、1168物理payload=9.125MiB数据、D512、lineMSHR128、WAD128、dram_latency100和原时钟/队列。S固定resident1024/bypass128/WB16不削弱、不挪容量；256个逻辑Tag覆盖与物理payload区分。F pooled WB没有独立16-entry WBUF，不能将其同S16峰做同容量占满比。

C1/C2仅重排已可回收的optional对象，不触WB_STAGED/INFLIGHT、mandatory WAD、active reader/pin、generation/owner检查、dirty forward或旧返回保护；set_done与reader unpin交错必须安全。Source78当前明确拒绝TVD/RO+localWBcap，不可直接打开现有cap16冒充合法组合。不得删断言以资格化。

## 真正缺失与NI

已有WB/copy计数、MS独立/重试/first-wait、WB占用面积、WAD峰、V真实服务足以做D0规划，不需要为这些数重跑。C1/C2决策可能真正需要：V服务按CLEAN/STAGED/INFLIGHT/COMPLETE分层、install→first-service/reclaim年龄及未服务/censor、optional回收原因与实际容量压力。先复用A追回的历史小CSV与输入manifest，历史普通reuse不能转换为当前有限V容量曲线。

真实ingress、queue-enter、first-head、admission分开；本交付旧MS只叫head。新计数一律默认OFF、同UID/generation只计一次，保持同人口分母。Lane O NI矩阵是设计，不是PASS：S的NI不能覆盖F/WV。W-only也需要自身真实路径资格。若增加新observer，按实际hook列CPU控制和S/WV/F的同ELF OFF/ON缺口，启动点数为所需ON+缺失OFF，不预设4+1。应用host开销/新增输出目标待实测，不能用常数假装已通过5%。

W-only现有exact3记录是HOLD/failure而非PASS，五模式Host为DRAFT。主机写入V3、MSHR64、Source92各自边界保留，不自动纳入。F−T(M1T0)与WV(M0T0)不同，WV/F不能证明T独立贡献。

## 下一步给Main的收敛决定

先用本交付的精确282 options候选与现有Host设计闭合W-only资格，再向用户报D0有限模式分解清单；如果选择新结构，先只做C1最小协议设计与轻量服务分层工程。正式Stage C/D仍需Main精确Source/预算/控制点及用户审查，本轮没有任何新增启动。统一配置最后要在未用于选择的冻结输入集验证，报告绝对REF改善、同硬件S/F、全部减速和负结果；不得按每程序最优拼GM。

C1工程补充：当前有directory-full preview_install与bank-compatible tvd_reclaim_one两个回收选择器，候选必须共用service_seen优先级，保持preview无副作用/幂等及revision一致，不能只改一处。新结构spec设计见WV_STRUCTURAL_SPEC_DESIGN_DRAFTS.json；新Core/ELF/option计数均NOT_FROZEN，未假造282新配置。OFFLINE_DELIVERY_QA仅证明小引用SHA/身份/282候选声明闭合，不是协议CPU或应用NI。
