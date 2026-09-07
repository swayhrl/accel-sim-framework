# C2：L2 sub-entry 候选验证

状态：`PASS — SPECULATIVE_CANDIDATE`。

实现使用与标准 `set_associative_tlb` 分离的 `subentry_tlb`：64KiB 页面按
16 个连续 VPN 组成一个 group，group LRU/替换而 leaf 独立有效。标准模式仍走原有
exact-page L2；`2MiB + sub-entry` 被配置验证拒绝。

`vm_m4b_subentry_test` 覆盖 group/leaf hit/miss、填充、sibling 保留、替换、端口、
计数和标准模式隔离；并与 M1--M4C 和 C3 定向套件共同完成 18 项通过。真实 decode1
单 kernel smoke 也以候选模式退出码 0 完成。

冻结选择、证据边界与不可宣称内容见 `C1_SUBENTRY_SEMANTICS_AUDIT.md`；本文件中的
结论不构成 target 硬件已被精确复现的声明。
