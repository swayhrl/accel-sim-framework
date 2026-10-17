# EP-L2 EN-v7 — 研究叙事与论文论证结构（独立编辑线）

2026-10-17。此文是论文改写蓝图，不是科学资格/硬件实现/实验配置变更，也不向Lane6已发布EN-v6-r21或Lane5科学账本直接写回。

## 一句话中心思想

**A cache line can stop being resident long before its dirty data stop being needed. Cache organization should transfer ownership at that boundary instead of automatically relocating the bytes.**

中文：**Cache行的Tag已经被替换，并不意味着其脏数据的生命已经结束。把替换理解为数据所有权转移，而不是数据物理搬迁，才能按各自真正的消费者回收资源。**

EP-L2并不主张首次发现“地址和数据分离”“dirty块暂存在LLC”“缓存存储可以共享”。精确的机制贡献是：在可复用旧Tag的同时，让dirty victim继续持有原来的banked payload slot；为新resident找到另一个合法landing；并将payload的本地释放与WB同地址排序责任完成分开处理。先前VWQ/last-write/DBI等作为明确的背景和约束，不是简单忽略的对手。

## 从技术报告到研究论文：六段真实逻辑

1. **Architectural tension / 背景矛盾：** Tag可见驻留、dirty数据本地驻留、WAD排序责任有不同的最后消费者，却被传统固定角色分配的实现捆在一起。强制resident→WBUF copy是在换角色，并非更新数据。
2. **Motivating failure / 需要回答的现象：** 本文B16基线在向WBUF复制128B时多占两次模型bank服务且受16条配额限制；受控五负载中三者有大量WBUF-full尝试。不过拒绝次数不是全局停顿，不直接证明性能损失。
3. **Core insight / 洞察：** Eviction is an ownership transfer, not necessarily a data movement. 新来的resident取得新landing；旧dirty payload不搬走，保留到lower真正接收；WAD继续到set_done。
4. **Hard part / 为什么设计不显然：** 1024 resident Tags、1168 128B payload slots、4banks、每bank每物理GPU周期至多一次128B服务；合法landing受bank约束。跨周期Bank拒绝和其它way的Fill可能改变重probe的LRU victim，必须把同一请求绑定到固定pending victim。WAD、MSHR、sector、generation/pin都需保持一致。
5. **Evidence / 证据：** 同预算、同binary和完整non-atomic SASS trace，五组CURRENT_ACCEPTED。所有观测的resident→WB copy消除，三负载WB-data-full消失；H0 geomean只有1.0016002037656606×且CFD退化。减少内部工作不等于应用加速，不能包装成明显性能提升。
6. **System implication / 更大意义：** 单独优化cache内部动作不足以确定GPU执行收益，下一步要区分“有限静态配额”和“下游服务/竞争”。Q4/D4独立成对诊断可确定适用资源区间；等总容量静态重划分及RTL/时序/PPA才可裁决动态弹性和净硬件代价。

## 建议论文标题和读者路径

首选：**EP-L2: Decoupling Tag Residency from Dirty-Data Lifetime in GPU L2 Caches**。
备选：**EP-L2: In-Place Ownership Transfer for Dirty Data in Banked GPU L2 Caches**。
不推荐“Maximizing GPU Performance through Elastic L2”之类无法用0.160%支撑的标题；也不推荐只写“优化WB Buffer”的低层次题目。

