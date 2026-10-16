# Lane 4｜历史复用与理想化性能诊断

先完整阅读同目录README.md、COMMON_CONTRACT.md、COORDINATION_PROTOCOL.md，再执行本文件。公共合同单独保存，避免六份副本漂移。

本轮身份：Lane 4；执行分支：`hrl/ep-l2-ft20261016-lane4-v1`。这是待启动的连续执行Goal，不是运行状态。历史文档中的字母Lane不在本轮重命名范围。

## Goal

先核查是否已有等价理想化结果；复用真正合格结果，缺失项实现默认OFF诊断并运行。此线不依赖完整EP-L2，不等待RO/TVD。不能只提交新的计划。

## 已确认的历史证据

- FINAL_CALIBRATION_CONVERGENCE_r1/CALIBRATION_DELTAS_FINAL.csv：D256/D512与L1 META/BANK headroom，不是理想L2。
- LINE_MSHR_CAUSALITY_r1/CONVOLUTION_2X2.csv：D512 M128=292211 cycles，M256=291108；Line-MSHR-full从931416到0。仍有MissQ/WAD/lower压力，不是整体上限。
- MOTIVATION_FIGURES_r1/wbuf_sensitivity.csv：4/8/16是同访问流的shadow，不是实际有限WBUF的性能运行。
- PERFORMANCE_HEADROOM_PLAN.md：H-SCHED/H-L2D/H-BW定义与四格实验。文档存在不等于已执行。
- 本轮GitHub只读核查尚未找到可确认已完成的完整理想L2结果；未读取节点本地未提交结果。你的第一项工作是补查节点结果，而非假设不存在。

## 历史资产审计

对所有ep-l2阶段refs及已定位结果目录做有界只读检索，关键词包括ceiling/ideal/perfect/unbounded/infinite/headroom及实际开关名。先manifest/status/summary，必要时raw；不遍历无关项目或大模型资产。分类：MATCHED_REUSABLE、HISTORICAL_ONLY、PLAN_ONLY、PARTIAL、ABSENT。

REUSE_AUDIT.csv每行记录原source/config/binary/trace/terminal/功能与ideal位、放宽了哪些资源、未放宽哪些约束、是否与新B16完全可比。旧无显式WBUF模型不自动等价新B16的I_WB：copy端口、生命周期和下层存储可能不同。

## 首批诊断

B16正常配置由Lane 1/5发布，作为新对照；Lane 4在等待时独立开发/测试，必要的旧父版本pilot明确HISTORICAL_DIAGNOSTIC。诊断接口与run配置归Lane 4，公共功能通过最小patch由Lane 1接入。

I_WB：只使WB staging数据容量不再成为拒绝原因（动态/充足额外诊断存储，明确超出物理预算），保留WAD容量与ordering、copy/read端口代价、bank、下层队列、scheduler、DRAM与写回数据语义。先证明WB-data-full为0，再比较cycles；WAD满不允许被一并关掉。

I_META：只解除Line-MSHR、descriptor、per-address count等容量拒绝；保留RAW/WAR/atomic顺序、sector合并、真实fill/response、cache容量和下层系统。位宽/容器必须支持增加值，不直接写巨大常数碰巧跑通。用足够容量+capacity-full为0证明non-binding；必要时单点加倍验证稳定，不做无穷网格扫描。

I_WB_META：仅首批显著压力代表点组合以上两项，识别单项解除后被另一项接替的情况；不能从两个单项小收益推出组合也无收益。

I_READ_HIT：乐观的L2读miss代价消除参考，所有符合语义的demand read（包含冷读）在正常L2 hit基础延迟后服务，保留L1、bank限速、NoC/响应排队。写、atomic及未完成生产者依赖不能被错误删除。若现有perfect-L2开关会跳过WAD/order/功能值或不经真实响应路径，它不合格；修成专用诊断服务路径并做数据/版本参考测试。理想值来自明确的功能参考存储/模型，不从不存在的cache line读未初始化值。必须标明它不保留真实miss流、不是EP-L2可实现收益，也不是所有设计严格的数学上界。

I_BANK：仅当cfd等有真实bank服务争用且上述诊断仍不能解释时，选择代表点解除bank排队；保持基础读延迟与NoC。不是默认全矩阵。

禁止用把hit_latency设0、read全部drop、忽略reservation fail、关ordering或直接同步回调等方法伪造天花板。

## 首轮安排

先convolutionSeparable、FWT_7_21、vectorAdd_4M、sad四点，B16与I_WB/I_META/I_READ_HIT按Lane 5配额运行（最多16格，baseline可复用）。I_WB_META先convolution和FWT两个点。真实模式就绪即滚动运行，不因另一诊断尚未完工而等齐。scan后排；cfd视I_BANK需要追加。

报告被解除资源确实non-binding的证据。内存时序会改变请求交错，单项放宽不保证cycles单调；若诊断比baseline慢，核对数据与状态、解释交错/流量变化，保留原结果，不自动夹到1或强行称严格上界。

严格区分：机制针对资源的余量、L2读miss消除的系统乐观参考、下层headroom。不能用全读命中收益替代WB/RO/TVD可实现收益。

## 必须产物

REUSE_AUDIT.csv、IDEAL_MODE_SOURCE_MAP.md、IDEAL_CONTRACTS.json、关闭等价与开启数据/生命周期测试、CEILING_RESULTS.csv、LIMITER_MOVEMENT.csv、原始日志索引、准确source/binary/config/trace manifest、patch/commit。

表中缺失项用NOT_RUN/PARTIAL等明确标签，不填0。最终区分“查到并复用”“新跑完成”“尚有阻塞”，不要仅输出已规划。
