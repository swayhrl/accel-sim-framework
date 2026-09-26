# L010｜Valkyrie: Leveraging Inter-TLB Locality to Enhance GPU Performance

Trinayan Baruah等；PACT 2020；DOI `10.1145/3410463.3414639`。复核：2026-09-26，Round 02。

## 阅读证据

作者公开PDF正文关键章节：§2.3、§3、§4、§5及敏感性讨论；不是仅摘要，也不宣称作者代码已复现。主入口：https://people.bu.edu/joshi/files/pactfp17-baruahA.pdf 。作者镜像：https://sarchlab.org/valkyrie_pact_2020.pdf 。本轮两处PDF页面截图均失败，表1/2按可解析文字及正文核对；图形柱高不转录为精确数值。浏览器可读正文，不等于本地已取得PDF字节，未登记猜测的文件哈希。

## 原文：新增能力

§3组合了LDT指导的跨L1翻译复制、同Shader Engine内环形探测，以及将预取缓冲从原L1容量中分离的组织。重点是其他CU可能已持有所需翻译，而不是同一warp内同VPN去重。预取直接占用需求TLB还会破坏邻居可探测的翻译驻留，二者需要共同设计。

## 实验入口

MGPUSim的AMD R9 Nano模型、64 CU、4KiB页；不是AWMA Ada模型。表2的十个工作负载及footprint见 `../empirical/ROUND02_DATA.json`，其中七个作者标为TLB-sensitive、三个为对照。正文明确数值与表格录入，未从失真的解析图中文字还原柱值。

敏感性数据必须保留分母和样本范围；正文部分mean未在相邻句重复列出参与样本，不自行把它展开成十条逐workload数值。页大小敏感性不能直接与LATPC改变footprint的大页实验求差。

## 我的比较判断

它是跨SM翻译局部性、复制与探测候选的直接近邻；不是当前同指令去重实现的逐细节等价物。不能把“本SM miss但其他SM有”“按共享关系复制PTE”“复制和替换共同决定peer供给”重新当作未经研究的新发现。

## 待验证问题（不是实验结论）

若AWMA出现L1 miss压力，应先测同一时刻peer命中机会与本地/L2服务代价，不能仅测整个执行期间多少SM触碰同一页。若同页集合很大但同时驻留很少，静态共享率不能支持远端查询结构。另需控制复制造成的需求容量损失及网络成本。

## Related Work可用句与边界

可用：Valkyrie利用跨L1翻译局部性，联合复制、邻居探测与预取存储组织。
不可用：其结果证明所有LLM、所有页大小或现代GPU内部都有同等远端翻译收益。
