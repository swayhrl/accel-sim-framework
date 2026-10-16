# Round A70｜O-A70 主流 MoE 自然工作量与执行组织（109）

执行者：Codex／O-A70；2026-10-16。终态 **NO_SURVIVOR_IN_SEARCH_SCOPE；0 主候选、0 备选、STOP**。本轮完成 CPU/source Discovery，不晋升硬件机制或 native Goal。

## 1. 结论与审查边界

主流 MoE 的 Prefill 与小批量 Decode 确实具有不同的专家工作粒度；但“专家 token 少，因此应分组、融合排列/计算/合并、重叠共享专家”已有直接软件实现。当前材料没有建立最强适用实现之后、真实自然路由下可重复的剩余完整区间 wall 代价。因此交付空候选数组，不把低 tile 填充、逻辑重复或源码 TODO 升格为硬件收益。

这不是全领域负结果。已覆盖的通用方案归 SOFTWARE_ABSORBED；自然请求的逐步专家分布、同表示后端配对及真实暴露时间仍待补。固定形状支持不全是源码适用范围，尚不能解释为硬件限制。最小后续方案仅供未来独立审查，见第6节；本轮没有执行它。

从指定起点 `8f24af162ba37b4fa37f7a18d89b0fdb62697942` 建立独立 sparse worktree，唯一提交前缀为本目录。已完整阅读 Goal 第0—4、O第7、第9—10节（实际读了全包），以及 CURRENT_STATE、协调协议第1—8节和证据索引相关 C16 项。没有等待或轮询其他 Lane，没有更改协调文件、旧报告、源码或现有环境。

## 2. 模型身份与自然工作量证据

