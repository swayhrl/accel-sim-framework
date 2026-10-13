# Round A6｜非LLM强软件路径核实与公开训练实验组审计

**执行者：ChatGPT／AI-ARCH Discovery。日期：2026-10-13。**

性质：文献与GitHub只读源审，另将结果写入协调知识层。本轮没有运行Codex、CUDA/JIT、训练、模拟器，也没有下载权重或大型数据。采用候选工具提交 `1a7f8d5d6f01326da161f52447eee013d1a630ec` 中两套Skill的审查方法，不安装Skill、不合并候选工具分支。研究入口核对为协调提交 `3d0a959d3d6b77de67fdf9cc3f891d4adcc5416b`；承接[A5独立审查](../reviews/AI_ARCH_ROUND_A5_LANE_T_N_INDEPENDENT_REVIEW_2026-10-13_V1.md)。

## 0. 本轮改变了什么认识

1. **非LLM不必以Sobek适配成功为前置条件。** 固定NequIP源码已经串起GPU邻居构建、OpenEquivariance张量积、能量和力/应力计算。适合优先设计真实静态结构的有限观察，尚不代表本机运行资格或硬件瓶颈成立。
2. **缺少连续时间索引，只阻断跨帧复用频率这一问题。** 既有Si文件仍可用于静态结构评估；不把这些帧声称为统计独立样本或连续MD轨迹。A5的时间身份限制保留，不扩大为所有原生观察均不可能。
3. **训练找到公开输入来源与明确软件配置的例子。** TorchTitan v3指定C4英文数据、Llama tokenizer和分组实验；公开源码展示输入生成方法。公开方法不等于论文原运行的逐token复现，不把历史软件快照当作作者的确切artifact。
4. **发现性观察与机制晋升继续分层。** 当前源码足以提出有限、可证伪的观测设计，但不能宣布强软件之后存在硬件收益。按照既有协调协议，发现性probe不要求事前证明完整oracle；仍须另有具体GPU授权。

## 1. 来源登记与阅读范围

