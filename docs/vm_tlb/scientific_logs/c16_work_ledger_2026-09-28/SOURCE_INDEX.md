# 审查来源索引

日期：2026-09-28。除H0/B0/C0外，仓库均为 `swayhrl/accel-sim-framework`。

本索引记录的是本次文档审查读到的证据，不表示再次执行原实验或重新校验node164全部raw。`ref`为commit时可直接用`git show <ref>:<path>`；`ref`为branch时，同时保存读取到的Git blob SHA，避免把未来branch变化误当成本次证据。Git blob SHA不是SHA256，不能混用。

`READ`：本轮直接读取对应文件；`FROZEN_HANDOFF`：读取用户提供的冻结交接；`PRIOR_REVIEW`：沿用此前已读且已审的明确交付；`INVENTORY`：只证明分支存在；`PENDING`：聊天已下发但本轮未见终局交付。任何一种都不是本轮重新跑出的实验结果。

## 冻结交接与枚举

- **H0 / FROZEN_HANDOFF**：`C16_AI_WORKLOAD_HANDOFF_CONTEXT_2026-09-27_M1F_READY_LANE4_RUNNING.md`；用户上传的完整交接。文件SHA256：`b42209ea223817410c215ab90c93619ab21d7ca62435cec5c3838a3d55f59c71`。本轮使用§4–15及运行/解释边界；其中旧partial进度不更新为当前进度。
- **B0 / INVENTORY**：GitHub `search_branches(query=c16,page_size=100)`；Framework分页100+100+82+空页，Core为9条。全名保存在`BRANCH_INVENTORY.txt`。282+9是分支数，不是实验数；没有逐个分支执行代码审计。
- **C0 / PENDING**：本对话下发的 `C16_MOE_TEMPORAL_PERIODICITY_POSTHOC_AUDIT_V1`。本轮确认Lane 6主分支仍为`0017527afba6861a4a0cfee95cce7b2a0397f284`；未见该post-hoc任务的独立终局报告，不登记为已完成。

## 历史平台、输入、trace与模型

