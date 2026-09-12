# Lane B Goal — 原生轻量目录与有界选择性采集

Goal：`C15_B_NATIVE_CENSUS_AND_BOUNDED_CAPTURE`。
分支：`hrl/vm-c15-native-capture-v0`。这是唯一允许C15原生GPU任务的lane，不是simulator实验窗口。

## 独立启动

完整读共同合同，完成C15-0.1。马上做C15-0.3能力盘点；不等待A静态库或C回测完成。可用本地锚点先做canary；缺GPU/权重时优先实现导入器、目录与对象schema、选择性采集dry-run和fixture测试。不能把CPU模拟模型调用称为原生GPU结果。

## C15-0.3 / C15-2.1：能力和部署preflight

核验当前GPU UUID/型号/VRAM/权限/已有owner、CUDA/PyTorch/Nsight/NVBit实际可执行版本、本地模型revision/权重完整性和必要库。原有CPU模拟主机可能没有GPU，不能假定截图CPU空闲等于可原生采集。
只有已授权可用GPU、本地完整权重、可支持原dtype/backend时才进入native。记录部署实际后端、量化实现、CUDA Graph、attention kernel选择、TP/PP/EP、KV布局、native或flattened分配、logits_all_tokens/last_token。
A未发布时生成common-schema provisional manifest；A发布后按identity合并，不通过改名掩盖差异。
验证T00/T01/T07/T24。产生`CAPABILITY_MATRIX.tsv`、`DEPLOYMENT_PREFLIGHT.tsv`；任何CPU fallback、silent dtype/backend变化或缺权重的部署拒绝作为原计划运行。

## C15-2.2：低开销采集canary

先极小合成CUDA测试验证Nsight/NVTX关联或既有PyTorch profiler路径，不算真实模型证据。记录profiler开关、capture范围、所有额外配置；Nsight Compute不作为全目录工具。
随后在一个本地真实部署的短scenario验证：无SASS输出、目录含launch+stream+kernel名、可识别重复launch、NVTX/关联ID可追溯CPU模块到GPU事件。CUDA Graph/async关联无法证明时显式降级。
如Nsight不可用可用现有PyTorch profiler；shape/stack只在独立标记pass开启。不得只为完成Goal升级共享运行库。
T07/T08通过后可扩大。输出`PROFILER_CANARY_RECEIPT.json`、`PROFILE_CONFIG.json`、`CAPTURE_OVERHEAD_AUDIT.md`。

## C15-2.3：原生baseline与开销

每新部署先1–2次warmup和3次unprofiled稳定重复，再独立profiling；cold load另计。保存event/wall timing测量定义与同步边界，不能把kernel duration sum当端到端时长。若实现有nondeterminism或变长路由，记录输入/seed和变化，不挑最快一次。
初始工程门：profiling中位wall overhead目标<=10%，>10%先减少指标/缩短独立采样pass并复测；仍高则标`PROFILE_PERTURBED`，可保留语义目录但不能把其时间作为无偏权重。3次不是强统计保证；median/min/max/CV均保存，噪声大在预算内最多补至7次。
T08/T20。产物`NATIVE_BASELINE.tsv`、`PROFILE_OVERHEAD.tsv`。

## C15-2.4：模型/算子/kernel目录

生成data contract中的KERNEL_CATALOG。真实shape来自模块参数/运行hook/可核验kernel接口，不能仅凭名字猜Attention/FFN。fused算子标复合语义，UNKNOWN保留。每次run的launch key包含context/device/stream/launch，不能跨run用序号直接join。
Prefill和Decode分开；decode1与后续少量步分开。核对Attention Projection/FFN/Attention Core/Norm/RoPE/Embedding-Output等存在的类别，不能因为原模型有16层就把新模型也写16层。
验收T01/T08/T15：所有目录event计数回到采集器同源总量；对应关系冲突不晋级；缺shape列出missing_reason。时间覆盖/语义覆盖单列。

## C15-2.5：新对象寿命V2

实现观测型storage/generation/view范围记录，不改变模型分配策略以使记录更漂亮。捕获实际allocation/replace/release证据和stream先后；KV层/step仅在runtime可见时确认。记录tensor view共享和allocator地址复用。
T09必须覆盖：同地址先Weight后Activation、同storage多view、KV grow/replace、未知release、跨stream乱序、旧generation响应。没有可证明事件顺序就`AMBIGUOUS_LIFETIME`，不能假定Python对象析构等于GPU释放。
至少核对一个真实部署中的Weight aliases及logits policy。不可观测部分仍为UNKNOWN，schema工具PASS不等于100%对象分类。历史C12 sidecar保持只读。
产物`OBJECT_LIFETIME_V2.tsv`、`OBJECT_ATTRIBUTION_COVERAGE.tsv`、`LOGITS_POLICY_AUDIT.md`。