主对象为[官方 Qwen3.5-35B-A3B config](https://huggingface.co/Qwen/Qwen3.5-35B-A3B/blob/41adbc1e50345066ac5153217957e9910204e632/config.json)（O01）。这是正式完整通用模型的逐层执行问题，没有为适配4080缩小专家数或维度。仅取 text_config 的专家部分：E=256，top-k=8，H=2048，专家 I=512，40 层，共享专家 I=512，配置 dtype=BF16。包含混合注意力/视觉能力不等于本 Lane展开 N/P 的状态或视觉议题。此 BF16配置不是论文 FP8 checkpoint 的完整身份，未来必须另冻权重和量化尺度。

目前可直接复核的真实 router 计数来自项目旧 E3（O03），固定 Qwen3-30B-A3B Layer24、S2/T2048 的保存层输入：16384 次 token-expert assignment，128 专家中93个活跃，活跃最小/中位/最大=1/14/1602。它不是随机均匀直方图，也不是生产请求分布。本轮只读已提交 JSON/runner；没有读取164或原 `.pt`，不重新证明 prompt、原始权重及输入的准入。

需明确索引与原文件的粒度差异：原 `UPSTREAM_AUTHORITY.json` 与 runner 的 STATE 路径写明 **prefill**，`NATURAL_ROUTING.json` 写明 **Qwen3MoeSparseMoeBlock expert loop**，代码逐专家 `torch.where → MLP → index_add_`。协调索引/Reset归档的 decode/fused 简称不能代替这一实际执行合同（O02—O04）。原时间和已接受科学终态均保留：N 11.577028ms、U 11.637968ms，差值在所观察波动范围；P逆排列等价且未建立顺序效应；H 6.473208ms改变激活集合，不是免费优化上界。没有重跑它，也不能将旧循环成本当作当前 fused 后端残余。

外部自然性分层：MonoMoE论文的随机微基准（O17）与 Sonnet 文本服务（O18）分开；源码 benchmark 同样产生随机 logits（O15）。文中 uniform 预期活跃专家公式是估算，不能当实际路由（O23）。这些材料未给出可与所有层、请求、decode step逐项关联的自然 n_e 序列。DeepSeek生产部署描述的Decode每专家批次通常在256 token以内（并未披露均值）（O21），不能把单卡 B1 的几何推广到整个 MoE 领域。

## 3. 当前强实现与直接近邻

以下均是固定源码/作者材料事实，**未在109 import、编译或执行这些库**。逐项链接、函数与行号、未披露项见 [EVIDENCE.tsv](EVIDENCE.tsv)。源码 pin 为2026-10-16 08:00 UTC之前返回的提交；模型配置另固定 revision。

| 来源 | 固定 commit | 已核能力与适用边界 |
|---|---|---|
| SGLang | `7098ec387c9f9d9f85a0c2c16bc1233f40f1d407` | standard dispatch与通信条件分支分离；none/triton注册 fused函数；通用runner有 pre/run/post及fused旁路；量化、gate/up合并、共享专家独立流执行有具体代码。共享融合受平台、后端及配置约束，不能假定CUDA默认全部融合（O06—O08） |
| vLLM | `fa75d3456d60a5ffe923818c4b495295675b38e1` | FP8 oracle按GPU、EP及表示选择并检查支持；Hopper block-FP8下EP1优先Triton、EP>1优先FlashInfer CUTLASS；小M的tile/N/pipeline已有变化（默认配置可被tuned配置覆盖）；稀疏小token条件下可跳过align（O09—O11） |
| FlashInfer | `18688d10022a183d36488858c9a3d7cd6ca03699` | CUTLASS API接受固定专家选择与路由权重、量化和fused finalize；MonoMoE提供SM90a、E256/H2048/I512、M≤8的persistent融合路径，超出形状直接拒绝（O12—O15） |
| DeepGEMM | `1fc9c66975ee322d628b3288534ca0e9ce12a64d` | README明确 contiguous专家段按M块对齐用于prefill，masked layout用于device counts/graph decode；Mega MoE为symmetric-memory多进程EP融合路径。该项仅能力说明深度，不声称完成其全部CUDA内核审计（O16） |

**单卡链条**：router logits/top-k → token分配或索引 → grouped/融合专家gate-up → SwiGLU/再量化 → down → 路由加权归并，并保留共享专家。Triton sorted-token路径直接从原activation按索引mask gather，不能默认物化一个按padding行数展开的feature矩阵。naive assignment还可能跳过排序；此时按assignment发tile，不应套用“每活跃专家一个tile”计算。

**多卡链条**：EP token传输及combine返回、TP结果归约属于额外部署合同。SGLang的a2a backend与compute runner是两条选择轴，`none`也不是所有部署都没有collective；TBO/SBO是已有通信重叠能力（固定文档O24；normal/low_latency可auto切换，分别由`--enable-two-batch-overlap`与`--enable-single-batch-overlap`显式启用，不声称本轮核遍其运行资格）。DeepGEMM Mega MoE的多进程路径不可移植成109单卡通信收益。

三项最直接论文近邻（均为作者实验/方法，非本轮复现）：

- [MonoMoE v1](https://arxiv.org/html/2609.04244v1)：O17—O18分别记录 H200/block-FP8随机核测试和50条Sonnet服务组；局部latency与请求mean TPOT分母不同。这是小token融合方案的直接软件反证。公开wrapper仅接收既有router logits，**不含生成logits的router线性投影**；固定源码形状比论文模型表窄，不能混同。
- [SonicMoE v2](https://arxiv.org/html/2512.14080v2)：§5 Algorithm4的token rounding会增删token-expert分配；它研究训练吞吐与质量，不能当本题保持top-k身份的执行重排。其融合/IO优化仍是软件近邻（O19）。
- [FlashMoE v3](https://arxiv.org/html/2506.04667v3)：4/8 H100、EP、单层forward的通信计算融合已实现；FP32方案对FP16基线的实验不是单卡同表示性能排名（O20）。[DeepSeek-V3 v2 §3.4](https://arxiv.org/html/2412.19437v2)说明H800集群prefill/decode不同部署与重叠，属于真实部署证据，未提供本题完整逐专家原始分布（O21）。

源码还有两个易产生虚假差异的细节（O13/O15）：MonoMoE默认可逐调用重排权重并分配scratch，公平计时应在load/preparation时完成等价打包并复用；benchmark的CUTLASS top-k预计算未计时，而Mono路径含top-k，应另列相等router边界。gate/up半部顺序也须反向核验相同逻辑权重。这里只指出比较合同，不将这些工程处理晋升成硬件候选。

## 4. 唯一工作量模型：有用工作、padding、访存与wall分开

定义同一实际step的token数T，top-k=k，专家e的真实assignment数n_e，R=Σn_e=Tk，活跃专家数A。平均R/E是计数恒等式，**不表示均匀路由**；n_e分布须来自实际router。

对于确实按专家分组、每块b行的路径，条件几何为：

`M_sched(b) = Σ_e b*ceil(n_e/b)`；padding行=`M_sched-R`；几何padding比例=`(M_sched-R)/M_sched`。

CPU对旧固定直方图独立重算（O22；未生成N/U/H）：

| 假定 b | 条件 scheduled rows | padding rows | padding / scheduled |
|---:|---:|---:|---:|
|16|17248|864|5.0093%|
|32|18304|1920|10.4895%|
|64|20544|4160|20.2492%|
|128|25344|8960|35.3535%|

这些是 **DERIVED/CPU_DIAGNOSTIC**，不是旧expert loop实际padding、当前动态所选b、Tensor Core指令数或可节约GPU时间。公式只适用于指定组织；naive、batched/masked和weight-major路径不能直接复用其代价解释。

O01模型的合法Decode B=1、k=8且每token选择不同专家时，恰有8个专家各1 assignment；假定b16则8行有用/128行scheduled。B=8时，R=64，A在8—64间，b16下scheduled在128—1024间。这里给的是确定边界，**未声称哪一自然分布实际出现**。Prefill处理的是多位置token数，不可将上下文长度当decode当步B。

同一模型专家权重元素量为每层 `3*E*H*I=805306368`。若固定block-FP8每元素1 byte，则每层routed payload为768MiB，128×128块的FP32尺度另192KiB；40层仅routed payload为30GiB。此为容量推导，排除shared/router/attention/embedding/KV/scratch等，不能当峰值显存或本步权重DRAM流量。完整模型不等同16GiB单卡已可运行；单层可放入也不证明全请求性能。

本题选定的真实变化是 **真实模型Prefill多位置 → Decode每步1—8 token时的专家粒度与后端适用切换**。算法必需工作是原router所选expert及共享expert的计算；padding是条件执行几何；实际访存取决于mask、布局、cache和量化；暴露wall还受并行、依赖、graph、调度影响。四者不能相互代换。当前只有配置、历史单点计数、源码能力及作者测试，未建立强实现后的残余wall。

## 5. 去重与零候选自审

| 筛查问题 | 最强反证/缺口 | 本轮裁决 |
|---|---|---|
| 用grouped GEMM、减少排序、融合两投影/归并解决小token | O07/O10/O12—O14已有具体实现；O15不能当自然统计 | 通用方案已由软件覆盖，无硬件晋升 |
| 用自然热点改变激活专家集合 | E3 H改变语义；Sonic TR也不是固定assignment执行组织；PC03本已停车 | 不重做合成热点，不把改激活集合当oracle |
| 共享专家重叠或双batch隐藏all-to-all | O08与SGLang已有能力；EP需额外部署；无自然配对残余wall | 不从API/重叠标签或通信数字反推109收益 |
| 形状不支持/后端切换还有代价 | 源码支持范围明确，但缺实际调用、配对时间和独立验证 | 普通软件适配/未回答，尚不成为硬件候选 |

Reset PC03已提出强MoE下的自然active-set问题，PC04已提出异构交接（O05）。本轮新增的是固定当前小token路径、公开wrapper的真实支持合同、旧索引范围校正及条件计数重算；不是发现新的性能现象。C16 Split-K/GROUP_M与FFN双流/merged负结果保留各自范围，既不重启，也不外推到所有MoE。

审查通过项：候选数量0≤2；直接来源与推导分列；随机/自然、Prefill/Decode、单卡/EP、配置/表示、局部/请求分母分离；未披露填明确缺口；没有用摘要最高倍数补配置；没有GPU/CUDA/JIT/模型import/权重或数据集下载/安装/Profiler/模拟器；没有跨Lane输出或协调文件改动。

## 6. 条件式未来最小native方案（未执行、未晋升、无自动授权）

目的仅是判断：在现有强软件之后，真实小token专家粒度与阶段/后端交接是否还有可重复的完整区间暴露成本。当前不推荐直接研究硬件，也不把本方案放进CANDIDATES冒充survivor。

1. **基准**：未来另获授权的一张H200-141GB，官方Qwen3.5-35B-A3B文本路径；冻结checkpoint revision、权重及量化尺度身份、软件SHAs、graph模式、请求token与分阶段边界。基线在适用范围取支持且最快的tuned vLLM Triton、FlashInfer CUTLASS和现有MonoMoE；不能用专家循环或无融合fallback。自然完整请求先获得各层各步n_e，并保留同一层input、router logits、selected ids/weights；B1与B8 decode、固定prefill块只是预定小网格，不能替代自然输入。
2. **诊断**：只在同一个保存真实层输入上比较执行组织。固定原expert集合/权重/路由概率、量化结果和gate/up顺序，packing可逆核验，top-k tie/softmax/renormalization输出必须匹配；Mono现接口重算top-k时先验证选择和权重身份，未通过即不计性能。允许相同token排列及逆排列、已有grouped与persistent对照；不构造热点、不丢token、不降低precision、不把免费删router或共享专家当完整同任务。准备/重排与重复scratch分配只作成本分解，持久预打包与额外内存必须计入生命周期。
3. **指标**：route-to-combine和router-logits-to-combine两个相同边界的配对wall；另测包含router线性及shared expert的完整MoE wall与请求TPOT。分离prefill、decode，按实际可重复噪声报告，不把分stage时间相加当并发wall。观察kernel gap、物化buffer和实际访存只能在后续另行批准工具后进行。本轮无Profiler授权可继承。
4. **独立验证**：探索材料固定Sonnet文本请求；冻结后另用未参与选参的GSM8K合法请求子集、不同prompt/context组成，保留原token和真实路由。现在未获取任何数据；未来需先冻结来源、许可/版本、seed和分割。它是独立请求验证，不是另一个模型的泛化证明；跨模型需要再选原生真实模型并核后端支持，不能直接拿不兼容Qwen3/DeepSeek形状冒充相同API验证。
5. **资源/停止**：GPU、环境/权重/请求许可与数值合同均须新Goal明确批准；现有109/RTX4080不支持所核SM90a路径。单层replay可节省准备成本，但只能回答层级；完整请求要保留足够显存，不能删专家或缩维。若无法保持route/weight/quant身份，先STOP；若强软件已消除配对暴露、完整scope权重不足、收益落入预冻噪声门或请求验证失败，结束候选。若只剩软件打包/选择器问题，归软件，不进入硬件机制。未来若扩成DeepSeek生产EP需多卡独立合同，不用单卡结果代替。

## 7. 资源、交付与复核

串行CPU/source worker，affinity CPU7（来自本shell允许0—23），读取资源合同后OMP/BLAS及Git pack/index线程均设为1（首次取回Goal前的Git内部线程数未观测）；未改全局Git配置。worker虚拟地址空间上限2GiB；已记录单worker最大RSS约45MiB（详见RECEIPT），不是系统峰值。宿主启动时MemAvailable=61406MiB只是一次快照，不监控其他Lane。没有subagent、本地计算池或GPU栈。

109成功公开HTTP响应累计9960799 bytes（源码/目录API，另见回执最终计数），worktree含私有source/output/tmp约11MiB；远低128MiB下载及256MiB新增盘上限。初次Git取回固定Goal约105.52KiB对象；未下载模型权重/真实数据集/PDF。浏览器只读官方模型配置和原论文HTML，未将版权全文入Git。109的HF连接超时与raw.githubusercontent DNS失败后，有界切换官方blob API；HF固定config页面通过浏览器核验。没有绕过访问限制。

四份提交文件为本REPORT、EVIDENCE.tsv、CANDIDATES.json和RECEIPT.json。`.private/`保存本Lane的源码快照、下载账本、CPU推导与复核记录，由本worktree独立excludesFile排除；没有删除文件或执行git clean/gc/repack/reset。结束前校验TSV字段/唯一ID、JSON、引用与哈希、Python源码AST（只parse不import）、git diff --check及路径白名单；提交、push后单次fetch-back核验commit/tree/四个blob并确认clean。RECEIPT避免自引用，精确最终commit/tree由私有readback和用户回执给出。所有native步骤保持未执行，交付后STOP。
