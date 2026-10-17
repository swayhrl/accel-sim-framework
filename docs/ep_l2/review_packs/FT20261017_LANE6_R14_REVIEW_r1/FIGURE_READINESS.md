# Each planned conclusion versus executable evidence

“可执行准备”不等于“允许现在运行”：Lane1唯一producer、Lane5独立资格/资源准入不变。现有21生产case由build_r0_1.py:repair_commands精确定义（A18），五pair输入元数据见Lane5 CONTINUE_R13准备；没有新binary/key或当前内容复核资格。

| Panel / possible conclusion | Exact observable / current implementation | Qualification and ready/missing work |
|---|---|---|
| Fig2a relative application cycles |五固定开发负载×B16/U_WB16；native cycles/instructions/full-application termination；同binary/common-config/trace/epoch/features，S=CB/CU | Lane1 Corec948/Framework3ab唯一官方binary+21实跑，Lane5 eleven gates和current V2每pair接受；可执行模板存在但全NOT_RUN，0pair。五对才geomean，不排除sad/slowdowns |
| Fig2b actual copy/send work |EPL2FTV1 copy_lines为完成copy transfer计数、staging_reads为成功send-read grant，wb_created/wb_lower_accept/wb_completed；C7d各类logical ops另列 |与2a同pair/窗口；source与send共WB_READOUT，copy目的写与普通写共RESIDENT_WRITE。未有独立physical分类映射；不能减去不同口径计数假装分解。正文已缩到可审计原生指标。rollback前工作保留 |
| Fig3a capacity pressure |FT wbuf_full、pool_full（U landing失败，不自动等于全池满）、staged_max/wb_occupancy_sum/observed_cycles、roles；C7d WAD full/hazard/occupancy独立 |bank-class落点不足与global-full未独立分列，不得把pool_full命名为“全池容量耗尽”；reserved occupancy有通用Tag reserved与payload-reservation不同概念，需准确映射/小事件补充。借用计数不是收益 |
| Fig3b bank service |application bank_logical_ops、bank_grants、attempts/retries/true_conflict_ops/events、bank_wait_cycles及per-bank；逐周期bank上限来自生产资格/断言 |累计grants≤cycle不证明逐周期≤1；等待总和不减GPU cycles；grant效率或useful-response不能从operation下降单独推出。相同所有权/返回正确性要求 |
| Fig3c pressure transfer |C7e successful read/write issues/bytes、missq/lowerq/scheduler/return压力与WAD lifetime；FT lower_accept/completion分开 |需原生指标和采样点审计，同accepted run/完整scope。全应用用application_cumulative，不叠加重叠kernel_shared_delta。指标不足时只保留已量化部分，不虚构下游因果 |
| Fig4 WBUF8 sensitivity |已有B8_BANKED/U_WB8 overlay，1160 slots/4×290 |source支持8，但无新binary独立资格；现主consumer只认1168，需scope适配，不可直接填。验证第二预算不能单独分离copy与sharing |
| Fig4 equal-total static repartition |合同条件1024 resident/112 bypass/32 WBUF，总1168；必要时compute-only1024/0/144必须标明丢bypass能力 |当前constants固定1024/128，WBUF只8/16；**无可执行配置/qualified runner**。科学触发后需owner实现/独立资格。改WBUF32不是等预算控制；copy-matched归因也无冻结开关 |
| Separate Ideal diagnostic |Lane4候选8ff56e，R1.1 18格计划与same-binary B16要求 |二新C++回归NOT_RUN，binary=null，repair+ideal独立资格缺；不是EP-L2真实机制、不是严格上界、不是旧1.721×复用；原主bridge不能擅自收理想结果 |
| Optional extension evidence |TVDab413、RO5ae8独立源候选，各自生产准备存在 |没有官方R2整合/新资格/应用；不能从U_WB binary或Python/static PASS推出TVD/RO性能。RO保持whole-commandlist oracle，覆盖率/额外reads/metadata成本另列 |

PPA不占用待测性能图位：设计字节预算与符号字段账可保留，真正面积/功率/频率未测。无结果时不能用成本场景柱形替代加速图。
