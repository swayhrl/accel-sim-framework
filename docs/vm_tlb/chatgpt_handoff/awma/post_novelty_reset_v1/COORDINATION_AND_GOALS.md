# AWMA：必要基线补齐与新问题并行筛选 V1

日期：2026-09-26。此文件是 ChatGPT-owned coordination，不是已执行实验报告。

## 0. 目标、状态与不可混淆的边界

主目标仍是新机制研究。当前 pre-L1 coalescer 保留为已验证的参考实现，但其新颖性尚未成立；历史 paper-qualification 仅说明材料/实现整理程度，不能替代最近邻比较。

本轮只做两条可并行的工作：
- Lane B / 174-new：移植一个必要的已有能力——同一动态 warp 访存指令内的 VPN 去重；同时核查现有 coalescer 的请求来源和剩余增量。
- Lane E / 174-new：研究剩余瓶颈与最近邻文献，最多提出两个可否定的候选；可准备小原型，但不得在缺少必要基线时宣称新颖性或正式收益。

不启动109、不新增GPU capture、不下载模型、不做新RTL/PPA、不迁移到gem5、不完整复现多篇论文。不要把当前coalescer必定成为论文设成目标。C16的memory-only/raw-AWQ/MoE数据不自动成为AWMA simulator-native input。

本次协调已核远端 parent：f4c5b942d39f8805529c09704b183ddc42eb4324，tree de934b3ce8676768eb2bf712c7a65348e4ef96df。没有执行新的174模拟。

## 1. 共同权威与必读文件

Repository：swayhrl/accel-sim-framework。

- 现有汇总：f4c5b942d39f8805529c09704b183ddc42eb4324。
  `docs/vm_tlb/review_packs/AWMA_PREL1_COALESCER_PAPER_QUALIFICATION_V1/` 下的 FROZEN_MECHANISM_ALL_TARGETS.tsv、HARDWARE_FEASIBILITY.md、PAPER_CLAIM_MATRIX.tsv。
- 冻结pre-L1 source：2bbbceabb5261777fe385289ecb6579791e0f232。
  `docs/vm_tlb/review_packs/AWMA_PREL1_TRANSLATION_REQUEST_COALESCING_DISCOVERY_AND_PROTOTYPE_V1/MECHANISM_CONTRACT.md`、MECHANISM_CORE.patch、SOURCE_FREEZE.tsv。
- 开发结果：163a8572f9272891b8109f9158aa79ca88d9e153。
- passive observer：6441fe9f91266220a52587c0313fb767007b5d92。
  `docs/vm_tlb/review_packs/AWMA_PASSIVE_TRANSLATION_RESULT_REUSE_OPPORTUNITY_V1/OBSERVER_CORE.patch`、TARGET_OPPORTUNITY_MATRIX.tsv、SOURCE_AUDIT.md。
- 归因工具：b85d388abe98e5da70b749b52075c33fad7cede4。
- A2归因：b8a4064cb1bbe832758acf9dceb1461844c1fe4e。
- 代表集设计：a383cc2bb04805c405b7dd2d0f918d4fe2738f32。
- 旧REDUCE独立验证：fc5ea3bf1f09be1d0fbe3eb11fc6f6a847e4d763；这是历史独立证据，不是今后新机制的未见holdout。

历史OFF周期/冻结pre-L1周期：
T0 527896/499441；T1 665802/647437；T2 93079/94034；SPLITKV 73923/73915；COMBINE 10480/10480；A1 114123/115415；A2 117698/115700。

模型、输入、page size、VA/PA映射、初始状态、source/config/binary与trace身份从原receipt恢复，不从目标名猜测。10/80是当前建模条件，不写成4080硬件公开事实。不重做已冻结平台/producer/校准任务。

## 2. 本次已核的文献语义与未取得资料

