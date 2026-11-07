# Q1工程异常与停止约束

固定合同仅一个非阻塞flock尝试、一个连续窗口。用户批准8h/3h上限不表示允许结束后再取锁。此次实际437.803s后监督器因VmSwap解析异常自动执行finally，锁和预约已经释放；因此即使普通工程问题已在CPU修复，也不得自动再次GPU。

普通工程修复确实在本Goal内完成，没有拆CPU准备Goal：
1. CPython原库路径复用修复；无安装升级。
2. 原derived目录名images_4_png核实；没有重造图像。
3. manifest大小写、sidecar完整绑定、actual runner恢复检查、异常解锁清理等在首GPU前通过CPU/source tests。
4. AF_UNIX过长时保留首次失败，仅对真实自身worker安全停止；同一锁内修复并完成EARLY_R1。
5. 原VmSwap逻辑未覆盖终态/字段消失，且错误PID未持久化。该缺陷使普通工程问题变为整个GPU窗口的退出；这是监督器设计缺口，不是被观察到的3DGS科学失败。
6. 新process_observation与监督器CPU回归覆盖终态/缺字段、PID复用、AccessDenied、混合真gap和partial evidence。它不回填当前失败缺失的PID，也未通过真实GPU重跑。

本轮后半段只有CPU检查、修复、分析、Git发布。没有申请扩额、第二scene、额外模拟器或另一个Codex Goal。保持原完整早期checkpoint，以免丢弃本次昂贵真实输入/执行资产；它们仍需未来明确授权下的实际恢复资格，本轮不自动派发。
