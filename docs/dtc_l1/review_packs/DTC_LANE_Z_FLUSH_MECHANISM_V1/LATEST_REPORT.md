# Lane Z — accepted evidence consumer / K0-K1 preregistration V1

状态：`CPU_CONSUMER_COMPLETE_PREREGISTERED_NO_NEW_SIM`。北京时间2026-10-18在原174容器完成，独立Framework分支 `hrl/iscas2027-dtc-lane-z-mechanism-174-v1`，worktree `/workspace/worktrees/accel-sim-iscas2027-dtc-lane-z-mechanism-174-v1`，基于Lane A `f5c37d6e`。只读消费A `f5c37d6edcce832a72cb0830021bffa78df6cc13`、M `d723784a8b897566b63113f95972f7a8d12a01ce`、T `f520a445436b57c0a0f2494fb858a1636f04d2bc` 的固定Git小证据；未重读旧raw/trace，未启动sim/native任务，未改Core、旧结果、原GM12或v0.13论文。

交付包括 [typed metric dictionary](METRIC_DEFINITIONS.md) 与逐字段 [TSV](METRIC_DEFINITIONS.tsv)、[旧证据表](OLD_ACCEPTED_EVIDENCE.tsv)、[预注册解释模板](PREREGISTERED_INTERPRETATION.md)、[缺失字段](MISSING_FIELDS.md)、[CPU验证](CPU_CONSUMER_VALIDATION.json)、[源blob SHA](SOURCE_BLOBS_SHA256.tsv) 和 [运行身份](INPUT_IDENTITIES.tsv)。来源提取快照保留在 `sources/A|M|T/`，不提交raw日志、trace、binary或build。

旧证据表保留A全部12原输入×5臂（含HOLD和负结果），M九臂及其两条旧DWT2D证据、T全部七点及三个accepted对照。相同UUID在不同来源重复出现是独立来源核对，不是新attempt或可叠加样本。A/M的BICG IO UUID不同，未合并。M的逐kernel cycles按原序保存；T的GEMM单kernel周期与总周期一致，Gaussian多kernel只保留有证据的ordinal/名称，逐核cycle明确UNAVAILABLE。没有从均值占用倒推出仍可查映射、lost-resident数或边界失效数。

已有反向证据完整保留：

| 旧accepted → T1-C | whole-run cycles | ready-to-complete core-cycles/cacheable warp |
|---|---:|---:|
| GEMM | 1,377,919 → 1,071,405 | 7.216094 → 12.391692 |
| Gaussian | 3,798,174 → 3,278,356 | 14.167021 → 17.909476 |

GEMM只有一个kernel，其收益不能来自跨kernel retained mapping。Gaussian的多kernel结果与映射保留解释相容，但当前缺逐地址/代际跨边界关联；两输入全程变快并未令post-ready区间一起变好。BICG旧OO128=47,533,116而C+=25,353,488 cycles；GESUMMV旧IO=193,506,220、OO=142,770,419而C+=99,700,244，负结果未删。T0 GEMM IO128=1,825,655较旧IO256=1,457,468退化也保留；不能据此对OO/C+逐周期因果拆分。

新2×2四格固定为 `C(K0,32×4)`、`C(K0,64×8)`、`C(K1,32×4)`、`C(K1,64×8)`；本次全部NOT_CONSUMED。固定报告同Tag K1/K0、同K 64×8/32×4、乘法交互及描述性加性交互，逐输入与原kernel序报告。没有按负载选择Tag、把旧T当新K0、或将发现集/条件派生/新结果灌入原GM12。新结果推翻旧解释也按同模板完整保留。

CPU验证413项通过；消费表2,790行、typed字段78个，固定源blob40个共1,879,456字节。核对固定来源manifest SHA、UUID/终态strict绑定、M原有序kernel与总周期/指令、outcome/dependency与lower守恒、64SM样本、服务区间恒等式、各均值分母、L2四桶和sector32B payload、DRAM各controller issued-command总和及32B atom换算；T七点natural exit与strict、整数sum及均值、原序逐kernel检查完整性也核对。M有35条原序kernel周期；T四个GEMM点有单kernel周期，另1,530个Gaussian kernel保留原序但周期UNAVAILABLE。`python3 docs/dtc_l1/review_packs/DTC_LANE_Z_FLUSH_MECHANISM_V1/consume_accepted.py --check` 可重现消费输出并检查包内SHA；验证PASS仅覆盖已封存小证据，不冒充本轮重扫raw或新增正确性/PPA验证。

U未被探测或消费，partial BICG cycle读取为0。后续仅在整个授权组自然终态、strict与正式审查包发布后才能消费；本任务不等待或轮询U。X若新增事件计数，须另附默认/有效开关、源码build、hook、clock/reset及边界合同；跨插桩前后不直接混比cycle。未发布字段维持UNAVAILABLE。

包内 `FILES_SHA256.tsv` 覆盖其余全部包文件（不自含）。内容提交的push/fetch-back验证会写入 `CONTENT_PUBLICATION_FETCH_BACK.json`；最终提交/树/远端引用/逐blob/clean验证回执保存在原174 `/workspace/dtc-lane-z-mechanism-174-v1/FINAL_FETCH_BACK.json`，避免提交自身SHA循环依赖。最终以该外部回执核实发布完成。
