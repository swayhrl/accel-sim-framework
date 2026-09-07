# C1：sub-entry 语义证据审计

状态：`PASS — REFERENCE_APPROX_SUBENTRY_16`（`SPECULATIVE_CANDIDATE`）。

审计范围限定为本地受跟踪材料、目标作者公开条目，以及两个可公开访问的参考
资料；没有继续无限检索。目标论文的本地材料确实指向 sub-entry 方向，但没有给出
可复现的叶选择、组替换、索引函数、容量换算或时序。作者公开条目也没有提供目标
实现的代码/工件。因此，依据 Window C 已授权的后备选择，采用
`REFERENCE_APPROX_SUBENTRY_16`，而不是把缺失的内容伪装成论文事实。

冻结语义如下：

- 仅在 64KiB 基页的候选 L2 模式下，一条组 entry 覆盖连续 16 个 VPN；tag 为
  `(ASID, VPN >> 4, page_size)`，leaf 为 `VPN & 15`。
- base-tag 未命中和 base-tag 命中但 leaf 无效都是 L2 翻译未命中；只有两者均命中
  才是 L2 TLB 命中。
- 组是填充、LRU 和替换单位。向同一组填充新 leaf 不驱逐 sibling；组替换清除全部
  16 个 leaf，并分别记录有效 leaf 的对象归因驱逐。
- 组数量/相联度、L2 port 和 L1/L2 lookup 时序沿用现有 M4C paper shell；这是一项
  `MODEL_DECISION`。索引沿用当前 generic hash 的形状但使用 base VPN，也同样不是
  目标硬件声明。
- 2MiB + sub-entry 被配置验证显式拒绝；标准 exact-page 模式仍完整支持 2MiB。

逐条来源、标签和限制见
[`PAPER_SUBENTRY_EVIDENCE_LEDGER.tsv`](PAPER_SUBENTRY_EVIDENCE_LEDGER.tsv)。
