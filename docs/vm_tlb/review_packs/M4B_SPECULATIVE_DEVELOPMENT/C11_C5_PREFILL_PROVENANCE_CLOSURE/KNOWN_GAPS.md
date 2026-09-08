# 已知边界（不是 C11 blocker）

- capture 没有实际 hardware PPN/page-map。C11 因而明确使用且只使用
  `MODELED_DRIVER_PA`；不得将其写成实测 PA。
- archive-level SHA256 的再次全量读取不是 C11 的低影响 provenance audit；A frozen
  `FORMAL_ARTIFACT_LOCK.md` 已记录 SHA256 和 `zstd -t PASS`，C11 对 archive path/
  size/readability 与 list/sidecar 做了当前检查。
- F6 仍是 `DIAGNOSTIC_NOT_EQUAL_COST_PRIMARY`。C9 V2 registration 的唯一正式 mapping
  class 是 pinned-contiguous-64KiB，不能让 2MiB selector 偷用 64KiB descriptor 并宣称
  common PA。因此 F6 不作为 C11 C5 execution point；这不是移除 comparator，而是防止
  不公平或未授权的 2MiB driver mapping architecture。
- 本包没有运行任何 C5 trace、没有生成 trace、没有 KV segmentation/12K/M5。
