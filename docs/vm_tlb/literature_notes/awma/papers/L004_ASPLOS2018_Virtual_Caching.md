# L004｜Filtering Translation Bandwidth with Virtual Caching

**Yoon、Lowe-Power、Sohi，ASPLOS 2018。DOI：10.1145/3173162.3173195。** 复核日期：2026-09-26。

## 阅读证据

[作者入口](https://arch.cs.ucdavis.edu/gpu/memory/2018/03/24/gpu-virtual-caches.html)；[原文PDF](https://arch.cs.ucdavis.edu/assets/papers/asplos18-gpu-virtual-caches.pdf)。本轮核§3、§4、评估条件与限制。在线图6/7截图失败；设计描述依据正文，不据未读图形填新数字。

## 原文：问题、增量与实现

作者观察到不少TLB miss访问的数据仍驻留缓存，因此用虚拟寻址L1/L2过滤翻译需求：数据不在虚拟cache层次时才访问共享翻译结构。它改变的是翻译位置，不是把同页请求合并。[§3、§4]

Forward-Backward Table维护缓存页面的VA/PA关系，承担同义地址、一致性请求和失效管理；权限随缓存行检查。这些是方案组成部分，不能只移植“跳过TLB”。[§4.1]

非inclusive GPU缓存情形下，读写synonym处理有保守fault限制。论文在其一致性/集成GPU模型下验证，而非证明该结构可直接用于Ada独立显卡。[§4.2、§5]

## 我的比较判断

“数据已经可访问时不重复翻译”“让cache过滤translation bandwidth”已有直接工作。未来若研究翻译推迟、旁路或tensor局部命中，必须先分辨它是否只是虚拟cache能力的改写。

这不是当前Lane E应当立刻实施的补丁：缓存tag、地址域、权限、一致性与shootdown都会受影响。它与只改翻译请求生成的经典去重参考不属于相同改动规模。

## 待验证问题／复现入口

可低成本先问：强基线后的翻译等待对应的数据，位于L1/L2还是确需访问内存？联合事件比单看TLB miss rate更能确定研究位置。这里是拟议诊断，不是已测AWMA事实。

对照不能使用PA索引cache命中结果为尚未翻译的VA免费决策。必须先给出实际可获得信息及保护协议。若没有模型支持，保留为范围较大的邻近方向，不用零延迟oracle代替。

## Related work可用句与边界

可用：该工作通过虚拟cache层次移动翻译边界，以过滤共享翻译带宽需求，并处理相应VM管理问题。

不可用：首次提出“尽可能晚地做地址翻译”。
