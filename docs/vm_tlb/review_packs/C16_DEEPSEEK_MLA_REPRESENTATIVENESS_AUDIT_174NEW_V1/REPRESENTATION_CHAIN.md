# 表示链审计

## A. MLA源码中的latent表示

精确配置为16个attention/KV heads、`kv_lora_rank=512`、no-PE维128、RoPE维64、value维128。源码先生成`compressed_kv`，拆成512维latent与单头64维RoPE key。若按源码可表达的压缩缓存形态保留两者，BF16每token为`(512+64)*2 = 1152`字节。

## B. V26/V27实际runtime cache

accepted Transformers 4.51.0 eager源码在cache update之前执行`kv_b_proj`，构造16头key `[B,16,T,192]`和value `[B,16,T,128]`，再把这两个展开tensor传给`DynamicCache.update`。因此实际每token缓存`16*(192+128)*2 = 10240`字节，不是latent cache；相对1,152 B latent形态放大`8.888888889x`。

## C. QK直接消费表示

QK query为`[1,16,1,192]`；key operand是cache key的转置视图：S2 `[1,16,192,2049]`，S3 `[1,16,192,8193]`。receipt中的storage pointer一致，说明QK消费展开后的persistent key（prefix加当前append），不是512维latent。转置视图不应再次计入cache容量。

A、B、C不是同一表示：A是source-implied latent，B是accepted eager runtime的展开cache，C是B的QK转置消费视图。