| 章节 | 读者需要带走什么 | 现有材料 | 需要避免 |
|---|---|---|---|
| Abstract | 三个生命周期、ownership transition、同预算、实际结果、价值边界 | H0五组、原位WB代码 | 8条验收术语与逐句自我否定 |
| Introduction | eviction结束Tag residency但不结束dirty数据需要，形成设计矛盾 | B16与U对照、VWQ/DBI | 用“首次解耦”夸新颖性 |
| Design | precheck→保留victim身份→新landing→Commit→t_a→t_d | Core `7b8e6ac7...`真实源码、31定向 | “要么锁定要么回滚”二选一当算法 |
| Methodology | 同总资源、同binary、完整输入与检验支持的范围 | Lane5 V2、H0五组 | Lane ID、hash、gen堆在正文 |
| Results | copy节省与WBUF配额解除为什么未必转化cycles | H0 Fig2/3、CFD反例 | 把累计拒绝事件减到cycles上 |
| Discussion / sensitivity | 后端与静态配置决定机制的有效区间，正反案例都值得解释 | r19 Q4/D4与待做强静态 | 选择有利条件当主H0平均 |
| Related Work | 过去工作分别改进dirty candidate、控制信息、MSHR与数据分配；本文解决post-eviction ownership | R20十二文献 | 总称别人都做copy |
| Conclusion | 它证明了何种可实现的协议能力；性能和PPA还有何问题 | 31项 + H0 | 0.16%升格为显著架构性能提升 |

## 已核对正式源码：跨周期事务不是“或许有两种实现”

- Core `7b8e6ac70b8fe0f1bd37efca11acb5284938825d` 的 `gpu-cache.h::tag_array::bind_ft_replacement`保存同一frontend在途请求指针和被选tag index。
- `gpu-cache.cc::tag_array::probe`在同一请求跨cycle再次probe时将变化的raw replacement candidate重定向到既有held victim；不同填充完成不会让同一FT事务改选victim。测试确实覆盖竞态Fill改变候选。
- `ep-l2-ft-cache.inc::ft_access`执行前置missq/MSHR/dirty WAD/合法landing检查，创建WAD及staging或landing reservation；Bank请求拒绝时同事务重试。最终native `data_cache::access`失败则`ft_rollback`恢复尚未提交的payload/tag身份和相关资源，不能撤销已消耗的Bank服务。
- dirty transfer到`WB_STAGED`后，`lower_accepted`只有在真实packet/lower数据承载交接时才释放旧payload，WAD直到WB完成(set_done)才释放。完整数值SASS正确性及RTL PPA没有由此自动证明。

## 现在论文能说什么，不能说什么

**已可说：** 合法的Bank-limited原位WB机制；Tag/dirty data/WAD的分离退休；现有五个完整non-atomic trace上零resident→WB copy，B16局部配额约束被解除；H0性能近乎持平及服务计数发生变化。

**尚不能说：** 动态池优于合理同总容量静态分割；任意GPU程序普遍更快；显著节能、节约面积或时钟不受损；TVD/RO已经并入这些应用结果；D4更快内存必使U-WB更快；数值SASS输出已经完整验算。

## r19新观测的处理：不能反向包装

截至独立审查的一次Lane5回执，D4 Convolution B16=267521、U_WB16=268544，U相对B退化约0.38%；它是该条件下的正式接受结果，但目前尚未合并进Lane6论文侧native intake。不要因为此结果与原假设方向相反就移除，也不能据一点推出系统级完整因果。优先等FWT和Q4成对后看S(h)、J(h)以及实际WBUF、WAD、下游服务；即便“越快越好”不成立，也可能揭示不同资源瓶颈的竞争关系。

## 与正在执行的Lane6如何合并

- 本编辑目录完全独立；先从最新Lane6 HEAD读取EN-v6-r21及后续真实D4/Q4 scientific intake，再挑选叙事重写的安全部分。
- 本次候选保留Fig1/2/3、H0五组全部原数和十二项引用；不覆盖H0原始CSV、科学V2与已有发行记录。
- 复制候选LaTeX到Lane6后必须带上原`figures/`、`references_verified.bib`，重新pdflatex/bibtex检查实际4+1页、图和引用；本协调草稿本身不是已编译/已验证的正式投稿PDF。
- 优先保持“问题→洞察→为什么难→机制→实验证据→边界”段间逻辑，而不是为了四页逐项挤压字号。

**此处所谓“包装”是提升抽象层次和论证节奏，不是放大数字或制造未测的物理成本。**