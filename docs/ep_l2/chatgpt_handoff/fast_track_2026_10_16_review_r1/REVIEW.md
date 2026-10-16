# EP-L2首轮交付审阅与接线收敛

日期：2026-10-16。原合同：6c136e2a56a008695f8c8b815723bf8f1a760db9。
本次仅发布协调审阅和下一段工作，不修改Core、执行分支、已冻结review pack或运行状态。

## 1. 审阅范围与结论

本轮回读用户报告的Lane 2/3/5/6准确提交，并补读Lane 1/4远端状态。审阅包括TVD目录源码、RO事务及共享store适配源码、Lane 5正式runner资格检查、Lane 6正文/PPA字段账、相关review包入口、来源和保留日志。未在174重跑测试或仿真，未重新计算所有已交付文件哈希，未进行PDF/SVG视觉验收。因此下面是有范围的源码/材料审阅，不替代生产路径独立资格验证。

| Lane | 本轮处置 | 明确不授予的结论 |
|---|---|---|
| 2 | 接收clean/dirty目录模块交付，允许并要求进入生产适配；统计字段按第4节修订 | 不是完整TVD接入PASS，不是TVD性能证据 |
| 3 | 接收oracle合同及共享store适配模块作为接线候选；资格依赖closed-world作用域 | 不是实际Tag/memport/epoch路径PASS，不是全RO独立验证 |
| 5 | 接收工具和旧版模块验证记录，继续进行差分/生产验证 | 旧模块PASS不自动覆盖Lane 3 r3，不授予B16正式运行资格 |
| 6 | 接收内部工作稿、可追溯来源和参数化bit账；进入精简论文稿修订 | 不是投稿定稿，不是物理PPA或新性能结果 |

已核实的是交付内容及其边界，没有把报告中的测试数量当作本轮重新执行的测试。所有阶段原始PASS/失败日志及结果保持不可变。

## 2. 冻结的审阅快照

Framework执行分支统一为hrl/ep-l2-ft20261016-laneN-v1，仓库swayhrl/accel-sim-framework。

| Lane | Framework发布SHA | 对应Core或审阅说明 |
|---|---|---|
| 1 | a23a13b7e9a0b286d4d5a952e7fe46ec2208fcbf | runtime Core 126394be46b15f55b9756d43eb9ca9a9baae1c84；runtime Framework 37dec04d223ae65167c5584e56887c74f6540d27 |
| 2 | 24158d2344d086d2ff3d6ba31d1099682aac8e9d | Core 56abbacc1192d68995e78561899719649f838079 |
| 3 | bfa193e76873ebf39ce5262483f4828f833dbc3d | Core ddedbf0fabd46c6e35358c9a0e78b77f52cab2c5；适配所基于Lane 1 Core为10d7f4fea1f9699b4e091091f7e23e072c19d453 |
| 4 | 1657e77020321e0095acb2e7922056b27d8edf50 | 仅有启动阶段状态的本轮审阅，不据此断言节点没有后续工作 |
| 5 | c603a5634b6b3f54aec10bdb1fc804e0a648b567 | 独立RO验证针对Core 57801b429166b47079444081aaaafbfe5050e0d5，不是Lane 3本次r3 |
| 6 | c6548bff73572f12f4b2abef8ba800e502f07ec1 | 正文/工具生产a792de58ce436fca225ee689a291a1b5fa8c3211为用户报告；本轮按发布SHA读取正文和账本 |

这些是审阅时的Git快照，不是未来永不变化的HEAD。下一次消费时有界fetch，固定实际所消费SHA。新HEAD不自动继承旧生产资格。

## 3. 已过时的依赖说明

Lane 2的receipt仍绑定Lane 1 Core 4fb91f0a的身份ABI，说明缺可执行allocator/pin/role接口。该阻塞已被较新公共版本部分解除：Lane 3已消费10d7f4fe共享store，Lane 1当前发布126394be生产候选。

Lane 1最新BASELINE_CONTRACT_V1.json中：directed_ready=true，runtime_ready=false，independent_qualification=false；binary与B16/U_WB配置hash已非空。STATUS记录旧source三个对照已完成、新all-OFF vectorAdd/cfd在共享registry运行，sad随后。这个状态仍不是可直接运行正式B16的资格，但不应继续描述为“没有binary/config或没有公共实现”。不得干扰这些已有任务。

Lane 5需要消费这一新候选，准备/开展生产资格检查；不能把旧receipt的空hash当当前事实。正式runner保留INDEPENDENTLY_QUALIFIED门槛。资格检查本身与正式性能运行不同：不得要求一个候选先独立合格才允许去验证它，形成流程互等。

## 4. 源码与指标审阅发现

### R1-METRIC：TVD服务字节不是下层节省字节

Core 56abbacc的ep-l2-tvd-directory.h::response_commit按每次response的requested-sector popcount累加avoided_lower_sectors和avoided_lower_bytes。STATISTICS.md已经提示实际lower transaction需要OFF/ON对照，但字节字段本身也不能作为精确节省：多个同sector请求在baseline可能合并为一次lower read，而逐response累加会重复。