R1. Pichai/Hsu/Bhattacharjee，Rutgers DCS-TR-703 (2013)，与ASPLOS 2014论文相关。
https://scholarship.libraries.rutgers.edu/view/pdfCoverPage?download=true&filePid=13643522050004646&instCode=01RUT_INST
定位：§5.2，印刷页4；本次读取的PDF含封面，0-based页4。作者在地址生成之后把warp内同虚拟页请求合并，与独立的cache-line访问集合分开处理。这里只据此移植“同动态warp指令的页请求去重”能力，不声称复现整篇论文。原文并未给出我们平台所需的所有group形成/分发时序；这些必须标为AWMA adaptation。该文VIPT并行cache/TLB设计不迁入本轮，避免比较同时改变数据cache路径。

R2. gem5 Vega TLBCoalescer，固定commit 56aca813700a6b107f2282f15af5e4d2cad0d0e2。
https://github.com/gem5/gem5/blob/56aca813700a6b107f2282f15af5e4d2cad0d0e2/src/arch/amdgpu/vega/tlb_coalescer.cc
复查函数：canCoalesce、recvTimingReq、processProbeTLBEvent、updatePhysAddresses。时间窗分组与AWMA live-entry追加并不完全相同；已发出的同页组会使另一个组暂缓，不能把它说成任意后来请求都加入已发出组。本轮仅作源码比较，不默认移植整个gem5 coalescer。

R3. Compiler assisted coalescing，PACT 2018，DOI 10.1145/3243176.3243203。
作者页面：https://pharm.ece.wisc.edu/publications.shtml
全文链接：https://pharm.ece.wisc.edu/papers/pact_2018.pdf
本次作者页面可读、PDF访问失败；学校目录也未提供可用下载。仍为 FULL_TEXT_NOT_OBTAINED。不得根据摘要补写translation table、生命周期或全部baseline细节。请用户补PDF；不阻塞R1能力移植。

R4. LATPC，MICRO 2025，DOI 10.1145/3725843.3756069。
作者机构摘要：https://yonsei.elsevierpure.com/en/publications/latpc-accelerating-gpu-address-translation-using-locality-aware-t/
作者目录：https://yonsei-hpcp.github.io/publications
本次未取得全文。课程目录的PDF线索也未成功访问。FULL_TEXT_NOT_OBTAINED；二手综述和自动论文评论不能替代原文。若候选涉及warp VPN规律、MSHR压缩、预取或walk batching，它是最近邻全文核查项。

R5. MASK，ASPLOS 2018。
https://www.pdl.cmu.edu/PDL-FTP/PowerMgmt/mask-asplos18.pdf
本次核了§4.1文字：翻译完成后等待warps接续发出数据请求，可能增加下游排队；§5包含翻译感知资源管理。因此“发现翻译完成后的burst”本身不是新颖性依据。PDF截图接口本次失败，不据未查看的图形提取新数值。

R6. RPAWS，IEICE Electronics Express 2026，DOI 10.1587/elex.23.20260028。
https://www.jstage.jst.go.jp/article/elex/23/12/23_23.20260028/_pdf/-char/en
本次取得正文并核§3.2：结合前端指令类别与ALU/LSU队列忙信号改变warp优先级。因此泛泛的“访存忙则发计算”不是新候选。论文实验百分比不作为AWMA数据。

R7. GCStack/GCScaler：公开实现https://github.com/yonsei-hpcp/gcstack_gcscaler 。作为分析基础设施最近邻，不在本轮声称Observatory方法创新。

本文所有任务设计、预算、停止规则都是本项目决定，不是上述论文原文规定。

## 3. 当前最需要检验的推断

历史七点满足：logical decision lookups - sum(unique pages per dynamic memory instruction) == frozen coalescer followers。
T0 3090304-367840=2722464；T1 7159808-529856=6629952；T2 411008-278464=132544；SPLITKV 233814-14952=218862；COMBINE 1099-83=1016；A1/A2 409024-292992=116032。

这是聚合计数等式，不是UID集合或算法等价证明。跨周期不等于跨动态指令，跨动态指令不等于跨warp。不得先把该推断写成结论。

