# C15 data contract — V1

本合同供A/B/C独立实现读取器。Canonical交换格式为UTF-8 TSV及JSON/JSONL；Parquet是可选大表镜像，不能因缺pyarrow停工。TSV缺失数值写`NA`，JSON写null，同时提供`missing_reason`；禁止空缺转0。所有计数用足够宽的整数，不经过float再存回。字节为B，KiB=1024B；秒、native GPU ns、simulated cycles、CPU core-hours分开。

## 1. Common identity and provenance

每份表通过同目录manifest关联：`schema_version, planning_sha, producer_lane, producer_source_sha, run_id, input_manifest_sha256, evidence_tier, metric_scope, capture_state, status`。

`deployment_id = sha256(canonical_json(identity_fields))`。身份字段为模型repo/revision、实现及版本、三个dtype/量化配置、硬件型号/ISA、phase-independent部署并行和layout模式；运行时间戳/本地路径不参与。`scenario_id`再加入phase、context、batch、生成步计划、KV state、logits policy。未确认identity不得与已确认部署自动合并；使用provisional ID且标`IDENTITY_UNRESOLVED`。

设备原生profile和模拟结构是不同身份：不能拿H100时间当V100模拟cycle权重而不说明。固定实验代码/依赖、输入prompt来源/hash、seed、tokenizer revision。不把私有prompt、token或凭据提交Git。

## 2. Minimum tables

### ASSET_INVENTORY.tsv — A

`asset_id, asset_kind, discovered_path_or_ref, model_id, revision, phase, dtype, framework, hardware_scope, availability, source_commit, hash_kind, sha256, size_bytes, readonly, missing_reason`。

路径只说明位置，不作为身份。先读轻量manifest和缓存索引，不全盘递归、不全量读所有trace。已有hash可复用时核对文件stat与source证据，不能把未重hash宣称成新hash校验。

### MODEL_REGISTRY.tsv / DEPLOYMENT_MANIFEST.json — A；B可产生provisional补充

`model_id, revision, deployment_id, dense_or_moe, attention_representation, layer_count, hidden_size, intermediate_sizes, head_dimensions, local_kv_heads, expert_count, top_k, shared_experts, weight_dtype, activation_dtype, kv_dtype, quantization_method, quant_group_size, tying_status, tensor_parallel, pipeline_parallel, expert_parallel, rank, kv_layout, allocation_mode, logits_policy, implementation_identity, native_hardware, fields_verified, readiness_tier`。

混合结构须保留per-layer表，不能强填单一标量。MLA/未知表示不套标准KV公式；TP下KV头是否复制必须实际核验。

### TENSOR_STORAGE_CATALOG.tsv — A

`deployment_id, shard, tensor_name, logical_shape_json, stored_shape_json, storage_dtype, role, disk_data_start, disk_data_end, stored_bytes, semantic_alias_group, storage_dedup_basis, source_hash, status`。

磁盘offset不是VA/PA。若header不能证明共享实际存储，tying只作为语义声明，不随意扣除bytes。量化payload、scale、zero、padding、runtime repack分开；未知runtime storage不填0。

### STATIC_FOOTPRINT.tsv — A

`deployment_id, scenario_id, object_kind, layer_or_expert_scope, quantity, value, unit, formula_id, assumptions_json, page_granule_bytes, evidence_tier, missing_reason`。

至少区分`allocated_payload_bytes`、`reserved_bytes`、`active_parameter_estimate`、`scenario_page_count`。4KiB/64KiB/2MiB只是粒度情景。对已知区间[a,a+s)用floor((a+s-1)/P)-floor(a/P)+1；未知地址只给对齐假设及上下界，不把ceil(total_bytes/P)说成精确多allocation页数。

### KERNEL_CATALOG.tsv — B

`deployment_id, scenario_id, run_id, phase, request_id, token_step, rank, device_id, context_id, stream_id, launch_id, correlation_id, module_path, layer_id, operator_class, semantic_evidence, kernel_name, implementation_id, shape_json, strides_json, dtype, grid_json, block_json, smem_bytes, start_ns, end_ns, duration_ns, object_storage_ids, allocation_epochs, capture_state, catalog_origin, missing_reason`。

`catalog_origin=NATIVE_NEW/NATIVE_HISTORICAL/TRACE_HEADER_ONLY`互斥；trace header没有native时间就不能伪装原生目录。launch_id仅在单次run中唯一，第二遍采集依赖语义/shape/stream/NVTX关联核验。并发期间时间和不能当makespan。

### OBJECT_LIFETIME_V2.tsv — B

`run_id, storage_id, allocation_generation, device_id, context_id, address_namespace, base, extent, view_offset, view_extent, object_kind, semantic_name, allocation_event, replace_event, release_event, event_order_basis, stream_id, lifetime_certainty, alias_group, source_evidence`。

