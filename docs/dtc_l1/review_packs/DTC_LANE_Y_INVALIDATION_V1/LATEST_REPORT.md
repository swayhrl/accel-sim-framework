# DTC_LANE_Y_INDEPENDENT_INVALIDATION_VALIDATION_174_V1

2026-10-18，Asia/Shanghai。**独立验证交付：FAIL_CLOSED；不授权Lane AA。** 完整模拟派发数0，生产源码修改数0。

Framework分支`hrl/iscas2027-dtc-lane-y-validation-174-v1`，独立worktree`/workspace/worktrees/accel-sim-iscas2027-dtc-lane-y-validation-174-v1`，基于已发布Framework `f5c37d6edcce832a72cb0830021bffa78df6cc13`。本Lane没有参与实现作者的源码编写或修复，不进入Lane X工作树修改代码。

只读绑定Lane X最新发布Core `f8b34dd7a738caddf4f23dd417e34c0b63c206d9`，冻结Core `6fba0136f8465b59fe5858a950fa39efb265f654`，Lane V合同 `26abd496417d9392245052e54fbd9ba27c6ffd96`。Core只有科学STOP文档差异，尚无新K0开关/K1实现。V合同已阅读绑定；其CONTRACT_FOR_REVIEW不代表实施批准。独立源代码审查确认请求/ordinary实际Tag失效、idle-cluster重复、MEMBAR与配置切换作用域均需区分。

本Lane完成独立Core完整库编译、真实配置注册/echo探针、CPU参考模型和生产头文件回归。最终运行结果：

|层级|结果|不能推导的结论|
|---|---|---|
|25组最小序列，73次模式比较|PASS_REFERENCE_ONLY；每项含错误期望退出1负控|不能作为生产K1 PASS；IO为shadow owner模型|
|14个独立编写命名探针 × 发布/冻结2个头文件|28次预期状态/退出码配对一致，含5类断言拒绝负例|现有替换/生命周期通过不等于source失效通过|
|原Core四个既有CPU回归|4/4，退出0|没有新K1覆盖|
|新库实际选项解析|3组有效echo退出0；未知及新选项0/1均预期退出1|默认既有开关0不是新K0运行证明|
|K1-01至K1-08生产验收|NOT_RUN / FAIL_CLOSED|无old-consumer/inflight数值与完整状态安全证明|

最终runner退出**3**是预期的科学门禁关闭；意外测试失败为0。shadow token见证发现元数据允许的潜在过期读组合，**不是SASS architectural load值证明**。不同合法sector乱序返回应接纳；重复、未请求、越界及旧generation必须拒绝。未通过生产修改或削弱断言取得PASS。

入口：`TEST_MATRIX.tsv`、`EXPECTED_AND_OBSERVED.json`含输入、期望、观察与退出码；`K0_DEFAULT_OFF_AUDIT.md`、`K1_STATE_SAFETY_AUDIT.md`、`OPEN_VALUE_SEMANTICS.md`解释边界；`VALIDATION_GATE.json`是机器可读裁决。`SOURCE_AUDIT.json`、`CONTRACT_BINDING.json`和`BUILD_AND_COMMAND_RECEIPTS.json`补充源/blob、编译产物SHA、实际动态库绑定及外部原始日志哈希。所有脚本/小型合成输入在本包；没有提交原始trace、模拟日志、二进制或build树。

重跑（CPU-only，成功执行且科学门禁关闭时退出3）：

```bash
python3 docs/dtc_l1/review_packs/DTC_LANE_Y_INVALIDATION_V1/scripts/run_validation.py \
  --core-repo /workspace/repos/gpgpu-sim_distribution \
  --core-source /workspace/worktrees/gpgpu-sim-iscas2027-dtc-lane-y-source-f8b34dd7 \
  --core-sha f8b34dd7a738caddf4f23dd417e34c0b63c206d9 \
  --frozen-sha 6fba0136f8465b59fe5858a950fa39efb265f654 \
  --framework-repo /workspace/repos/accel-sim-framework \
  --lane-v-sha 26abd496417d9392245052e54fbd9ba27c6ffd96 \
  --external /workspace/dtc-lane-y-validation-174-v1
```

runner会核远端发布锚点，若移动或合同改变则停止，要求重新审查，不静默沿用PASS。再次复跑前保留旧外部证据或换新external路径。Core源码worktree由固定发布SHA detached建立；无需进入实现作者工作树。日志/构建产物仅在本Lane独立external目录。

Lane AA建议：当前不得启动K1。若后续新Core无法证明K0 OFF与冻结模型同义，应对相同完整输入重跑K0/K1严格配对，旧结果不能替代。完整模拟派发权仅归Lane AA，本包不创建dispatcher或后台模拟任务。

Git交付：本包文件SHA256见`SHA256SUMS`；最终提交push后fetch-back逐blob核对，外部最终回执写`/workspace/dtc-lane-y-validation-174-v1/FINAL_FETCH_BACK.json`，绑定最终提交以避免自引用。最终提交SHA由交付消息给出。
