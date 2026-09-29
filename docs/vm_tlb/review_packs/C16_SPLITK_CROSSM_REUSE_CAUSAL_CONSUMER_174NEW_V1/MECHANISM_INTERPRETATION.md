# 机制解释

K2560 split1在PER_MTILE下L2 hit从90.5%降至35.5%，DRAM增至5.93倍、timing增至3.39倍。K3072同方向但hit损失较小。split8两个K的约95.9%高hit均降至约28%，DRAM增至5.51/6.11倍。新增miss sectors×32B与新增GEMM DRAM高度一致。跨M combined weight-side地址共享因此是高L2 hit的重要来源，split-K的小局部集合有助于复用存活。

边界：不能细分qweight/qzeros/scales；PER_MTILE也扩大VA/TLB footprint；不推断replacement；不推广到所有GEMM/LLM。