| ID | ref | 文件（相对仓库根） | 读取blob SHA | 深度 |
|---|---|---|---|---|
| S01 | a402828860ced26124ddbf3c9d87baa6f6774d55 | docs/vm_tlb/review_packs/C16_E1_PAPER_EVIDENCE_AND_RESULT_INFRASTRUCTURE_V1/C16_E1_EVIDENCE_LEDGER.md | e849987dad060005679beb4b0efa0f053db74fdd | READ，已冻结证据账本，不代替底层raw |
| S02 | hrl/c16-moe-scientific-log-v2 | docs/vm_tlb/scientific_logs/C16_MOE_EXPLORATION_LOG.md | 4e9a08a4f6b8bd7cdbbc630bbe9534eced9c9226 | READ，历史MoE账本；E3状态存在时效问题 |
| S03 | hrl/c16-4080-r5-evidence-closeout-r6-fix | docs/vm_tlb/review_packs/C16_4080_U5_U9_R5_CLEAN/README.md | 763654d34a23a7d85f3c901ef353ca0dede9b88e | READ，明确R4定量数据排除；未复验旧raw |
| S04 | hrl/c16-data-pipeline-v1-integration-174new-r1 | docs/vm_tlb/review_packs/C16_DATA_PIPELINE_V1_END_TO_END_R1/README.md | 275a1e6ed2d94e68150185b369ab44dc5b92f464 | READ，synthetic pipeline与归档，不是GPU性能结果 |
| S05 | hrl/c16-qwen0-decode-analysis-174new-v4 | docs/vm_tlb/review_packs/C16_QWEN0_DECODE_ANALYSIS_174NEW_V4/FINAL_DECISION.json | 2f6ce697588c11fd7ab54d71446ca2cc99442c81 | READ |
| S06 | hrl/c16-ldgsts-special-path-109-v5 | docs/vm_tlb/review_packs/C16_LDGSTS_SPECIAL_PATH_109_V5/FINAL_DECISION.json | c7b55eb62da205ca63f0ed9477dbdb786a05cc13 | READ |
| S07 | hrl/c16-qwen25-7b-awq-fused-109-v6 | docs/vm_tlb/review_packs/C16_QWEN25_7B_AWQ_FUSED_109_V6/FINAL_DECISION.json | c6f4ebb3d889c6210ab6d64621ca98a1460d2b76 | READ |
| S08 | hrl/c16-qwen25-7b-awq-characterization-109-v7 | docs/vm_tlb/review_packs/C16_QWEN25_7B_AWQ_CHARACTERIZATION_109_V7/FINAL_DECISION.json | 7a574ffc36a0e1b6e7d2501c64eaa0d5242ac0b5 | READ |
| S09 | hrl/c16-qwen25-7b-pair-closure-109-v10 | docs/vm_tlb/review_packs/C16_QWEN25_7B_PAIR_CLOSURE_109_V10/FINAL_DECISION.json | a3d2aa7bdd8099f9f8f794eb064e2882f65f103b | READ |
| S10 | hrl/c16-unified-consumer-174new-v11 | docs/vm_tlb/review_packs/C16_UNIFIED_CONSUMER_174NEW_V11/FINAL_DECISION.json | 5ae16acdaebd9bca55726d17085ad3365e5f3d66 | READ，仅当时状态 |
| S11 | hrl/c16-qwen3-consumer-174new-v16 | docs/vm_tlb/review_packs/C16_QWEN3_CONSUMER_174NEW_V16/FINAL_DECISION.json | 5273efcff92f452e9bbfdc78f990987af24b2b52 | READ，简短终局标签 |
| S12 | hrl/c16-qwen3-cross-lineage-174new-v17 | docs/vm_tlb/review_packs/C16_QWEN3_CROSS_LINEAGE_174NEW_V17/FINAL_DECISION.json | 3e6e6d5bc9c3de6f0120ac52f503f361f51fe11a | READ，简短终局标签 |
| S13 | hrl/c16-qwen3-attention-kv-consumer-174new-v19 | docs/vm_tlb/review_packs/C16_QWEN3_ATTENTION_KV_CONSUMER_174NEW_V19/FINAL_DECISION.json | d71dec1957d7f8cc95715c4c65d9c8823b13c9af | READ |
| S13a | hrl/c16-qwen3-attention-kv-consumer-174new-v19 | docs/vm_tlb/review_packs/C16_QWEN3_ATTENTION_KV_CONSUMER_174NEW_V19/V18R2_INDEPENDENT_AUDIT.json | d73ae14d6d83bd0b616ce4a457dc170f93ad2731 | READ，160静态路径/8执行/152零/2048事件 |
| S14 | hrl/c16-deepseek-v2-lite-persistent-mla-109-v26 | docs/vm_tlb/review_packs/C16_DEEPSEEK_V2_LITE_PERSISTENT_MLA_109_V26/FINAL_DECISION.json | ade46079b488f37bdce536ee6fd48aa34fc65d27 | READ |
| S15 | hrl/c16-deepseek-v2-lite-s3-mixed-qk-109-v27 | docs/vm_tlb/review_packs/C16_DEEPSEEK_V2_LITE_S3_MIXED_QK_109_V27/FINAL_DECISION.json | 8b3029f4643ce8bac99e2428dc54cba8bcfc8d01 | READ |
| S16 | hrl/c16-deepseek-s2-s3-consumer-174new-v30 | docs/vm_tlb/review_packs/C16_DEEPSEEK_S2_S3_CONSUMER_174NEW_V30/FINAL_DECISION.json | 70a77b0eb5b4b6923407f54d65fda988f6fda657 | READ，简短终局标签 |
| S17 | hrl/c16-gpt-oss-20b-s2-producer-109-v29 | docs/vm_tlb/review_packs/C16_GPT_OSS_20B_S2_PRODUCER_109_V29/FINAL_DECISION.json | 7ab36eb9cfbc5735a1e76eca31b2cbffb75d8204 | READ，native MXFP4/SM89 blocker |
| S18 | hrl/c16-olmoe-s2-producer-109-v32 | docs/vm_tlb/review_packs/C16_OLMOE_S2_PRODUCER_109_V32/FINAL_DECISION.json | d4bd6c37301ed2c3a18f2ebaf36337fbe0cc8098 | READ |
| S19 | ab26365dc663268b0799818db6687ed466e8c925 | docs/vm_tlb/review_packs/C16_OLMOE_S2_PRODUCER_109_V34/FINAL_DECISION.json | 70f82e2f4b79208fb2e923b8d355abc7ddc8f297 | READ |
| S20 | hrl/c16-olmoe-static-audit-formal-109-v35 | docs/vm_tlb/review_packs/C16_OLMOE_STATIC_AUDIT_FORMAL_109_V35/FINAL_DECISION.json | cdba5eebff343e4770f53fe7aeedcd20700cd88f | READ |
| S21 | hrl/c16-olmoe-nvbit-jit-selector-formal-109-v36 | docs/vm_tlb/review_packs/C16_OLMOE_NVBIT_JIT_SELECTOR_FORMAL_109_V36/FINAL_DECISION.json | 3dd0c4d7318e30e71fe1834c8e42553fb323d11c | READ |
| S22 | hrl/c16-olmoe-variant-aware-formal-109-v37 | docs/vm_tlb/review_packs/C16_OLMOE_VARIANT_AWARE_FORMAL_109_V37/FINAL_DECISION.json | 46a7adddec89c9bd60328ac3679095a1901a7e48 | READ |
| S23 | hrl/c16-olmoe-variant-a-formal-109-v38 | docs/vm_tlb/review_packs/C16_OLMOE_VARIANT_A_FORMAL_109_V38/FINAL_DECISION.json | a63bead9abf3972525991c1f1aa03343633f174f | READ |
| S24 | 85563ec6f55a0ad743d21483aa49c24fdb5cf3bf | docs/vm_tlb/review_packs/C16_OLMOE_V40_FORMAL_ADMISSION_174NEW_V1/corrected_fc0f3cf67edf/FINAL_AUTHORITY_DECISION.md | 8ed41d6475c972223d135124e20fa96d0ed4ad12 | READ |
| S25 | 378487015e513ed666c0929ca3f6c00392ff11c3 | docs/vm_tlb/review_packs/C16_E3_Q30_ROUTING_DIAGNOSTIC_109_V1/SCIENTIFIC_INTERPRETATION.md | a5d22285732fe33fb33bd2d183f1aaa499d41cae | READ，覆盖旧MoE日志的E3待执行状态 |

