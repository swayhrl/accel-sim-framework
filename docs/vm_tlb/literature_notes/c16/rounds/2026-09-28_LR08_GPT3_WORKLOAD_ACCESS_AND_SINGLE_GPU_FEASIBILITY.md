# LR08：GPT-3在体系结构论文中的含义、可获取性与单卡研究可行性

日期：2026-09-28。维护者：ChatGPT。

本轮仅做原文、作者代码、公开可获取性核查和算术推导；未执行GPU、作者artifact、模型下载或新的模拟。不是Codex执行handoff，不改变Lane4，不插入Lane6/7/8当前任务。

## 1. 问题与结论

用户问题：GPT-3是否是当前AI负载/访存体系结构研究的主要对象？一张RTX4080 16GB和现有Accel-Sim能否获得并分析GPT-3或关键层？

判断：GPT-3是重要的经典大Dense结构参照，不是当前研究唯一或必需的中心对象。原始OpenAI训练权重、公开结构重建、独立训练的GPT-3式benchmark checkpoint、OPT等开放替代模型必须分开。我们可以在4080上研究GPT-3-175B公开尺寸的关键算子甚至单个block，而不必取得或驻留整个175B模型；这属于结构/形状驱动的合成负载，不能称原始GPT-3实机复现。

## 2. 可获取性：配置不是checkpoint

截至本轮核查，未找到OpenAI原始GPT-3训练权重的官方公开下载途径。官方openai/gpt-3仓库README列的是生成样本、合成任务数据、数据统计、重叠样本和model card，不是模型权重。[S1]

2025-08-05官方gpt-oss发布说明明确称其为GPT-2之后首批开放权重语言模型；当前官方open-models页面展示gpt-oss及其衍生系列。gpt-oss不是GPT-3。这里不推断任何非公开合作方是否持有权重。[S2]

公开API访问不等于本地权重或本地GPU执行，不能用远程输出获得该模型在自己的4080上的kernel、地址trace、cache/TLB计数。

必须保留一个例外：MLPerf中的GPT-3式训练基准确有定制checkpoint。MLCommons说明其基准从随机初始化预训练，生成稳定的定制checkpoint，再由提交者继续训练；这是独立构造的基准资产，不是OpenAI原版权重。[S5]

## 3. 回到具体论文/实验组，而非只数GPT-3名称

| 工作 | 本轮核对范围 | 实际实验对象/方法 | 不能推断的内容 |
|---|---|---|---|
| LLMCompass，A Hardware Evaluation Framework for Large Language Model Inference | arXiv:2312.03134正文§III/IV相关段落；作者repo的transformer/matmul代码 | §IV使用GPT-3单层、FP16、batch8、输入2048、4-way TP；作者GPU矩阵乘校准路径显式用torch.randn生成两个operand；系统/算子性能模型与GPU校准分层 | 不能说原始GPT-3-175B checkpoint在单卡完整运行；不能把某个randn路径等同于全部结果的实现 |
| NeuPIMs: NPU-PIM Heterogeneous Acceleration for Batched LLM Inferencing，ASPLOS2024 | arXiv:2403.00579 §8.1与Table3；PDF第10页截图核表 | 列GPT3-7B/13B/30B/175B配置；按模型、batch、TP/PP及ShareGPT/Alpaca长度分布合成系统workload，采用周期级模拟；GPU-only基线单列为A10040GB实机 | 原文这些设置不能证明取得了OpenAI原权重；序列长度分布不是逐token自然执行轨迹 |
| MLPerf GPT3训练基准 | MLCommons2025-05-05官方方法说明 | 独立训练的定制checkpoint与继续训练过程 | 不是OpenAI原始checkpoint；训练基准不是C16推理微架构证据 |
| FlashInfer | arXiv:2501.01005v2 §4.1 | serving实验采用Llama3.1-8B/70B；kernel与端到端实验分开 | 不代表整个研究领域的模型使用率 |
| SpecMD，2026预印本 | arXiv:2602.03921v1 §5.1及实现章节 | OLMoE、Mixtral、Qwen1.5-MoE、Phi-3.5-MoE研究expert管理 | 软件显存expert cache不是硬件L2；这里只用于说明该类问题需要MoE对象 |

LLMCompass作者代码定位：
- repo `PrincetonUniversity/LLMCompass`；读取时main commit `2e015fd2ee750e6cad8d7152df52551e5b41ef20`；实际tree `50b317994ef1239667401c02c9cfb3d854487862`。
- `software_model/transformer.py` blob `96867e69b3041d0babf14c5d8bc11c54ddb9e72f`：TransformerBlockAutoRegressionTP保存形状Tensor、按device_count切权重/heads，并组合算子与通信成本。
- `software_model/matmul.py` blob `a4db3fc1b0175595a0c646b31420e4fdb7f222ad`：`run_on_gpu`中input1/input2由torch.randn和目标M/K/N构造。
- 本轮未执行artifact。上述代码是本轮获取的固定commit，不冒充论文提交时的原始commit。

