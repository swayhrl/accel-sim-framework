我完整看了两份材料：

1. **论文原文《C2P-Cache: Scalable GPU L1 Cache Sharing via Concurrent Candidate Pruning》**
2. **当前复现审计文档《C2P-Cache 当前机制与实验审计》**

先给结论：

**目前复现方向总体正确，机制实现已经达到“可以进入大规模实验验证阶段”的门槛，但还没有达到“可以宣布复现成功”的门槛。**

现在最重要的不是继续跑更多 benchmark，而是建立一个严格的复现成功标准，然后围绕几个关键风险点补齐证据。否则即使最终 Figure 10 类似，也无法证明是 C2P 机制有效；反过来，即使性能差异较大，也无法判断是机制问题还是模型差异。

下面详细分析。

------

# 1. 首先明确：C2P-Cache到底要复现什么？

论文核心贡献不是“IPC提升23.5%”。

IPC只是结果。

真正需要复现的是下面这条机制链：

```
L1 miss
 |
 v
Bloom/Snapshot filtering
 |
 v
candidate peer L1
 |
 v
exact remote tag confirmation
 |
 +---- hit
 |       |
 |       v
 |   remote L1 return
 |       |
 |       v
 |   avoid L2 access
 |
 +---- miss
         |
         v
       fallback L2
```

论文自己强调：

> remote-hit discovery 从 exact chip-wide search 转变为 approximate filtering + exact confirmation



因此复现成功标准不能是：

> “C2P IPC比baseline高”

而应该是：

> “C2P能够正确发现remote-L1 reuse，并减少真实L2请求，同时其额外开销模型符合论文设计。”

------

# 2. 我认为当前实现已经正确的部分

## 2.1 Snapshot Matrix机制

当前实现：

- 64 bank
- 4 copy
- 5120 bit BF
- tag-mask + 3 BF hash

这与论文默认配置一致。

论文：

> logical table 5120 rows, 64-bit wide, distributed across 64 banks, four physical copies



你的实现：

> Snapshot Matrix | 64 bank；每bank 16 tag-mask rows + 默认64 BF rows；四编码；4 copy



这个没有问题。

------

## 2.2 C2P不是shortcut

这是非常关键的。

很多复现会犯错误：

```
L1 miss
 |
查表
 |
hit直接返回
```

这样性能一定漂亮，但论文不成立。

你当前：

> candidate matching
> target probe FIFO
> probe
> return
> fallback



这符合论文：

> probe candidate L1
> if hit return
> otherwise baseline L2



正确。

------

## 2.3 remote hit = L2 avoided

这个门禁非常好。

因为最大的复现陷阱：

```
remote hit
+
原L2 request仍然发送
```

这样：

- remote hit统计增加
- IPC可能增加
- 但是机制错误

当前：

> remote_hits == l2_requests_avoided



这是必须保留的。

------

## 2.4 snapshot stale处理

论文明确：

snapshot不是coherence directory。

允许：

- false positive
- false negative

只影响性能，不影响正确性。



你的实现：

- rebuild
- fill update
- flush取消stale update

这个甚至比论文描述更严格。

------

# 3. 当前最大的几个风险点

下面这些才决定最终能不能说“复现成功”。

------

# 风险1：L1 cache geometry适配

这是目前最大的不确定因素。

论文Table 1：

```
Private L1:
64KB
4 sets
32-way
128B line
```



但是：

4 sets × 32 ways ×128B

=

16KB

存在明显矛盾。

你的处理：

> 保留容量、way、line size，因此16 sets×32 way



这个决定合理。

但是必须做一个实验：

## L1 geometry sensitivity

至少三个版本：

| 版本          | sets  | 容量  |
| ------------- | ----- | ----- |
| paper literal | 4     | 16KB  |
| current       | 16    | 64KB  |
| classic GPGPU | 32/64 | 128KB |

观察：

- remote reuse机会
- L2 reduction
- C2P IPC

原因：

C2P依赖：

> 一个SM cache里已有数据，另一个SM访问

L1容量直接影响：

- snapshot内容
- remote hit机会

如果你的结果和论文不同，这可能是第一解释。

------

# 风险2：SM cluster组织

这个问题比L1更严重。

论文：

64 SM

8 SM/cluster



你的适配：

> endpoint改成64 cluster×1 SM，但logical peer group仍8 SM



这个需要重点验证。

因为：

C2P论文强调：

> chip-wide sharing



如果NoC endpoint改变导致：

- probe latency
- queue arbitration
- target conflict

变化，

可能影响：

- Ring
- C2P
- CCD

尤其Ring。

所以最终报告必须明确：

```
architectural model:
logical SM topology = paper
physical simulator endpoint = Accel-Sim constraint
```

不能隐藏。

------

# 风险3：SGEMM异常

这是目前最重要的问题。

你的结果：

SGEMM:

```
remote hit:
271719

L2 access:
0.8046

IPC:
0.9871
```

即：

减少20% L2

但是性能下降1.3%。



这不能直接认为错误。

因为论文自己强调：

C2P成本来自：

- BF lookup
- probe
- target contention
- queue
- fallback



