# L008｜Marching Page Walks: Batching and Concurrent Page Table Walks for Enhancing GPU Throughput

**Lee等，HPCA 2025。DOI：10.1109/HPCA61900.2025.00123。** 登记日期：2026-09-26。

## 阅读状态：仅作者摘要，尚未取得全文

[作者页面](https://ipoom-jeong.com/publication/marching-page-walks-batching-and-concurrent-page-table-walks-for-enhancing-gpu-throughput/)已读。其出版方PDF入口本轮未成功取得。**不能将此条与已读正文笔记混为一类；以下不是完整算法复述。**

## 作者摘要足以支持的内容

工作以PTW排队为问题，组合批处理与提高walker并发访存能力，试图降低等待、提高GPU吞吐。它是“减少请求数”和“提高实际遍历服务能力”之间的重要近邻。

## 仍为UNKNOWN的内容

批组的精确匹配条件、单walker并行的依赖处理、有限表项与端口、回退与公平策略、全部实验配置、与LATPC及Neighborhood的逐项比较，均未从本轮原文证据核实。不从标题推断是同VPN、同PTE-line或同叶级页表分组；不从LATPC引用它就复制LATPC参数给它。

## 我的用途判断

若Lane E暴露真正PTW/PWQ压力，它应进入优先全文获取清单。若仅剩L1-hit延迟，它不是当前必须完整复现的基线。

暂可作为相关研究存在的引用，不能用来证明“该论文没有某种规则”，更不能依据摘要判定我们的新方案已避开它。

## 下一次补读定位

先找核心结构/请求流图、并发依赖状态机、容量/端口表，再读实验对象与各子机制消融。取得全文后更新本条状态与来源，而不是覆盖掉本轮未读状态的历史。