在新revision新增或重命名为tvd_served_sectors/tvd_served_sector_bytes（或同等明确名字）；旧schema需兼容时保留deprecated别名，并禁止把它导出成DRAM节省。净流量变化由匹配B/M的实际lower read transactions/read bytes和DRAM bytes分别计算；不混淆L2出口与DRAM边界。保留请求服务量与合并影响，不凭TVD命中计数推算流量收益。这是统计语义修订，不要求重做旧模块全部测试。

### R1-VERSION：独立验证覆盖范围有版本差异

Lane 5验证的RO Core为57801b42；Lane 3当前r3为ddedbf0f，并已加入真实共享store/pin/bank适配。因此必须验证r3及后续实际接线差分，不能用旧16项oracle/5组模块测试自动盖章。Lane 3当前remaining hooks明确包含实际Tag、cache/memport路由、epoch加载和runtime开关，不能仅凭完整Core build宣告这些路径存在。

Lane 5 runner V1仅有ro布尔标志。配置hash会区分不同配置，现有B16/U_WB使用没有因此失效；但接收RO正式模式前应版本化扩展语义向量，明确tag_detach与line_mshr_bypass分别开关，并逐组合绑定资格。不能用一个ro=true掩盖四种模式或沿用未覆盖组合的资格。

### R1-ORACLE：保守整commandlist scope可保留

Lane 3 RO_ORACLE_CONTRACT采用whole_commandlist、TRACE_MODEL_CLOSED_WORLD，并声明外部写入/别名/先前写回退尽等条件。它比孤立kernel分类更保守；这是实验作用域假设，不是SASS证明了真实硬件没有外部写入。接线需保持初始化边界、证书身份及非法请求回退；不得为增加coverage私自缩小epoch。FWT的已绑定certified_lines为空不能当工具故障或RO有效工作量；须保留该负覆盖样本，正路径canary选证书确有成员的开发负载。

### R1-PAPER：工作稿保留，论文稿去工程报告化

Lane 6正文真实区分旧校准/new WBUF、shadow/oracle/ideal和未完成结果，预算146/145KiB与9.125/9.0625MiB正确。显式0..32计数需6bit、512索引需9bit的修正也应保留。该稿仍混入用户确认、Lane分工、commit、receipt、运行状态等工程叙述；这些移到可复现附件，正文聚焦问题、机制、因果实验与结果，不能因移除工程叙述而暗示尚未实现的功能已完成。

PPA_LEDGER的T_RO=128被明确标为算例，不是实现参数；源码transactions的completion槽按物理payload_budget索引，不能把128项算例用作真实RO开销。下一版逐字段绑定实际实现，说明物理分配槽数、可同时live数量及可复用字段；不得为贴合算例额外施加128上限改变机制。未知工艺PPA继续标未知，不等于应停下bit账和正文。

历史图表无需补跑：Lane 6使用的STREAMING_REUSE_PREFINAL_r1确为12行子集；同一cdab5765提交还有DRAFT_FIGURES_CHECKPOINT_r1/plotting_tables/SOURCE_ROWS.csv，含13个COMPLETE_VALID行和scan。后续核对该检查点的准确源CSV/hash再迁移图表，保留prefinal不覆盖。13行完成不等于本轮新机制性能完成。

## 5. 接下来只收敛执行，不扩研究范围

优先链：保护Lane 1已有all-OFF任务并完成资格 -> Lane 5独立归一化 -> B16/U_WB16首批匹配结果。TVD/RO/ideal在独立工作树上接线，不能回写正在资格检查的binary。

Lane 2/3负责各自完整生产适配补丁及可达性测试，Lane 1保持最终集成权；“唯一集成者”不等于所有接线劳动都交给Lane 1串行完成。具体动作见CONTINUE.md。所有预算、primary、oracle、TVD额外一拍与原来科学边界不变。

## 6. 可回读的证据位置

路径相对Framework，除Core源码外均取第2节相应发布SHA：
- lane1/STATUS.md、BASELINE_CONTRACT_V1.json（前缀docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/）。
- lane2/RECEIPT.json；review_packs/FT20261016_LANE2_DIRTY_MODULE_r2/SOURCE_MAP.md、STATISTICS.md、normal.log。
- lane3/RECEIPT.json；review_packs/FT20261016_LANE3_SHARED_STORE_r3/SOURCE_MAP.md、RO_ORACLE_CONTRACT.md。
- lane5/RECEIPT.json；util/ep_l2/ft_lane5/run.py。
- review_packs/FT20261016_LANE6_PAPER_PPA_r1/PAPER_DRAFT_ZH_V1.md、PPA_LEDGER.md。
- 历史cdab5765b65f6e1575d9c185de127a1c1c49dd70：docs/ep_l2/review_packs/DRAFT_FIGURES_CHECKPOINT_r1/source_provenance.md及plotting_tables/SOURCE_ROWS.csv。
- Core仓库swayhrl/gpgpu-sim @56abbacc：src/gpgpu-sim/ep-l2-tvd-directory.h。
- Core @ddedbf0f：src/gpgpu-sim/ep-l2-ro-transactions.h、ep-l2-ro-store-port.h。

本轮没有对整库、全部测试、所有生成图或节点现存进程作穷尽认证；formal performance仍需绑定实际生产版本的独立证据。
