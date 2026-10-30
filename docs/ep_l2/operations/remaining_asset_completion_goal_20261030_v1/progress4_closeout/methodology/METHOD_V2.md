# 174-new / 109 / 真164 trace采集与交付方法论

本稿是有限经验总结Lane实际读取源码与回执后形成的文档候选，由主Lane复核后归档；它不签准Root范围、采集、工具激活或科研资格。事实截至EVIDENCE_CATALOG_V1.json绑定的不可变交接快照；实时进度应重开最高数字交接、真实PID/ticks与同run回执。外部ChatGPT审稿未收到，不能写“已审”。

## 一次交付的身份

单位是精确输入profile：qid、binary SHA、完整argv、输入文件或可复现生成契约及生命周期、producer/格式、actual loaded image、完整launch/record域与消费者用途。程序名、binary数、输入数、普通/裁剪数、对象版本数分别登记。旧CLI实际别名、修复新ELF或别的输入，不能偷改原行状态。[P01/P24；identity/cli/ledger]

证据按阶段分层：源码事实、CPU夹具、原生QA、实际采集、全记录/完整性闭合、归档COMMIT/父链、公共读取、exact consumer证据。科学或性能资格不自动继承；格式7、CFI9与custom source、typed auxiliary分开。编译成功、进入流程、有trace都不能写成consumer已支持。V11所示public81/81、SM70 NAS125、RAW7与原153 effective仅1闭合/152未闭合并不矛盾；修复Poly等为独立身份。

## 源码指导缩减

每个循环记录源码位置、类别、迭代状态/输入/同步依赖、缩减方案、保留不变量、预期launch/record及可信度、信息损失和适用实验。类别区分：初始化、算法必要迭代、分阶段归约、benchmark重复、warmup、事件/stream同步、原QA与I/O。

优先缩减可证明不积累算法状态的benchmark轮数；保空间N、类型、grid/block、各kernel变体、warmup、算法内循环、输入初始化和原QA。modern6例仅benchmark100到2，保16M int/64MiB、k6及s64→1完整归约，source预算5launch/2D2D不能冒实际观测。[P09；loop]
100到2仍丢98轮缓存/热/稳态/噪声及平均计时历史，不能声称缓存轨迹或性能不变。新source/ELF/argv/profile留原件。缩空间/改数据/删变体/改同步或warmup另给理由和损失，不能沿仅重复缩减方案直接推广；也不默认要求所有潜在分支先通用支持。

## 必要流水与并行

### S0 身份与源分析

必要：原qid/binary SHA/argv；输入文件或生成契约及生命周期；actual loaded与static image关系；producer/格式/用途。

新增触发：逐循环类别、状态依赖、保留不变量、launch/records预算与信息损失；CLI不明才核parser/ELF。复用：已接受binary表、同版本source和只读清单。执行：CPU source Lane，主Lane接受方案。

### S1 冻结与实际入口

必要：完整CODEMF、reachable caller硬pin、双host实际imports、schema/status和服务约束。

新增触发：新ABI/版本分支对应负例；原代码不变不全重做。复用：同byte H/P/Wire/O/资源保护母件。执行：有限CPU准备，主Lane工程准入。

### S2 原生QA

必要：原函数/marker或布尔返回＋exit/file域；actual参数/形状；无tracer；owned关闭。

新增触发：必要sourcebug修复形成新ELF；不发明通用PASSED或独立oracle。复用：同binary/argv/input/QA环境已接受QA；纯observer修复不默认重跑。执行：单一GPU队列。

### S3 实际采集

必要：canonical Comfy/GPU/IO和Native资产租约；actual code/launch/参数；完整producer正终态；同run关闭。

新增触发：必要输入域或关键control/texture/mask实际取证，不以App exit0代替collector。复用：相同QA/map及未变协议；新profile不能继承旧资格。执行：GPU只采集及小终态，释放后CPU解析。

### S4 完整POST

必要：全部声明record/warp/CTA/EXIT；RF/CBANK/static/control按真实格式；CRC/allSHA和必要group一一绑定。

新增触发：CFI terminal特例先实际独立控制匹配及窄许可，再全RF F9；不能要求futureF9绕成循环。复用：已接受F9/GROUP/CRC/wholeSHA及原bytes，优先单次C++流读。执行：CPU有限角色，payload/TMP真164。

