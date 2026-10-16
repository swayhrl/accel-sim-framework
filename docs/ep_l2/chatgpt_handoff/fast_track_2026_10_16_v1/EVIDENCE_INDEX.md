# 本轮只读证据索引

## 已检索来源

1. Framework EP-L2 refs（本轮实时读取）
https://api.github.com/repos/swayhrl/accel-sim-framework/git/matching-refs/heads/hrl/ep-l2-

2. 主分支review_packs目录（用于定位，不作为性能完成证明）
https://github.com/swayhrl/accel-sim-framework/tree/b7dbdecb94054f08aaf2e33bfef48e453747ceb5/docs/ep_l2/review_packs

3. 主分支calibration目录及contracts
https://github.com/swayhrl/accel-sim-framework/tree/b7dbdecb94054f08aaf2e33bfef48e453747ceb5/docs/ep_l2/calibration

4. 主分支util/ep_l2
https://github.com/swayhrl/accel-sim-framework/tree/b7dbdecb94054f08aaf2e33bfef48e453747ceb5/util/ep_l2

5. 已完成校准差分CSV
https://github.com/swayhrl/accel-sim-framework/blob/aa44f9e8d685b6f9bbe410b996e07ef185a8de96/docs/ep_l2/review_packs/FINAL_CALIBRATION_CONVERGENCE_r1/CALIBRATION_DELTAS_FINAL.csv

6. Line-MSHR实测CSV
https://github.com/swayhrl/accel-sim-framework/blob/b7dbdecb94054f08aaf2e33bfef48e453747ceb5/docs/ep_l2/review_packs/LINE_MSHR_CAUSALITY_r1/CONVOLUTION_2X2.csv
D512 M128: 292211 cycles / 931416 line_mshr_full_block。
D512 M256: 291108 cycles / 0 line_mshr_full_block。
该对照仍有WAD/MissQ/下层约束，不是完整理想L2。

7. Headroom计划（是计划，不能作为执行证明）
https://github.com/swayhrl/accel-sim-framework/blob/b7dbdecb94054f08aaf2e33bfef48e453747ceb5/docs/ep_l2/project_spec/PERFORMANCE_HEADROOM_PLAN.md

8. WBUF shadow范围与释放事件规范
https://github.com/swayhrl/accel-sim-framework/blob/b7dbdecb94054f08aaf2e33bfef48e453747ceb5/docs/ep_l2/project_spec/MOTIVATION_FIGURES_PLAN.md

9. 真实lower accept hook：Core l2cache.h，680–730范围内L2interface::push
https://github.com/swayhrl/gpgpu-sim/blob/ca3e7bc0b8f61b5d7c052bcda2a91955a1e5c919/src/gpgpu-sim/l2cache.h
该hook在m_L2_dram_queue->push之后调用shadow WB lower-accept，不是在set_done。

## 当前结论范围

外置WBUF的物理预算来自本轮用户确认；16 primary / 8 sensitivity是本轮推荐实验选择。各ideal模式、分支名、任务名均为新执行合同，不是已有实现或结果。

此索引没有断言仓库全部分支/节点结果均已逐文件穷尽。Lane 4须对本地未提交结果补查并报告精确可复用性。
