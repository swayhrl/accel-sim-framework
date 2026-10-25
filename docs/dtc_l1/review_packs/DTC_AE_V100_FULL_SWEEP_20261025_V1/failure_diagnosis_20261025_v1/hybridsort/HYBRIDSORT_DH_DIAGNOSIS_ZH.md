# hybridsort-DH 全部失败诊断

直接触发已证实：第1个 histogram kernel 在统计阶段命中真实 OO-PIB 非空断言并 SIGABRT；随后 launcher 记录缺少自然遥测闭合。该点只跑到68个 kernel 中的第1个，任何打印的周期都不接受为全输入科研结果。

源码缺陷已证实：无目标寄存器的 global RED/ATOMG 被解码为原子 LOAD。M4 在准入时占用 PIB 并登记 external dependency，但 `writeback_complete` 对这种零目标指令返回 false，导致两条返回写回路径均不调用 M4 completion。dispatch 的 `dtc_l1_retire` 只处理 PAPER_BASE，无法替 OO 关闭此依赖。真实源函数与真实 OO header 的独立 CPU fixture 已重现这一缺口，AE0/AE1 相同。

历史归因高度一致，但不是完整逐 UID 现场重放：完整新读并核 SHA 的首 kernel 含2048条 RED，全部 dest_num=0、PC04b0、maskffffffff；64个 CTA 每个恰32条。原始 raw 显示64个不同 SM 的绑定消息，但 set_kernel 打印早于 can_issue 检查，不能把它直接当作 CTA 分配记录。结合首 kernel、64CTA/64SM、空初态和同构资源，1CTA/SM、32条原子/SM 是调度源码支持的高置信推断。较低泄漏密度能解释为何仍有空间推进并到达 kernel 收尾，不能排除途中出现瞬时 PIB-full stall。131072条 cacheable global load 已全部被 service_retired 计入；先前 inflight==0 断言通过，随后 pib==0 失败。Core 的 active/core-cycle 条件未覆盖 OO-only sidecar drain，提供了另一处生命周期集成缺口。

没有捕获中止时逐 UID 的 PIB 内容，不能声称“实测恰有2048条残留”或确定每条 source_completed 位。这里的2048是源码与输入推导。首 kernel 的157690254条线程指令与首kernel已打印周期仅作故障定位。没有遥测容量、内存或磁盘守护 STOP；该点通过V4前端启动，未属于热更新目标；资源检查全通过。

修复优先级：按指令 UID 跟踪全部源请求的响应完成，独立于目标寄存器；只在最后源响应后关闭 M4 一次，保持原子副作用、顺序和 warp 完成语义。再补齐核心/kernel 的 sidecar drain。不能只删除断言、在 dispatch 提前关闭或对每个响应无条件关闭。先覆盖 RED/ATOMG、返回值原子、多响应、重复响应、共享原子排除、AE0/1 和终止排空的 CPU 测试，再设计独立版本的受限修复实验。

本轮没有启动/重跑模拟，没有修改活动 Core、原始分类或历史账本。机器证据与精确文件 SHA 见 HYBRIDSORT_DH_DIAGNOSIS.json；完整首 kernel 原子审计见 FIRST_KERNEL_ATOMIC_TRACE_AUDIT.json；公共 CPU 复现见 ../bfs/CPU_SOURCE_FIXTURE_RESULT.json。
