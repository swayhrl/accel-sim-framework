# C16 Split-K 跨M权重复用因果对照 — Master V1

日期：2026-09-28。

## 0. 当前证据

已接受：

- static footprint audit：
  `c72d28b17247f25d0c3613604ab6cab1737666e0`
- native K-threshold series：
  `b17193ff6b3786fd01d5bfe83b5c1a0a03859729`
- independent threshold consumer：
  `6d226cd99946d3bd7b41c5ee005285183efbb915`
- native L2 read-hit diagnostic：
  `915707348617f7a8f432bad7a434a98d78b487c8`
- simulator non-admission：
  `f64a8c9100d0f2e779063291d31de1737a819304`

当前最强解释：
固定M/N/grid/scratch时，split1完整weight+metadata集合跨越L2容量附近后，L2 read hit下降、miss与DRAM大增、timing恶化；split8 local集合更小，未出现相同knee。

剩余主要缺口：
**NCU read-hit不是tensor级归因，也尚未直接证明跨M tile重复使用同一weight地址是这些hit的主要来源。**

因此不再使用未合格模拟器，改做真实GPU上的地址共享因果对照。

---

## 1. 核心counterfactual

固定：
- M=256
- N=49152
- K只取2560和3072
- group_size=128
- split只取1和8
- synthetic formula与accepted GPT3 proxy一致
- grid/scratch/reduction完全不变

构造16份**bit-identical** qweight/qzeros/scales replica。

所有cell都分配16份replica，保证分配总量一致。

目标kernel新增一个runtime `replica_mask`：

`replica_id = Mtile & replica_mask`

其中Mtile仍来自accepted：
`blockIdx_y / j_factors1`

两个状态：

### SHARED
`replica_mask=0`

所有16个M tile都访问replica 0。
其余15份已分配但不访问。

### PER_MTILE
`replica_mask=15`

Mtile 0..15分别访问自己的bit-identical replica。

因此：
- 算法结果应相同；
- 每个CTA读取的weight字节数相同；
- CTA grid相同；
- K-loop相同；
- split/reduction/scratch相同；
- 总GPU allocation相同；
- 唯一有意改变的是**不同M tile是否命中相同的weight-side物理地址**。

这是人工因果对照，不是自然GPT-3模型行为。

---

## 2. 为什么选择K2560与K3072

K2560：
- full weight+metadata = 62.34375MiB
- split1 L2 read hit≈0.9059
- split8≈0.9586
- split1明显比split8快

K3072：
- full = 74.8125MiB
- split1 L2 read hit≈0.6340
- split8≈0.9589
- split1优势已显著缩小

若跨M地址共享是关键复用来源：

- K2560 split1：SHARED→PER_MTILE应导致明显hit下降、DRAM上升、timing恶化；
- K3072 split1：SHARED本就已大量失去复用，因此PER_MTILE额外损失应相对较小；
- split8：SHARED状态local set很小且hit高；PER_MTILE若破坏跨M共享，应明显降低hit并增加DRAM。

这能直接检验“跨M共享 + 容量是否允许其存活”这一机制。

---

## 3. 统一patched kernel，避免codegen混杂

不能拿原binary与新replica binary直接做主比较。

必须构建一个独立extension，A/B/SHARED/PER_MTILE都使用**同一套patched GEMM kernel binary**。

建议kernel新增：
- `replica_mask`
- qweight/qzeros/scales per-replica stride

每个CTA都无条件执行：
- Mtile计算
- `replica_id = Mtile & replica_mask`
- 三个base pointer offset

SHARED mask=0与PER_MTILE mask=15走同一指令路径。

split1和split8可以用同一extension的runtime split_k_iters：
- split1：直接返回plane0，不启动reduction
- split8：正常sum(0)

不得修改GEMM数学、tile形状、dequant算法、K-loop、block/grid公式。

---

## 4. GPU矩阵

2 K × 2 split × 2 address-sharing state = 8 cells。

每cell：
- correctness
- launch audit
- 10 global warmups
- 25 mirror blocks，50 timing samples
- 2 same-cell warmups/sample

建议mirror：
`A_SHARED, B_SHARED, A_PER_M, B_PER_M, B_PER_M, A_PER_M, B_SHARED, A_SHARED`

这里A=split8，B=split1。

NCU 8 profiles：
每cell一份。

冻结：
- L2 read hit sectors
- L2 read miss sectors
- L1/TEX bytes
- L2 bytes
- DRAM bytes
- duration

A GEMM与reduction分开。
主因果比较只用GEMM read hit/miss + GEMM DRAM + module timing。

---

## 5. Correctness与identity

16份replica必须：
- 每份与replica0 byte-identical
- qweight/qzeros/scales各自SHA闭合
- VA ranges不重叠
- input不复制
- output/scratch不复制

所有SHARED/PER_MTILE输出应在现有容差内相同。
优先要求bitwise equal；若因split accumulation造成A/B不同，保持原A/B tolerance，但同一split的SHARED vs PER_MTILE应要求bitwise equal。

Launch必须保持：
- K2560/K3072:
  - split8 GEMM grid 49152
  - split1 GEMM grid 6144
  - block [32,2,1]
- split8 reduction grid 24576
- scratch不变

---

## 6. 主判读

### 强支持跨M weight-side reuse

需要：

1. K2560 split1：
   SHARED→PER_MTILE导致明显L2 read hit下降、miss/DRAM上升；
2. K3072 split1：
   同方向但额外恶化相对更小，符合SHARED状态下capacity已破坏部分跨M复用；
3. split8：
   PER_MTILE显著破坏其高hit优势，说明split8的高hit确实依赖跨M地址重复；
4. 同一patched binary、grid、scratch、compute、allocation闭合。

此时可以把项目结论提升为：

> weight-side跨M地址复用是当前L2 hit优势的重要来源，而split-K通过减小每个split的局部工作集提高了这种复用在cache中存活的机会。

仍不得说：
- 只有qweight；
- NVIDIA replacement细节；
- 所有LLM/GEMM普遍如此。

### 不支持

如果PER_MTILE几乎不改变hit/DRAM：
当前跨M复用解释需降级，停止继续机制设计。

---

## 7. 流水

Lane8 / 174-new：
- CPU-only source patch设计、static proof、memory budget、runner contract
- 先发布EARLY_GATE

Lane7 / 109：
- 同时CPU-only build/prep
- 只有EARLY_GATE支持后才GPU
- 一次GPU lock完成8 cells

Lane6 / 174-new：
- 同时准备consumer
- producer完成后独立重算

Lane4不动。

本阶段不抓SASS、不跑Accel-Sim。