已确认source落点：passive OBSERVER_CORE.patch在shader.cc用inst.get_uid()与access.get_uid()关联动态指令和逻辑请求；pre-L1 patch在translation_controller物理L1 launch附近登记leader/follower。新增只读source map可连接这两层，无需重新抓GPU trace。不要直接沿用(sid<<32)|uid打包而不检查位宽与复用；跨run比较应使用trace稳定身份，不是调度顺序产生的裸simulator UID。

# LANE B — 必要基线与剩余机会，一次连续执行

Stage：AWMA_INTRAWARP_TRANSLATION_BASELINE_AND_RESIDUAL_V1
Execution branch：hrl/awma-intrawarp-translation-baseline-residual-v1
Node：174-new。独立worktree/build/output，不改协调分支和Lane E工作区。

## B1. 来源分解与真实资源审计

优先复用已有receipt/事件数据。缺少逐请求来源时增加只读映射，功能/观测开关分离，关闭观测不分配额外大表。

记录kernel身份、CTA lifetime、warp lifetime、动态warp指令实例、访存operand/access class、逻辑access UID、pre-L1 leader/follower，以及该请求真正L1 launch而非translate retry。

来源互斥分类：SAME_DYNAMIC_WARP_INSTRUCTION / SAME_WARP_OTHER_INSTRUCTION / OTHER_WARP_SAME_CTA / OTHER_CTA / UNKNOWN。不得只用PC、硬件warp槽号或相同VPN推断同一动态指令。跨run用稳定trace指令实例与地址/sector/lane-mask对应，不强求裸UID值相等。

同时统计每SID每真实模拟cycle：compare/registration、leader launch、follower READY read、consume；以及pending-compare HWM。已有L1端口预算不自动约束未消费该端口的coalescer操作。只报告源码与实测能支持的吞吐，不把C++函数调用全算硬件服务。

如冻结模型存在未建模多端口，只收紧解释并输出差距，不擅自修历史机制。不以硬件资源未闭合拖住request-set比较。

## B2. 只移植一个已有能力

名称：WARP_VPN_DEDUP_REFERENCE；不是新机制，也不是ASPLOS全系统复现。

在同一动态warp访存指令的有效地址已经自然生成、原data coalescer构造访问集合后，为相同合法translation identity形成组。身份含当前模型实际支持的ASID/VPN/page_size/generation/access兼容条件，保留lane mask、各sector/cache-line事务与访问UID。

每组由最先在原路径具备合法发起资格的成员代表启动正常translation；不根据未来完成时间挑leader。组内其它成员不另发相同页翻译，等待真实组翻译完成；保留结果直到该动态指令组合法消费结束。不是把pre-L1表简单增加instruction ID后只允许“重叠在途”合并：已完成但同指令尚未消费的组仍需保持正确生命周期。

对照开启时允许明确、有限地改变翻译请求生成，这是被研究变量；历史OFF仍原样可复现。不得关闭所有resident prelaunch、降低原TLB延迟、复制无限结果端口，或把64KiB换4KiB。其它页组仍可按原V1并行推进，不增加全指令all-pages-ready屏障。cache数据路径、物理映射、原子/写语义不改。

容量由源码支持的每live instruction最大access/page-group数与现有resident instruction上限确定，不从7个样本观察最大页数硬编码为2，也不因warp32就假设最多32个sector。超限必须有有限、不会丢访问的fallback。解释原文规定与适配选择。

先固定group形成、查询与结果分发的延迟/吞吐合同，再看性能。原文未给出的本平台延迟标UNSPECIFIED_IN_SOURCE / AWMA_ADAPTATION。若沿用与data coalescer并行的同周期抽象，明确它是结构参考而非时序已闭合；不得免费广播任意数量消费。不要本轮做RTL。不能低成本实现完整性能路径时，交付已闭合的结构覆盖/成本分析并标PERFORMANCE_NOT_RUN，不用一个简化的晚到头部forward替代。

## B3. 内联正确性与固定矩阵

