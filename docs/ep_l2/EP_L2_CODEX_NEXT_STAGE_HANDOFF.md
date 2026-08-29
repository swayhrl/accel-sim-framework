# EP-L2 下一阶段 Codex 执行摘要

> 本文件是 `ELASTIC_PAYLOAD_L2_ARCHITECTURE_AND_ROADMAP.md` 的近期执行摘要。
> Codex 开始前必须先阅读完整文档。

---

# 1. 本阶段目标

不要立即实现完整 EP-L2。

当前只做：

```text
A. Target Baseline v0
B. RO opportunity shadow study
C. TVD opportunity shadow study
```

完成后停止，等待研究决策。

---

# 2. 固定基点

Core：

```text
32f9b8d52490044f487c14811121ed0368e48a48
```

Framework：

```text
d24455a1981d7f099f641b5b6f17adb08d973a4a
```

新分支：

```text
Core:
hrl/ep-l2-target-baseline-v0

Framework:
hrl/ep-l2-exp-v0
```

不得修改 frozen branches。

---

# 3. Target Baseline

每 L2 slice：

```text
64 sets
16 ways
128B line
1024 resident entries

128 bypass-only payload entries

MSHR line entries =128
request descriptors=256
max descriptors/address=32
descriptor lifetime=until response

WAD=128 line-address entries

L2→DRAM=128
FR-FCFS=128
DRAM ReturnQ=192
```

L1 Primary：

```text
64KiB
4 sets
128 ways
128B
4 banks
20 cycles
```

Memory：

```text
850MHz primary候选
1GHz headroom候选
```

850/1GHz最终primary尚未决定，不要自行决定。

---

# 4. 两个Target Baseline

必须有：

```text
B0-Legacy:
1024 resident RAM 1R1W
128 bypass RAM 1R1W

B0-Banked:
1152-entry 4-bank physical RAM
但静态限制1024 resident +128 bypass
每bank 1×128B op/cycle
```

B0-Banked用于和未来Unified Pool公平对比。

---

# 5. Target Baseline验收

机制关闭时验证：

```text
functionally correct
no request loss
no stale Fill
no descriptor leak
no payload leak
no WAD leak
bank op <=1/bank/cycle
```

同时采：

```text
L1 blockers
L2 Tag/Set
MSHR
descriptor pool
payload role
lower queues
DRAM bandwidth/scheduler
bank conflicts
```

---

# 6. 代表workload

先跑：

```text
vectorAdd_4M
scan
spmv
convolutionSeparable
cfd_097k
dwt2d
sad
sgemm
btree
3mm
gemm
fastWalshTransform_7_21
fastWalshTransform_11_19
```

不必立即跑51项。

---

# 7. RO Opportunity Shadow

只观察，不改变请求行为。

实现：

```text
per-kernel/epoch oracle read-only classification

统计：
RO request/miss coverage
same-line arrivals before Fill
waiter count
potential detach
potential duplicate lower read
read amplification
tag cycles saved
MSHR relief
descriptor/payload/lower traffic cost
```

Shadow policies：

```text
all RO
waiter_count==1
oracle low-overlap
merge N then overflow independent read
N=1/2/4/8
```

---

# 8. TVD Opportunity Shadow

不改变真实cache hit/miss。

模拟：

```text
metadata=8/16/32/64/128
payload budget=0/8/16/32/64/128
```

统计：

```text
clean/dirty victim reuse
reuse before/in/after WB
potential avoided read/bytes
metadata-only miss
payload-only miss
promotion opportunity
dirty-inflight write wait
```

Policy：

```text
read serve-in-place
clean write/atomic promote
dirty inflight read forward
dirty inflight write/atomic wait
```

---

# 9. 禁止事项

本阶段不得：

```text
实现Unified Pool动态借用
实现RO no-MSHR真实请求路径
实现TVD真实hit
实现graphics bypass borrowing
开始完整性能评估
写论文结论
```

---

# 10. 交付

```text
TARGET_BASELINE_CLOSEOUT.md
RO_OPPORTUNITY_REPORT.md
TVD_OPPORTUNITY_REPORT.md

target_baseline_summary.csv
ro_opportunity.csv
tvd_opportunity.csv
payload_role.csv
bank_pressure.csv

review_pack.tar.gz
```

最终汇报：

```text
target baseline是否Tag/MSHR/descriptor/lower-bound
RO coverage与read amplification
useful tag release rate
TVD potential hit/avoided traffic
bank/port风险
未决参数
```

完成后 STOP。
