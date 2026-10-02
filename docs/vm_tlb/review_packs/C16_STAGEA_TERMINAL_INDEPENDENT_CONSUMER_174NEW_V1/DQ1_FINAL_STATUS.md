# DQ1：自然关键路径组成

历史合法的 MP01 BF16 prefill 证据保留：在其 Graph-OFF 相关 CUDA 区间内，attention、gate/up 和 down projection 的局部权重通过 3% screening；activation 低于 3%。MP05 AWQ B1 仅是不同表示/运行路径的支持性 control，不是 MP01 或 BF16 decode 的可替代样本。两点的 Graph-OFF 局部比例均不能自动变成成熟 Graph-ON 的整请求贡献，whole-run ceiling 仍未识别。

MP02/MP03 compiled decode 所需的语义时间分摊没有形成：Observer V2 的 Python hooks 在编译路径上得到 0/4608，Lane7 对已有 FX/Inductor/cache 与 runtime kernel 名的映射判为 `LEVEL_0_UNRESOLVED`。静态图顺序、通用 kernel 名、operation count 或 FLOPs 均不能补出逐 family wall union；历史 Mode C 语义比例因正确性 STOP 更不能迁移。

终态：`DQ1 = QUESTION_INCOMPLETE`，decode 缺口为 `MP02_MP03_COMPILED_DECODE_SEMANTIC_ATTRIBUTION_NOT_IDENTIFIABLE`。保留 MP01 的局部发现，但它未升级为完整问题或 Tier1 准入。
