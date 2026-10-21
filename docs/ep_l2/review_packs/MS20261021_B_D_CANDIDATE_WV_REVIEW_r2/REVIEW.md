# B → D/A2/E2：FWT / SGEMM 的独立 W/V 机会审查 r2

**FWT 已有真实 victim 读服务和 dirty-forward 事件，但只来自未被 E 接受的历史运行累计快照；SGEMM 有 global store 和 resident 脏数据，旧运行没有测得 WB readout / DRAM 写出。** 前者支持 V 可被真实 workload 触发，后者支持保留低 W 压力对照。两者都不构成本轮新增的完整应用正确性或性能结果。

沿用 D 的既定 S-only 提名，不重新按 F 速度或命中数挑选。D HEAD `49343880865edb22a17523790fc32dd55975966c`；S-only 候选表最后修改于 `0eb15c6458cf84403ce2eddfa1a25f4864c52787`。只读提取脚本约0.054s，读取6,548,050B，其中 FWT 两份保存 raw 各最多1.5MiB。额外台账/联合fixture边界只读核对单列在 ADDITIONAL_BOUNDARY_OBSERVATION.json。没有 trace 正文、SQLite、大范围存储扫描、构建、GPU/native/完整模拟启动或监听器；未修改 A/E/其它项目数据、输入登记、预算及资格。旧 r1 筛选与 r2–r5 fixture/native 历史均保留。

## 证据分层与交付给 D 的决定

| 项目 | FWT_7_21 | SGEMM medium |
|---|---|---|
| 输入身份 | 原七输入，D_V1_FWT_7_21，composite `f3695b85379fb762faaf9830bda449e0a5f1e4d3e351774cf33d90850059b460` | D 候选，**未在 E 正式登记**，composite `694ce08c82354963d0a24f45b13020c9a98d21e60b511166812d6176b4f486cb` |
| 传统 W 机会 | S 观察到178,569 WB/复制行，WBUF重试890,294 | 旧 B0 WAD-full/hazard、DRAM写出、WB readout均0；显式 WBUF copy字段未提供，不能伪造为0 |
| 读写关系 | 保存的完整epoch模型：131,072读line均有store，41,943,040对应lane-line读引用，19kernel | 保存语法审查：2,390,784条 LDG.E.SYS、33,792条 STG.E.SYS warp记录；没有地址集合聚合，读写line交集和先后关系均UNKNOWN |
| 实际 V 读取 | 历史 F 末次64-slice快照：184,660 response / 5,909,120B | **未提供 V 观测，不是0次命中**；旧 B0 没有该机制的 response/dirty-forward输出 |
| dirty-forward | 同一未接受快照：12,489次 | 未提供，UNKNOWN |
| 淘汰后短距离复用 | 响应证明被保留对象确有读服务；没有evict→read年龄/距离或完整应用率 | UNKNOWN；SGEMM计算/共享存储复用不证明L2 victim复用 |
| 本轮用途 | 保留 D 先验优先级；作为“已出现机制事件、完整资格缺失”的候选 | 保留低 W 压力/写入不等于写回的独立对照候选；不是获准运行输入 |

这是两个互补候选的科学审查，不是增添条件或启动申请。FWT 原S-only选择由高WB/copy/同址hazard和无序读写重合支持；现在的 F 事件仅用于检验该假说，不反过来宣称之前是基于性能盲选的新样本。SGEMM没有因未知 F 结果而移出，也不自动替换 Btree。vectorAdd 的高写回/dirty读地址无交集负对照、Conv的稀疏V锚点、SAD低W对照仍按r1保留。

## FWT：实际服务证据与未接受边界同时保留

E011_618407f0 (S)、E012_63be0bb4 (F) 均为 `INCOMPLETE`、`independent_acceptance=NOT_ACCEPTED`、`complete_input_verified=false`。E原因是 orphan 消失，未收集到kernel退出状态；不能根据日志外观推断正常退出。中央 accepted_results 中没有这两个尝试，也没有接受的 FWT S/F pair。本轮没有运行 parser 重认证或改变这些状态。

