# 科学解释

源码与精确枚举支持：split8把每个split的qweight唯一集合降为总qweight的1/8，同时每个split仍访问一半qzeros/scales metadata。GPT-3 K=12288时，每split静态unique weight+metadata为43,646,976 B（41.625 MiB），低于64 MiB；split1完整集合为313,786,368 B（299.25 MiB）。2560完整集合为62.34375 MiB，3072为74.8125 MiB，所选K点确实跨越容量附近。

源码还证明固定split/Ntile的weight与metadata地址不随Mtile变化，因而不同Mtile静态上重复消费同一集合。线性block ID中，同一Ntile跨相邻Mtile的距离为384，中间经过383个其他Ntiles。

这些结果只支持启动最小native threshold screen；它们不证明真实CTA执行顺序、L2命中、替换或唯一容量因果。若native timing与DRAM不随完整集合跨越L2区间而系统变化，应降级当前机制假设。
