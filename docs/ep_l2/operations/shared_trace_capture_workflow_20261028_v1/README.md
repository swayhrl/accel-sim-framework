# 共享trace采集与轻量兼容验收流程

最新工程功能见[V16：两架构按资产恢复已验收](CURRENT_PROGRESS_V16.md)、[按需读取恢复流程](ON_DEMAND_READ_RESTORE_INCREMENT_V16.md)和[当前范围总账](FINAL_DELIVERY_SCOPE_SUMMARY_V16.json)。共享NAS数据与bounded restore分别有实际证据，保留153延期、RAW/Pilot缺口和原科学例外；以下版本均保留历史时点。

当前状态见[V15：75对资产与逐资产恢复边界](CURRENT_PROGRESS_V15.md)、[可复用完整流程](R2_REUSABLE_CAPTURE_POST_ARCHIVE_READ_SOP_V15.md)和[证据引用](FINAL_R2_PUBLIC75_EVIDENCE_REFS_V15.json)。统一发现75／75、RAW7及SM70125 NAS访问已验收；旧默认物化门仍待隔离restore-one修复。以下V4—V13段落均保留各自历史时点，不能作为当前运行状态。

本流程供174-new所有项目线复用。174-new负责调度，109提供RTX4080采集和CPU工程计算，真164保存正文、归档和回执。默认交付包括精确输入身份、采集、必要后处理、常规与完整CTA裁剪资产、归档提交、公共目录及适用模拟器的轻量准入证据。

用户于2026年10月28日明确调整：不要求每个程序完整模拟器重放，以更轻量的方法验证能够进入模拟器；同时整理已遇问题并将采集流程归档。这覆盖此前逐项完整回放的默认要求。已经完成的完整回放继续复用。

- [采集和归档操作流程](CAPTURE_AND_ARCHIVE_SOP.md)
- [轻量模拟器验收标准](LIGHT_SIMULATOR_ADMISSION.md)
- [已证实问题与防再犯措施](PROVEN_PITFALLS.md)
- [机器可读流程规则](WORKFLOW_POLICY_V1.json)
- [最新问题清单与原始证据](PROVEN_PITFALLS_V4.json)
- [证据索引](EVIDENCE_INDEX.json)

本次发布的是生效的工作规则、操作流程和已有实证。轻量冒烟的新适配器必须经过代码及实际执行验收，不能因为文档发布就声称其已经部署或某个资产已经通过。既有capture、POST、COPY和发布入口按各自冻结代码与新鲜运行授权继续使用。

源默认KEEP，当前释放0。全库正文恢复至174或174-new已取消；按需读取和物化继续保留。资产工程与科研性能实验的资格、历史结果、预算分别管理。

V4历史时点：25类留证问题、41份原始证据快照。template已实际通过完整CTA轻量试跑；这不代表所有资产已通过。Gaussian-s256采集正常退出，后处理和公共发布尚待完成。

控制消息通过独立SSH stdin通道传递，归档正文和审计日志继续保存在164。该通道通过真实SSH/systemd的22秒审计延迟验证；每个实际作业仍需精确输入、资源和闭合验收。


## V5增量进展

[公共56/56、Gaussian部分结果复用与CPU流水恢复](CURRENT_PROGRESS_V5.md)。[增量证据索引](EVIDENCE_INDEX_V5.json)。历史版本保持原样。

## V6资产优先范围修订

[最新交付范围与Gaussian后处理完成情况](CURRENT_PROGRESS_V6.md)。[增量证据索引](EVIDENCE_INDEX_V6.json)。161项全量适配已取消为本轮硬门槛，未启动专项延后。V4/V5保留其时间戳状态。

## V7实际归档与范围收尾

[公共64/64、typed8/153及超大多流RAW归档例外](CURRENT_PROGRESS_V7.md)。[15份增量验收证据](EVIDENCE_INDEX_V7.json)。[当前交付范围规则](WORKFLOW_DELIVERY_SCOPE_V7.json)。全量161与全库SM70正文恢复均不再是本轮硬门槛；超大多流fullPOST按用户选择留明确缺口。

## V8 公共68与原33交付总账

[当前68常规与68裁剪、独立RAW3及24完成9待办](CURRENT_PROGRESS_V8.md)。[25份原始增量证据](EVIDENCE_INDEX_V8.json)。[原33项精确表](ORIGINAL33_DELIVERY_TABLE_V8.md)。[机器缺口总账](CURRENT_DELIVERY_GAPS_AND_DEFERRED_EXCEPTIONS_V8.json)。统一66保持冻结时点，live68可独立读取；旧版本原样保留。

## V9 中型三输入公共71增量

[公共71/71与原33项27完成6待办](CURRENT_PROGRESS_V9.md)。[薄增量证据索引](EVIDENCE_INDEX_V9.json)。[机器时点增量](CURRENT_DELTA_V9.json)。V8及原33账本保持其原始时点，新6对象consumer保持UNKNOWN。

## V10 当前64输入轻量兼容证据

[64启动路线、63退休证据和61精确配置完整接受](CURRENT_PROGRESS_V10.md)。[64行瘦投影](CURRENT_64_EXACT_CONSUMER_LAYERS_V10.json)。[三份Root原始证据及NAS完整审计入口](EVIDENCE_INDEX_V10.json)。这是精确路线的分层证据，不是全部consumer配置或新科学资格。

## V11 当前采集与共享归档状态

[统一发现71常规71裁剪与RAW3、scan范围修订和末项SDK42采集](CURRENT_PROGRESS_V11.md)。[五份薄增量证据](EVIDENCE_INDEX_V11.json)。scan旧窗口不完整现场继续保留，完整采集后才按用户批准的RAW范围归档；四项后处理与当前SDK任务保持运行。

## V12 研究规模优先与成本审计

[大默认后处理范围调整、243来源单位成本视图与小中规模计划](CURRENT_PROGRESS_V12.md)。[243行瘦投影](REGISTERED_COST_THIN_V12.json)。[待QA的规模建议](RESEARCH_SCALE_PROPOSALS_V12.json)。[原始小证据及NAS全表引用](EVIDENCE_INDEX_V12.json)。V11保留历史时点，新小版不替代旧大版完成状态。

## 重复次数缩减方法

[逐workload重复缩减方法](WORKLOAD_REPETITION_REDUCTION_METHOD_V1.md)与[可填写审查模板](WORKLOAD_REPETITION_REDUCTION_REVIEW_TEMPLATE_V1.json)。优先保原工作集和算法覆盖，2轮需评估保留与丢弃信息；已做的小scan仅为工程冒烟，不能继承原版研究等价。

## V13 R2完整采集与执行检查

[四个原空间R2输入的120次完整采集及尚待执行的后处理](CURRENT_PROGRESS_V13.md)。[构建实证与边界](R2_BUILD_CAPTURE_LESSONS_V13.md)、[机器时点](CURRENT_DELTA_V13.json)和[小验收与代码快照索引](R2_WORKFLOW_EVIDENCE_REFS_V13.json)。完整采集不代表F9、consumer或新科学资格。
