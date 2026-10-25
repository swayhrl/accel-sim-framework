旧 GESUMMV CH 的 metadata 闭合准备

对象为 `E2-AEV100-769e6d9fd5f9cd53-CH`，原 UUID `0b3b03d2-1cfd-46d2-adc8-721c5e51c4f2`。原模型已退出，INTENT、DONE、NATIVE_EXIT、registry execution_receipt 一致。旧 RESULT 的实际错误为 `AssertionError('not a reviewed closed failure signature')`：冻结的 runtime_assert → telemetry → host → cap1m 链遗漏 expected_growth 资源停止类型。

独立 review 绑定已发布 `587c163ec312d3a5abdc3c392db03048e99fa747` 的逐点诊断，再重读原始证据。938 个 outer sample 仅最后一个 physical_disk_pass=false，physical_RAM_pass 始终为 true；最后 BA 的唯一 STOP 原因为 CURRENT_GUARD:expected_growth，host 与 cgroup 域均 CONTINUE。实际 free=40,906,543,104 bytes，required=40,914,488,049 bytes，差 7,944,945 bytes（约 7.58 MiB）。原 8.125 GiB peer ceiling 是当时的真实采样值；后来 metadata 核减不能改变该历史采样。961 条连续 progress 及最终 SIGTERM 已核对，raw 双 SHA 一致。此结果只能闭合 UNACCEPTED，accepted_cycles=null。

当前核验时，本点 local ARCHIVE_RECEIPT 与 164 cohort 目录均不存在。本轮没有 COPY、restore、模型、信号、authority 或 out 写入。CPU 资格共 28 项通过；未来 apply 的新归档、既有归档复核、错 plan/publication、receiver HOLD、坏 restore 和重复闭合分支均只在独立 fakeRoot 执行。

Root 后续具体执行步骤：

1. 发布本工具、CPU driver、只读 review plan、资格与本说明，完成全字节 readback。新 publication receipt 提供 verified、commit、tool_sha256、qualification_sha256。
2. 具体授权后运行 `review_gesummv_expected_growth_v1.py --apply --plan <GESUMMV_EXPECTED_GROWTH_READ_ONLY_REVIEW_PLAN_V1.json> --publication <新publication receipt>`。工具重新完整核验，要求 plan 未漂移。
3. 若归档仍不存在，仅调用已 pinned 的原 `sweep_outbox.py` COPY 到真实 164，并独立核验 archive 与 native_restore。遇 receiver/resource HOLD 则退出，不制造 POSTPROCESS 或新模型。若归档已存在，仅独立 verify，避免重复 COPY。
4. 完成后在 `FIX/analysis/gesummv_expected_growth_metadata_closure_v1/<原UUID>/` 保存旧 ENGINEERING RESULT 的字节前像、REVIEW 与独立 POSTPROCESS.RESULT.json。原 RESULT、NATIVE_EXIT、DONE、科研账本和预算均保留。

报告全部放在原 out 之外。归档前后验证原 source manifest 一致，不向已归档 out 追加任何分类文件。该独立 closure 不覆盖运行中 R16 的 frozen classifier 或内部 results；Root 的全失败证据汇总应显式引用此 POSTPROCESS。新 repair 验证点与旧 negative 保持独立身份。
