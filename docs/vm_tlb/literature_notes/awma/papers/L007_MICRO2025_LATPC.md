# L007｜LATPC: Accelerating GPU Address Translation Using Locality-Aware TLB Prefetching and MSHR Compression

**Ha等，MICRO 2025，pp.418–431。DOI：10.1145/3725843.3756069。** 复核日期：2026-09-26。

## 阅读证据

来源为用户提供的`3725843.3756069 (2).pdf`，15页（含封面），SHA256：`d7f32ee8c4ac0afa8c7de88056a0f0d67d22a5b295ba26d5e489186820ea6735`。已读全文，本轮复查图10/14；更细的既有全文笔记见本仓库`docs/vm_tlb/chatgpt_handoff/awma/post_novelty_reset_v1/LATPC_FULL_TEXT_REVIEW_AND_LANE_ADDENDUM_V1.md`，authority `3594aa192a9362dbd5b15e8bd7508773a17cc1a7`。

出版入口：https://doi.org/10.1145/3725843.3756069 。PDF不随笔记上传。

## 原文：已有能力与新增能力

已有coalescer先把同一动态warp指令的同VPN请求去重，输出unique VPNs；这不是LATPC新增。[§2.1，p.419；§5.1–5.2，图10/12]

新增三部分：Regularity Detector逐个处理unique VPN并提取Base/Stride/Index；LATC用Base+Stride+32-bit mask在一个MSHR中跟踪多个**不同VPN**的miss；LATP批量处理相同叶级页表区域的walk，共享前序遍历，叶级PTE仍分别读取。[§5.2–5.4]

32个mask位置不是32个同页等待者。它的根到叶命名为L1–L4，与Neighborhood论文相反。按512-page范围分组的条件依赖本文页表/页大小/DRAM行模型。

## 实验与限制

主模拟为RTX2060-like、30SM、4KiB页；24个传统GPU workload主动选择VM压力样本。1.47×是相对已有合并、无预取baseline的IPC几何均值，不是LLM推理整体速度。表2主L1 MSHR为16项，不是引言举例的12项。[§6.1–6.2，表2/3]

RTX4080 Super/CUTLASS是页大小动机小实验，不是LATPC真机实现。2MiB实验还改变部分workload footprint；不能把1.47×与1.18×解释成只改变页大小的同一组对照。[图2；§6.6]

硬件建模给检测器及MSHR tagging各加1cycle，并有技术库/存储估计；本文数值不直接转成AWMA PPA。[§5.5]

## 我的比较判断与启发

它进一步支持AWMA先补warp内去重基准。不是因为LATPC与旧PREL1逐行相同，而是我们欲宣称的新能力已有很大部分属于它的baseline。

若剩余问题是多页分散和miss跟踪压力，这才是需认真移植/比较的候选。当前AWMA的max-one/two-page样本不能自动承接作者高分散动机；也不能为了得到结果把64KiB改4KiB而不改变研究问题声明。

有价值的方法警示：§7中MSHR subentry能力会改变Valkyrie的增量。因此“在旧/弱基准上有效”不能代替“超过合理已有能力”。

## Related work可用句与边界

可用：LATPC在同指令页请求去重后，利用VPN规律减少miss跟踪资源压力并组织批量遍历。

不可用：LATPC只是同VPN合并，或其基线没有coalescer。
