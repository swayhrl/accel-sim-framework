# R21准备卡｜动态几何图到等变能量/力计算的就绪边界

2026-10-02。**PREPARATION ONLY。不是已成立性能机会，不是execution Goal；GPU/109/174/训练全部未授权。**

## 问题

GPU邻居构建、合法skin复用与prepared-graph跨层共享已经存在。真实拓扑更新以后，consumer所需双向CSR、边置换和chunk-source执行计划是否仍占完整能量/力计算的明显成本？同语义其它强后端是否已解决？

## 已核源码

- Sobek：`c1f815bfee1de420342c7b660fb2b1f9eab2441e`，graph.py blob `667a4056c7760c06e8f1538a06ece4afc9b01313`；有stable sort、双向CSR和chunk/source计划，亦已有缓存。
- ALCHEMI Toolkit-Ops：`32445c5f00e83fccd475589f1a6f5ac9e81e6b02`，neighborlist.md blob `d7f07b98b5731ca6d90c934fbc84a89b2db6d374`；GPU算法、多格式、容量和重用能力必须纳入。
- Sobek边大张量的流式化、cuEquivariance/OpenEquivariance primitive不算新候选；OCTANE应作为邻居列表近邻进一步核全文，当前只有机构说明。

## 第一关：不要开始建平台

只做一个trained几何模型的接口/输入核查。MACEWrapper与MD22可作公开来源入口，但尚无模型/数据hash闭合；MD22数组顺序不是已证实的时间顺序。必须证明实际模型与消费者模式/所需导数兼容，不能改模型迁就库。MACE演示的LJ fallback必须禁用或显式失败。若source显示最合适后端不需要这些准备、或现成接口已消除重复，则直接记录并停止，不先移植Sobek。

## 后续小实验角色（另行冻结合同后执行）

Bstrong：同语义强实现＋GPU邻居构建＋预分配＋合法重用＋跨层prepared graph共享。区分真实需重建帧与合法复用帧，不能人为每帧重建。

Dready：同一帧完全相同拓扑/索引在计时前准备好；当前几何特征、网络前向及所需力求导仍计算。只作敏感性诊断，不叫线上收益或严格上界。

Spublic：公开接口直接消费compatible邻接格式/置换、共享prepared graph。生成/维护结构成本全部计入。不能把普通接口集成收益自动升级硬件。

主要边界：当前帧坐标/类型/周期盒已就绪→能量/力提交。不做演化轨迹的bitwise复现、不训练、不加不需要的double backward，不跑全模型/shape网格。

## 决策

在candidate前冻结离散edge coverage/periodic-image/cutoff身份，及基于模型和reference的能量/力数值合同；不复制R20 outer-niter门槛或LLM容差。失败先保存输出及差异再退出。重复校验与正常测量合并，不另开长期资格平台。

强软件之后准备成本小、合法复用摊薄、必要搜索/算术主导、另一后端更好、没有真实输入或移植过重，均停止。只有完整区域稳定响应，才设计一个有成本的小干预并留出未参与选择的帧。

当前结论：**源码支持一个可检验的问题；新颖性、真实性能、SM89适用性和input authority均未闭合。** R20不重启。

完整讨论与来源：`../rounds/2026-10-02_ROUND_21_POST_R20_PROBLEM_DISCOVERY.md`、`../empirical/ROUND21_SOURCE_REGISTER.tsv`。
