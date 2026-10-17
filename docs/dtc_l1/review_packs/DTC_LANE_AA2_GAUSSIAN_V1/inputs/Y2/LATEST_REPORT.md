# DTC_LANE_Y2_INDEPENDENT_K1_REQUAL_174

2026-10-18，Asia/Shanghai。**PASS_K1_OO_MODEL_SCOPE**。这是独立Y2 Goal与CPU模型资格收据；原Y1 V1正确FAIL_CLOSED交付保持不变。未运行完整Gaussian/GEMM、未建立新执行authority、未修改Lane X生产源码。

新分支`hrl/iscas2027-dtc-lane-y2-k1-requal-174-v1`，独立Framework worktree：`/workspace/worktrees/accel-sim-iscas2027-dtc-lane-y2-k1-requal-174-v1`。从V1 `b673d046b38f61159b5db67a477d58d1afa4662f`建立；V1整个包tree保持同一Git对象，未重跑其原Goal。

只读锚点：Lane V合同`26abd496417d9392245052e54fbd9ba27c6ffd96`；冻结Core`6fba0136f8465b59fe5858a950fa39efb265f654`；Lane X新行为Core **`c0a5e2c31e407c57e3a4af3ce529c921e8059a05`**，来自指定独立分支。X的Core push/fetch-back收据已核；只有新行为提交进入独立detached source/build，不借用旧f8b34dd7冒充K1。

最终CPU检查共62项，并独立运行Core现有7个CMake回归：

|证据层级|检查数量|结论|
|---|---:|---|
|逐字生产函数体 + 显式环境夹具|26|source正/负控、请求/ordinary提交分离、grant/partial/late waiter、WB反压、sidecar、proxy过滤、同cycle三种次序及错误返回拒绝符合预期|
|直接生产OO/observer + 真实ordinary cache API|2|finite OFF/ON的retained/live Ref、容量压力、generation重用和最终回收通过|
|新编译真实Core库的生产配置/parser/echo|6|省略/OFF/ON有效；未知选项预期拒绝|
|冻结/新common header配对|28|14个用例的状态/退出码一致；K0有界回归通过|
|Core现有CMake CPU测试|7/7|补充回归通过，未当作独立测试作者证据|

正控明确撤销至少一条此前可查询DTC Tag；无source事件的负控明确保留映射。K0省略/OFF与冻结原LDST函数体CPU状态相同。每项比较包含输入、期望、观察、退出码和独立比较器错误期望负控。最终runner退出0；拒绝用例的SIGABRT是指定预期结果。

资格**仅限OO逻辑模型/API及逐字生产语句在夹具中执行的范围**。不是完整shader/LDST ABI集成、真实packet/NoC、真实operand collector或architectural load数值证明。`VALIDATION_GATE_V2.json.fixture_limits`逐项列明替身和未测内容；这些边界不能写成已经测过。真实数据值、跨SM coherence、全ISA支持仍UNPROVEN，不把全ISA证明作为本轮OO结构资格的假定前提。IO=`IO_K1_UNIMPLEMENTED_STOP`；MODERN=`HOLD`。原子目录sweep的零新增模拟cycle是已披露的软件模型假设，不是硬件/PPA结果。

交付文件：`TEST_MATRIX.tsv`、`EXPECTED_VS_OBSERVED.json`、`K0_EQUIVALENCE.md`、`K1_CONSERVATION.md`、`SOURCE_EVENT_TIMING.md`、`VALIDATION_GATE_V2.json`及本报告。`SOURCE_BINDING.json`/`EXTRACTED_BODY_BINDING.json`绑定commit/blob/提取SHA；`BUILD_RECEIPTS.json`及`TOOLCHAIN_IDENTITY.json`绑定compiler、flags、binary/hash、实际动态库解析及逐命令收据。脚本和最小合成输入均在本包；原始开发/构建/执行输出和二进制仅留外部目录。

CPU-only复跑（保持原收据，用新的run-label；远端Core变化需独立fetch、detached目录和重新审查/绑定）：

```bash
python3 docs/dtc_l1/review_packs/DTC_LANE_Y2_K1_REQUAL_V1/scripts/run_requal.py \
  --core-repo /workspace/repos/gpgpu-sim_distribution \
  --framework-repo /workspace/repos/accel-sim-framework \
  --source /workspace/worktrees/gpgpu-sim-iscas2027-dtc-lane-y2-source-c0a5e2c3 \
  --core-sha c0a5e2c31e407c57e3a4af3ce529c921e8059a05 \
  --x-review-sha 741a56a0f1f6f3a66653538b3897aab764114747 \
  --external /workspace/dtc-lane-y2-k1-requal-174-v1 \
  --run-label rerun_review_01
```

runner缺可执行新Core或已知真实flag时输出PENDING / `AWAITING_X_EXECUTABLE_SOURCE`，不会沿用旧STOP或静默给PASS。测试若揭示生产bug，应将最短复现及SHA交X修复，本Lane不改生产代码；修复后按新SHA从头验证。当前未发现生产bug。

文件SHA见`SHA256SUMS`。独立commit/push后fetch-back逐blob核对，clean；最终外部回执位于`/workspace/dtc-lane-y2-k1-requal-174-v1/FINAL_FETCH_BACK.json`，避免自引用提交身份。完整模拟派发权仅归Lane AA；本包提供OO模型资格，不创建新的执行authority，也没有完整输入运行收据。