定向测试：同页多sector、异页、同PC不同动态指令、warp/CTA槽复用、ASID/generation/access不匹配、组完成与新请求并发、重试、队列满、指令结束清空，以及无组内重复时与OFF的零变化路径（若显式增加延迟则单列该已声明成本）。旧TLB已发服务不免费取消。

仅使用T0/T1/T2/SPLITKV/COMBINE/A1/A2；它们都是已见开发数据。旧OFF、旧pre-L1的完整结果直接读权威，不重跑作为仪式。

先将T1/T2的instrumented OFF复现并合并来源观测；然后只为缺失source map补必要observer run。新reference七点各一次。若当前pre-L1缺逐请求来源，最多七点各补一次只读观测，要求周期/service与各自已接受结果exact一致。最多两点可加预先固定的保守时序对照，仅在实现时序会改变比较结论时使用。新full-kernel replays总预算18次，默认不填满；不做host-time warmup/重复测量，不跑ideal/0-80全矩阵。普通工程问题本轮修完继续；资源允许时并行，不把科学采用顺序误当计算串行依赖。

每点只报三组：历史OFF / WARP_VPN_DEDUP_REFERENCE / frozen PREL1。记录cycles（明确用cycle reduction百分比）、true L1/L2 launches、MSHR/PTW、功能mapping、每组/每请求来源、等待与下游流量、source-supported进度/瓶颈摘要。observational neutrality、logical coverage、untranslated/unobserved/duplicate=0、terminal/quiescence内联完成。

B组已经计算出的“请求属于相同组”的结构覆盖不等于“动态性能节省”。任何extra physical launch需要区分独立新页请求、miss完成后的delivery reprobe、重复观察、已有在途请求；不沿用lookup_requests的名字作为物理服务定义。

## B4. 结束判定与给E的交付

报告当前pre-L1 followers与reference可覆盖集合的交集/差集及UNKNOWN数；并列服务与性能，不把总数相等当集合相等。不自动实现gem5、CAC、LATPC，也不继续修pre-L1。

结论允许：CLASSIC_INTRAWARP_CAPABILITY_COVERS_CURRENT_BENEFIT / RESIDUAL_INCREMENT_REQUIRES_EXPLANATION / COST_OR_SEMANTICS_NOT_COMPARABLE。这是在当前数据上的判定，不宣称文献等价定理或所有LLM规律。

最少交付：REPORT.md、SOURCE_AND_ADAPTATION.md、REQUEST_SCOPE_AND_OVERLAP.json、COMPARISON_RESULTS.json、RESOURCE_ASSUMPTIONS.md、NEUTRALITY_AND_CORRECTNESS.json、CONSUMER_HANDOFF.json、RAW_INDEX.json及校验清单。支持表格可用TSV，但不为管理再建数据库。

CONSUMER_HANDOFF必须绑定reference source/config、timing/port合同、可用raw/observer字段、逐target身份、B判定和已测残余症状。完成一次commit/push/fetch-back/clean后STOP。

# LANE E — 新问题筛选与有限原型准备，并行执行

Stage：AWMA_POST_COALESCING_RESEARCH_HYPOTHESES_V1
Execution branch：hrl/awma-post-coalescing-research-hypotheses-v1
Node：174-new。可与B同时开始，不重做B的source map或reference。

## E1. 先利用现有证据完成独立部分

已知研究动机是service减少与cycles不单调对应，不能直接把它命名为新机制。重点筛选两个待验证问题（不是保证有创新的两个机制）：

Q1：合理warp内去重以后，剩余翻译等待究竟还阻碍哪些动态指令/warp进度？与常规数据访存阻塞区分。允许答案是当前样本剩余翻译机会很小，不需要硬造第二个TLB问题。

Q2：在不增加speculative translation的条件下，翻译准备提前量、完成服务与有限下游接收之间，是否存在经典合并/现有调度方法未解决的失配？必须用实时可获得信息提出决策，不使用baseline未来时间戳或读未来trace。不能只提“抑制burst”或“访存忙先发计算”。

