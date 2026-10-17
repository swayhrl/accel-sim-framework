# 发布回读边界

科学内容提交2071c6e58的全部120个小型审查文件已push并fetch-back，逐文件与远端blob核验，HEAD/tree一致、worktree clean，见CONTENT_PUBLICATION_FETCH_BACK.json。

随后仅补充该回执、完成清单、本文和入口README，重建FILES_SHA256.tsv，再次commit、push、fetch-back。最终完整HEAD/tree/文件SHA/clean核验的回执写入独立raw root：

- /workspace/dtc-t1c-holdout-174-v1/FINAL_FETCH_BACK.json
- /workspace/dtc-t1c-holdout-174-v1/FINAL_COMPLETION_AUDIT.json

这两份外部回执绑定最终Git提交，不纳入自身提交的哈希链。COMPLETION_AUDIT.tsv的PUBLISH行分开说明内容回读与最终外部回执；全部Goal完成以这两份真实存在、核验通过的最终回执为准。

原始TERMINAL_ARCHIVE_TERMINAL.json的失败状态不改写；TERMINAL_ARCHIVE_REPAIR_RECEIPT.json和FINAL_CONTRACT_AUDIT.json记录恢复后的确定性身份闭合。没有重新启动模拟点。
