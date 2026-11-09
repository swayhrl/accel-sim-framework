# EP-L2 optional CLEAN128 exact5：授权后执行检查点

时间：2026-11-09 12:03 UTC 之后。唯一 Main：本 EP-L2 API 会话。

## 授权和现场

用户已明确批准 `EP_L2_OPTIONAL_CLEAN128_EXACT5_EXECUTION_V1`：GEMM EXT0/1/2、Stencil EXT0/2，各一次。授权原文 SHA256：`900e9b6b1a31f1a9f3b8dd13c7e4580df415f27af3acc5727e59d930b7d7efc0`。上一接管回执提交 `eb41e43b814d5b67267b8b2b00c143e625da6f20`。

本批实际目录：`/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1`；授权原文留在其 `control/USER_REQUEST.txt`，`control/ACTIVATION_MANIFEST.json` 明确记录绑定中，五点当前均未注册为 cohort。

只读现场核对：Native epoch 2，registry 与 epoch SHA 相符，registry SHA `6edffb87df4a25ba4d852dd50907d82fa8e5dc6f4a00122d524269b43da15485`。共享注册表总计 70 条，其中 EP-L2/EP-MAIN 52 条；本批精确 point/cohort/关键词匹配 0，`accel-sim.out` 活动进程 0。此处的 70 与交接所述 52 属于全表与 EP 子集的口径差异。尚未执行预算登记、消费或模型启动。

现场申请 SHA256 `646e6b5c718f68de6c1f12fd5c3fc2f0f73b07761757d009d0c773ac790c7247`，与固定 Git 副本 JSON 实质字段逐项相等。五份配置、constructor、输入绑定及历史模板 Spec 的 SHA 均通过只读检查，五点各 283 项 canonical 配置也通过。`preactivation_check.py` 是只读防重检查，不能作为 Host/consumer/Native 正式释放或资源准入的替代。

## 尚未闭合的激活差额

已接受的 A Source5 CPU、实际 X1 单 slice ABI 和 283 constructor 可复用。旧 Source78/812 的 Host、Native 与数学 parser **不能直接绑定本批**：旧 parser 要求 `V2.live == V2.role_tvd`，而 A EXT2 的 V2 仅表示 Base、全局 role 包含 Ext；旧 Host 严格锁定旧 Source、旧模式及资格文档。必须将实际 X1 四类记录的 64 slice 检查与保持原数学/完整命令人口的验证链整合，并绑定新 Source5 的 43 字段 Host、Native22+实际 Host/Trace-child pins、五份不可变 Spec 和 scoped 唯一入口。此项未闭合前，首次消费会有不可退款的验收风险，因此尚未注册或启动。

下一项具体工作：完成并验证该 Source-specific consumer 与 Host/Native 合同，然后在共享锁下增量登记 GEMM 3、Stencil 2，实时资源准入后按点独立执行。不会再请求相同五点授权。
