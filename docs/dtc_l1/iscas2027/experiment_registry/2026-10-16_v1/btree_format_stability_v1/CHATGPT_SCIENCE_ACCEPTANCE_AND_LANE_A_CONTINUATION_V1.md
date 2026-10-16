# DTC-L1 / ISCAS2027 — Btree E-list CPU科学审查与Lane A有条件续接 V1

日期：2026-10-16。**裁决：ACCEPT_CONDITIONAL_DERIVED_INPUT_CPU_GATE；允许原Lane A在独立再准入/注册后，按先前预批准的上限执行六臂。**
本文件是新增科学审查与既有A Goal的补充合同，不是启动新Goal，不是原44行计划的变更，不声称六臂已注册或启动。

## 1. Evidence and exact identities

- 用户此前批准的源决定：实验台账协调分支 `f2c106a1b767042733600fcfe3b4ba88f1e6ef26` 下的 `btree_format_stability_v1/SCIENTIFIC_DECISION.md` 与 `GOAL_CPU_ONLY_174.md`。
- CPU执行分支 `hrl/iscas2027-dtc-btree-format-stability-174-v1`，已回读HEAD `fb13326a7d8d6b72f0cfd47151c8c898b967a62e`，审阅包 `docs/dtc_l1/review_packs/BTREE_E_LIST_STABILITY_CPU_V1/`。
- CPU `GATE.json`：G0/G1/G2/G3 全PASS，状态原样为 `DERIVED_INPUT_ADMITTED_FOR_BTRE_E_LIST_CONTRACT`（沿用BTRE标识拼写）。`PRECHECK_RECEIPT.json`、`POSTCHECK_RECEIPT.json`、`G1_DERIVATION.json`、`INPUT_IDENTITY.json`、`BTREE_CONSUMER_EQUIVALENCE.json`、`REFERENCE_DECODER.json`、`CORE_COMPATIBILITY.json`、`ENGINEERING_FAILURE_HISTORY.json`和六臂提案相互支持；GPU/模拟器运行数=0。
- G0固定原list与原两个成员的完整SHA；原kernel-1 SHA `80c00c479a79c4a0c470de34c0b5b4421eb8e737e6cbb3a4046304b1f555395e`。独立新kernel-1 SHA `6295eb13625bbc8f25a712917b1b92a02ffcd2e1faba542e555f7845a1288722`；原list和kernel-2均逐字节不变。
- 新bundle身份 `6e59d31e018befcdd8d9244e6c90d09ab8dd51c665c77785857b690f051ed585`，在原174的只读候选目录 `/workspace/dtc-btree-format-stability-cpu-174-v1/candidate`。三个文件的大小、SHA和bundle hash算法以`INPUT_IDENTITY.json`为准；不是Git中的大trace。
- G1仅修改kernel-1 `findRangeK` 的PC1c40/LDG.E.SYS/4B、单个有效P lane但mode0原列表32word的固定6000行；按所核旧producer的ascending E-list合同，E=32位全1、选择原raw_word[physical_lane_id]，重新表达为现有parser的单word P-list；6000 touched、5792改变地址（同时改变sector/128B line身份）、208结果相同，其他行字节保留。
- G2是**完整两个kernel**的CPU验收（findRangeK、findK），合计16000CTA、128000warp、15609327 warp记录、444467849活动线程指令、2011551条访存记录。冻结生产 `trace_parser.cc` SHA `f63db893d39bfcd4cbf679ea1158fd9a0594211181333e13b2fdbb478d60ddb7` 的实际list/kernel/threadblock/instruction消费，与独立reference decoder的每kernel指令和活动lane地址流SHA完全一致；未执行Core。前导失败为CPU工具将风险PC的4B宽度误用于所有memory记录，修正为opcode实际4/8B并保存失败；未改输入或运行binary。
- 现有有限服务与traditional Core/binary的静态合法域PASS，**不是运行时自然完成、信用/引用/物理行/PIB及lower排空的PASS**。后者仍归A的逐臂strict receipt证明。

## 2. 科学资格：能说什么，不能说什么

上述证据足以接受一个**定义明确、有旧producer源码支持、全记录确定性变换、当前parser合法读取的条件派生输入**。历史producer的精确revision为 `0e2fddcdef37fc59ad786553892b75567a5f2cdb`，源码SHA256为 `8dcb5ad444a6cb6a3cfb1271308e27b8395ee16afae0135703b3ac3820b09d4a`。该producer只证明family compatibility，仍无实际capture/build、ELF/SASS和native output绑定。
 
