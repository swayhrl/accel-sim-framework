# DQ3：内存/服务候选定位

MP01/MP05 过去合法的局部 Tier0 screening 仍是线索：两点的 attention、gate/up 和 down projection 有非平凡 Graph-OFF 区间权重与源端布局/kernel 线索；activation 未过局部 3% 门槛。这些不是 L1、L2、DRAM 或 TLB 服务时间测量，也没有识别成熟 Graph-ON 整请求中对应的精确贡献。

对 MP02/MP03 compiled decode，Python-hook 观测失败且 compiler-native 映射停在 `LEVEL_0_UNRESOLVED`；没有可辩护的 kernel→语义 family 时间分摊。仅有 traffic、kernel 名、静态 FX 节点或历史 Mode C 比例，均不能替代 native timing exposure 加 service-time attribution。

终态：`DQ3 = QUESTION_INCOMPLETE`，decode 缺口为 `COMPILED_DECODE_MEMORY_SERVICE_ATTRIBUTION_NOT_IDENTIFIABLE`。现有线索不足以授权 Tier1，也不能宣称某级缓存或 DRAM 是瓶颈。