object_kind：`WEIGHT/KV_CACHE/ACTIVATION/WORKSPACE/UNKNOWN`；不能确认生命周期/跨stream先后时`AMBIGUOUS_LIFETIME`，保守统计而非强分类。地址复用必须新generation；合法tensor view共享同storage ID，不能重复算分配容量。新V2不回写历史sidecar。

### SAMPLE_PLAN.tsv — C；B bootstrap使用同schema

`plan_id, selector_sha, deployment_id, scenario_id, stratum_id, semantic_key_json, implementation_key, shape_regime, selection_reason, sampling_unit, target_launch_signature, target_indices, warmup_indices, weight, weight_basis, inclusion_probability, seed, split_role, expected_capture_bytes, execution_scope, eligibility_status`。

`split_role=TRAIN/RETROSPECTIVE_TEST/PROSPECTIVE_HOLDOUT/ORACLE_DIAGNOSTIC`。确定性代表点的inclusion_probability为NA，禁止声称无偏。目标测量kernel不得双计；被其他窗口用作warmup时仅计成本，不重复计测量值。

### FINGERPRINTS.tsv — C（B可用C固定版本生成）

`deployment_id, scenario_id, sample_id, object_kind, metric, value, unit, numerator, denominator, evidence_tier, metric_scope, address_namespace, page_or_line_bytes, order_model, sm_mapping, initial_state, estimator_id, sampling_fraction, seed, error_bound, missing_reason, source_receipt`。

基础指标：refs、requested bytes、读写比例、unique页/行、每页/行触及字节范围、窗口重访/跨窗口并集交集、range长度/fragment count。对象统计必须有UNKNOWN/AMBIGUOUS行。跨页/跨行访问按完整宽度处理，不能只用首地址。inactive lanes不计；atomic单列，不能静默当普通读或读写两次。

`order_model`取`SET_ONLY/PROVEN_WARP_ORDER/DECLARED_SYNTHETIC_INTERLEAVING/SIMULATED_EVENT_ORDER/UNKNOWN`。没有真实顺序时集合可精确，但全GPUreuse distance不精确。无SM映射时不得输出真实私有L1 MRC。tag-only曲线必须填capacity/assoc/replacement/filter/warmup，标`CONTROLLED_TAG_ONLY_PROXY`。

### SAMPLING_COVERAGE.tsv — C

`plan_id, universe_hash, basis, stratum, total_mass, represented_stratum_mass, actually_sampled_mass, represented_fraction, sampled_fraction, missing_categories, audited_tail_fraction, status`。

95%目标指有可核验代表的类别覆盖质量，不等于95%都被trace；同时列真实采样质量。若所有类别都被定义进strata，represented=100%也不证明误差小，必须额外看holdout。

### Error and cross-config tables — C

`plan_id, split_id, source_roi, reference_arm, candidate_arm, metric, reference_value, estimate, absolute_error, relative_error, percentage_point_error, interval_kind, interval_low, interval_high, effect_reference, effect_estimate, effect_resolution, prediction_verdict, validation_verdict, test_set_previously_seen, scope`。

count/rate/cycle/sign分开；分母为0时标undefined。已知真实delta的回测可以报告符号命中，但部署到未知场景时不允许用该真实值帮助选择。

### COST_LEDGER.tsv — all lanes

`work_id, parent_work_id, lane, stage_id, attempt, operation, start_utc, end_utc, wall_s, cpu_core_s, gpu_active_s, peak_rss_B, peak_vram_B, bytes_read, bytes_downloaded, bytes_written, warmup_s, retry_s, measured_or_estimated, result_status`。

嵌套parent只汇总不重复加子任务；历史成本缺失为NA。不得用“采了1/10 kernel”推导“总成本省10倍”。

### UPGRADE_DECISIONS.tsv — A integration / C

`deployment_id, compared_class, known_dimensions, novel_dimensions, uncertainty, audit_window_evidence, decision, reason, proposed_next_scope, expected_cost, requires_new_authorization`。

决定：`KNOWN_CLASS_PROFILED/CHARACTERIZED_NOT_TIMING_VALIDATED/STATIC_ONLY/NEEDS_T2_AUDIT/PROPOSE_T3/INCONCLUSIVE`。本轮所有T3申请`requires_new_authorization=true`。

## 3. Evidence tiers and limits

沿用审定设计：`STATIC_DERIVED/NATIVE_PROFILED/TRACE_DERIVED_EXACT/SAMPLED_ESTIMATE/CONTROLLED_TAG_ONLY_PROXY/SIMULATED_CONTEXT_WINDOW/FULL_ROI_VALIDATED/UNRESOLVED`。

后两种模拟标签在本轮只能引用已有freeze来源，不产生新回放。来源为完整模拟，不代表样本加权估计也是FULL_ROI_VALIDATED。

## 4. Publication validation

所有publish表验证：唯一主键、必需列、单位、缺失原因、范围合法、引用hash存在、无secret、无被作废C13 ID。实现无新第三方包依赖的最小schema checker；Parquet镜像与TSV抽查逐值一致。fixture结果必须`SYNTHETIC_TEST_ONLY`且目录隔离，不能进入研究结果库。
