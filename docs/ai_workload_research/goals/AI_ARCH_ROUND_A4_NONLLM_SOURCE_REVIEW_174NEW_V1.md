# Round A4｜非LLM动态图自然输入与强消费者兼容性审计

**执行者：Codex Lane N／174-new CPU-only（第二独立窗口，可与Lane T并行）**  
**Stage：AI_ARCH_A4_NONLLM_SOURCE_FEASIBILITY_V1**  
**权限类型：SOURCE_ONLY；不是109 GPU、174模拟器、模型训练或机制执行授权。**  
**科学归属：AI-ARCH Discovery。AWMA Round21历史实验/源码结论只读，不重开AWMA R21。**

## 一、具体科学问题

在**真实几何变化**、GPU邻居构建、合法topology/skin复用及当前强等变张量积后，究竟存在什么**已知语义保持的producer→consumer数据与索引准备**？谁需要receiver和source两个视图？能否找出自然完整能量/力路径中的潜在关键成本，而不是重新发现Sobek已经消除的大边张量？

## 二、必读资料和固定公开源码

1. AI-ARCH协调分支`Round A3`、`Round A2`、[AWMA Round21](https://github.com/swayhrl/accel-sim-framework/blob/0b8310ee4afe8429b3ed2de381594794ee12ae31/docs/vm_tlb/literature_notes/awma/rounds/2026-10-02_ROUND_21_POST_R20_PROBLEM_DISCOVERY.md)以及`ROUND21_SOURCE_REGISTER.tsv`。**先列已核过的C01–C09事实，后仅补新的接口/输入缺口**。
2. [Sobek arXiv 2607.18074v1](https://arxiv.org/html/2607.18074v1)及[固定源码](https://github.com/Cortex-Discovery/sobek/tree/c1f815bfee1de420342c7b660fb2b1f9eab2441e)：重点`sobek/nn/tpconv/graph.py`、`tpconv.py`、`README.md`；区分uvw/uvu约束、radial-linear输入、edge indices和`sender_perm`、forward/gradient阶数。
3. [ALCHEMI Toolkit-Ops固定源码](https://github.com/NVIDIA/nvalchemi-toolkit-ops/tree/32445c5f00e83fccd475589f1a6f5ac9e81e6b02)；看`docs/userguide/components/neighborlist.md`及最新官方公开文档的GPU selective rebuild；区分matrix/COO/tile、periodic shifts、skin、必要容量/overflow检查和host sync。
4. [NequIP源码固定commit](https://github.com/mir-group/nequip/tree/27d9d2182da918ab7be0017d8300e53278f5e00e)与已收录的OAM-S官方模型页、Si extxyz 64原子输入`mir-group/nequip-tutorial@8f90935ba42fd9e03df323cf03428c456d87b881`。MACE替代候选只在公开模型/配置清楚时才检查；ALCHEMI示例在加载失败时回退Lennard-Jones，**必须登记此风险，不能把回退当神经网络结果**。

## 三、有界审查工作（不要实现新的pipeline）

- **节点预检与隔离**：确认174-new磁盘、CPU/RAM负载、Git source/ref；若资源不足STOP，不能与Lane T共享输出/同一可变工作区。只读取已有仓库或少量公开源文件；不全量clone、不安装GPU依赖。
- **消费者语义兼容性矩阵**：是否有真正同构的张量积连接类型、内部/外部weight、径向网络最后投影、edge ordering/periodic shifts、features layout、float32/混合精度、force gradient顺序；NequIP/OAM-S和Sobek不匹配的地方清楚写`INCOMPATIBLE/UNVERIFIED`，不能靠“都是equivariant”认为可以互换。
- **producer→consumer数据契约**：ALCHEMI生成哪种邻居数据、cell/skin是否可复用、如何产生发送者/接收者CSR、双向排序、`sender_perm`及后续Graph缓存；谁是必需步骤，谁是历史重复工作；禁止假设每层/每步一定重新sort。
- **自然几何可用性**：Si extxyz与MD22候选分别检查frame count、元素/单位/周期盒子、模型适用域、公开输入SHA能否取得；**只有真实连续时间索引可认证，才允许估计rebuilt frames频率**。没有真实连续性则只做independent geometries，不伪造MD轨迹。
- **结果边界**：目标region应是给定几何→GPU合法邻居准备→完整神经网络能量+需要的一阶force→结果可用；训练double backward另计、绝不因加大瓶颈而自动加入。只有source支持的API，不能声称已原生运行/计时。
- **是否可辨识**：若没有可兼容的强模型/后端和自然几何，保留`NO_NATURAL_MODEL_CONTRACT_YET`；若官方直接COO/prepared graph已完整覆盖，先归为`SOFTWARE_SUFFICIENT_POSSIBLE`，不立硬件。

## 四、交付与科学裁决

只新增：
`docs/ai_workload_research/reviews/AI_ARCH_A4_NONLLM_SOURCE_REVIEW_174NEW_V1.md`

至少包括：
1. 冻结公开源码ref、原文节/图与最新资料可能差异；
2. (model+geometry)候选及语义合法性matrix（PASS仅针对源码可确定部分）；
3. neighbor producer→CSR/perm→强TP consumer之间真正的数据、同步、缓存和数值契约；
4. 哪些输入是论文合成图、哪些有真实训练或几何帧、哪里仍未披露；
5. 最多一个未来合法观察region设计或明确无准入，资源/STOP；
6. 来源分层：PAPER_AUTHOR/SOURCE_CODE/OUR_HYPOTHESIS/UNKNOWN，不写任何新NATIVE_MEASURED。

只在自己branch/worktree commit/push并远端fetch-back；禁止merge实验分支或直接改`hrl/ai-workload-research-coordination`。报告exact HEAD、文件路径与证据限制，由ChatGPT后续独立审查。

## 五、严格禁止

不运行109 CUDA/JIT或其它GPU任务、不运行174 Accel-Sim、不下载模型权重或真实几何大数据、不建立MD平台、不修改AWMA R21/R22与R27R3、C16旧Stage A，不调容差或制造不同模型算法的“等价”对照。不下载/执行未知脚本或安装large dependencies。遇到有歧义的模型接口或真实时间顺序，直接标UNKNOWN/STOP该分支，不把工程兼容性“修”成科学合同变化。