## C15-2.6：少量scenario扩展

最多3个本地真实部署。优先已有锚点、较大Dense、结构不同者；缺结构差异部署可以paired quant替换，但说明覆盖缺口。
每部署最多8个轻量状态：B=1的短/中/长上下文×Prefill/Decode，以及中长度较大batch×两阶段。256/2048/8192是候选，按真实支持/预算预先冻结；不支持则明确新scenario ID。decode观察少量后续步不启动长generation。MoE需多个已有合法输入并记录实际专家token分布/active union；无真实router telemetry不使用synthetic均匀分布填充。
T07/T08/T20/T24逐scenario检查；不得将目录采集升级为全模型SASS。产物`SCENARIO_REGISTRY.tsv`和目录分片。

## C15-2.7：先发布目录

尽快commit/push可消费catalog+寿命摘要+开销receipt；不等选择性采集全部完成。大文件留私有scratch，发布小TSV摘要和content hash。C只读导入已发布版本。

## C15-3.4：选区计划（不互等）

优先读取C已发布selector固定commit。若尚未发布，按bootstrap规则选2–4个目标窗口：Weight-heavy Attention projection、FFN、存在的Attention core/KV更新、Embedding/Output，按真实语义/shape确定，不能看未测性能挑点。特殊kernel实现不能被普通层替代。bootstrap结果写`BOOTSTRAP_FIXED_RULE_NOT_SAMPLER_QUALIFIED`。
每窗口保留前置生产者/必要完成边界；此上下文只用于正确输入与原生状态，不声称恢复模拟器状态。target与warmup分别列；依赖无法安全裁剪则放弃该窗口采集，保留目录。
总上限12窗口/部署。初/中/末层+seed内部层是候选来源，不强制所有kernel都采到。缺类别报告`COVERAGE_GAP`，不能为凑12剪掉复杂kernel。
T10/T14/T15：计划固定后hash；测量target不可重复，不能用下一遍run的裸kernel序号无验证地执行。

## C15-3.5：选择性capture canary

验证实际NVBit/tracer支持的DYNAMIC_KERNEL_RANGE/区域过滤，而不是只读README。极小fixture先证明：选择内有trace、选择外无SASS、stats.csv/embedded header和kernel list一致。
真实capture先一个小窗口，在第二次执行核对语义、shape、dtype、grid/block、stream和input revision。身份漂移先重建选择绑定再运行；不能把filtered wrong kernel当目标。
T10/T11/T21/T24；max4GiB/20min，监视未压缩增长率，超限只保留partial、不输出完整指纹。压缩后的体积不能掩盖解压成本。

## C15-3.6：预算内capture与提取

通过canary后逐窗口运行，每GPU仅1个采集器。本轮不写新GPU端采样器，不裁CTA做timing，不强制巨型kernel691重新全采。已有hash-identical地址扫描产物直接复用；新巨型kernel超预算则目录/shape保留，升级申请。
原始trace+sidecar+manifest不可覆盖；每窗口自然terminal与过滤身份闭合后才发表。C尚未发布指纹库时先输出捕获receipt和目录，不自写不一致字段；可用固定版本C读取器在自己的输出目录解析。
产物`CAPTURE_MANIFEST.tsv`、`CAPTURE_STATUS.tsv`、`TRACE_INPUT_RECEIPTS.tsv`、小型特征摘要。

## 故障与终态

无GPU/模型：schema/导入器/dry-run/所有fixture继续，并从冻结C12 trace header导入`TRACE_HEADER_ONLY`目录；native durations为NA。结果明确`CAPABILITY_LIMITED`，不能伪造三部署动态覆盖。
有GPU但未达3部署/8scenario/12窗口：这些是预算上限，不是完成指标；按已冻结覆盖计划及缺口评价。预算用尽后完成验证和handoff，不扩时间/磁盘/下载范围。
最终报告区分：真实新native、历史native、header-only、synthetic fixture各有多少；哪些窗口合法；成本多少；C可消费的commit/hash；哪些需要新授权。所有代码和结果只push B分支。
