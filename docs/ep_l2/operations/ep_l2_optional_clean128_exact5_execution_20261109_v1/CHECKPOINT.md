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

## 12:30 UTC 后增量

已新增 Source5 专属 `SOURCE_CPU_QUALIFICATION.json`，逐一 pin 既有生产 CPU、ELF 构建、实际 283 项 constructor 和 A 原始记录 ABI；其状态仅为工程资格，应用接受为 false。`exact5_consumer.py` 的正式调用现强制要求 Source 资格文件路径及 SHA。`consumer_preflight.py` 已在 174-new 只读通过：五份草案唯一、冻结数学主体 SHA `7cc347a6c62974eedf9e1e39b007c2716fa886d26057f005c938c820b48e1817`、Source5 资格引用和真实 A 单 slice CPU 三种模式均对齐；还验证 EXT2 的 `Base live=128`、`Ext live=128`、`role_tvd=256`，篡改该守恒关系会拒绝。

该组件 preflight 不能代替 64 slice 完整应用验收。尚缺正式 Host/Native22 与 Trace-child pins、五份不可变 Spec、scoped Native 路由及全应用 consumer 接线。因此当前仍为五点登记 0、消费 0、模型运行 0；不能调用草案或旧 UMT1 脚本启动。

## 12:43 UTC 后增量

在 174-new 运行 `runtime/consumer_population_fixture.py`，使用 A 生产 CPU 的三种模式原始记录，将每种单 slice 记录仅用于构造**小型合成 64-slice ABI 人口**。三种模式的 64-slice 类型/字段/守恒、最终时钟选择通过；缺失末项、较新时钟不完整和 Ext 容量篡改均被拒绝。此测试不含完整应用命令、kernel、FT、drain 或真实模型，不得称为应用验收。

`documents/SOURCE5_NATIVE22_CLOSURE.json`、`SOURCE5_HOST_TRACE_CHILD_DEPENDENCIES.json` 和 `RUNTIME_FULL43_CONTRACT.json` 已按当前节点文件建立。五份草案 Source5 相同，均含严格 43 字段和 283 项；Native22 与草案中 22 个路径的 SHA 相符。Host-child 五条为当前身份 pin；历史接受身份仍未知。这些是静态依赖资料，不是 Host 工程资格、正式 Spec、Native 安装或启动准入。

旧 UMT1 Host 仍硬编码 Source812、旧请求/两 cohort、F 模式和旧阶段门槛；旧 `ep_perf_common_v2.py` 只支持单请求事务。当前必须做本批两个独立请求的运行时适配、Source5 Host 验证和 scoped Native 安装，并对接 `exact5_consumer.py`。在正式入口通过前，五点继续登记 0、消费 0、启动 0；授权有效，无需再次请求同一五点许可。

## 12:54 UTC 后增量

发现原五份草案 `eligibility_ref` 仍指向旧 Source78 输入资格，且 `scientific_option_contract.complete_282=true`；不能直接正式释放。现用原输入绑定/历史输入身份作为**输入证据**，与 Source5 CPU/构建资格显式接合，形成 GEMM 和 Stencil 两份 `SOURCE5_INPUT_ELIGIBILITY_*.json`。它们声明旧 Source 资格与应用接受均不继承。`exact5_mode_contract.py` 已逐项核对五份草案与固定申请的 Source、输入、283 项、点位、资源和命令人口。

五份 `BOUND_SPEC_CANDIDATE.json` 只修正上述资格引用、283 声明和 Source5 consumer/mode 引用，且保持 `launch_permission=false`、Host/Native 未绑定。候选不是不可变正式 Spec，不能提交给 Native 执行。旧模板的 Source812 Host、双族 registry 事务、正式 Native 路由和完整应用 consumer 接线仍未完成。当前仍无模型结果或科学 cycles。
