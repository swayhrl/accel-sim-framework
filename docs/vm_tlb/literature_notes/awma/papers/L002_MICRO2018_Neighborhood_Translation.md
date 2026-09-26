# L002｜Neighborhood-Aware Address Translation for Irregular GPU Applications

**Shin、LeBeane、Solihin、Basu，MICRO 2018。DOI：10.1109/MICRO.2018.00036。** 复核日期：2026-09-26。

## 阅读证据

作者提供的[原文PDF](https://www.csa.iisc.ac.in/~arkapravab/papers/micro2018_neighborhood.pdf)。本轮核查§III–V及结果解释；PDF第6页图7、第8页实验表已视觉复查。未复现实验。

## 原文：问题、增量与实现

一次页表内存读取带回整条cache line，而一个PTE只占其中一部分；不同VPN的在途/待处理walk可能需要同一行内的其他PTE。作者让返回的页表行帮助完成邻居walk，或完成其部分上层遍历，而不是仅用返回的一个PTE。[§III、§IV]

IOMMU buffer增加部分完成层级、下一访问地址、可合并标记；PWST跟踪各walker。预计可由已有walk服务的待处理请求暂不单独发起，因此它有真实等待策略，不是免费并行广播。[§IV，图7]

该文叶级称L1、根级称L4；4KiB页、8B PTE、64B cache line下，叶级邻域为8个页面。评估为集成GPU/gem5、规则与不规则负载，不是当前AWMA平台。[§III、§V-A]

## 我的比较判断

需分清三种粒度：相同VPN、不同VPN但PTE在同一cache line、不同VPN位于同一叶级页表/DRAM行。它们的共享内容、硬件匹配与收益来源不同。

本方案也不是AWMA已经否定的“到accessq-head后才复用PPN”：这里在PTW返回时消除尚未执行的邻居页表访问。不能把AWMA那个负结果推广为“一切返回时共享都太晚”。

## 待验证问题／复现入口

若Lane E显示miss侧压力，先统计强基线后不同VPN的PTE-line重叠和请求是否同时存活。只见地址邻近、不见并发待服务，不能直接计算可省walk数。

对照至少需要正确的PTE cache-line粒度、部分walk状态和等待策略；不能把多个不同VPN直接共用同一PPN。若当前平台页表布局无法对应，应先说明映射假设，不硬套32KiB邻域。

## Related work可用句与边界

可用：Neighborhood-aware walking利用页表cache-line粒度，把一次页表读取的内容用于多个相邻翻译请求。

不可用：此前只有同VPN合并，或者首次提出让相邻页共享页表访问。