优先读R1/R5/R6及其最近邻引用；CAC/LATPC全文若未取得仅标待核，不用二手摘要宣布没有相关设计。检索以可执行规则/服务位置为中心，不仅按拟命名名称查重。对每个候选填写：问题、已有能力、明确剩余差别、必需信息、有限资源、可能代价、最小反例、预期指标和否定条件、原文定位/阅读深度。最多保留两个，不要求凑满。

源码审计要明确：request ready、head-ready、TLB结果生成、地址apply、cache admission不是同一个事件。scoreboard不能分memory/compute来源时保留未知。A1/A2不同context的捕获不自动代表模拟器执行了完整前序；初始状态必须按各receipt写明。

## E2. 可提前做什么

可以只读分析已有10点表与既有Observatory日志、建立最小算法/定向fixture、准备observer接口或原型patch；不得把缓存状态/全局真相当运行时硬件oracle。默认不再跑整kernel、不综合RTL、不再写paper qualification。

从源代码能直接证明不具备必要状态或与已核前人机制重叠，就淘汰该候选。R5已明确讨论translation completion后的data burst；R6已实现按EU忙/指令类型调度。两者不应再作为我们的宽泛新发现。

## E3. 与B合流，不忙等

B结果存在时，单次fetch其execution branch并只读消费已提交CONSUMER_HANDOFF；不读取其活动worktree。尚未完成则把本轮文献/源码/fixture成果提交，标PREP_COMPLETE_AWAITING_BASELINE，不循环轮询、不制造等待token，也不因此另开管理任务。后续在同一E窗口消费B结果即可。

只在B的比较语义闭合、候选最近邻原文足以判断其区别、且能指出具体剩余问题后，允许本Goal内直接继续最多2个小型性能原型；这是探索，不是创新认证。

若继续：每个候选固定一个配置，最多3个预选development目标，最多6个candidate full replays；选样按B残余症状与对照角色，在看candidate结果前记录。基准必须包括B的合理去重reference，不能只对历史OFF求收益。baseline结果可复用，不改B实现；多个科学变量需拆分或明确标组合干预。同一候选不进行参数扫描、失败后不自动修三版。不使用旧REDUCE/Pair C再次冒充新holdout。

若CAC/LATPC等尚缺原文而候选差异依赖其细节，暂不跑该候选性能，不用缺全文拖住无关source分析。允许整条E线没有合格新候选，此时给出最小新workload问题及资产缺口，而非未经授权采集。

## E4. 交付与停止

REPORT.md、最多两张HYPOTHESIS_CARD、CLOSEST_WORK_COMPARISON.json、SOURCE_FEASIBILITY.md、NEGATIVE_CASES.md、PROTOTYPE_STATUS.json；实际执行时附完整试验矩阵/receipt，未执行必须显式NOT_RUN。

最后只回答：有无值得正式开发的新机制；与最近邻差别是什么；哪项证据仍缺；下一步必要动作。不得输出“论文ready”替代新颖性判断。一次commit/push/fetch-back/clean后STOP。

## 4. 公共执行规则

源码/配置/构建/输出各lane隔离，trace与模型只读共享，检查CPU/RSS/I/O后尽可能并行。large raw仍在node164；174只留代码、binary及有限scratch。源/索引/manifest可由accepted证据确定性重建时自行继续，实质payload或唯一身份信息确实丢失才上报。HTTPS失败切已配置SSH；传输故障不重跑科学实验。

只在正确性/科学身份无法保持、需要扩大授权范围或实际超过预算时停下询问；小文档、脚本、路径问题并入本次修复。不清理任何其他lane数据。

## 5. 当前需要用户补充的唯一资料

请提供CAC（PACT 2018，10.1145/3243176.3243203）与LATPC（MICRO 2025，10.1145/3725843.3756069）的全文PDF，任一先到先读；不需要账号、密码或远端密钥。两篇未取得全文不阻塞Lane B。

本协调发布不等于174任务已经启动；用户需把对应lane启动指令发到原Codex窗口。
