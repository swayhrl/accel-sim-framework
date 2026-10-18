# Fixed logical cost estimate — no synthesis claim

这是预估的组合逻辑描述，不是面积、频率、功耗或硬件零延迟证明。没有RTL综合/PPA或GPU/应用运行。

S=2^s时，bank为L[1:0]原连线，row低s-2位是两个不重叠字段逐位XOR；set拼接row和bank。常量移位/掩码/4×及加bank可视为连线/截取，不能由此把XOR、enable选择、扇出及布线说成零面积。

|固定geometry|row bits|两输入XOR数量（组合逻辑功能量级）|若硬件同时保留OFF/ON|
|---|---:|---:|---|
|S=32，W=4或8|3|3|约3个bit的old/hash row选择，加policy控制/布线|
|S=64，W=4或8|4|4|约4个bit的old/hash row选择，加policy控制/布线|

XOR之间并行，逻辑深度约一个XOR层；运行时可切换实现还可能串接enable mux。地址到达时间、row decoder前的critical path、bank/Tag fanout、geometry可编程选择和实现工艺都可能引入额外代价。本模拟保持已有Tag读延迟和service quota，等价于假设该逻辑能装进原索引预算；此假设应由后续硬件研究独立检查。

Tag entry仍保存完整logical line key和原physical identity/LRU，数量S×ways不变；比较位宽、physical数据位宽和80KiB数据池不变。没有因hash增加way、访问端口、PIB或服务宽度。test报告中的C++`sizeof`仅用于对照host字段布局，不能当芯片bit/mm²。

若将来声称优于ordinary C+，需同Tag/数据容量、ways、延迟、端口、配额与一致性条件的C+ hash控制，并统一计入hash时序和成本。本轮C+源码保持原样，不能据合成miss变化推出DTC独占收益或应用speedup。
