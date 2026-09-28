# 科学解释

## 1. 当前采集是否可用

可用。164 上正式 raw、catalog 与 ACK 的 SHA 均匹配；manifest 管理的 35 项逐项通过大小和 SHA 校验。六个 session 都有独立 2048-token prefill、64 个连续 greedy decode step、逐步输入/输出 token 链和 2048→2112 的 DynamicCache 长度递增。四个 capture session 各有 16×64=1024 行，合计 4096 行且无重漏。T0/T1/T2 的 prefill 输出、输入序列和完整输出序列完全相同，因此只在这一固定 TEXT 测试上支持输出级 hook neutrality。

hook 并非直接截获 MoE 内部 `selected_experts` 或 expert kernel 发射顺序；它从同一个 gate 输出按模型源码相同的 float32 softmax、top-k、可选归一化和 BF16 cast 记录路由。transformers v4.55.0 官方 `modeling_olmoe.py` 的 SHA 与 receipt 中 `413888fc3be7e037727586f25900b629cc5dbc06b227a4f0d42c67cacb597bc7` 一致。tie 顺序细节没有额外证明。

## 2. 原 TEXT 与 V34 复现到什么层次

T2 Layer1 前32步与 V34：ordered top-k 相同 `30/32`，unordered set 相同 `32/32`，平均 Jaccard `1.000000`；新 output token 对齐旧 next token `32/32`，新 input token 对齐旧 next token `0/32`。这把旧结果从“runner不明”推进为显式 cached-greedy runner 下的序列复现。

V34 的 hash 序列化源码未归档，因此即使 dtype/shape 一致，也没有把两代 router-input/logits hash 声明成可比。

## 3. 主要时间结构是否随输入改变

是，主要峰位置和强度随输入明显改变：

- TEXT Layer1：主峰 lag `22`，Jaccard `0.942857`；lag11 `0.938784`，比 null p95 高 `0.638306`。
- CODE Layer1：主峰 lag `16`，Jaccard `0.925926`；lag11 `0.180280`。
- STRUCTURED Layer1：主峰 lag `14`，Jaccard `0.879030`；lag11 `0.159665`。
- PROSE Layer1：主峰 lag `1`，Jaccard `0.222940`；lag11 `0.171341`。

因此更稳妥的结论是“路由时间结构跟随固定输入族而变化”，不是“OLMoE 固定具有11步周期”。TEXT 的 lag22 可是 lag11 的谐波，不能当第二次独立发现。

## 4. PROSE 的11步现象如何解释

PROSE Layer1 lag11=`0.171341`，null median=`0.139114`，p95=`0.164213`，只高出 p95 `0.007128`；它在本层32个lag中排第 `4`，而主峰位于 lag `1`。这是弱超线，不是与 TEXT 等强的突出峰。三项替代输入的上尾比例与 Holm 校正在 `ROBUSTNESS_DIAGNOSTICS.tsv` 中保留；全层/全lag共享时间置换也单列，未用于改写 producer 原规则。

同一条64步序列的前后半段进一步显示：PROSE lag11 从前32步 `0.118332` 变到后32步 `0.263655`，不稳定；相对地，TEXT lag11 前/后半为 `0.928042` / `0.947090`，CODE lag16 为 `0.930556` / `0.944444`，STRUCTURED lag14 为 `0.860382` / `0.882604`。这些只是同序列内稳定性描述，不是独立 holdout。

## 5. 是否有独立于 token 重复的额外描述性证据

input-token 条件置换结果见 `TOKEN_CONDITIONAL_CHECK.json`。它只在相同 input token 组内交换整条 Layer1 routing record，保留 token 时间序列。结果若超过条件参照，也只能说明在该固定序列中还有上下文相关残余；hidden state 包含完整上下文，不能叫 token 因果证明。若组不可交换或 null 退化，则明确记为无法辨认。

具体地，TEXT lag11 与 PROSE lag11 都落在各自 input-token 条件置换 p05–p95 内；CODE 的主峰 lag16 与 STRUCTURED 的主峰 lag14 仍高于对应条件参照。因而现有补充证据不支持把 TEXT/PROSE 的11步现象说成独立于重复 input token 的额外信号；CODE/STRUCTURED 的主峰则保留了上下文相关的描述性残余，但仍不是 token 因果证明。

## 6. 是否值得新增 GPU 实验

当前暂不值得立即新增 GPU 实验。现有采集已经足以说明 TEXT 历史序列可复现，同时主要周期随输入改变，PROSE 的 lag11 证据很弱。若未来论文问题必须升级到自然语言总体泛化，应先预注册多个独立 prose prompts、固定主要 lag/效应量和多项校正规则，再另行授权；本 consumer 不代为启动。

## 原规则与科学解释的分离

producer 的机械函数复算结果为 `PERIOD11_REPRODUCED_ACROSS_INPUT_FAMILIES`。原协调合同在 GPU 前声明了四输入比较、Layer1/lag11关注和候选结论，但精确的“TEXT过p95且三个替代输入至少一个同位置过p95”布尔函数未在 pre-GPU manifest/receipt 中找到，而出现在结果阶段 analysis 代码中。本报告原样保存机械结果，同时不把它当成强周期跨输入泛化证明。
