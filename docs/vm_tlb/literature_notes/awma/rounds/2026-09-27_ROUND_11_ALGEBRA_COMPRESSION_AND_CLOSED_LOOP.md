# Round11｜代数重写、无损数据流、跨CTA执行与闭环AI负载

日期：2026-09-27。维护：ChatGPT。**文献支线，不是执行Goal；未运行论文代码、下载模型或占用109/174。**

## 1. 当前映射与阅读口径

用户已明确保留窗口名称：**Lane F＝R101，Lane G＝R102，均在109**。旧Round10文件中的H/I只作为历史别名，不要求正在执行的窗口改名、重启或切换branch。当前R101/R102合同保持不动。

本轮登记15项核心工作：12篇正文关键方法/实验/局限章节；1项作者技术文章与源码；1项摘要加源码；1项会议元数据加artifact。另核6个作者仓库文件与NVIDIA cluster文档。28条实验/分析组记录不等于28项已复现实验。部分是已有方向的近邻重读，不作为全部新增论文数。

CREDIT正文抓取未成功，ClusterSim完整论文未取得；二者不升级为全文或实验核验。作者事实、源码事实与我们的推导分开。

## 2. R101近邻：有限映射、代数计算图和实现是三层

R1101 Polar Express的系数是离线确定的，不是在每步训练中重新求解；附录J还讨论矩形计算重写与低精度稳定化。修改多项式、正则化、迭代数或矩阵划分，都可能改变有限步映射，不能仅因极限polar factor相同就称严格同一任务。

R1102 Gram Newton–Schulz把矩形问题的迭代转到较小Gram对象，数值实现用restart保持稳定；另有对称GEMM和融合epilogue。正方形情况并非一律走Gram重写，作者采用标准NS的对称kernel路径。公开专用kernel要求Hopper/Blackwell，不能当4080已资格。

**我们的判断：**这不要求F中途更换S128/K128实验。F的同shape机制响应仍有意义；未来若要推广“必须把A/B/C留片上”，应检查是否已有代数/对称软件能减少相同中间对象。HiMuon的`M*N<=16384`是所读实现的dispatch边界，不独立证明硬件容量下界。

## 3. R102近邻：编码输出还需要匹配消费者

R1103 UCCL-Zip将压缩与发送交叠，并把collective压缩放入kernel；其P2P尺寸曲线使用合成BF16，RL组另有真实权重，不混成一类输入。§4.2位字段文字与前文描述不一致，本轮不代作者补齐。

R1104 DFloat11采用动态长度编码、LUT和两阶段展开；容量受限LLM的主要速度对照包含CPU offload。R1105 ZipServ则以同一格式区分阶段：decode融合解压/GEMM，prefill采用先展开再计算。部分DFloat11对照尺寸由整block实测线性缩放，并非全部直接测量。

**我们的推导：**无重叠时可先核算`Tenc + Mc/B + Tdec < M/B`；有流水时必须检查critical path，不能直接加独立分项。压缩比、changed-element比例、首块ready与receiver可消费时刻是不同指标。G的真实before/after input若缺失，这些论文的分布或压缩比不能替代它。

这不是另开压缩lane：先作为G结果的比较依据。reference存在Triton TODO也不是硬件瓶颈证据；软件有解不排除成本更低的硬件，但必须面对强软件能力。

## 4. 新训练后备：loss与梯度累加的生命周期

R1106 CCE前向不物化完整logits，但仍需全词表LSE。反向过滤小梯度是另一机制。原文记录初始pretraining受到过滤与低精度累加影响，改用Kahan和FullC后再验证；微调成功不能直接替代pretraining结论。

官方C1104源码README已有`cce_exact`，表示关闭classifier和embedding两侧梯度过滤，并非保证与torch逐bit相等。R1107 Liger FLCE还有chunking与forward内梯度组织，构成直接强软件对照。

