# Open value semantics

Architectural load数值、STORE/ATOMIC payload副作用、多SM coherence、release/acquire/scopes和完整ISA支持均 **UNPROVEN**。本包合成`warp_inst_t`与真实`mem_fetch`仅携带地址、identity和时序，没有SASS architectural load值oracle；也未运行CPU shadow-value oracle。即使以后加入shadow oracle，它只能发现元数据允许的潜在过期读，不能冒充SASS load值证明。

旧consumer在E后仍由旧physical完成证明的是生命周期保留；E后同址miss证明的是lookup不可见。读回何值还依赖下层写可见性、ordering与scope。无选中source事件时旧Tag仍可能命中，K1不会自动修复L→S→L或跨SM可见性。

OO结构资格不以完整ISA证明作为假定前提，但不能推广成数值或coherence PASS。K1-07的完整STORE/ATOMIC/BYPASS/PROXY+ACK路径仍PARTIAL，IO orphan未实现STOP，MODERN HOLD。未运行完整Gaussian/GEMM，没有新执行authority，AA2完整模拟仍由其既有授权单独控制。
