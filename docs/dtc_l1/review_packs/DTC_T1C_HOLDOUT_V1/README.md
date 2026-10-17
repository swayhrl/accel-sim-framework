# DTC_T1C_HOLDOUT_174_V1

用户批准的固定T1-C独立验证：DWT2D先行，strict通过后BICG；最多两个新attempt、最多1个并行，无性能选点或新机制。

授权全文见AUTHORIZATION.md。预注册PRE_REGISTRATION.tsv、SOURCE_INPUT_IDENTITY.json、CONTROLLED_DELTA.tsv、ORDERED_KERNELS.json、POLICY.json和PREREG_FILES_SHA256.tsv须在任何新性能出现前commit/push/fetch-back。资源暂不满足则等待；未知DTC authority、科学身份/输入/配置不闭合则STOP。

输入采用Lane A已验完整原trace和12条CPU body证明，不重扫629成员。原A/M/T和旧raw只读。最终交付FULL_MATRIX.tsv、TERMINAL_MECHANISM_COMPARISON.tsv、STRICT_AUDIT.json、EXECUTION_RESOURCES.tsv、SCIENTIFIC_SCOPE.md、LATEST_REPORT.md、FILES_SHA256.tsv以及run_receipts/、strict/。raw位于原174 /workspace/dtc-t1c-holdout-174-v1。
