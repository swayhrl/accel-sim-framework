# 两个原attempt的observer /proc收尾异常取证

只读完整检查历史INTENT、launch/PID、raw、progress/resource、strace及现行registry。原charged=1和UUID不变；原矩阵仍不完整。

## cfd DM

- cohort：`E2-AEV100-85700545918390d7-DM`；UUID：`97c43b01-9628-490f-839e-4a2a8126122e`。
- 原错误：`CalledProcessError(2, ['/root/data/ep_l2_dtc_l1_native_v2/bin/experiment', 'run-native', 'E2-AEV100-85700545918390d7-DM', '--project', 'DTC_L1'], '', '{"status": "HOLD", "reason": "[Errno 2] No such file or directory: \'/proc/1263485/stat\'", "error_type": "FileNotFoundError", "errno": 2, "model_retry": false}\n')`。
- 已记录progress 220条，末completed=341281796，end=NONE；没有已捕获NATURAL。
- raw最后输出simulation thread exiting / exit detected；人口终值吻合不构成科学PASS。
- strace：`exit_group(0)且明确+++exited with0+++`。这不等于frontend p.wait返回码。
- 当前模型与strace launcher generation均已消失。2个额外send成功但未进入progress；payload截断，不能补造NATURAL。
- 原NATIVE_EXIT / DONE / SCIENCE_QUALIFICATION缺失；保留UNACCEPTED、SOURCE_KEEP，accepted_cycles=null。

## b+tree DM

- cohort：`E2-AEV100-e7c791ce2e4b09ee-DM`；UUID：`f6c79f5f-6b0e-42d7-a5be-c3013fa7aaba`。
- 原错误：`CalledProcessError(2, ['/root/data/ep_l2_dtc_l1_native_v2/bin/experiment', 'run-native', 'E2-AEV100-e7c791ce2e4b09ee-DM', '--project', 'DTC_L1'], '', '{"status": "HOLD", "reason": "[Errno 2] No such file or directory: \'/proc/1270448/exe\'", "error_type": "FileNotFoundError", "errno": 2, "model_retry": false}\n')`。
- 已记录progress 99条，末completed=441924205，end=NONE；没有已捕获NATURAL。
- raw最后输出simulation thread exiting / exit detected；人口终值吻合不构成科学PASS。
- strace：`仅exit_group(0)，末尾没有+++exited+++确认`。这不等于frontend p.wait返回码。
- 当前模型与strace launcher generation均已消失。2个额外send成功但未进入progress；payload截断，不能补造NATURAL。
- 原NATIVE_EXIT / DONE / SCIENCE_QUALIFICATION缺失；保留UNACCEPTED、SOURCE_KEEP，accepted_cycles=null。

R13可依据本独立工程disposition跳过等待这些旧点的缺失回执，继续派发从未启动的点。不得用本报告填旧DONE/EXIT、refund或标PASS，也不得因此宣称288点原矩阵闭合。新repair验证为独立请求/UUID，不覆盖或清零原attempt。

详见同目录JSON的逐文件SHA、末行、真实exit证据、资源记录、现行PID检查与因果边界。
