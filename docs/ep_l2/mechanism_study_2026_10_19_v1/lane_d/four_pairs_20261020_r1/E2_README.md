# Lane E2：外部空间恢复后正式主配对终验

原174独立资源准入PASS后，复用原唯一控制器，依次完成CFD、DWT、SAD；三对六端全部独立接受，连同原Conv共四对CURRENT_ACCEPTED。每对已分别推送并通过中央inbox/events交付D，包含精确身份、周期、机制计数、原生退出证据及结果位置。

| 新配对 | S cycles | F cycles | S/F | 完整指令数/端 |
|---|---:|---:|---:|---:|
| cfd_097k | 79093 | 79157 | 0.999191480 | 143129372 |
| dwt2d | 166519 | 167643 | 0.993295276 | 148684429 |
| sad | 110773 | 109754 | 1.009284400 | 157583646 |

六端均真实exit0/wait status0，PID/start_ticks/boot身份与持久化原生回执闭合，全指令、64slice、硬件drain、requester/response/payload/WB等科学终验PASS。main61、原source/config/input/资格及构建身份保持，未重复17项原生测试。

原T0=1792414193；累计20/40，剩20；main已用12/32、contingency已用8/8。新结果累计3,607,362,584 B，旧加新17,916,938,968 B，本轮实际增长589,725,365 B。外部V3释放8,968,978,432 B未被当作结果生成量抵扣。

终验资源快照workspace可用12,330,840,064 B、Share可用44,219,682,816 B。原控制器STOPPED，无活动run/lease，无后台等待器。

FWT两端INCOMPLETE、Vector S COMPLETE_VALID、Vector F RESOURCE_LIMIT/exit-15、全部旧失败/撤回/HOLD及前14次保留体积/收据身份不变；没有重试或退回启动计数。

下一批边界：本轮具备资格且从未启动的主S/F队列已全部处理。剩余原32矩阵为Btree S/F（HOLD）及18个尚无当前producer/profile独立资格的消融/诊断条件。保留余20次；未采用新的预算重分配，旧FWT重跑建议仍仅是建议，Vector F也不自动重试。SGEMM继续仅独立探索候选，不能替换正式端点；C额外fixture不升级。逐条件记录见REMAINING_ORIGINAL_MATRIX_PROJECTION.json。