### S5 裁剪与轻量consumer

必要：完整CTA/warp顺序和字段；body等同/CRC；exact软件/config实际启动、退休和owned关闭。

新增触发：按用途风险增补必要少数CTA；预算不足为UNKNOWN_BUDGET。复用：已物化样本、原取样器；不默认全程序/全feature/全配置。执行：CPU模型可与GPU流水。

### S6 NAS归档父链

必要：精确成员计划；COPY全SHA/closed-reopen receiver/COMMIT；父真实COMMIT后绑定derived。

新增触发：新kind或成员上限只改确切域，不能减SHA；unknown关闭/EIO先保留。复用：已接受COPY协议母件，源KEEP/released0。执行：CPU/NAS；未核近期/计划复用不清缓存。

### S7 公共交付

必要：CAS保旧catalog/版本；immutable discovery实际返回请求id；共享读取/按需恢复metadata；有效台账与远端读回。

新增触发：实际新schema才窄兼容和对应回归；实际需要某资产再有界恢复正文。复用：已接受CLI/按资产restore；全库Native正文回读取消。执行：主Lane发布，不自动升级science。


各阶段满足自身前置后即可流水，消费者、归档不必机械串行：未跑消费者的库存可以如实归档或以typed条目发布，标明NOT_RUN和缺口，不计为最终适用consumer交付。后补证据使用新不可变版本/overlay，不回写旧COMMIT；只有真实父COMMIT后才可绑定derived，public存在也不赋consumer资格。

GPU保持一个canonical队列；源码、独审、CPU后处理、NAS归档、小模型可以有限并行。资源数字属于当次Role，不把旧全局deadline、旧sender状态或旧Native写预算抄到新NAS-only任务。实际Mem/CPU/Quota/AS/IO域需一致；主Lane工程准入不是再次向已全权授权的用户索权。完成/闲置智能体要实际续作，发消息入队不等工作已开始。

## 停止、复用与数据保留

程序exit0不代表collector完成；文件增长也不够。核同run完整launch/record域、错误、真实PID/ticks、cgroup、reader/child joins及proposal/ACK/release，关闭后才解锁。超时不是死亡，不能重启当前活跃run、热替换源码或碰foreign。unknown EOF、SHA、权限/程序错误先诊断；仅已批准明确瞬断按精确规则退避。主Lane可沿已有owned控制通道结束已确证死等，仍须实际关闭。EIO令诊断失败也不能丢Native租约；复用preloaded保锁母件。[P16；copy]

Source KEEP、released0；新payload/code/log/scratch真164，Native至少5GiB实际余量。清理副本另需NAS完整接受、唯一性与近期/计划/未知复用检查，不由本稿授权。全库Native正文回读已取消；metadata restore计划检查所有成员和父依赖，并不等正文已恢复。

复用同bytes的完整F9/GROUP/CRC、QA与样本；只重做新代码/数据/格式/consumer实际影响的证据。新COPY receiver SHA依然必要。完整大数据校验可一次流读同时算CRC和多层SHA，不能为了快变成抽样；不因习惯反复解压、跑QA/GPU或全旧资产二次长计划。新receiver/真实父绑定/公共请求id仍须闭合。

## 高收益故障判断

PITFALLS_V1.json含24个实际坑、规则、证据与适用限制。先检查CLI与env存在性；再查实际NVBit dump artifact而不是bool，sentinel后flush；首386附着不能伪造entry；POD先落身份再逐字段诊断，合法NULL明确unknown，不倒猜历史地址。QA按程序原合同，元素/字节与短读必要时最小修复成新身份。static152/nonNOP137/path54不同，padding仅准精确位点；legacy imm是最后typed IMM_UINT64，非猜0。旧RAW与新image差异保留，54→47丢零有效mask事件，不能称全字段无损。source/libm recipe文档SHA不是实测GPU数组SHA。[P01–12/P20]

跨host alias、reachable COMMON pin、实际服务CPU/Quota与真实入口status逐项实核，不靠辅助函数自证。父COMMIT后绑定；public catalog要同步immutable发现并断言请求id实际存在。共享restore窄兼容新的真实schema与父依赖，不修改旧历史。[P13–19]