为什么论文使用频繁：公开尺寸、重复decoder结构、大矩阵与历史可比性使其适合成本建模。这是我们的归纳，不代替作者未明确披露的模型选型动机。

当前代表性：2025年MLPerf Training v5.0已用Llama3.1-405B替换GPT3基准。官方选型讨论提及RMSNorm、RoPE、GQA等更新。[S5/S6] 这只说明训练基准演进；结合上表推理实例可判断研究对象已多样化，不能据几篇论文给出全领域频次或市场占有率。

## 4. 原始175B配置与重要细节

GPT-3论文Table2.1与§2.1：[S3]
- 96个Transformer层；
- hidden size H=12288；
- 96 attention heads，head dimension128；
- FFN宽度4H=49152；
- 原论文context window2048。

原论文明确交替使用dense和locally banded sparse attention。不能默认96层全部dense，再声称忠实原版复现。若只测一个dense层或dense FFN，明确范围即可；未核清局部稀疏mask细节前，不自行创造所谓原版sparse层。

原版结构使用GPT-2式FFN，不应直接套用Qwen的gate/up/down三投影。任何8K/32K合成context也是超出原训练context的敏感性实验，不是自然GPT-3长上下文能力测试。

## 5. 4080容量计算：以下均为公式推导，不是实测峰值

按每个参数2B的FP16/BF16，忽略bias、norm、embedding和workspace；主矩阵采用计算视角的[K,N]：

| 矩阵 | shape | 参数量 | 权重字节 | MiB |
|---|---|---:|---:|---:|
| Q/K/V合计，是否融合另行定义 | [12288,36864] | 452984832 | 905969664 | 864 |
| attention输出投影 | [12288,12288] | 150994944 | 301989888 | 288 |
| FFN升维 | [12288,49152] | 603979776 | 1207959552 | 1152 |
| FFN降维 | [49152,12288] | 603979776 | 1207959552 | 1152 |
| 单block主权重合计 | 12H² | 1811939328 | 3623878656 | 3456 |

即单block主权重约3.375GiB，单个FFN矩阵1.125GiB、两矩阵2.25GiB。

B1、2048位置、完整MHA的单层紧凑K/V：
`2(K,V) × 1 × 2048 × 12288 × 2B = 100663296B = 96MiB`。

因此在推理模式、不保存训练梯度/optimizer、控制workspace的小batch场景，单block容量原则上适配16GB卡；具体峰值仍必须实测，不能声称所有batch/backend都能放下。

完整175B仅参数：FP16/BF16约350GB(decimal)，即326GiB；理想4-bit打包仍87.5GB，约81.5GiB，另加metadata/KV/临时空间。取得权重与能否GPU全驻留是两个独立限制。

### TP局部形状不可忽略

同一FFN矩阵FP16全尺寸1152MiB；假设按可整除轴做TP8，单分区144MiB，理想4-bit数据36MiB。未切分的理想4-bit矩阵则288MiB。这只是算术示例，不是GPT-3原版量化checkpoint，也未计scale/zero。

所以“GPT-3-175B”标签相同，TP设置不同，每GPU工作集和缓存机会也会差很多。单卡可研究一个分区的局部算子，但不能把缺失的通信、其他分区和同步当作免费，更不能据此给多GPU端到端性能。

## 6. 三条可执行路线及范围

### A. 公开尺寸的合成算子/单block——当前最合适

按原论文尺寸和显式backend构建，无需175B下载。优先FP16/BF16 FFN或dense attention，固定seed、有限值分布、dtype、layout、输出reference。109上实机记录kernel/计时/必要计数，174只在后续明确批准后处理少量合法SASS或做详细模拟。

适合研究：形状、切块、CTA供给、split/reduction、资源压力、受控地址/容量敏感性。

不能研究：GPT-3真实任务质量、真实激活离群值、AWQ校准质量、自然稀疏/路由、原始模型生成内容。合成稀疏mask或换精度需另行定义，不继承原模型语义。

### B. 开放训练权重的GPT类模型——需要真实数值时

Meta OPT是独立训练的公开decoder-only系列，并非原始GPT-3。当前官方组织下`facebook/opt-1.3b`可直接取得代码/权重入口。[S7] 它适合提供真实hidden/KV/生成状态，但单个小OPT层不能代替175B层的尺寸。

不建议为“必须有GPT-3”下载几百GB；先说明真实训练权重对于当前问题增加什么证据。原始175B单层权重本身不公开，不能声称只下载一层就绕过可获取性问题。

