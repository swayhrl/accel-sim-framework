# L003｜MASK: Redesigning the GPU Memory Hierarchy to Support Multi-Application Concurrency

**Ausavarungnirun等，ASPLOS 2018。DOI：10.1145/3173162.3173169。** 复核日期：2026-09-26。

## 阅读证据

作者提供的[原文PDF](https://www.pdl.cmu.edu/PDL-FTP/PowerMgmt/mask-asplos18.pdf)。本轮复核§4.1–4.4、§5.1–5.4文字。在线截图失败，本轮不据图形读取新数值；不是新完成的全套视觉复核。未复现实验。

## 原文：问题、增量与实现

背景是多地址空间并发：共享TLB抖动、页表请求与普通数据在缓存/DRAM中互相干扰。作者也明确讨论翻译完成后多个等待warp连续发送数据请求。[§4]

三项机制分别控制不同边界：TLB-Fill Tokens限制哪些warp可填共享TLB，不禁止其他warp查询；translation-aware L2 bypass处理页表数据对数据缓存的污染；translation-aware DRAM scheduling提高page-walk服务优先级并兼顾应用公平和吞吐。[§5.2–5.4]

这些是在多应用并发模型下评估的联合改动，不能把整体收益归给其中任意一项，也不能直接套到一个孤立Qwen kernel。[§5、§6]

## 我的比较判断

“翻译完成产生数据突发”“优先处理翻译”“感知压力控制资源”都不足以单独形成AWMA创新。需要定位到具体决策点及其未解决约束。

但MASK的DRAM页表请求优先级，并不等于它已经实现了AWMA的L1端口head/prelaunch仲裁；也不等于一个地址空间必有其多应用TLB抖动问题。

## 待验证问题／复现入口

先区分压力在共享TLB容量、数据L2、DRAM还是请求发起端。不同问题对应不同对照，不应把整套MASK移植作为所有新机制的前置任务。

在当前单kernel研究中，若只见下游排队，应先确认真正争用资源及翻译/数据请求类型。不可把GPU scoreboard register hazard数直接当作被某个翻译阻塞的warp数。

## Related work可用句与边界

可用：MASK联合管理翻译与存储层次中的干扰，说明减少翻译延迟与保护数据访问性能需要协同考虑。

不可用：无人研究翻译服务与数据请求的相互作用。
