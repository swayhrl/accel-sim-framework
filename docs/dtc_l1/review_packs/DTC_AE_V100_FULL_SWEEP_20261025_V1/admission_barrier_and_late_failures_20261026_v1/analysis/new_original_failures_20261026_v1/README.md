# 原矩阵新增四个失败：逐点诊断

这些是旧Framework3b362/旧Core2e3bef来源的原矩阵attempt，均保持UNACCEPTED、SOURCE_KEEP和原预算/UUID，不用新验证替换旧失败。

| 点 | UUID | 已确认直接原因 |
|---|---|---|
| GESUMMV CH | 0b3b03d2-1cfd-46d2-adc8-721c5e51c4f2 | required40,914,488,049 > free40,906,543,104，仅差7,944,945bytes；唯一peer为旧R1全额8.125GiB。disk_pass=false传入expected_growth，BA SIGTERM；非模型/内存错误。 |
| scalarProd CM | 0a6cce7f-bb75-4fd6-a545-014d39ef8de0 | 6条连续成功发送后，首kernel同步bulk解析CTA0..62期间30秒freshness耗尽；资源均PASS，rc-15，无fatal。 |
| hybridsort e911 DM | 2ca00227-7ea3-4ada-a79f-eb1ddd56e7d6 | 首kernel结束统计OO PIB非空assert，自身SIGABRT/exit1。 |
| hybridsort e911 DH | b91f0981-33c3-41e5-983f-9cdd4ecadf87 | 独立raw证实同一首kernel terminal assert，自身SIGABRT/exit1。 |

scalarProd适用已修FW02775的同线程cooperative heartbeat；hybridsort新输入首kernel完整64.16MB SHA闭合审计确认全部2048 RED均0dest/fullmask，适用已修Core9eed的atomic completion与kernel quiescence drain。两点首kernel人口已到20,554,396指令/64CTA，仍不能接受partial cycles；残余PIB逐UID/数量没有被记录。修复适用性不等于新验证已经PASS。

GESUMMV故障样本required =5GiB floor +26,821,626,609 own已知写入 +8,724,152,320 peer。独立核旧R1为23consumed/remaining0/无未花费claim，18点已archive+native恢复，5未archive各cap256MiB。保守future upper=1GiB+5×max(2cap,size+16MiB)=3.5GiB，可条件metadata reconciliation释放4.625GiB，故障同一快照会由负7.94MB变正4,958,110,991bytes。

本包只给评估，没有修改authority。应用必须EX锁下重读重算、保留旧registry/epoch/q字节，只改reserved_write_bytes并append history；state/consumed/预算/source/orchestrator均不动。如果独立consumer已经关闭旧R1，不能覆盖CLOSED或提高其floor。所有未来请求仍需新鲜真实资源检查。

包内逐点JSON绑定完整raw/progress/resource/strace/PID/launch/INTENT SHA；只引用原证据路径，没有复制raw或trace。旧历史源与模型不变，未启动/重跑模拟。
