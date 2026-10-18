# DTC_LANE_AB_OLD_DISPATCH_AUTHORITY_AUDIT_174_V1

**SAFE_TO_RETIRE_DISPATCHER_CANDIDATE**。仅审查并提交待批准退役方案；目标authority仍活着、FLOCK仍持有，**没有停用，也没有解除AA2 HOLD**。

原174主机huangrulin-174、root账户。独立Framework分支 `hrl/iscas2027-dtc-lane-ab-old-dispatch-authority-audit-174-v1`，worktree `/workspace/worktrees/accel-sim-iscas2027-dtc-lane-ab-old-dispatch-authority-audit-174-v1`；base为AA2发布 `fa7bd9ee7667ebb94e919295755311a2a2da4541`。只新增本审查包；未改原Goal、Core、脚本、锁、日志或raw。

最终只读观察：**2026-10-18T01:32:49.325309+08:00**（Asia/Shanghai）。

|核对项|结果|
|---|---|
|PID/start_ticks|1425986 / 584741606，仍与AA2同一实例；cmdline为旧watch、poll120|
|FLOCK|fd9仍持 `FLOCK ADVISORY WRITE`；原路径 `/workspace/fast64-primary-r4/.fast64_4_2d_core41_autodispatch_v1.lock`，device156/inode37920070；全局/proc/locks阴性不能证明释放|
|脚本身份|磁盘、打开fd255及冻结Framework18a68dcc Git blob一致；SHA256 `6521332b1bf6814cc165a5dce1150d82eee50813ec363e4d271224d8f123728b`；3个helper pin均匹配|
|当前等待|两个Base strict/structural文件均缺；日志前缀20384838字节只有WAIT事件，52674行；最后一条2026-10-18T01:32:27+08:00。成对重复由tee/stdout同日志解释，不当成两实例|
|已派发证据|IO/OO两个目标run、launcher/supervisor/closeout及结果路径均不存在；所读完整日志前缀无派发/monitor启动事件；不对已删除历史任务作绝对断言|
|实际进程|目标仅有sleep120子进程PID2994672/start_ticks901031869，且继承同FLOCK；最终无可见目标IO/OO simulator、runner或monitor；相关Core41 collector PID1482676独立存在，保留|
|潜在后续|Base变true→两worker资源gate→IO/CPU36，再monitor→OO/CPU37；第73行local展开缺陷可令IO后monitor失败，OO未必可达；不能依赖此bug永久禁发|
|科学边界|旧Core41两臂是2DConvolution；冻结2D FORMAT_APPLICABILITY_REVIEW_PENDING/本轮任何arm STOP，与Gaussian AA2不是同一工作。技术gate不读取当前科学STOP|

最小方案：**另获用户明确批准并重新核身份/子进程/任务后，仅向该父shell实例发送一次SIGTERM；不碰进程组、模拟器、monitor或其它collector，不删锁/改脚本。** sleep继承fd可能使FLOCK继续保留，需让其自然结束并只读确认全部原inode holders消失；不能用父PID退出代替锁释放。具体前提、影响和不扩权条件见 [AUTHORITY_DECISION.md](AUTHORITY_DECISION.md)。本Goal只读限制来自用户本轮明确指令，因此停用必须等单独批准，不在本次自动执行。

收据：[DECISION.json](DECISION.json)、[初次观察](OBSERVATION_INITIAL.json)、[最终观察](OBSERVATION_FINAL.json)、[未来分支Bash最小fixture](FUTURE_BRANCH_FIXTURE.json)、[源码/政策SHA](SOURCE_SHA256.tsv)。两个小型工程分类/fixture问题完整披露：初次simulator前缀分类误收7个bash控制进程，已按确切accel-sim.out名称修正；旧原始观察未改，见 [PROCESS_CLASSIFIER_CORRECTION.json](PROCESS_CLASSIFIER_CORRECTION.json)。初次真正EP-L2 simulator在最终观察已不再可见，未被本Goal停止，终态不作推断。

复核脚本 [capture_readonly.py](scripts/capture_readonly.py) 只读/proc、旧小文件与日志前缀，写本AB一个预先不存在的命名JSON；不执行旧helper、dry-run、模拟器，不发送包括signal0在内的任何信号，不尝试flock。已有两份观察禁止覆盖；今后状态变化应在新审查包重新取证。本包只保留小型收据和SHA，不复制20MB原日志或binary/trace。

全部信号、加/解锁、删锁、旧脚本修改、模拟器/helper执行、trace读取和接管均为0。独立commit/push/fetch-back逐blob核同后clean；最终外部回执写 `/workspace/dtc-lane-ab-old-dispatch-authority-audit-174-v1/FINAL_FETCH_BACK.json`，避免提交自身hash循环。完成本只读Goal后结束，等待用户决定是否在另行批准范围内停用目标；不重启AA2或任何历史Goal。