### C. 大开放模型逐层streaming或CPU offload——条件使用

现有Q30工程已经有逐层materialization/replay模式，可复用通用loader经验，不继承另一模型的cache与语义。FlexGen也是单16GB GPU配合CPU/disk/量化运行大OPT的先例。[S8]

这类执行可以获得局部真实张量，但传输及前序缓存状态与常驻模型不同。并非原始GPT-3权重的替代获取方式，也不应冒称纯GPU部署性能。

## 7. 与当前模拟器的衔接

Accel-Sim输入是所执行kernel的指令/地址trace，不是把model name改成GPT-3即可。新的native kernel需要自己的ISA覆盖/target身份核对；旧Qwen trace不能因矩阵名字相同而替代。[S9]

推荐层次：合成算子native筛查 → 选少数有意义目标 → bounded SASS与输入资格 → 另行授权后详细模拟。原来的C16WARP1地址记录不能直接当完整timing trace。

不能用同一block的权重buffer连续跑96次就称96层GPT-3：它会引入真实96层不同权重并不具有的地址复用；同一层自重复也不能代表跨完整模型的一轮间隔。单层加速不能未经验证直接乘96。

4080测量/trace也不是A100、H100或多GPU执行。抽象资源敏感性需明确模型假设，不能跳过平台校准或把通信设为零后宣称完整系统收益。

## 8. 当前值得回答的问题，而不是新开模型流水线

第一候选：大Dense FFN形状下，现有局部结论是否仍成立？例如同一后端、同一精度，在GPT-3尺寸中分开比较M=1与M=256的两个FFN投影。这个实验不是简单把“GPT-3名字”补进表格，而是检验更大的N/K与权重工作集是否改变并行与访存关系。M轴是局部形状实验，不自动等于自然prefill/decode。

第二候选：在固定head dimension和query shape的受控attention中，多头KV与分组KV的资源/流量差异有多少由后端消除？修改KV-head数属于人工结构对照，GPT-3本身没有因此变成GQA；要比较不显式展开KV的合适实现，不能重做Qwen3 eager repeat的已知结论。

第一轮建议只选一个问题、少量native点。没有明确问题时，不为补模型数启动trace或full timing。

本轮不下发新Lane、不改变6/7/8执行、不新增GPU锁申请、不授权新full timing。资料准备可在174-new CPU侧做，真正native任务以后排入109/Lane7。

## 9. 阅读登记与原文入口

[S1] OpenAI GPT-3官方仓库，README，blob `18c45498c3b5411c87bb69d6b8706ce42e40ebfe`：
https://github.com/openai/gpt-3

[S2] OpenAI，Introducing gpt-oss，2025-08-05，以及当前开放模型入口：
https://openai.com/index/introducing-gpt-oss/
https://openai.com/open-models/

[S3] Brown et al.，Language Models are Few-Shot Learners，arXiv:2005.14165，Table2.1/§2.1，PDF第8页已截图核读：
https://arxiv.org/pdf/2005.14165

[S4a] LLMCompass论文，arXiv:2312.03134，§IV-A；本轮网页为该入口显示的论文版本，不冒充ISCA定稿逐字复核：
https://arxiv.org/html/2312.03134
作者artifact：
https://github.com/PrincetonUniversity/LLMCompass

[S4b] NeuPIMs，arXiv:2403.00579，§8.1/Table3，PDF第10页已截图核读：
https://arxiv.org/pdf/2403.00579

[S5] MLCommons，2025-05-05，模型选型、数据与定制checkpoint：
https://mlcommons.org/2025/05/training-llama31405b/

[S6] MLCommons，2025-06-04，Training v5.0明确替换GPT3基准：
https://mlcommons.org/2025/06/mlperf-training-v5-0-results/

[S7] OPT论文与当前可取的小模型入口：
https://arxiv.org/abs/2205.01068
https://huggingface.co/facebook/opt-1.3b

[S8] FlexGen，arXiv:2303.06865，本轮原始摘要/方法方向，不声称运行了代码：
https://arxiv.org/abs/2303.06865

[S9] 既有C16已接受trace/source/native边界与本轮项目上下文；本轮不重新审查模拟器，不复用旧平台假设为新kernel资格。

现代对象例子：FlashInfer §4.1；SpecMD §5.1（2026预印本，不冒充正式会议录）：
https://arxiv.org/html/2501.01005v2
https://arxiv.org/html/2602.03921v1

本文没有对会议全量论文做统计，不给GPT-3使用率/排名。原文事实、作者代码观察、我们的算术与实验建议分别标注；不将阅读、可获取和容量推算视为实机完成。
