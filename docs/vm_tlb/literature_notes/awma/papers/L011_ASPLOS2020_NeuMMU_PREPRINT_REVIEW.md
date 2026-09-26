# L011｜NeuMMU: Architectural Support for Efficient Address Translations in Neural Processing Units

Bongjoon Hyun等；ASPLOS 2020论文；DOI `10.1145/3373376.3378494`。复核：2026-09-26，Round 02。

## 阅读证据与版本

本次实际阅读的是作者预印本：`arXiv:1911.06859v1`，2019-11-15，14页，https://arxiv.org/pdf/1911.06859 。重点核§II-C、III-C、IV、V/VI；已看印刷p4 Table I、p8 Fig10–12、p11 Fig16。最终会议版与预印本差异未核，不把预印本数值自动当成会议版逐字确认。代码/实验未复现，本地PDF字节未取得。

## 原文：研究问题与组合方案

SPM型NPU的分块DMA产生翻译突发。方案包含miss后同页pending请求合并（PTS/PRMB）、增加PTW并行吞吐，以及按walker保留上层翻译路径的TPreg。它不是GPU pre-L1合并，也不是仅扩大TLB；PRMB结果按周期返回，不能忽略分发成本。

## 实验与可迁移边界

配置、工作负载组和数字见 `../empirical/ROUND02_DATA.json`：128×128阵列、8通道、固定内存延迟/带宽模型，非cycle-level DRAM。密集CNN/RNN与稀疏NCF/DLRM的访存和迁移行为分开处理；较大batch只测部分代表层，不冒充整模型训练。

版本内部保留一个未调和差别：Table I的activation/weight SPM为15/10MB，§III-C示意叙述使用各10MB；不私自统一成同一配置。作者页表层号从根L4到叶L1，与LATPC根L1到叶L4相反，引用时保留各自记法。

## 我的比较判断

NPU结论不能直接推出“LLM GPU的TLB无用”。有用的是分开检查驻留局部性、未完成请求重复、不同页的并发需求、迁移粒度。相同“AI负载”标签不能抵消SPM/DMA与warp/cache执行模式的差别。

## 待验证问题（不是候选授权）

若AWMA剩余问题是短时服务需求，先区分缺失容量与到达速率；同VPN去重后仍存在多少不同页？合并之后的吞吐是否足够？无此证据，不移植128 PTW或据此修改页大小。

## Related Work可用句与边界

可用：NeuMMU联合未完成请求合并与翻译吞吐扩展，针对SPM型NPU的DMA需求。
不可用：所有AI GPU均应以吞吐代替局部性，或者该文的oracle性能能作为AWMA理论上界。
