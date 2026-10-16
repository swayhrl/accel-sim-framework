# R0.1发布前检查（准备稿，未执行）

精确输入/命令以PLANNED_RELEASE_IDENTITY.json为准；不是正式release合同。Framework53a1503d/Core62dc1d均已freeze；runtime binary=null。相同原生产source/build路径，没有新worker。

1. Lane5独立确认live workspace≥48GiB，Lane1构建另留2GiB增长；可用RAM至少64GiB并满足8GiB构建reservation后的floor；registry无重复build、配额可用，真实进程无冲突。不停止/调整DTC-L1，不接管Ops删除，不把本pack的旧快照当准入许可。
2. 同一入口`/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane1-r0-1/util/ep_l2/ft_lane1/build_r0_1.py`，Core `/workspace/worktrees/gpgpu-sim-ep-l2-ft20261016-lane1-r0-1`，新out `.../lane1/review_r5/r0_1_build_attempt_r1`，`--execute`。build仍 `/workspace/build/ep-l2-ft20261016-lane1-r0-1`，必须不存在；不得复用旧R0/R1 binary/build或并发编译。当前不执行本步骤。
3. 检查精确clean producing HEAD、R0 vendor f90c430c、CMake/toolchain/flags/version stamp、两个新test executable hash、4个模式完整有序config/aux/environment hash。审阅CMake生成的flags无NDEBUG。正式应用trace仍null：由Lane5逐run冻结kernelslist和全部trace内容，不复用旧key。
4. 唯一producer build完成后，执行清单内21个定向进程：host4、clock8、warm-clock4、partition4、directed1；逐项exit/log/hash与终态，任何错误保留诊断并禁止release。13项Python工具PASS不能填充此处。
5. 实测build/resource日志和失败残留保留。只有producer生产定向通过后，复制到**新revision**只读二进制快照，关闭重开核hash，记录source/Framework/binary/config和test exe完整身份；旧二进制/日志/CSV原样保留。新BASELINE R0.1合同使用新文件名，旧BASELINE_CONTRACT_V1仅历史。producer PASS仍不等于独立资格。
6. Lane5用准确新身份独立执行physical_bank_clock、memcpy_payload_identity及受影响原九项回归，签最新资格和current acceptance；consumer必须继续拒绝旧六条run。只有Lane5准入与资格都满足，五个B16/U_WB16新pair才可开始；不等待TVD/RO/ideal集成。首个当前科学接受pair交Lane6。
7. 新结果与回执提交原执行分支，保留旧packs；push后fetch远端准确SHA、回读receipt/manifest/文件hash。若源码、语义、输出或配置有变化，发布新revision和新key，不能覆盖已冻结结果。