两端绑定 Core `d010911e3174a3764791183cd108fe4664ba8731`、Framework `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`、main SHA256 `61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5`。S config `1e9d74d838e746e5c0d911bd60aeb4793c54153570bd0b33a2930f4c6d5d7a95`，F config `5a6e1627a6623085f9f51be5ba83f683f17e12407c803904446f53344c48003c`。完整 run_key/qualification/input/raw身份保存在 FWT_UNACCEPTED_OBSERVED_MECHANISMS.json。receipt SHA 与台账精确匹配；raw只验证读取区间SHA及读取前后size/mtime稳定，**未重新hash整份raw**。

各类记录取保存tail中最后连续的slice0…63，一slice一次；FT的observed_cycles在同次snapshot内一致，作为累计快照边界检查，未用于候选排序/速度计算。提取保留原始行及tail offset/hash，不将跨kernel打印重复相加。它仍是最后可见累计快照，不是受接受的全epoch terminal。

| 原始观测 | S保存快照 | F保存快照 |
|---|---:|---:|
| WB created / completed / lower accept | 各178,569 | 各207,546 |
| copy_lines / copy_bytes | 178,569 / 22,856,832 | 0 / 0 |
| logical copy reads / writes | 各178,569 | 各0 |
| wbuf_full / pool_full原始重试字段 | 890,294 / 0 | 0 / 188,629 |
| dirty installs / clean installs | 功能OFF | 207,546 / 32,495 |
| actual V read responses / served bytes | 功能OFF | **184,660 / 5,909,120** |
| dirty-forward responses | 功能OFF | **12,489** |
| promotions / directory queries | 功能OFF | 37,675 / 441,298 |
| V bank / ICNT / WB等待观察 | 功能OFF | 8,373 / 250 / 2,593 |
| lower read packets / bytes | 954,036 / 30,529,152 | 873,164 / 27,941,248 |
| lower WB bytes | 22,856,832 | 26,565,888 |
| physical grants | 11,713,359 | 11,304,326 |
| unclassified refusal observations | 0 | **137** |

正负结果都保留：F没有复制，但WB写出更多、pool_full原始重试出现188,629，且有bank/ICNT等待与137条未分类refusal。**不将这些重试或等待观察相加成独占GPU stall**。两快照的lower-read算术差80,872 / 2,587,904B、WB差+3,709,056B，只能作为未接受的描述性差异；不是完整配对、不是V单因素反事实，也不证明显存物理带宽节省。lower字段处于lower issue边界，不改名为DRAM接受。没有公布或使用两次F/S速度。

按准确Core源码，`response_commit`只在真实Payload bank服务、成功response enqueue后递增read_responses；dirty_forward来自begin_read时的mandatory-WB标志。因此这是实际生产路径计数的事件见证，不只是目录命中预测或静态集合推测。12,489是有mandatory-WB背景的响应子集，不能把其余172,171全叫clean-victim读取：已完成WB后的保留对象也可能贡献。计数不提供UID/generation逐事件审计或数值byte reference，新资格仍归E。

累计安装240,041、promotions37,675和responses184,660是三种不同事件；查询含重试，均不是唯一地址、唯一请求或常驻容量。不能据此给hit rate、平均重用距离或独立避免的lower-read数。V-OFF同背景控制、完整终止与输入/数据资格仍缺失。whole-commandlist RO模型保持原状：其认证覆盖为0，不改为kernel局部RO，不能把W/V响应移作RO/T/M成功证据。

## SGEMM：写入在缓存中存在，但旧运行没有W流量压力证据

D保存完整2,216,170,035B单kernel的原字节/native语法/非原子审查，本轮不重扫；kernel body SHA `1b0739908e3aef52cedea68962172ccac55f0c2d4c651623cb8fb0655475db06`，commandlist SHA `0a0d21711ff3f3de1604fc0a243d5be2df5155147bb09bc4533bd017b62f5913`，native composite为表中694ce…；三种hash定义不混用。审查是输入候选证据，不是SASS数值验证、RO证书或E运行资格。

