# E2 消融/诊断准入清单

main61保持不变；A2 HEAD73d1951bd、D HEAD0eb15c645已独立读取GitHub。D现有正式归因仅Conv r2，CFD/DWT/SAD已请求增量复核；E按精确接受计数独立作有限观察，不替代D归因或把请求等待相加为GPU停顿。

| 优先批次 | Conv条件 | 独立资格 | 预计每端 | 结果预计/硬上限 |
|---|---|---|---|---|
| 1 | W_ONLY、F_MINUS_V | 各自PASS，待正式执行 | 55–85分钟 | 100–130MB /384MiB |
| 2 | F_MINUS_R、S_COPY_FREE | 各自PASS，待正式执行 | 55–85分钟 | 100–130MB /384MiB |
| 3 | WV_M、WV_T | 各自PASS，待正式执行 | 55–85分钟 | 100–130MB /384MiB |

每个条件有单独QUALIFICATION、配置SHA、完整输入SHA及profile原生证据审查。复用适用的旧有限原生断言及当前17项WAD修复证据，未重跑17项、未构建main，也未用S/F应用资格直接替代。额外B/C联合fixture仍未获资格。S_COPY_FREE仅为复制服务理想化诊断，不作为物理P1吞吐或完整方案加速。

首批W_ONLY/F_MINUS_V通过原唯一中央控制器，最多双路；每个控制一旦接受即独立推送并交D，复用既有S/F锚点而不重跑端点。预计六项双路合计约2.75–4.25小时；每项硬超时仍3小时。

当前20/40、剩20、contingency8/8已耗尽；六项均实际启动后26/40、余14。当前新结果3,607,362,584B、总结果17,916,938,968B。六项最坏新增2,415,919,104B，新结果上界6,023,281,688B、总结果上界20,332,858,072B，均保持6/20GiB原上限。

DWT/CFD四槽位修订仅提案：FWT的S_COPY_FREE→DWT S_COPY_FREE，W_ONLY→DWT W_ONLY，F_MINUS_V→CFD F_MINUS_V，F_MINUS_R→CFD F_MINUS_R；原矩阵未改，未登记或启动新条件，需用户批准及目标输入/profile独立资格。完整拟修订矩阵、配置、输入、时间和容量条件见DWT_CFD_REALLOCATION_PROPOSAL/README.md和PROPOSAL.json。

原T0、旧20次、所有FAILED/INCOMPLETE/HOLD保持；FWT、Vector F、Btree均不重试。2026-10-21北京时间18:00新启动、22:00intake截止不变；没有新Goal、第二控制器或额外迁移请求。