**后备问题，不执行：**冻结无过滤的loss forward/backward，比较中间态保存、重算和梯度累加的完整成本；不是R81 grammar词表问题换名。如果现有CCE/Liger/compile路径足够，就不开发专用loss机制。

## 5. 跨CTA不是免费扩大片上容量

官方D1101说明cluster从SM90起支持，blocks共驻同一GPC；DSMEM访问还要求参与blocks保持存活。4080/SM89不能冒充原生cluster平台。

R1109 ClusterFusion是直接近邻，较大cluster并不单调获益。R1108 CREDIT所读代码`effective-bandwidth-overlap-v2`用非DSMEM baseline的有效带宽估算重读节省，并扣控制、局部replay、store残差、remote store。它是已读源码模型，不称已核实的论文全套结果。

R1111 ClusterSim的artifact有cluster寄存器、mapa/barrier.cluster、launch API和SM间互连；默认H100配置不等于与AWMA SASS/SM89校准自动兼容。本轮不迁移174。

**比较框架：**省下的global物化/重读，应与remote访问、同步、共驻限制、独立并行单元减少和更长状态寿命一起核算。

### 5.1 ClusterFusion++的量纲问题

R1110 v1 §4.1把`1.31MB / 1.8TB/s`写成约`0.73ms`。我们的十进制量纲复算是：

`1.31e6 / 1.8e12 = 7.28e-7秒 = 0.728微秒 = 0.000728毫秒`。

原表报告5.32→4.90ms是作者观测；该字节/带宽估算不能解释这项差值。这里只登记**单位错误与归因不足**，未重现实验，也不推断实测虚假。其near-token-identical输出与未改变的PPL同样不等于decode逐token完全一致。

## 6. 拓宽负载：推理时VJP与动作时效

R1114 RTC在guided inference中计算向量—雅可比积，**推理也可能需要activation及局部反向状态，而不更新权重**。作者机器人设置模型延迟为baseline76ms、RTC97ms；控制改进不是kernel更快。Kinetix受控delay、真实机器人、LAN及额外注入delay分开记。

R1115 VLASH用旧动作推进自身状态估计以匹配新动作执行时刻，不是预知未来环境；v2又有action quantization和共享观测训练，不能把这些效果都归于异步runtime。

R1113跨平台VLA论文的性能组使用固定224×224图片和提示，质量另用LIBERO；Orin power mode同时改CPU/GPU/内存。R1112 Alpamayo主要与容量受限HF offload比较，分层估计的全驻留对照不是同卡真实全驻留执行。

**我们的后备入口：**固定guided policy下的短时VJP状态生命周期。未来需要区分模型时间、chunk产生率、`t_apply-t_observation`、动作连续性与任务质量。先做真实policy小片段的输入/source设计，不下载新机器人模型，不把局部replay当闭环任务结论。

## 7. 保留三张问题卡，不新增执行窗口

| 卡片 | 下一步必要证据 | 不继续的情况 |
|---|---|---|
| S11-A：有限矩阵函数计算图 | 消费F结果，比较对称/Gram与片上retention各自改变什么 | 剩余收益由现成等价软件覆盖，或改变了有限映射 |
| S11-B：loss反向中间态 | 同一无过滤合同下的强CCE/Liger基线 | 只是弱eager开销或质量变化 |
| S11-C：推理VJP状态 | 真实policy/输入及反向消费者依赖 | 没有真实状态，或只是不同控制算法的比较 |

压缩流水作为G近邻，不追加第三条相似lane；DSMEM作为可能的未来能力对照，不重建平台。小原型可帮助发现原因，不要求先证明5% headroom；最终仍需成本、消融与未参与设计的验证。

## 8. 核心来源登记

