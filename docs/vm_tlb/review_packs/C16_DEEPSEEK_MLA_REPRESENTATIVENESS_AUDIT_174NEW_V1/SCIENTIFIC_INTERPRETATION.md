# 科学解释

## 实际缓存了什么

V26/V27测到的是Transformers 4.51.0 eager实现的`DynamicCache`：16头BF16 key（每头192维）和16头BF16 value（每头128维）。它不是512维compressed MLA latent。S2 decode1后实际cache为20,981,760字节，S3为83,896,320字节。

## 哪些属于MLA本身

精确模型源码先形成512维低秩latent，并单独形成64维RoPE key；16头Q/K维度、低秩投影和RoPE解耦属于该模型的MLA语义。上下文从2049增至8193时，无论选择latent cache还是展开cache，保存的token数量与总容量都约增长3.998536倍。

## 哪些属于当前实现

accepted eager源码选择在cache update之前展开：复制RoPE分量到16头，并缓存完整每头K/V。由此实际cache为10,240 B/token，而source-implied latent形态为1,152 B/token，容量放大8.888889倍。QK再直接读取该展开key的转置视图。后续Transformers源码已经改为先缓存单头latent/RoPE、再展开，证明V26/V27表示不是MLA不可避免的要求。

## 如何重读15.99倍events

S2→S3 active-lane events为15.988312倍，但cache长度/字节仅为3.998536倍；同时selected paths从20变131、executed paths从16变24，median executed-shard events约增长7.996340倍，且accepted authority明确记录S2/S3函数不同。因此15.99倍是上下文扩大与实现/launch/static-path变化的混合结果，不能解释成MLA固有流量，更不能当DRAM字节。

## 是否值得继续

现有结果不支持设计cache/TLB机制。若项目仍关心部署代表性，唯一值得的后续是同模型、同输入、同语义下“展开cache实现 vs latent-cache实现”的最小匹配比较；它应先验证容量和runtime行为差异，再讨论性能。本Goal不授权GPU执行。
