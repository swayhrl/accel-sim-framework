# 下一阶段 DTC 结构方向与最小实验合同草案

本文仅供 DTC-L1-11 科学审查。**当前授权的新增模拟、request、预算和 GPU 采集均为 0**；以下结构候选没有自动获得实现或执行资格。E1 指本轮固定同 build OFF 的 Oracle 观察，E2 指历史真实结构实验在各自身份和配置下的响应，E3 是尚待验证的机制假设。E1/E2 不能互相替代，也不能当作 E3 因果证明。

## 三项优先方向

| 优先 | E1：本轮观察 | E2：历史真实结构响应 | E3：待验证的有限机制与关键反证 |
|---|---|---|---|
| 1. 下游服务与本地完成协同 | GESUMMV/MVT/ATAX/BICG 对三种 data-availability 干预强响应；vectorAdd、scan 也有正响应 | GESUMMV DH-P0/F128/F256 为 89,502,220/86,464,623/90,151,547 周期；vectorAdd 为 217,305/213,053/236,217，正负并存 | 在保留 sector 回复、有限注入/返回队列、generation/Ref 守恒和有限 notify/collect/WB 的条件下协调服务。若仅换阶段或加容量却出现同等/更慢，必须接受该反证；不复制 Oracle 虚拟服务为免费硬件。 |
| 2. PIB/Ref 与 physical 生命周期 | L1 虚拟 data-ready 仍保留真实 Tag/physical/PIB，却在若干输入强响应；3MM/GEMM L2 精确零而 M/L1 有响应；ready/collect 均值仅提示可查阶段 | V2 Physical×PIB 的 16 个已接受点在 fixed8 只有约 0.78%/0.84% GM 变化；其他历史 E/M/Q/F 点也有正负 | 审查 admission、完整引用注册、有限 completion 之间的耦合，设计能证明无丢 credit、无旧 generation 误唤醒、无跨 warp 次序假设的候选。physical 占用不能直接当成活跃压力。 |
| 3. Tag 映射与前进性先验安全 | Oracle 未消除 512 logical Tag、640 physical 与 PIB 压力，无法从 L1 大响应单独归因 Tag | 已有 1024Tag/physical640 两种候选达到合法 `NO_FREE_LINE` 无前进状态，16 格安全 HOLD、未启动 | 先在隔离 CPU fixture/源码级证明 Tag 与 physical 回收的前进性及 Ref 保护。只有独立安全复核通过、用户另批新身份和预算后，才可谈实际模型；当前 HOLD 不解除。 |

## 候选 1 的最小实验合同草案

此草案供批准时改定，**不是启动指令**。候选定义必须先给出源代码级作用点、有限队列/端口/容量和时序、sector 与 parent 生命周期、硬件状态位/面积估计及失败处理；不能使用无限服务、虚拟全命中或绕过非 eligible 请求来制造性能。生产 Core、现有 Oracle binary、Source、论文和历史台账保持冻结。CPU fixture 先覆盖 32/64/128B 与部分 mask、重复/迟到回复、generation、Ref 与 credit 守恒、队列背压、公平性、fence/store/atomic 和终态 drain；独立安全审查未 PASS 即 HOLD，不注册科学请求。

若另获明确科学授权，可考虑一个 **预登记** 的 10 输入首批：GESUMMV、MVT、ATAX、BICG、vectorAdd、scan（机会正例），3MM、GEMM（L2 精确零对照），myocyte、srad_v1（L2 回退对照）。这 10 个在见候选性能前固定，不按结果换程序。一个冻结候选 binary 下，每输入实际运行同 build、同非候选选项的 OFF 和候选，共 **20 个新科学格**；既有 Oracle OFF 与历史 DH-P0 均不可代替新 OFF。若后来要覆盖固定 CORE32 剩余 22 输入，须在首批终态、lifecycle、数值范围说明、资源/成本及独立审查合格后，由用户另行核准精确增加 **44 个新格**；不得从旧 request 余额或 UUID 中借用。实际阶段/预算以未来批准文件为准。

每格固定输入 digest、trace/command scope、Core/Framework/binary/lib/config/options SHA、真实 native PID/start/UUID、完整 kernel 序列及 CTA/active instructions、每 kernel 与总周期、队列/sector/Ref/PIB/physical/完成路径原口径计数、strict、true164 归档和 native typed restore。输出包括所有正、精确零、负、失败和缺失；在相同实际接受交集上算 GM，不能只选择胜出模式或只用初始正例。面积/PPA、有限吞吐、功耗及 CH 强基线另列为需证明或 UNKNOWN；没有证据时不写等面积/可实现同量收益。对原生完整应用数值、capture ELF/输入内容和 coherence 仍需独立资格，不能由当前 trace strict 自动晋升。

方向 2/3 若进入执行，必须有独立具体合同、Source/成本/安全门槛及新预算，不能沿用本草案的 20 格或自动共享候选 1 的资格。尤其 1024Tag HOLD 和跨组回收不得借此解封。下一科学授权前 STOP。
