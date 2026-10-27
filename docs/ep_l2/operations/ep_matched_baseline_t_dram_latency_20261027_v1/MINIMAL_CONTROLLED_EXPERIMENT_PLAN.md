# 未执行的最小后续候选

本Goal停止：五新启动全部消费，未运行60、未扫更高延迟、未修改T或自动新增应用。维持现有T并报告真实Tag压力不足，不能把降低保护条件当验收方法。

优先候选一（需要新Core资格与独立授权）：在m_dram_latency_queue入队记录packet identity+enqueue_core+deadline_core；出队Scheduler push记录push_core，分别汇总固定等待min(push,deadline)-enqueue、到期后等待max(0,push-deadline)，计deadline后Schedulerfull/HOL的观察。每channel有界sum/count/max/固定hist，明确burst/packet/RO三种人口，借/还credit和完整drain守恒；零业务分支改变、不新增队列容量、无动态输出频率影响。先外部CPU fixture observerOFF/ON对比所有事务顺序、接受周期、退出、返回身份和资源最终清空。新passive counters不能补进已冻结/已完成六点，不重跑以填旧表。

候选二（仅独立授权后，最多一个有现实地址/MLP依据的负载）：复用真实trace，原硬件配置，同binary T-ON/OFF精确配对，先被动证实独立NEW与满路不可替换预约实际联合，再研究T。若没有真实压力即保留负结果，不继续缩容/延迟扫描寻找正结果。不得拿人为压力fixture当真实应用收益。

当前证据不足以把L1 MissQ容量或FR-FCFS/credit某一资源确认为端到端主因；本轮观察到MissQ、LowerFIFO、Scheduler饱和，强因果排序仍需同producer单变量、局部服务与端到端cycles一起测量。没有自动批准这些应用启动，没有使用旧epoch2/DTC余额、GPU采集或SM70/GPU109迁移资源。