| ID | 工作与版本 | 深度与关键边界 |
|---|---|---|
| R1101 | Polar Express，2505.16932v5 | 正文关键章节；有限步与稳定化分开 |
| R1102 | Gram NS，作者2026技术文章 | 技术文章+README；非假定正式会议稿 |
| R1103 | UCCL-Zip，2604.17172v2 | 正文关键章节；合成P2P/真实RL分开 |
| R1104 | DFloat11，2504.11651v3 | 正文关键章节；NeurIPS2025元数据，offload与resident分开 |
| R1105 | ZipServ，2603.17435v1 | 正文关键章节；部分对照为推导 |
| R1106 | Cut Your Losses，2411.09009v2 | 正文关键章节+源码；过滤与无过滤分开 |
| R1107 | Liger，2410.10989v3 | 正文关键章节；整套与单kernel效果分开 |
| R1108 | CREDIT，2609.01864 | 仅摘要+作者README/成本模型 |
| R1109 | ClusterFusion，2508.18850v1 | 正文关键章节；属于近邻重读 |
| R1110 | ClusterFusion++，2604.23553v1 | 正文关键章节；量纲问题保留 |
| R1111 | ClusterSim，IISWC2025 | 元数据+artifact；完整论文未取得 |
| R1112 | OOM-Free Alpamayo，2605.11678v1 | 正文关键章节；RTCSA accepted由元数据支持 |
| R1113 | Cross-Platform VLA Scaling，2509.11480v2 | 正文关键章节；固定性能输入与质量组分开 |
| R1114 | Real-Time Chunking，2506.07339v1 | 正文关键章节；模拟与实机分开 |
| R1115 | VLASH，2512.01031v2 | 正文关键章节+README；不用旧版17.4×混合新版数字 |

## 9. URL与源码blob

- R1101 https://arxiv.org/html/2505.16932v5
- R1102 https://dao-lab.ai/blog/2026/gram-newton-schulz/
- R1103 https://arxiv.org/html/2604.17172v2
- R1104 https://arxiv.org/html/2504.11651v3
- R1105 https://arxiv.org/html/2603.17435v1
- R1106 https://arxiv.org/html/2411.09009v2
- R1107 https://arxiv.org/html/2410.10989v3
- R1108 https://arxiv.org/abs/2609.01864
- R1109 https://arxiv.org/html/2508.18850v1
- R1110 https://arxiv.org/html/2604.23553v1
- R1111 https://doi.org/10.1109/IISWC66894.2025.00048
- R1112 https://arxiv.org/html/2605.11678v1
- R1113 https://arxiv.org/html/2509.11480v2
- R1114 https://arxiv.org/html/2506.07339v1
- R1115 https://arxiv.org/html/2512.01031v2
- D1101 https://docs.nvidia.com/cuda/cuda-programming-guide/01-introduction/programming-model.html

作者源码读取日期2026-09-27；只绑定实际返回blob，不伪造未查询的main commit。

| ID | Repo / path | Blob SHA |
|---|---|---|
| C1101 | Dao-AILab/gram-newton-schulz / README.md | 282897d18538a7c7eb35ea986d66dea8a5818b0f |
| C1102 | zhengxiongli08/CREDIT / README.md | e541c3bf8c6d031b91cf14ec837f2c7d3a11a74d |
| C1103 | zhengxiongli08/CREDIT / dsmem_eval/cost_model.py | 3c7ef0483fbbcd875a78192f14ef7b1688568435 |
| C1104 | apple-aiml-research/ml-cross-entropy / README.md | 3d43c40d2b294ea33400443f9d43910d72bfc3b8 |
| C1105 | Tim453/ClusterSim / README.md | 1048050df9662fd4b358d7e31ae5fd96580df4a6 |
| C1106 | mit-han-lab/vlash / README.md | 6b057051e1a7bb8789c03ddae1a63bc594cede0b |

C1104旧apple路径返回301，按repository id887718293查到新owner；不据旧URL失败宣称artifact不存在。

完整中文报告另含15张阅读卡与28条实验组TSV。当前状态：`ROUND11_LITERATURE_COMPLETE_NO_NEW_EXECUTION`。只写文献目录，不改accepted实验、raw、R101/R102 Goal或执行分支。