原Btree `PASS_CHECKED_SCOPE`及`FORMAT_APPLICABILITY_REVIEW_PENDING`保持不变；旧解码结果与新E-list条件结果均不可升级为original native capture equivalence。对旧/新输入只能分别形成**同输入内部**的性能比值；跨输入只审查同设计角色的相对排序与有限稳健性，不能交叉分母。特别是旧canonical B16-N/TC80-N曾采用cap8192，而新六臂为cap32768；两组B16/C80的跨输入cycles变化有cap混杂。重点用原来和新轮都为cap32768的C+、IO256、OO128（以及核实同样条件的IO128）审查地址解释敏感性。不得把“排序相同”写成原capture恢复，也不能把“排序不同”用调cap挽回。

## 3. 仅原174 Lane A允许的后续动作

1. **继续原活动Goal** `DTC_SERVICE_AND_MODERN_BASELINE_CLOSURE_174_V1`；在原174账户/容器检查实时HEAD、launcher/watcher、PID+start_ticks、auth token/lock、剩余原作业和实际资源。文档审核时读到的A HEAD `33d935c498a43a3d28ea21072b5fceb230574096`（37原numericPASS/4live/3旧Hotspot HOLD）是锚点，不是重置目标。保持原44行只读，绝不修改 `REGISTERED_ROWS_V2.tsv`/原attempt或再启动旧Goal。
2. A先**只做准入和注册准备**：fetch CPU独立分支的已核SHA及其review pack；在原174只读候选目录逐文件重新算SHA/大小、校验只读输入路径的完整两kernel/list/ROI、G0-G3与实际parser/consumer、冻结两个Core/binary、六臂effective config和服务合同。保留A独立preflight收据。CPU通过不替代A运行资格。
3. 六臂上限，且在看到新性能前**同一bundle、统一cap32768和各自冻结有效配置**：B16-N、TC80-N、TRAD96/C+、IO256、OO128、IO128。六项分别有唯一manifest、lineage、UUID、独立raw/log/review目录；资源、模式、有效PIB/MSHR、line/sector、普通side path和finite quotas由A核有效选项。旧B16/C80 cap8192结果不得充当新分母。没有WAIT128、2D、LUD、modern、SpMV/LayerNorm新臂。
4. **唯一启动权仍为原A现有authority和其唯一lock/watch路径**。如能以此前合法Hotspot V2附属准入/单authority派发方式处理独立lineage，则以新的预注册和严格watcher走相同权限边界；**不得为新六臂启动第二个持久dispatcher/另建竞争锁，也不得修改冻结原44行manifest以偷带新任务**。若现有authority不支持这种独立注册/派发，停止于CPU准备，提交唯一authority兼容方案交审，不强行运行。
5. 调度优先保护4个仍在运行的原作业和主Goal自然完成；经实时内存/RSS/swap/磁盘/PID/start_ticks确认有安全空槽后，才能由原A权威滚动新增新arm。没有安全空槽就等待原作业释放；不能为提高利用率停止、重启或稀释原任务。普通工程/receipt/manifest确定性修复可solve-and-continue，变更身份、cap、合法域、服务模型、运行authority或主张时STOP科学审查。
6. 每臂自然exit0、全kernel/body/ROI与source/output SHA、effective选项、credit/reference/PIB/physical/lower/response/ordinary完成和排空、采样与有限服务11项/适用性严格检查。传统有限指标写UNAVAILABLE。严禁以“启动成功”“CPU parser PASS”代替terminal strict。
7. 新六臂全部matched后，分别计算该新输入相对B16-N、TC80-N、C+的IO256/OO128比值及同128深度的IO128/OO128对照；保留全部负收益和异常。出现回退/排序反转时仅停止**向六臂以外扩张、改参数或另造解释**，不选择性中止已预注册六臂来隐藏不利结果。不要产生original GM12、替代GM11或混合输入平均，不声称equal area/native。
8. 小型严格收据、预注册表、raw SHA索引、当前launcher和资源状态及科学结果push到A原有handoff/review pack并fetch-back，标明独立派生lineage；向ChatGPT汇报需审内容。此说明不需要新建A的Codex Goal窗口。

## 4. 其它工作与论文

- 2DConvolution CPU评估仅 `UNRESOLVED_FORMAT_APPLICABILITY`；30个局部见证与固定first(P)=1偏移相容，未证明实际capture producer、完整10PC动态E、全部65536CTA、SASS及独立输出基址。**本轮STOP**：不生成2D派生trace、不跑2D任何arm、不复开Lane B源调查。
- LUD已有正面global源码模型证据，但capture绑定仍未闭合；不追加执行。
- 论文可写“对旧producer源码支持的条件E-list解释建立独立完整parser准入”，但在六臂严格结束前不得写新Btree性能。对2D只描述未决，旧Btree/2D/LUD优势始终显式带风险。更新英文v0.7 STYLE时不代入历史旧平均/面积，当前论文源码未在本会话交付。
- V11及此科学合同都只属协调分支；本次写文档不会启动任何模拟。
