# MP03 B4 continuation：缓存身份独立复核

本复核仅读取 164 durable 的 continuation `MP03_B.json`、`CACHE_BEFORE.json`、`CACHE_AFTER.json`、运行与 GPU/lock receipt，并对照事前冻结的 `31af510d85e89344acf6e4c519ae5f0419d50d40`。五个缓存 root 的 before/after 文件清单、逐文件 size/SHA、聚合内容 SHA 完全相同，详见 `CACHE_IDENTITY_RECALCULATION.tsv`。这是对已发布快照的独立比较；174 没有访问、清除或重建 109 的在线 cache。

本次只启动 MP03_B，旧 MP02_A、MP02_B、MP03_A 的 JSON SHA 与原 durable raw 精确一致，未重跑。GPU UUID 与 PREEXEC 相同，lock 已取得并释放，保守 GPU-active 为 9.442614 秒。预热前 AOT root `/torch_aot_compile/e3e9e809…` 的路径、347 文件及内容 SHA `49c6e49f…` 通过合同门槛，内嵌 Qwen2 源码身份亦通过。两次 warmup 均有四行，各行 32 个 token 与原冻结数值规则匹配；`Qwen2Model` 仍有有效 AOT compiled function，`enforce_eager=false`、`VLLM_COMPILE`、`inductor`、无 CUDA Graph，attention/linear 分别为 `FlashAttentionImpl` 和 `UnquantizedLinearMethod`。

但两次 warmup 后的实际 `local_cache_dir` 仍指向上述 `e3e9e809…` AOT root，而 PREEXEC 要求最终转到 `/c97581f1bb/rank_0_0/backbone`，其冻结内容 SHA 为 `3f78b163…`。所以 `DQ2_EXECUTION_IDENTITY_FAIL` 的严格含义是：**在本 continuation 合同规定的两次 warmup 后，MP03_B 没有复现 9122 所绑定的最终 compile-cache 执行身份；formal timing 无合法准入。** 原版 MP03_B 在更早的旧 cache-path gate 停止，warmup/formal 均为 0；continuation 的 formal 仍为 0。

这不是 Mode B 推理错误、关闭 CUDA Graph 导致错误、AOT 路径无效或 B4 必然更慢的证明。也不能称 c975 路径为唯一正确的 vLLM 实现；它只是**本次事前合同**要求匹配的执行身份。warmup 正确性不能代替缺失的 formal 计时。本轮不提出第三种 cache identity policy，不再救 MP03_B。