完整custom source通过不等ordinary7/HB物理overlap/consumer通过；完整CTA退休不等全程序/全feature/全配置/数值仿真/科学资格。参考程序原QA弱点照实记录；不默认新增独立oracle、全部host数组、全部潜在分支或所有consumer配置。[P21–24]

## 实际读过的证据

引用说明的是各自阶段，候选没有由本稿提升为Root批准。以下是实际打开计算SHA的源和回执；原件未改。

- **C8_actual**：/root/share/mnt164/huangrulin/traces/receipts/remaining_asset_completion_goal_20261030_v1/root/ROOT_SDK42_C8_SAME_EXECUTION_INPUT_FULL_F9_GROUP_SHA_CRC_OWNED_ACCEPTANCE_V1.json；6216B；SHA256 9acfaf063692710994bd3e79d25b4991ee4b8b20e245ce128742d9cbbbbcd428
- **QA_source**：/root/share/mnt164/huangrulin/traces/receipts/remaining_asset_completion_goal_20261030_v1/REG128_exact_program_QA_contract_repair_20261030_v2/ROOT_REG128_EXACT_QA_PARTICLES_REUSE_SEG_READY_SMOKE_SOURCE_FIX_REVIEW_ENTRY_V2.json；10093B；SHA256 0471695383ef2c14e86139ec8aac1dbed89342920c67e0093b8b2feccee6e18a
- **TEX_actual_candidate**：/root/share/mnt164/huangrulin/traces/receipts/remaining_asset_completion_goal_20261030_v1/TEX_kmeans400_actual_A4_cpu_analysis_v1/ROOT_KMEANS400_ACTUAL_A4_DESCRIPTOR_COORDINATE_SOURCEVALUE_AND_OWNED_CPU_REVIEW_ENTRY_V1.json；9936B；SHA256 d049d2ee27c06d4fca10f9b0f7944f2dec3b27d5d3ba6a8947d8ee5122221077
- **attachment_source**：/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/private_candidates/modern_reduction_hash_observer_prepare_20261030_v4/runtime/producer/modern_reduction_hash_observer_attachment_v4.cu；41274B；SHA256 77ca74c1aeff01394431c206189caa74ada0bdfc0f6ceda2e86c0592df32c63d
- **baseline**：/root/share/mnt164/huangrulin/traces/receipts/remaining_asset_completion_goal_20261030_v1/root/ROOT_ACTIVE_GOAL_PROGRESS_HANDOFF_V11.json；36920B；SHA256 00382c8c593c48c1731b3d9d3caea0ecce48948b7ce5b8b641cedac0b9315400
- **cli**：/root/share/mnt164/huangrulin/traces/receipts/remaining_asset_completion_goal_20261030_v1/CLI_semantics_audit_v1/ROOT_F18E_ACTUAL_ELF_HOST_CLI_CHAIN_STATIC_AUDIT_V1.json；5848B；SHA256 3ab4ed49821ce6c20545d26805a5b5bb7deff8f18b861c937bfbf33d27984c7b
- **common_pin**：/root/share/mnt164/huangrulin/traces/receipts/remaining_asset_completion_goal_20261030_v1/root/ROOT_LUD_QA_CANDIDATE_PREEXECUTION_COMMON_PIN_REPAIR_V1.json；1179B；SHA256 30f09d2fe514003122fbbba5a01a3ea3df1f9573d1a881f284ed53ade95253df
- **control_actual**：/root/share/mnt164/huangrulin/traces/receipts/remaining_asset_completion_goal_20261030_v1/root/ROOT_LUD256_INDEPENDENT_CONTROL_OBSERVER_ACTUAL_ACCEPTANCE_V1.json；114586B；SHA256 71820f235d7d0c664ca296e9debb387bbaa36554488c6440dad2cd40d2c373b4
- **copy**：/root/share/mnt164/huangrulin/traces/receipts/remaining_asset_completion_goal_20261030_v1/root/ROOT_PILOT2_FORMAL_COPY_PUBLIC_V2_ENGINEERING_SOURCE_ADMISSION_V1.json；2247B；SHA256 95e4c65f64662c1fa6b233528b0f81cf58a216bf7908f45adfe88d6bf61a72a1
- **discovery_erratum**：/root/share/mnt164/huangrulin/traces/receipts/remaining_asset_completion_goal_20261030_v1/root/ROOT_PILOT2_PUBLIC77_DISCOVERY_STALE_SNAPSHOT_ERRATUM_AND_REFRESH_V1.json；1580B；SHA256 97f663e1ac9ba6599cc32867efcfbf2aa48db22e8dd6288abf39628e6d02b440
- **dump**：/root/share/mnt164/huangrulin/traces/receipts/remaining_asset_completion_goal_20261030_v1/ISA_producer/lud_observer_dump_api_failure_fix_20261030_v2/ROOT_LUD_OBSERVER_DUMP_API_RETURN_FALSE_STRICT_ARTIFACT_FIX_EXECUTABLE_SOURCE_ENTRY_V2.json；6472B；SHA256 9816bf2b9b06005d716d789f14e9d447713a28d96121fbdeab84d25b99901acc
- **dump_source**：/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/private_candidates/lud_observer_dump_contract_fix_20261030_v2/checked_loaded_cubin_v2.h；1249B；SHA256 6675202a8ec16f953a41c7141d5561d7f3fc69e764d47f4fa74782e83b6546f8
- **env_source**：/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/private_candidates/sdk42_reduction_c8_same_execution_capture_prepare_20261030_v2/runtime/capture_only_leaf_v1.py；18024B；SHA256 abbe00cd74e768b141bfebd88a90323f31cdbbcd62a7b55106bb899b4ec292ee
- **flush**：/root/share/mnt164/huangrulin/traces/receipts/remaining_asset_completion_goal_20261030_v1/ISA_producer/lud_observer_channel_flush_fix_20261030_v3/ROOT_LUD_SENTINEL_PUSH_FLUSH_ONLY_OFFLINE_SO_PROTECTED_STAGE_REVIEW_ENTRY_V3.json；6646B；SHA256 006111ee943c99a8e2093597e04bb12ee9e78a9e7e5020b2b6b6db1c6245e997
- **flush_source**：/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/private_candidates/lud_observer_channel_flush_fix_20261030_v3/observer_flush.cu；199B；SHA256 88e7937647676a88a6d97e26a2df24fe370b622c1fc1625d0b19c815c9a6db00
- **full11**：/root/share/mnt164/huangrulin/traces/receipts/remaining_asset_completion_goal_20261030_v1/root/ROOT_SIMPLESTREAMS_R2_FULL11_CPU_POST_SOURCE_FINAL_ACCEPTANCE_V1.json；3505B；SHA256 958cf7f82405c6b18ebc5b45af8483b35eb9d191adcac44f0a2966ef5c08a437
- **full11_static**：/root/share/mnt164/huangrulin/traces/receipts/remaining_asset_completion_goal_20261030_v1/multistream_producer/simpleStreams_full11_source_v3/ROOT_SIMPLESTREAMS_FULL11_V3_STATIC_VIEW_FIXED_SIGNABLE_ENTRY.json；3725B；SHA256 26de0b15c762705108f0af6a1fdc139e155cdb8e412dfbe4feccebb34b0afab6
- **identity**：/root/share/mnt164/huangrulin/traces/receipts/remaining_asset_completion_goal_20261030_v1/root/ROOT_CURRENT153_BINARY_PATHS_REAL_SHA_ATTESTATION_V1.json；78244B；SHA256 7b36f0564ced6b07fca6e7d1a2c612a49c533d90ee35977bfb6e40f3e851f321
- **imm**：/root/share/mnt164/huangrulin/traces/receipts/remaining_asset_completion_goal_20261030_v1/multistream_producer/fullsource_archive_and_projection_source_v1/ROOT_SINGLE_CTA_IMM_RECOVERY_AND_PROJECTION_SOURCE_REVIEW_V2.json；3853B；SHA256 286800b6667922ef22242496f6601969f823530fbec30b9cb299d578e2fb52eb
- **imm_source**：/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/private_candidates/simpleStreams_fullsource_singleCTA_ordinary7_projection_candidate_20261030_v1/frozen55_source_contract/SOURCE55_IMM_PROVENANCE.json；716B；SHA256 2a20f1d0edad69ba642832522d8de9413239997d7ae6f5f14af1ab57205f106b
- **input_actual**：/root/share/mnt164/huangrulin/traces/receipts/remaining_asset_completion_goal_20261030_v1/root/ROOT_MODERN6_ACTUAL_HASH_REPRODUCIBLE_INPUT_AND_OWNED_FINAL_ACCEPTANCE_V1.json；3340B；SHA256 a73b670f6beae530ba70774b738567a17652dcb44e5864d7b1ac433f0c4efb44
- **ledger**：/root/share/mnt164/huangrulin/traces/receipts/remaining_asset_completion_goal_20261030_v1/effective_stage_ledger_20261030_v1/UNIFIED_FROZEN153_EFFECTIVE_STAGE_LEDGER_V3.json；970691B；SHA256 da72d1d28d8b6929d73d4b56cbff2dc074b873eb9e8132107c465fe963c0bfe7
- **loop**：/root/share/mnt164/huangrulin/traces/receipts/remaining_asset_completion_goal_20261030_v1/actual_input/modern6_repeat2_source_prepare_20261030_v1/ROOT_MODERN6_REPEAT2_CPU_BUILD_AND_LOOP_REDUCTION_REVIEW_ENTRY_V1.json；5884B；SHA256 38b0c5b9dfb648f760306083d08abd32147c8f2fd96b82c557dcae43f3b122cb
- **method**：/root/share/mnt164/huangrulin/traces/receipts/remaining_asset_completion_goal_20261030_v1/root/ROOT_METHOD_AND_ACTUAL_PIPELINE_PITFALLS_V2.json；3673B；SHA256 6512af72fd035714c07ce577c0e2163297c0637701ed4b9a522ec4c46f7e31c8
- **model**：/root/share/mnt164/huangrulin/traces/receipts/remaining_asset_completion_goal_20261030_v1/root/ROOT_SMALLPOLY3_REAL_CONSUMER_ENTRY3_RETIREMENT_AND_OWNED_ACCEPTANCE_V2.json；14835B；SHA256 0a57536737eaac33abf8396075beecc562f28910a23c093874a2233b1228b36e
- **nullable**：/root/share/mnt164/huangrulin/traces/receipts/remaining_asset_completion_goal_20261030_v1/TEX_kmeans400_observer_api_pod_diagnosis_v1/ROOT_KMEANS400_A4_API_NULLABILITY_DIAGNOSTIC_PROTECTED_SOURCE_READY_REVIEW_ENTRY_V1.json；9227B；SHA256 a4c475fdc951251b3cc0f69f9f17c5ef2733e153899555e7b675e6800e7808bd
- **public81**：/root/share/mnt164/huangrulin/traces/receipts/remaining_asset_completion_goal_20261030_v1/root/ROOT_SMALLPOLY3_PUBLIC81_CURRENT_DISCOVERY_AND_PAYLOAD_FINAL_ACCEPTANCE_V1.json；70019B；SHA256 a9866055819c81e8fba337f40c3c2afde61fe04f3fa98e694bc783a32b4babb6
- **restore**：/root/share/mnt164/huangrulin/traces/receipts/remaining_asset_completion_goal_20261030_v1/root/ROOT_PUBLIC12_INSTALLED_BOUND_RESTORE_CONTRACT_METADATA_INSPECTION_ACCEPTANCE_V1.json；12932B；SHA256 38ec50996795a74f7130dab0155c2bb45472ddb08fca6dff7bd288bb9d95b7a1
- **scope_literal**：/root/share/mnt164/huangrulin/traces/receipts/remaining_asset_completion_goal_20261030_v1/root/ROOT_SMALLPOLY3_ORDINARY_SCOPE_STATUS_LITERAL_PREEXECUTION_FAILURE_V1.json；1340B；SHA256 d0900a466e1076e03cd347b16293bc7912895f3e83e3df2569cc4e8fb491ebd1
- **smoke_actual**：/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/private_candidates/remaining_smoke_QA_countfix_reg128_20261030_v1/runtime/ROOT_SMOKE_QACOUNTFIX_REG128_ACTUAL_UNINJECTED_QA_OWNED_ACCEPTANCE_V1.json；3741B；SHA256 97a0cca636711c1cc99dd825cb91453ca99b673d023ebd25febacb0167b17a6b
