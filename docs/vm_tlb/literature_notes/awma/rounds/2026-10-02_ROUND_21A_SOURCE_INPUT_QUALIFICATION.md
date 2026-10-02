# Round21A｜模型、强后端与真实输入资格：问题收窄为OEQ图准备是否值得

日期：2026-10-02。性质：source/input qualification。未执行109 GPU测量。

## 结论

Round21最初的“动态图双向CSR/执行计划准备”不能作为通用问题继续推进。MACE的cuEquivariance融合路径和NequIP的OpenEquivariance默认路径都能直接消费COO edge indices；尤其NequIP当前OpenEquivariance wrapper固定使用 `deterministic=False`，该atomic卷积允许任意edge顺序，不要求receiver sort或transpose permutation。

因此把Sobek特有的双CSR/plan准备当作几何AI共同必需成本，会锁住特定后端制造动机。

保留下来的更窄问题是：

> 在真实NequIP能量+力推理中，是否值得为同一动态图支付一次receiver-major排序与sender transpose-permutation准备，从而使用OpenEquivariance的deterministic convolution，并把准备成本在多个interaction layer和force backward中摊回？

这是软件执行组织/producer-consumer readiness问题，仍不是硬件机制。

## 固定source facts

### NequIP

Pin: `mir-group/nequip@27d9d2182da918ab7be0017d8300e53278f5e00e`.

`InteractionBlock`生成uvu tensor-product instructions，并把 `edge_dst/edge_src`直接传给`TensorProductScatter`。

官方`OpenEquivarianceTensorProductScatter`构造：

`TensorProductConv(... deterministic=False ...)`

并直接forward `edge_dst, edge_src`。没有NequIP侧receiver sort、双CSR或sender permutation准备。

NequIP单元测试对OpenEquivariance/CuEquivariance与base TensorProductScatter比较forward以及x/edge_attr/edge_weight梯度；float32采用atol=rtol=1e-5。NequIP更高层的通用float32 model output similarity默认tol为`5e-5`，并用5次求值平均处理数值随机性。当前首轮模型合同采用该官方model-level tolerance，不自造R20式阈值。

Foundation model候选固定为 `nequip.net:mir-group/NequIP-OAM-S:0.1`：
- public trained materials foundation model；
- S preset = 2 interaction layers, l_max=1, features [128,64]；
- float32 first admission；
- OpenEquivariance是官方推荐GPU acceleration path。

选择S而不是L不是为了找性能正例：2026公开issue记录OAM-L / l_max=3的OpenEquivariance force-conservativity缺陷；首轮用S降低已知无关bug风险，但仍必须独立做energy/force正确性检查，不能引用issue当本机资格。

### OpenEquivariance

Pin: `PASSIONLab/OpenEquivariance@dc9979099c65113adcc016977c5c60974f9ddafb`.

`TensorProductConv`有两个明确模式：

- `deterministic=False`：atomic aggregation；receiver/sender indices可任意顺序；无需transpose permutation。
- `deterministic=True`：fixup/deterministic aggregation；要求adjacency按receiver排序，并提供将row-major nonzeros映射到column-major的sender permutation。README明确说明此模式可避免atomics并可能更快。

因此第一层诊断必须先测“准备免费时deterministic full-model是否有>=5% headroom”；若没有，任何在线图准备都不值得继续。

## 真实输入authority

候选固定为官方NequIP tutorial仓库：

- repo: `mir-group/nequip-tutorial`
- commit: `8f90935ba42fd9e03df323cf03428c456d87b881`
- file: `sitraj.xyz`
- Git blob: `baac4e23364d00d29b2410fa60a92ade0cbf35a3`
- size: 784661 bytes.

文件自身可见64个Si原子、周期cell、positions、forces、energy/stress标签，多帧extxyz。官方repo并未在我们已读文本中承诺frame顺序等同连续MD时间索引，因此首轮只把帧当独立真实几何样本，不计算neighbor rebuild frequency、不做时间摊销声明。

执行时先解析总帧数N并冻结：
- discovery = floor(N/2)
- holdout = floor(N/6), floor(N/3), floor(2N/3), floor(5N/6)

这些索引仅由N决定，在任何性能数据之前冻结。若索引重复或输入结构不合法则STOP。

## 首轮最小实验边界

本轮不把neighbor search混进来。先冻结一个由真实frame和模型cutoff产生的合法COO图，研究：

`unsorted graph COO resident on GPU -> full energy + required forces committed`

三种角色：

- A0 strong baseline: 官方OpenEquivariance atomic path，保留任意顺序COO；与candidate使用同一强compile模式。
- Dready: receiver-sorted graph + transpose permutation预先就绪；deterministic OEQ；sort/perm不计时。只用于判断downstream headroom。
- Donline: 从与A0相同的unsorted COO开始；一次GPU receiver sort + edge metadata reorder + sender permutation全部计时，然后deterministic OEQ。只在Dready >=5%时运行。

不是每层重排。prepared sorted graph必须在interaction layers之间共享。

如果deterministic patch不能走与A0相同的强compiled inference路径，就STOP；不允许用compiled A0对eager candidate，也不允许把A0降级救candidate。

TF32首轮关闭。Energy/forces和edge identity按NequIP官方float32 model-level tolerance与精确edge multiset检查。参考是同一OAM-S权重的unmodified NequIP/e3nn路径；A0先资格化，之后Dready/Donline都对同一reference检查。

发现阶段和在线阶段都使用完整energy+force边界，不用单kernel speedup作科学结论。

## 投入规则

Dready若完整模型稳定收益<5%：关闭本候选，说明即使图准备免费也没有足够headroom。

Dready若>=5%，才运行Donline。

Donline若稳定收益<5%：收口为准备成本/现有atomic strong baseline已足够，不设计硬件。

Donline若>=5%，才打开预冻结四个holdout独立frame；仍只支持Native software response，不自动进入109更大矩阵、174或hardware。

## 当前状态

Source/input authority足够形成一轮bounded Lane F Goal。模型package与dataset的实际SHA256、109环境、CUDA/OpenEquivariance build和full energy/force数值合同仍须在执行前资格化。

R20保持CLOSED。