| ID | 固定原始来源 | 本轮阅读范围与证据层次 |
|---|---|---|
| N1 | [mir-group/nequip@27d9d2182da918ab7be0017d8300e53278f5e00e](https://github.com/mir-group/nequip/tree/27d9d2182da918ab7be0017d8300e53278f5e00e) | 直接读取下列ASE、邻居后端、编译目标和导数源码；SOURCE_CODE，未编译 |
| N2 | [OAM-S:0.1作者模型页](https://www.nequip.net/models/mir-group/NequIP-OAM-S%3A0.1)；[官方OEQ指引](https://nequip.readthedocs.io/en/latest/guide/accelerations/openequivariance.html) | 模型页本轮完整打开失败，仅取得搜索返回的作者说明；模型128/64及Si范围沿用A5已审事实。OEQ官方使用路径与固定源码交叉核对；不宣布checkpoint字节合格 |
| N3 | [Si tutorial@8f90935ba42fd9e03df323cf03428c456d87b881](https://github.com/mir-group/nequip-tutorial/tree/8f90935ba42fd9e03df323cf03428c456d87b881) | 110帧×64 Si、blob和SHA沿用A5的独立核验；本轮不重复下载或重hash |
| T1 | Wanchao Liang等，[TorchTitan arXiv:2410.06511v3](https://arxiv.org/html/2410.06511v3)，2025-06-07版本 | HTML §2.2、§3.1–3.3、Tables 1–6、§8.10；PAPER_AUTHOR。未声称重新核对全部PDF图像或复现代码 |
| T2 | [pytorch/torchtitan@4e31b862d1d161b330b64be5b8db52c46c33ba58](https://github.com/pytorch/torchtitan/tree/4e31b862d1d161b330b64be5b8db52c46c33ba58) | **由本窗口选择**的2025-06-06历史快照：以v3日期之前的Git提交检索得到；非论文明确指定执行commit。直接核数据loader和模型注册 |
| T3 | Ruisi Zhang等，[SimpleFSDP arXiv:2411.00284v2](https://arxiv.org/html/2411.00284v2) | §3.3、§5–5.3文字所给实验对象、对照和结果；未从图上读额外数值。强软件近邻，不是本机结果 |
| T4 | [PyTorch作者DevLog：Graph-based CPU Offloading，2026-06-23](https://docs.pytorch.org/devlogs/distributed/2026-06-23-cpu-offloading/) | 方法、配置与限制文字；技术报告，不当作正式论文。未核图数据、运行日志和完整输入身份，不将T1的C4来源自动转移到此组 |

没有使用第三方论文总结填补配置。`未披露`只指本次已核版本/位置；没有完成检查则写`未核实`。

## 2. 非LLM：可以连接起来的真实软件路径

### 2.1 已核固定源码

所有文件均来自N1固定commit。

| 文件 | 本轮直接确认的事实 | 科学边界 |
|---|---|---|
| [`nequip/integrations/ase.py`](https://github.com/mir-group/nequip/blob/27d9d2182da918ab7be0017d8300e53278f5e00e/nequip/integrations/ase.py)，blob `b2b052bce71eb977ac25f3b5dc47aabf04dc0670` | 按邻居后端是否支持CUDA，决定先搬输入还是先CPU变换；`calculate`调用构图/变换后执行模型，并把实际输出的能量、力、应力送回CPU | CPU数据组织、邻居构建、传输、模型、输出回传是完整工作；模型单独计时不等于ASE完成时间 |
| [`nequip/integrations/mixins.py`](https://github.com/mir-group/nequip/blob/27d9d2182da918ab7be0017d8300e53278f5e00e/nequip/integrations/mixins.py)，blob `d902de57983e56597bd4242911846ba9cc5a02bf` | `from_compiled_model`从产物metadata读取cutoff/type names；接受`neighborlist_backend`与kwargs | 不应使用tutorial的5.0 cutoff替代OAM-S模型实际metadata；模型选择与原子类型映射必须固定 |
| [`nequip/data/_nl.py`](https://github.com/mir-group/nequip/blob/27d9d2182da918ab7be0017d8300e53278f5e00e/nequip/data/_nl.py) | 默认matscipy为CPU后端；已注册alchemiops并支持CUDA。`alchemiops_batch_cell_list`传positions、batch_idx、cell、PBC、cutoff、max_neighbors给公开库，并把边及周期shift写回数据字典 | 不是缺少GPU构图接口；GPU后端不保证在64原子小系统上更快。版本、容量溢出和边集合等价仍须运行核验 |
| [`nequip/data/transforms/neighborlist.py`](https://github.com/mir-group/nequip/blob/27d9d2182da918ab7be0017d8300e53278f5e00e/nequip/data/transforms/neighborlist.py)，blob `308a91947f6ed284566cd491fc4d5fcc2fe0377d` | 普通transform调用构图，可按边类型cutoff剪枝；另有Sorted transform显式排序和transpose permutation | 普通路径不能被写成必然执行双向排序；此adapter未显示跨帧skin状态/重建旗标，不能仅因ALCHEMI库具备该能力，就宣布NequIP这条调用已启用跨帧复用 |
| [`nequip/nn/_tp_scatter_oeq.py`](https://github.com/mir-group/nequip/blob/27d9d2182da918ab7be0017d8300e53278f5e00e/nequip/nn/_tp_scatter_oeq.py)，blob `ac84136596d9f365e050806aa544ec240455b1e0` | TPProblem接收原模型irreps与instructions；TensorProductConv使用`deterministic=False`，并按model_dtype显式cast输入 | 不要求先变成Sobek统一multiplicity；也不能凭modifier存在就宣布OAM-S/4080数值测试已通过。排序与确定性合同不能随意加严以排除强后端 |
| [`nequip/nn/grad_output.py`](https://github.com/mir-group/nequip/blob/27d9d2182da918ab7be0017d8300e53278f5e00e/nequip/nn/grad_output.py)，blob `a66bb975ad82cb5ebe829e2fdb838f6ded596f05` | 能量对位置及形变求导得到力/virial/应力；`create_graph=self.training`；另有edge-vector路径 | 力推理不等于仅forward，也不等于训练double backward；周期结构通常涉及应力输出，须保持各臂相同输出集合，不把额外工作免费删除 |
| [`nequip/scripts/_compile_utils.py`](https://github.com/mir-group/nequip/blob/27d9d2182da918ab7be0017d8300e53278f5e00e/nequip/scripts/_compile_utils.py)，blob `4b472ad56adf441136a1ea06ca9b2ec334414cd5` | `ase`目标固定单帧；`batch`目标保留batch与num_nodes字段，准备双帧示例以处理0/1特化；二者均定义能量/力/应力输出 | 不把ASE单帧与另一个batch编译产物的差值当纯batch因果。源码支持batch接口，不等于已证明同一个编译产物对所有B都无重编译 |

**归纳，不是实测结论：** 接口障碍已从“需要先拼装一个新物理模型/新GPU算子”收窄到“核实既有软件在选定模型、设备和输入上的正确执行”。下一轮不必再做Sobek适配综述，也不需要先认证MD时间序列。

### 2.2 重新限定要回答的问题

优先问题不是“动态MD每帧准备有多慢”，而是：

> 对同一组真实Si结构，采用原生NequIP＋OEQ并完成同样的能量、力及约定应力输出时，增加每次提交的结构数后，时间主要改变在CPU/输入准备、GPU构图，还是模型执行？

该问题属于P01工作量组织与瓶颈迁移；不是物理SM扩容实验，也不是新硬件headroom证明。真实连续时间顺序只在后续讨论skin复用收益时需要。结构批量组合必须保持每帧原子、周期盒和边隔离，不能把多个结构拼成一个互相作用的大晶体。

### 2.3 已写出的最小观察设计（DESIGN_ONLY，未授权109）

候选对象：`NequIP-OAM-S:0.1`，原模型OEQ路径，既有Si文件中按固定规则预选32个不同结构；选样不看时间或优化收益。保留其余结构供以后按新合同验证，不在本轮追溯命名holdout。

| 条件 | 改变项 | 保持项 | 用途 |
|---|---|---|---|
| N-C2 | CPU matscipy构图，B=2 | 同模型、同32结构、同batch编译目标、同输出 | 成熟CPU构图对照 |
| N-G2 | GPU alchemiops构图，B=2 | 与N-C2相同 | 观察构图放置与传输的净效应；不是纯GPU算子加速 |
| N-G4 | GPU构图，B=4 | 总32结构及结果保持 | 中间任务规模 |
| N-G8 | GPU构图，B=8 | 总32结构及结果保持 | 较大任务规模 |

B=1的ASE目标只作独立参考，暂不并入纯batch曲线。4个配置的完整工作量相同，每结构时间为整组完成wall/32。额外GPU-event区间单列构图与模型，不把并发kernel持续时间直接求和充当wall。

未来执行须先验证：模型包实际ID/hash和metadata；正确加载OEQ而无fallback；输入与周期shift、边集合和max_neighbors无漏边；单帧与批量输出数值合同；实际调用模型而非命中结果缓存；编译/预热与正式计时分离；相同B路径是否触发新编译或kernel选择；后端版本兼容。是否需要应力必须事先固定，不能只测快的输出。

否定条件：GPU构图没有净收益、收益仅来自普通软件选择/批处理、CPU及传输完全主导、输出不合格，或需要大幅移植才能比较。均不能据此声称新硬件问题。噪声或数值不稳定应标未判定，不筛选正结果。

**本轮状态：SOURCE_PATH_SUPPORTED / MEASUREMENT_DESIGN_READY_FOR_REVIEW；不是NATIVE_VALIDATED。** 没有发放下载、编译或GPU权限。

## 3. 训练：一个公开输入明确的主例，两个强近邻

### 3.1 TorchTitan：按实验组审计

T1指定C4英文数据和Llama 3.1官方tiktoken。使用95GiB、HBM2e/降TDP的非标准H100，作者未给确切峰值TFLOPS；吞吐按每GPU计算、每10步记录，在第90步读取；不是多次独立重复的置信区间。以下仅记直接核到的实验事实：

| 组／位置 | 模型、平台、输入 | 改变／控制 | 作者结果及边界 |
|---|---|---|---|
| TT1／Table1–2 | 8B；8与128 GPU；local B2，global B分别16与256；C4；选择性重计算 | 各固定规模内部逐步加compile、Float8 | 基线已经FSDP；跨两表global batch不同，不能叫固定总工作强扩展；Float8是精度/实现组合，不是纯算力干预 |
| TT2／Table3 | 70B；256GPU，FSDP32、TP8，local/global B16/512；full AC、compile、Float8 | 仅在此共同基线上加AsyncTP | 897→1010 tokens/s/GPU；70.3→67.7GiB。软件通信重叠的系统结果，不是未兑现硬件余量 |
| TT3／Table4 | 405B；512GPU，FSDP4、TP8、PP16；local/global B32/128 | 同既有优化，1F1B改interleaved | 100→130 tokens/s/GPU，内存78.0→80.3GiB。更高吞吐同时花更多容量 |
| TT4／Table5 | 8B；8GPU；local B1；CP1→8、FSDP8→1 | 上下文32,768→262,144同时变化 | 是长上下文可行性系列；不能把tokens/s下降解释为相同工作下单独CP退化 |
| TT5／§8.10.2 | 8B、C4、global B32、3000步 | 多种并行与数值优化组合 | loss检验另列，不转移成每个405B性能点的长期质量或逐梯度等价 |

作者明确目的包括组合优化、扩展性与训练配置比较；我们的归纳是“软件会改变资源需求和数据寿命，扩资源前须固定执行策略”。没有替作者补齐未披露的逐token记录、运行seed或microbatch命令。

### 3.2 公开输入路径究竟落实到哪里

本窗口选择T2历史快照，只用来检查公开能力，不冒充T1运行版本。

- [`torchtitan/datasets/hf_datasets.py`](https://github.com/pytorch/torchtitan/blob/4e31b862d1d161b330b64be5b8db52c46c33ba58/torchtitan/datasets/hf_datasets.py)，blob `023b4a29e946ac7d3234dea10717bff609cd1e20`：C4指向`allenai/c4`、en/train、streaming；按DP rank拆分；逐文档加BOS/EOS并装入token buffer，生成输入及右移标签；保存buffer与迭代状态。`c4_test`另有测试数据入口，不能代替自然语料性能。
- 该loader本身未锁HuggingFace数据revision；因此未来自己的实验仍须固定分片、tokenizer文件、RNG、读取位置及训练初始状态。公开代码降低了新实验设计障碍，不自动补出作者原运行身份。
- [`torchtitan/models/llama3/__init__.py`](https://github.com/pytorch/torchtitan/blob/4e31b862d1d161b330b64be5b8db52c46c33ba58/torchtitan/models/llama3/__init__.py)，blob `fffd1092acfbce796fdfefdc2144e322147d1165`：该快照有debug、8B、70B、405B配置，**没有现成1B项**。不将debug模型称为8B缩放复现，也不为单4080方便而悄悄改深度。

### 3.3 强软件反例：SimpleFSDP

T3 §5使用C4、Llama3.1及H100集群；比较FSDP2-eager和更强的FSDP2-compile。8B在32/64/128GPU的一维FSDP组，相对compiled基线平均少用8.65%峰值显存，吞吐大体相当；作者解释通信已被隐藏。其automatic wrapping还显式联合通信可隐藏时间与预取内存预算。

这说明生命周期确有容量价值，却未必暴露为速度收益。不能只选相对eager的大数值，也不能重新把“通信预取需考虑容量”作为空白。读到的batch字段若原文没有明确local/global，不代作者命名；本轮不复现SimpleFSDP。

### 3.4 2026增量：CPU卸载已是强软件近邻

T4报告graph-based activation offloading，已有view replay、固定页内存池及defer/prefetch策略。作者在8×H100环境比较Llama3 8B、Qwen3 14B等，并报告省内存与吞吐的权衡。其正文未提供本次可核的自然token身份；不能直接继承T1的C4。文中约300GB/s传输说法没有在本轮以原始硬件日志验证，**不作为4080 PCIe参数**。这只限制一般“把激活提前搬到CPU”的新颖性，不证明本机性能。

**训练选择结论：** C4＋TorchTitan从输入与软件透明性看比私有352B更适合作为研究起点；但论文硬件与本机仍不同。分布式通信问题保留多GPU属性；单GPU只能另外定义保存/重算/搬运等局部训练问题，不能替代同一分布式实验。新建从头训练不要求假装拥有作者checkpoint，但必须固定自己的完整初始状态。

## 4. 两张问题卡与当前优先级

**Q-N6（第一优先）：** 同一批真实结构、同一强模型，构图放置和提交粒度何时改变完整评估时间？已有具体公开接口和四条件设计；缺模型产物/本机数值及运行资格。适合讨论一次有限发现性观察，尚非新硬件机制。

**Q-T6（研究保留）：** 固定合法训练步与强编译实现，选择保存、重算或主机迁移激活后，时间/容量前沿如何随输入工作量及可用资源变化？TorchTitan和SimpleFSDP提供实测/软件边界。重计算会增加工作，卸载会增加传输，不能把它们都当免费oracle；具体小规模模型与本机预算仍未冻结，不发训练Goal。

两题都不是“现象必须先证明5%全模型收益才准研究”。发现需要合法变量和观测、有限代价及STOP；机制晋升再要求稳定剩余约束、最近邻和实现成本。0个新GPU授权不等于0项科研进展。

## 5. Round A7｜收敛一份非LLM发现性观察合同

**执行者：ChatGPT／AI-ARCH Discovery；Codex本轮不新增任务。**

默认下一步不扩大论文清单：围绕Q-N6补齐模型包元数据、版本组合、正确性判据、实际测量边界与四条件预算；将源码支持的部分与必须在GPU canary确认的部分分开，形成一份可直接审阅的候选合同。优先沿公开现成路径，不开发Sobek adapter、不建MD模拟平台。

GPU阶段须另行明确授权模型获取、设备编译和canary/计时；在此之前不启动109、不清理其cache、不触碰GPU锁。训练Q-T6保留文献/方法研究，不再要求Lane T重复352B审查。Lane N的V2文档修复独立处理，不阻塞本窗口已直接读取的源码证据。

## 6. 交接与未做事项

本轮读取Lane N分支HEAD仍为`e355f096eeac44328d7463ef3256cc649ec9cb03`，不声称V2已修复或窗口实时运行状态。C16 Stage A、AWMA R27R3及两个Lane历史STOP不改；A5审查保留。只新增本文件及协调导航，未合并任一执行/工具分支，也未更改问题图谱的历史V1。
