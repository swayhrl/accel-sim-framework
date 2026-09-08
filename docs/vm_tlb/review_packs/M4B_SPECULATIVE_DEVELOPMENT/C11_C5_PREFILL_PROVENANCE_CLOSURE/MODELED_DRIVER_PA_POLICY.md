# `C5_MODELED_PA_HIGH_UNUSED_BIT_V1`

## 结论

原始 capture 记录了受 runtime binder 约束的 SimVA allocation，却不包含可用的
GPU PPN/page map。因此 C11 采用 C9 已允许的 `MODELED_DRIVER_PA`，不把该 PPN
称为测得硬件 PA。

固定策略是：对于每一个 admitted 64KiB Weight page，

```text
SimPA = SimVA + 0x0000c00000000000     # 3 × 2^46 bytes
SimPPN = SimVPN + 0x00000000c0000000   # 3 × 2^30 pages
```

它是一次性、性能结果无关的 mapping decision；没有根据任何 replay 调参。

## 为什么不是单一 bit 48

初看 bit 48 位于 SM86 explicit DRAM mapping string 中的高位 `0` 区。然而 C11
审查了真实 C5 shell，而非只看该 mask：

- `gpgpu_memory_partition_indexing 2` 选择 IPOLY；
- `src/gpgpu-sim/addrdec.cc:144-154` 将 `rest_of_addr_high_bits` 输入 IPOLY；
- `src/gpgpu-sim/hashing.cc:49-70` 的 32-way IPOLY 实际消费低 0..14 位；
- L2 配置 `S:64:128:16,...:P` 也使用 IPOLY，`gpu-cache.cc:126-130` 对
  `partition_address >> 13` 计算高位 hash。

12 个 memory channel 走 `gap` path。单 bit `2^48` 使 `(addr >> 8) % 12`
发生变化，故它不能诚实地声称“不改变 placement”。C11 拒绝了该方案。

## 选择 offset 的源码可验证证明

选择的 `3×2^46 = 12×2^44` 满足：

1. `(offset >> 8) = 3×2^38` 可被 12 整除，因此 channel residue 不变；
2. gap-path 的 IPOLY input 增量恰为 `2^36`，在 32-way IPOLY 读取的 0..14 位外；
3. `partition_address` 增量为 `2^44`，L2 IPOLY-64 的高位输入增量为 `2^31`，
   在其读取的 0..18 位外；
4. L1D 是 linear set index，set bits 在低位；DRAM bank policy 为 linear，且
   explicit row/bank/column mask 不使用这个高区。

`util/vm_tlb/c11_c5_artifact_tool.py --validate` 对两段的全部 15,442 个
admitted page base、全部 32 个 IPOLY preliminary index 逐项验证第 1–2 点，
并静态断言第 3 点的地址位界。

这只保持 C5 各 arm 的 channel/subpartition/cache-set placement 公平；physical
tag 本身当然变为 nonidentity，这正是 C9 所要求的 translation 语义。

## namespace、安全与不重叠

两个 source VA extent 均小于 `2^47`；加上 offset 后小于 `2^49` 的 C9 modeled
PA limit，并使 PA bit 48 为 1、source VA bit 48 为 0。64KiB offset 未改变，页内
offset 和 page adjacency 完整保留。每段的 prefill/decode PA extent 相互不重叠；
validator 同时检查 wrap、PPN 33-bit overflow 与 descriptor overlap。

此规则是 `MODELING_DECISION`，不是 PPA 或真实 allocator claim。
