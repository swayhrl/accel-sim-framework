# 实测、静态约束与缺失证据

已测 CPU：原 X2 7/7 CTest、正常统计5例；AE生产 header/parser137项、逐请求 OFF对照56组和四种旧几何；AG预览14/14 CTest、正常打印5例、实际 LDST8例、完整配置注册8例。AC独立80进程、16 parser负例与68个AC×AE四组合实际LDST有限交错用例通过；新集成15/15 CTest。资源纯CPU10项、strict malformed/calibration18项、runner7项（含独立OOM watchdog）。每次runner CPU测试只创建一个自有Python sleep child并用pidfd终止回收；多次脚本版本检查留有独立CPU目录，均未消耗科学UUID。AF独立15 witness为状态安全证据。

已测输入身份：两份原 list、GEMM1/Gaussian510成员流式SHA全部匹配，两输入成员共1,988,136,520字节读取，未解压复制；身份表记录dev/inode/size/mtime/ctime。输入完整窗口：所有原命令、所有CTA和active-thread instructions，不裁prefix，不预热选段。GEMM739,246,080；Gaussian283,685,120。成员未变由每次运行前/后 stat稳定性复核；不是每次重复读取2GB。

旧 T 全量输出仅校准参照：固定 f520a445436b57c0a0f2494fb858a1636f04d2bc 中的全GEMM/全Gaussian旧K0 64×8，独立SHA与逐kernel共同指标表已导出。它们不进入 AG新BASE列。AA5 1/4实际启动、0/4完整strict，67/510 prefix与451.4s资源STOP只作为历史；无性能校准资格。

本轮性能实测：实际Popen child 0，预算消耗0/8，完整strict PASS 0；各点整数cycles与仅对本轮同输入BASE的比值见RESULTS.tsv。未通过完整strict者不报告性能cycles，原始prefix仅保存在失败raw。两输入仍为发现集，host wall永不作GPU速度，不替代独立验证、GM12或旧AA5四格。

公开输出可测范围：最终累计共同计数、OO ready/pending/new、PIB/physical积分、collection/ready/WB区间和lower create/inject/response/credit、L2 accepted32B sectors及DRAM实际 issued32B atoms。积分平均以DTC_SERVICE_V1_samples=64×最终corecycles归一，不能重加累计kernel snapshots。ready-conditioned区间只在定义一致时比较。新ON专属统计仅非比较诊断；OFF不打印填UNAVAILABLE。

固定X2/AE正常出口不提供真实collection/WB同周期重叠、逐消费者通知时序、真实输入每set/bank冲突直方图或逐Ref/ledger/sector最终私有收据；UNAVAILABLE，不从aggregate推造。AC ON新frame可提供自身collection/WB同周期重叠、stage occupancy/backpressure及quota直方图；仅ON非比较诊断，OFF未打印仍UNAVAILABLE，不能声称直接测出相对BASE的重叠差值。oo_wakeups只计waiter通知事件，不代表unique消费者或early-ready人群；tag_evictions不等于bank冲突。AE CPU oracle的bank冲突不代表真实输入测量。K0无K1专属frame，填UNAVAILABLE而非0。DRAM n_ref_event继承未初始化，不比较；实际read/write atoms由互斥命令计数求和，atom32B由冻结BL2×buswidth16×chips1确定，不用DTC128B credit代替下行字节。

原SASS输入不提供load返回值、真实happens-before、同SM查询复用/实际Tag驻留或native数值正确性。全输入sim严格通过也只是有界timing/identity模型检查。静态固定hash、容量与有限quota约束不是SRAM面积/频率/端口综合结论；AC若纳入必须明确新增结果存储，不能称免费技巧。AD未资格，AF机会未证明。