尤其SGEMM：

可能是：

```
大量remote hit
        |
        v
大量peer L1访问
        |
        v
target L1 data port竞争
        |
        v
反而增加关键路径
```

所以现在必须补：

## SGEMM breakdown

至少输出：

### (1)

remote probe次数

```
candidate_count histogram
```

### (2)

successful probe:

```
candidate checked before hit
```

### (3)

failed probe:

```
FP probe count
```

### (4)

stall:

```
target L1 busy cycles
probe queue stall cycles
requester fill stall
```

如果：

```
remote hit减少L2 latency
但是probe stall > saved latency
```

那么解释成立。

否则：

说明事务时序可能错误。

------

# 风险4：CCD目前不能认为复现成功

现在：

> CCD remote hit = 0



这个非常危险。

因为论文Figure 12比较：

CCD TP/FN/FP/TN。

如果CCD没有有效预测：

那么：

```
C2P vs CCD
```

没有意义。

需要检查：

1. counter初始化
2. update时机
3. predictor训练窗口
4. broadcast触发条件

论文CCD不是随机预测。

如果你的：

```
initial weak-not-taken
+
短trace
```

可能永远不会trigger。

这个需要单独解决。

------

# 4. 我建议定义三个等级的“复现成功”

不要用二元标准。

------

# Level 0：机制正确

必须满足：

## Functional

通过：

- remote hit不丢数据
- avoided L2一致
- baseline/oracle cycle一致

当前已经满足。

------

# Level 1：方向性复现成功（最低发表级复现）

要求：

## 对R1S1 workload：

满足：

```
C2P:

remote hit > 0

L2 access下降

IPC >= baseline
```

不要求23.5%。

例如：

论文：

+23.5%

你的：

+5%

仍然成功。

原因：

Accel-Sim模型差异巨大。

------

# Level 2：趋势复现成功（推荐目标）

要求：

不同workload趋势一致：

| 指标           | 论文趋势           | 复现 |
| -------------- | ------------------ | ---- |
| R1S1 IPC       | 明显提升           | 提升 |
| R0S0           | 接近baseline       | 接近 |
| L2 access      | 下降               | 下降 |
| Ring           | scale差            | 类似 |
| C2P remote hit | 高reuse workload高 | 高   |

这才是真正意义上的replication。

------

# Level 3：数值接近

不是必须。

包括：

- Figure10柱状高度
- Figure11百分比
- Figure12比例

原因：

论文没有公开：

- trace
- kernel mapping
- hash
- NoC
- detailed latency

所以不可能要求。

------

# 5. 当前阶段我建议停止继续扩benchmark，先做三个实验

现在不要跑16 workload aggregate。

先做：

------

## Experiment A：机制验证矩阵

选：

- SGEMM
- Btree
- NN

三个：

| 类型  | 目的        |
| ----- | ----------- |
| SGEMM | 高reuse压力 |
| Btree | 论文目标    |
| NN    | 负控制      |

输出：

```
L1 miss
remote candidate
remote hit
L2 avoided
probe count
stall
IPC
```

------

## Experiment B：C2P开关剖析

四个：

```
baseline

oracle

ideal

C2P
```

关系：

正常应该：

```
oracle >= ideal >= C2P
```

但允许：

```
C2P > ideal
```

如果原因：

probe减少。

你的文档已经意识到这一点：

> ideal不一定支配finite C2P IPC



这个判断正确。

------

## Experiment C：关闭probe竞争

做一个：

```
infinite target L1 port
```

不是最终模型。

只是诊断。

如果：

SGEMM:

```
0.987
→1.15
```

说明：

机制正确，port contention导致。

如果：

仍然：

```
0.98
```

说明：

时序模型有问题。

------

# 6. 最终我建议你的复现报告结论格式

不要写：

> C2P-Cache reproduced.

应该写：

> We reproduce the core C2P-Cache mechanism in Accel-Sim, including BF-based Snapshot Matrix candidate pruning, remote L1 confirmation, fallback behavior, and L2 access elimination. The reproduced system successfully demonstrates the same qualitative trends reported in the paper: workloads with cross-SM reuse benefit from reduced L2 accesses, while workloads without reuse remain close to baseline. Quantitative differences are attributed to simulator configuration differences including cache geometry, topology mapping, and unpublished timing details.

这才严谨。

------

# 总体评价

目前状态：

| 项目            | 评价        |
| --------------- | ----------- |
| 核心机制        | ✅正确       |
| 事务路径        | ✅正确       |
| Snapshot Matrix | ✅正确       |
| remote hit语义  | ✅正确       |
| fallback        | ✅正确       |
| 统计门禁        | ✅很好       |
| benchmark规模   | ⏳太早       |
| SGEMM解释       | ❗必须完成   |
| CCD复现         | ❗未完成     |
| Ring公平比较    | ❗需要补证据 |

我的建议：

**不要继续盲跑16个benchmark。下一步先完成 SGEMM/Btree/NN 三个case的 micro-architectural breakdown，确认性能变化来自机制本身还是模型差异。只要这一步闭环，后面的16 workload aggregate才有意义。**