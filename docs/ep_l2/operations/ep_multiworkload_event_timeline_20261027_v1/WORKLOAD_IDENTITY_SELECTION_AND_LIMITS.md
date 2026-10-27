# Workload identity, selection and limits

本说明仅综合已冻结资料。DTC 发布核对截点为 `2026-10-27T03:46:36.630513+00:00`，精确分支提交为 [`b7a654356b75caeb45fbec392eb488151c600a9e`](https://github.com/swayhrl/accel-sim-framework/commit/b7a654356b75caeb45fbec392eb488151c600a9e)；不声称之后未核对的分支、私有筛选或今日全部提交已经完成 EP 筛选。资料整理时间为 `2026-10-27T06:12:31.178480+00:00`。本次仅重读本地小资料，没有 NAS、Trace 正文、actor 或模型操作。

| 数量 | 实际单位和边界 |
|---|---|
| 118 / 93 / 89 / 25 | 原 DTC 可读资产记录 / 普通路径记录 / 去别名输入向量 / 显式 fraction/trim 排除记录。不能当作程序数。 |
| 71 + 17 + 1 | 原89的 BASIC_FORMAT_PASS / DOMAIN_REVIEW_HOLD / BODY或SHA失败；71也不是 EP 资格。 |
| “72” | 71加一个独立 Cutcp 当前 store-path 裁决候选；原 HOLD 与四旧 cell 的未准入边界保留。没有据此产生72个 EP 合格程序清单。 |
| 125 / 25149 / 22769 | 后续 Root 接受的 NAS bundle / member / unique object 访问身份；不同于原118或原89。 |
| 110 | 对125条完整 recorded-command-content 重新规范化所得内容组；不是110个科学工作负载。 |
| 53 | 旧 EP 59个 suite-program family 中46 regular+7 fraction-only有 Trace 的历史家族口径；不是当前125输入。 |

完整 command 身份保留有序的全部 memcpy 类型、GPU地址、字节数和其它字面命令；仅 kernel 文件别名替换成既有 payload SHA+size，重复 launch 仍重复。125个小 commandlist 的历史实际复读总量980332B；93 ordinary记录的旧89分组逐组通过更强 whole-command 核对，仍为89。Suite、版本证据、程序、实现、输入参数与 capture provenance 继续分列：相同 recorded payload 不自动合并不同版本或程序。CUDA9.1、PolyBench11.0等路径不是已证明的上游 source commit；NO_ARGS的编译期尺寸仍 UNKNOWN。

当前冻结矩阵是 **11个不同程序+Vector额外NI端点=12次新完整启动上限**，不是12程序再加OFF/ON。CUDA为Vector/Conv/FWT，Rodinia为CFD/DWT/Gaussian，Parboil为SAD/SGEMM，PolyBench为ATAX/BICG/GESUMMV。具体12行、全部 SHA、参数出处、kernel数和成本元数据见 `WORKLOAD_CANDIDATES_AND_MODES.csv`。预先提出的流式、模板邻域、gather、butterfly、wavelet、matvec、dense reuse和tiny Gaussian负控制覆盖均为 **HYPOTHESIS**，不是已测Tag压力或正收益预测。Conv约714.5M active-lane instructions/6.845GB、SGEMM约1.659B/2.216GB，保留完整输入，不为成本裁成ROI。

**模式不可混同比较。** Vector两个端点使用同一新Source5、输入、四config/全部282选项、F模式（FT2、T/M开启）；仅 `EP_L2_EVENT_TIMELINE=0/1` 不同，LIFE均为SUMMARY_STAGE。其它十程序使用正式S（FT1、TVD关闭、T/M不适用），物理64slice/32channel/32set/8way与固定服务资源按冻结矩阵/配置保持。SourceQ对其支持S，不表示已经证明它们不含可只读数据。其 **T=N/A**，不能把无RO事务或零detach计为完整F机制负结果；跨程序F/S差异也不能归因于局部性或T。只有Vector具有本轮 exact whole-command/128B/canonical-VA证书及新Source真实loader证据。旧CFD/DWT r5、原MAIN S/F、旧Vector或D结果只作明确身份下的历史先验，不拼成新producer NI或性能配对。

选择与排除不等于资格。另表 `WORKLOAD_EXCLUSIONS_AND_ALTERNATES.csv` 列其余114个 bundle（不是114个科学失败）：包括原地址/正文HOLD、fraction/trim、派生实现、第一批legacy诊断16-kernel边界、未纳入原89的后续资产，以及有限多样性预算未选的普通备选。FWT选logK11/logD19完整16 kernels；旧7/21的19 kernels不可截前16替代。Gaussian matrix4完整6 kernels与-s16的30 kernels不同。原Hotspot稀疏mask/address HOLD不由派生model-conditioned PASS清除；Pathfinder不同版本/参数不按名字合并。特别纠正历史可用性口径：当前125已列full-labeled MVT与123.7GB的full-labeled 2MM；旧EP的MVT缺失/2MM fraction-only仅属旧时间点，不能作今天排除它们的理由。它们未进入本矩阵，不能据目录访问自动补上EP消费者资格。Gemver不在这份冻结125标签清单，不声称别处永远不存在。

Root125接受状态明确为 `ALL125_25149_SHARED_NAS_ACCESS_ACCEPTED_NOT_NATIVE_CONSUMER`，重用冻结 whole-body SHA基础；不授予Native restore、消费者、科学资格或OS ACL只读保护。第一批使用既有真164 bundle view，逐member对应冻结storage backing，不借DTC本地完整副本。FWT的CAS commandfile父目录不含全部16 kernel，必须保留 canonical bundle view。当前SourceQ `57e2c0e62dc84d6d33cd8b96af3f6e6d45879213f5c93f3a4fa43b51a4031400` 是新producer CPU/input支持；四个权限字段均false，不能替代每case预算、native资格、真实PID/argv/env/全member open、完整终态及归档恢复。运行接受状态由Main真实point/DONE/归档收据记录，本选择表不声称十二点全部已运行或接受。

**PROVEN（限定于所引快照）**：发布与文件身份、125 full-command映射、旧89强去重保持、冻结12行/11程序、Root125访问范围、SourceQ支持模式。**HYPOTHESIS**：局部性及可能Tag机会。**UNKNOWN**：未证上游source版本、完整原生capture和数值SASS输出、未选输入当前EP资格、未运行点性能和机会。所有本批结果的范围仍是 `TRACE_DEFINED_COMPLETE_DECLARED_COMMANDLIST`，**capture_completeness=UNKNOWN、numeric_SASS_output=UNKNOWN**；记录内完整结束不升级为原始应用捕获完整性。

证据主索引（完整路径/SHA见同目录manifest）：`PUBLICATION_AND_AUTHORITY_READBACK.json` SHA `b63b9bbdd5f676d1e50367792a3f92a32de120a7305e22feda53c69ce2fb8c1c`；`AUDIT_COUNTS_AND_SOURCE_REFS.json` SHA `91fce14bae932db86c63c539ae899b43c48b95322a9ce1d7c7ceb6b51b298744`；V2十一输入 SHA `c3c1219f9d67af5dc4bed48ffcca82ced312175f7fc0e9b5ebf8f3c1c6b16345`；strong command检查 SHA `a304fcf9bf82f323987d8e3f9cf0fbfb4b58b86b30c3ce1da9c3bdb219002de3`；当前冻结矩阵 SHA `7834f22c632af035864e11d3adf30bc38ef95db69a1f91df24da0923cdf43fd1`。Root125 receipt `b2ac6f6dff997a5ee63e99832622802b798f8847d6bcecb8584371435e6fd190`、访问snapshot `90c498ca1fa83a85eeb07f79221a5580e40d6ce922aa6eb6e9beecc5cdfb9e62`、member metadata `d6dbc6c88bfdf40983fd71388db55f52e8833805ece08cbd1485f044daf76549` 为前次已读证据，本次未重新访问NAS。