## E1主线、模拟器准备与新探索

| ID | ref | 文件（相对仓库根） | 读取blob SHA | 深度 |
|---|---|---|---|---|
| S26 | 59ddb8ba2a33ef12b73bfc859f3a994e0b4ef4ca | docs/vm_tlb/review_packs/C16_E1_CLEAN_BASELINE_CONSUMER_174NEW_V1/FINAL_DECISION.json | e63916411fe0f2025f7c0b822fe987dad8d5cb41 | READ；完整执行背景另见H0/S01 |
| S27 | cdd3ec7afbb1611cc52a4b74d32b38a3edabd131 | docs/vm_tlb/review_packs/C16_E1_SEMANTIC_NCU_V2_CONSUMER_174NEW_V1/FINAL_DECISION.json | 1c7a2897e363f1ddab7b80edfd0bce37f706dba7 | READ |
| S28 | 5b11dd41e98044fcad76da4a906c7ba8609eb828 | docs/vm_tlb/review_packs/C16_E1_RESIDENCY_INTERVENTION_CONSUMER_174NEW_V1/FINAL_DECISION.json | ca79194011b05e95e02c10d31d517e18eb8f58fd | READ |
| S29 | 4f9242d177220721cb9e669aad5dd9e29f04407d | docs/vm_tlb/review_packs/C16_E1_NATURAL_REUSE_RESIDENCY_CONSUMER_174NEW_V1/FINAL_DECISION.json | 5f246eb051c533199675c1af3f8cfd7d4f1b60c4 | READ |
| S30 | 1dcab9c8d932973399c5811dc817802bfb3b9dfe | docs/vm_tlb/review_packs/C16_E1_L2_PERSISTENCE_INTERVENTION_CONSUMER_174NEW_V1/FINAL_DECISION.json | ab7b1a747139124bbdab35da258e1d50b8699ff7 | READ，保留producer/consumer规则分歧 |
| S31 | 5481d85951180dae90776442c3e0620af96a4712 | docs/vm_tlb/review_packs/C16_E1_SHARED_RESIDENCY_DESIGN_REVIEW_174NEW_V1/FINAL_DESIGN_REVIEW.json | d8d1476fc398c6eb55253f3fea3365759993458c | READ |
| S32 | eb4e737e24c27d1908a2fdf43f465ed5e0cfc66f | docs/vm_tlb/review_packs/C16_E1_COVERAGE_SCALING_CONSUMER_174NEW_V1/FINAL_DECISION.json | 13cb5351b881b1cd9a70f186b1517f7c40bd917c | READ |
| S33 | 278964bfb243a93adf43e748eb3e067e34b16b8a | docs/vm_tlb/review_packs/C16_E1_OPERATOR_FAMILY_EXPANSION_CONSUMER_174NEW_V1/FINAL_DECISION.json | 05d09f57ceb23c5870e7b18969bf75474af04f9a | READ |
| S34 | 0ccd19d4511e8d55c31eb9d8899d33c35da8778c | docs/vm_tlb/review_packs/C16_E1_RESIDENCY_COST_BENEFIT_CLOSURE_CONSUMER_174NEW_V1/FINAL_DECISION.json | 778609653d6a7498b04c70b8297a1848a3cd40e2 | READ |
| S34a | 0ccd19d4511e8d55c31eb9d8899d33c35da8778c | docs/vm_tlb/review_packs/C16_E1_RESIDENCY_COST_BENEFIT_CLOSURE_CONSUMER_174NEW_V1/SCIENTIFIC_INTERPRETATION.md | 9e539efe77db8013f7cee1ec54af5679289723e8 | READ，aggregate attention与代表kernel的区别 |
| S35 | 7d458d789975ac4ac2999c4e7d7624064ba96d66 | docs/vm_tlb/review_packs/C16_GPGPUSIM_HOST_ACCELERATION_QUALIFICATION_V1/QUALIFICATION.json | 9c55a7700c5ad4fdfa739861229180a1f79059cd | READ |
| S35a | 7d458d789975ac4ac2999c4e7d7624064ba96d66 | docs/vm_tlb/review_packs/C16_GPGPUSIM_HOST_ACCELERATION_QUALIFICATION_V1/CANDIDATES.tsv | 55d9d499f4ece4658dd93d3a87dac220db4f3a90 | READ，原表整组行重复，账本只计一组 |
| S35b | 7d458d789975ac4ac2999c4e7d7624064ba96d66 | docs/vm_tlb/review_packs/C16_GPGPUSIM_HOST_ACCELERATION_QUALIFICATION_V1/README.md | e608a87e7534c07afca7d7e34cf4439a3de5577e | READ，16-kernel prefix未包含completed target |
| S36 | 013370ec4a0f37fcba2b2bd4329048c8113a30a3 | docs/vm_tlb/review_packs/C16_E1_STRONG_BASELINES_AND_SURVIVAL_OBSERVER_CLOSEOUT_174NEW_V1/README.md | 19e744cbf63d71145f972bdc4b03cfe1dc7d49f7 | READ；代码细节资格沿用已审交付，不在本轮重跑 |
| S37 | 4f45bf0aaec0d0fb63fb39adb835f89dcf5da1ef | docs/vm_tlb/review_packs/C16_E1_PAPER_BASELINE_TERMINAL_REVIEW_PREP_V1/README.md | b85ccc064a01cf3c93b50ad5fe2ea60c9fe18e2a | READ；binary精确gate修复沿用已审交付 |
| S38 | dc41de767b55f3ba1532627f1cb5dc176ea539ee | docs/vm_tlb/literature_notes/c16/README.md | 12e3aad73f02070f8af66dc79fa14061501199cd | READ；各轮论文阅读深度按原笔记，不作新外部检索 |
| S39 | dcbd60f98753ec678642bd4be745469409ffb734 | docs/vm_tlb/review_packs/C16_LOWBIT_DATAFLOW_SCREEN_V1/HYPOTHESIS_SCREEN.md | NOT_REHASHED_THIS_PASS | PRIOR_REVIEW；另有DATAFLOW_EVIDENCE.tsv和MINIMAL_NATIVE_AB_PLAN.md |
| S40 | 0017527afba6861a4a0cfee95cce7b2a0397f284 | docs/vm_tlb/review_packs/C16_MOE_TEMPORAL_ROUTING_AUTHORITY_SCREEN_V1/FINAL_DECISION.json | dfe4185da21209658884ff2f2071d3fcb5d92d79 | READ；本轮branch与该commit仍identical |
| S41 | 0e88faa28c9066b48e394dce657d7a16e6332a32 | docs/vm_tlb/review_packs/C16_LOWBIT_SPLITK_NATIVE_AB_109_V1/FINAL_DECISION.json | ea06c0c2fca0e47b68361a03d2fac6b1bb6ec8bb | READ |
| S41a | 0e88faa28c9066b48e394dce657d7a16e6332a32 | docs/vm_tlb/review_packs/C16_LOWBIT_SPLITK_NATIVE_AB_109_V1/TIMING_SUMMARY.tsv | a142a23799902a5964ae32db9affe3c283078443 | READ；没有重新计时或重新跑NCU |

## 本轮没有完成的审查深度

早期3090/AutoDL/retry570的每次局部运行、迁移各R版本、每个coordination分支、Qwen3 S3 V20/V21全部底层产物，不在本轮逐文件重算覆盖内。分支已枚举，不据分支名虚构结果。若未来需要其数值作论文证据，应回对应producer/consumer及raw单独复核。

部分阶段不存在统一命名的`FINAL_DECISION.json`或`SCIENTIFIC_INTERPRETATION.md`。本轮对404路径继续使用实际目录定位，不能将“某个猜测文件名404”解释为“实验未做”。例如host acceleration实际权威文件名是`QUALIFICATION.json`。
