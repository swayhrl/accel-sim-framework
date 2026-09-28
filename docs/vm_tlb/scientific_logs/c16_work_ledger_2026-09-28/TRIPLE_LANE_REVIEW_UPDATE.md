# 最新增量：Lane6 / Lane7 / Lane8 三项结果审查与当前研究判断

日期：2026-09-28。

本文件晚于OLMoE多输入producer、Qwen3 KV backend audit和DeepSeek MLA representation audit。它不改写历史实验；只追加已完成结果与当前解释。原70条总账 + EXP06–EXP08 + 本次EXP09–EXP11 = 76条逻辑工作记录，不是76次独立实验。

## 1. Lane6：OLMoE多输入独立重算

节点：174-new，CPU-only。
结果commit：`52f5b86b5a50dda4d1d3413e6d456b4d7f18c565`。

接受的中文结论：
- 164 durable raw、六个session、4096条路由记录和连续KV链均闭合。
- 原历史TEXT的专家集合/输出token得到强复现。
- 主要路由重复间隔明显随输入改变：TEXT约11/22，CODE 16，STRUCTURED 14，PROSE 1。
- PROSE的lag11只是弱超线，且前后半段变化大；不能与TEXT的强11步结构等同。
- input-token条件置换后，TEXT/PROSE lag11不再超出参照，因此现有数据不支持“与重复input token无关的普遍11步规律”。
- 当前不值得立即新增GPU采集。若以后研究自然语言总体泛化，应先冻结多个独立prose prompts、主要lag、效应量与多项校正规则。

旧producer的机械分类保留在原artifact中，但项目层不采用“不同输入共同稳定存在11步周期”作为科学结论。

## 2. Lane7：split-K与执行前访存状态

节点：109 / RTX4080。
结果commit：`3aad5887b9b4c5bec801962bf8035fed9d485f47`。

固定原split8/split1实现，不扫描其他split。

M256 timing：
- up_proj：warm下split1约快30.0%；扰动后仍快约26.9%，优势缩小约3.08个百分点。
- down_proj：warm下split1约慢1.29%；扰动后约慢6.63%，退化扩大约5.34个百分点。

独立4xL2 buffer遍历明显改变目标DRAM traffic；尤其split1 warm时DRAM很低，扰动后显著增加。L1/L2统计量变化远小于DRAM变化。

当前可接受解释：
- split策略的收益不只由静态M/N/K或是否有reduction决定，执行前的访存层次状态会改变相对收益。
- up_proj仍显示“减少split/reduction后更快”，down_proj则显示“减少split导致并行度不足，且访存状态变差时更糟”。
- 因此一个有意义的问题是：split策略需要同时权衡并行度和数据驻留/复用状态，而不是全局固定split值。

不能扩写：
- conditioner只是一个确定的4xL2独立buffer访问，不等于证明所有cache均冷；
- 不能据当前数据唯一归因到L2，也可能涉及TLB、调度、频率等状态；
- 没有tensor级流量归因；
- 旧ABBA协议和本次mirror协议不拼接数值。

本实验本身关闭，但留下一个比“继续调split=2/4/16”更有价值的机制问题：**并行度—驻留状态联合决策**。

## 3. Lane8：DeepSeek MLA实际cache表示

节点：174-new，CPU-only。
结果commit：`0cc55f1b498bf66085b789a3a8c0ae8c71c34a47`。

接受的中文结论：
- V26/V27的Transformers 4.51.0 eager路径实际缓存展开后的16头BF16 K/V：
  - key `[B,16,T,192]`
  - value `[B,16,T,128]`
  - 10,240 B/token
- 精确源码中的MLA latent形态为512维compressed latent + 64维RoPE component，BF16约1,152 B/token。
- accepted runtime persistent cache相对latent形态约放大8.89倍。
- QK读取的是展开key的转置视图，与cache共用storage，不是额外latent cache。
- 后续公开Transformers实现已改成先缓存latent/RoPE再展开，证明V26/V27的展开persistent cache不是MLA模型本身的必然要求。

因此，原V26/V27约15.99倍active-lane-event增长必须重解释：
- 上下文/cache容量仅约增长3.9985倍；
- selected paths、executed paths、单shard事件和kernel函数也发生变化；
- 15.99倍不是MLA固有流量，更不是DRAM bytes。

现有DeepSeek证据不支持直接设计cache/TLB机制。若未来还关心部署代表性，唯一有价值的GPU后续是同模型、同输入、同语义下“展开cache实现 vs latent-cache实现”的最小匹配比较。

## 4. 当前项目状态

- Lane4 / 174-new：原R0/M1/diagnostic长跑继续；不读取partial，不更改。
- Lane6 / 174-new：OLMoE多输入独立分析已完成并STOP。
- Lane7 / 109：split-K访存状态实验已完成并STOP；RTX4080窗口空闲。
- Lane8 / 174-new：DeepSeek MLA表示审计已完成并STOP。

## 5. 当前优先候选

短期不建议继续：
- 继续为OLMoE固定11步周期加GPU样本；
- 从Qwen3 eager repeat-K或DeepSeek旧expanded-cache事件直接设计TLB/cache机制；
- 做split1/2/4/8/16的纯参数扫描。

值得保留的两个新问题：
1. **split-K的并行度—驻留状态联合决策**：需要先形成可预测机制，再决定是否做一个更小的native验证，不要变成autotuning。
2. **DeepSeek expanded-cache vs latent-cache matched comparison**：只有在项目需要部署代表性/真实访存差异时才值得109测量。

GPT-3公开尺寸的Dense层可作为后续规模对照，但应等待Lane7结果整合后确定实验变量，避免只是“换一个更大模型名”重复旧实验。

本增量不授权M1F，不改变Lane4 gate，不自动启动新的GPU或模拟器实验。