旧 B0-Legacy / B0-Banked 保存统计均绑定 Core `ece1a3a77c5628763e0a4605bfd1c639ee6a1495`、Framework `f08d2ce857972fad73c4e1ab7162ba94c6336507`、保存config composite `85562fce759876616806d32791ea3b7d1b13ee68cf20a84e48c63c96f67b8c0d`。命令list SHA与D候选一致，但本轮没有重新绑定整份trace或把旧执行升级为当前main61资格。准确旧接受记录、原raw hash及64slice统计见 SGEMM_HISTORICAL_B0_COUNTERS.json。

- 两种旧运行的DRAM successful read均12,578,816B，write均0；WAD-full、hazard、WB readout均0。
- **B0-Banked有135,168次resident-write逻辑服务**，每slice的resident-dirty历史峰均528。峰值是每slice各自的历史高水位，不求和冒充同一时刻占用。B0-Legacy的bank字段0来自不启用bank成本模型，不能作为“无写入”的依据。
- D trace审查的全局STG记录33,792，FFMA33,555,456，LDS.U.128为8,380,416、STS261,888。可说明稠密计算与共享存储活动；不是L2 read/write集合或重用距离。
- 显式新WBUF copy字段不存在，V read/dirty-forward未观测，全部标UNKNOWN/NOT_INSTRUMENTED。旧banked总logical ops1,819,898、retry/true-conflict/wait均0，是旧配置背景，不能证明当前有限4bank生产路径无竞争，亦不能把resident-write成本算成WB copy。
- 终止pending硬件干净与resident仍含dirty line可以同时成立；zero DRAM写出不意味着read-only，不证明host已收到输出，亦不证明从未发生任何未计数的复制。没有强制flush或扩大资源来制造压力。

读写地址交集、先写后读、dirty evict→read、clean-victim复用、有限目录/池内存活及实际V服务均UNKNOWN。矩阵输入read-heavy或高共享存储复用的常识不代替这些量。**SGEMM在现有证据下不列为强dirty-victim/copy压力样本**；保留为不同机制背景的独立对照，且仍待E登记与资格。捕获脚本/应用revision未知的原限制未消除。

## 联合fixture、资源及剩余缺口

E登记的 `unqualified_extra_joint_scenarios.r35` 精确文件/hash已回读并保留 E_FROZEN_JOINT_SCOPE_REVIEW.json：`B_C_joint_scenario_accepted=false`，失败分类是旧fixture不可达的新lower包预期；128B父请求分四sector，后续合并使reuse_seen保持，不能虚造额外包凑22。旧20个lower包、未完成的parent/descriptor断言及B/C替代fixture源码边界保留。本轮没有执行或新认证它，也没有以FWT计数、旧SGEMM或其它正式最小组合gate替代其独立闭合。A2/E2既有11+7gate范围与历史原始结果不因本审查变化。

本轮边界快照看到E actual starts45、controller STOPPED，`maximum_actual_starts` / `remaining_start_capacity` 为null；D4934388公布的批准上限是46。**这是来源之间尚待E2解释的状态差异，不推断无限预算、不修台账、不申请使用剩余额度**，也不从过时top-level status反推活动任务。精确JSON/hash与时间分开保存；本报告不替代E实时资源准入。

交付事项：

1. **D**：维持先验S-only候选，不按新F指标重排；FWT增加“未接受执行中的真实V/dirty-forward事件”证据层，SGEMM保留低W压力/读写关系未知的对照。原七输入分母、FWT完整配对缺失和SGEMM探索组身份不变。
2. **A2**：不需为本报告改协议、主binary或扩大资源。若未来必须解释短距离/sector/generation关系，仅提出最小、预登记且有截断标记的事件需求；本轮不实现观测框架。当前aggregate counter不足以完成byte-level或联合生命周期正确性证明。
3. **E2**：保留E011/E012 INCOMPLETE，不自动重跑/追认；核对上限null与已发布授权的关系。本轮不提交启动spec。需要FWT完整终止、同背景V-OFF或新观测时，由E按当期真实授权、资源、输入、source/config/binary身份单独审核，未满足前只保留缺口。

全应用V独立lower-read节省、独占GPU等待改善和淘汰后短距离分布均未获证明。后续只按结果事件短增量接收，不常驻轮询。
