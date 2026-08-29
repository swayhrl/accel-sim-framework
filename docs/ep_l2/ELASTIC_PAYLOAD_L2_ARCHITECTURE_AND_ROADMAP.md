# Elastic Payload L2：总体架构、协议细节与研究路线

> **文档定位**
>
> 本文冻结当前讨论中已经明确的架构语义，区分：
>
> 1. 已确认的设计事实；
> 2. 暂定但尚需实验选择的策略；
> 3. 不应自行假设的开放参数；
> 4. 正式实现前必须完成的 opportunity study；
> 5. 从目标 baseline、机会分析、功能实现到论文评估的完整路线。
>
> 本文同时面向研究者阅读与 Codex 后续执行。除明确标为“开放决策”的内容外，Codex 不得自行改变语义。

---

# 1. 一句话概括

本工作的当前核心不再是完整的 Late Physical Binding，而是：

> **解耦 Resident Tag、请求/等待者元数据与物理 Payload；将原本静态分给 resident cache 和 bypass return 的 line-sized 数据容量合并为统一 Payload Pool，并在此基础上支持可替换的只读 Pending Tag 与 WAD-backed Transient Victim Directory。**

暂用名称：

```text
Elastic Payload L2
```

可缩写为：

```text
EP-L2
```

该名称仅作为内部工作名，不是最终论文标题。

---

# 2. Round-1 对研究方向的影响

Round-1 使用的是经过修正的 QV100 conventional sector-L2，而不是本工作的目标结构。

Round-1 配置为：

```text
64 L2 slices
32 sets × 24 ways × 128 B / slice
192 MSHR entries / slice
4 merge targets / MSHR
32-entry MissQ / slice
64-entry L2→DRAM FIFO
64-entry FR-FCFS scheduler queue
192-entry DRAM return queue
```

Round-1 的主要作用是说明：

```text
在该配置下：
MissQ / lower path 压力明显；
per-MSHR merge target 静态限制明显；
Set all-reserved 与 FillPort blocking 基本不出现；
utilization 与 blocking 不能等价解释。
```

因此：

1. 完整 LateBind 不再因“当前 QV100 Set/Way 已成为主要瓶颈”而成立；
2. 但目标硬件配置与 QV100 不同，目标配置下必须重新确认 bottleneck 是否前移；
3. Tag–Payload 解耦、统一 Payload、TVD 和 RO no-MSHR 仍有独立价值；
4. Round-1 结果不能直接代替目标 baseline characterization。

---

# 3. 已确认的目标配置

以下配置均以 **每个 L2 slice** 为单位，除非另有说明。

## 3.1 整体 L2

```text
L2 slices                          64
Memory channels                    32
Slices / channel                   2
Cache line                         128 B
```

## 3.2 Resident Tag / nominal resident cache

```text
Sets                               64
Ways                               16
Resident Tag Entries               1024
Nominal resident payload entries   1024
Nominal resident capacity          128 KiB / slice
```

全芯片 nominal resident L2：

```text
64 × 128 KiB = 8 MiB
```

## 3.3 Bypass Payload

Baseline 中存在单独的 bypass return 数据阵列：

```text
Bypass Payload Entries             128 / slice
Bypass capacity                    16 KiB / slice
```

它用于不分配 resident tag/data entry 的 bypass 请求返回数据。

## 3.4 Proposed Unified Payload Pool

```text
1024 resident payload
+
128 bypass payload
=
1152 physical Payload Entries / slice
```

每项：

```text
128 B
```

容量：

```text
144 KiB / slice
9 MiB physical payload capacity over 64 slices
```

注意：

```text
9 MiB 是物理 line payload 总量；
8 MiB 是 nominal resident cache capacity；
多出的 1 MiB 原本是 bypass-only payload。
```

## 3.5 Unified Payload RAM banking

确认采用：

```text
4 banks × 288 entries
完整 128B line 按 entry 交错映射到 bank
```

建议基础映射：

```text
bank = payload_id mod 4
row  = payload_id / 4
```

每 bank：

```text
1 operation / cycle
1 operation = one 128B line read or one 128B line write
```

因此 aggregate upper bound：

```text
4 line operations / cycle / slice
```

但具体能否达到取决于 bank conflict。

## 3.6 Baseline physical RAM ports

Baseline 仍有两块独立 RAM：

```text
Resident RAM:
    1024 entries
    1 bank
    1R1W / cycle

Bypass RAM:
    128 entries
    1 bank
    1R1W / cycle
```

因此 baseline 理论 aggregate upper bound 也是最多：

```text
2 reads + 2 writes / cycle
```

但它受静态角色约束；proposed 受 bank mapping 约束。

这意味着评估时必须同时提供：

```text
Legacy physical baseline
Bank-matched static-partition baseline
Unified-pool proposed
```

避免把 banking 改造收益误算成容量统一收益。

## 3.7 MSHR / Request Descriptors

确认采用：

```text
MSHR line entries                 128 / slice
Shared request/target descriptors 256 / slice
Per-address linked-list cap        32 requests
```

含义：

```text
MSHR entry:
    跟踪一个不同的 outstanding block address

Request/target descriptor:
    跟踪一个等待该 block 的具体 requester
```

例如：

```text
MSHR[A]
  ├─ target/request descriptor 17
  ├─ target/request descriptor 44
  └─ target/request descriptor 203
```

每地址最多 32 个 descriptor。

## 3.8 MissQ lifetime

已确认：

> **MissQ / request descriptor entry 一直保留到 Fill/response 完成。**

因此它不是“下层发出后立即释放”的短 FIFO。

本方案当前将 256-entry MissQ 与 256-entry shared request/target descriptor pool视为同一长期请求节点资源。

若实际 RTL 中两者是不同物理结构，正式实现前必须更正此映射，不能静默复制两份 256 项资源。

## 3.9 Lower response identity

确认：

> **下层 response 原样返回 transaction ID / payload ID。**

因此 no-MSHR 路径可以使用 Payload Entry 作为 completion anchor，无需额外的大型 address-indexed return table。

## 3.10 WAD / WBQ Address Tracker

```text
Entries                       128 / slice
Granularity                   line address
Baseline release              WB response
```

基础职责：

```text
检测 pending writeback 与新 lower read 的同地址 hazard
保证内存侧读写顺序正确
```

本工作将它扩展为：

```text
WAD-backed Transient Victim Directory
```

## 3.11 Lower-side队列初始目标

当前建议：

```text
L2→DRAM FIFO                  128
FR-FCFS scheduler queue       128
DRAM→L2 ReturnQ               192
```

作用域当前按如下方式解释：

```text
L2→DRAM FIFO:
    per L2 slice / memory subpartition

FR-FCFS scheduler:
    per memory channel

DRAM→L2 ReturnQ:
    per memory channel
```

如果实际 simulator 配置作用域不同，Codex 必须先给出源码映射再修改。

## 3.12 DRAM

理论主配置：

```text
32 channels × 16 B × DDR × 850 MHz
= 870.4 GB/s
```

可选 memory-headroom sensitivity：

```text
1 GHz
= 1024 GB/s
= +17.65% theoretical peak bandwidth
```

当前未冻结 850 MHz 还是 1 GHz 作为最终 primary。

原则：

```text
不能仅为了让 bottleneck 前移到 L2 而人为提高 DRAM；
应根据目标芯片/真实实现依据冻结 primary；
另一档作为 headroom sensitivity。
```

## 3.13 L1 Primary / Secondary

Primary：

```text
64 KiB / shader core
4 sets
128 ways
128 B line
4 L1 banks
20-cycle L1 latency
```

Secondary：

```text
112 KiB / shader core
4 sets
224 ways
128 B line
```

实际主结果使用 Primary 64 KiB。

L1 的 MSHR、MissQ、bank port 和 write/allocation policy 尚未冻结，必须在目标 baseline closeout 前补齐。

---

# 4. 总体架构

```text
                         Requests from upper level
                                   │
                                   ▼
                    ┌──────────────────────────┐
                    │ Resident Tag Array       │
                    │ 64 sets × 16 ways        │
                    │ tag/state/data_ptr       │
                    └───────────┬──────────────┘
                       hit      │       miss/pending
                                │
          ┌─────────────────────┼──────────────────────────┐
          │                     │                          │
          ▼                     ▼                          ▼
   Resident/TVD read      Normal MSHR path          Certified RO path
          │              128 line entries                  │
          │                     │                    RO_PENDING Tag
          │                     ▼                          │
          │           Shared 256 request nodes            │
          │                     │                          │
          └──────────────┬──────┴──────────────┬───────────┘
                         │                     │
                         ▼                     ▼
                Unified Payload Pool      WAD / TVD
                 1152 × 128B              128 entries
                 4 × 288 banks            tag→data_ptr
                         │                     │
                         └────────┬────────────┘
                                  ▼
                         Miss/lower issue path
                                  │
                         L2→DRAM / MC / DRAM
                                  │
                                  ▼
                        response carries payload_id
                                  │
                                  ▼
                   attached Fill / detached response
```

---

# 5. 核心贡献候选

## 5.1 Decoupled Tag–Payload Unified Pool

Baseline：

```text
1024 resident-only data entries
128 bypass-only data entries
```

Proposed：

```text
1152 dynamically role-assigned Payload Entries
```

Resident Tag、RO transaction、bypass request 和 TVD entry 均通过 `data_ptr` 指向 Payload。

数据角色切换时：

```text
不搬动 128B 数据；
只修改 owner/state/pointer。
```

## 5.2 Replaceable Read-Only Pending Tags

对经过严格认证的只读 miss：

```text
不分配传统 address-indexed MSHR；
分配 resident RO_PENDING Tag；
分配 Payload landing entry；
分配 request descriptor chain；
Tag 在 Fill 前允许被替换；
Payload/transaction 继续完成。
```

若 Tag 被替换后同地址再次到达：

```text
允许产生独立 lower read。
```

它以额外 memory traffic 换取：

```text
减少 MSHR/address-coalescing metadata约束；
降低 transient resident-tag occupancy；
扩大 unique RO transactions in flight。
```

## 5.3 WAD-backed TVD

在已有 128-entry WAD 上增加：

```text
data_ptr
victim role/state
retention age/replacement metadata
```

复用统一 Payload 中未被 mandatory transaction 占用的 entry，形成：

```text
无需独立 victim data array 的动态 victim cache。
```

第一版 TVD read hit：

```text
serve-in-place
```

不立即 promote 到 resident。

---

# 6. Tag Entry 建议字段

Resident Tag Entry 至少需要：

```text
tag / block address portion
valid
cache state
dirty/sector information
replacement metadata

payload_ptr[10:0]

RO_PENDING
transaction_generation
```

其中：

```text
payload_ptr width = ceil(log2(1152)) = 11 bits
```

`transaction_generation` 或 ownership token 用于避免 stale Fill 修改已经复用的 Tag。

## 6.1 Stale Fill 防护

场景：

```text
Tag way T originally belongs to transaction A
T is replaced and reused by B
A response returns later
```

A 的 response 只能在满足：

```text
T still attached
AND T address matches A
AND T generation matches A
```

时将 Tag 状态转为 VALID。

否则：

```text
按 detached response 处理；
不修改当前 T。
```

---

# 7. Payload Entry 建议字段与角色

Payload Entry 数据：

```text
128B payload
```

控制字段至少包括：

```text
role/state
valid
owner type
transaction/payload generation
attached_tag_valid
attached_tag_index
attached_tag_generation

waiter_head
waiter_tail
waiter_count

optional TVD owner
optional WAD/TVD index
```

建议逻辑角色：

```text
FREE

RESIDENT_CLEAN
RESIDENT_DIRTY

NORMAL_FILL_PENDING
RO_FILL_ATTACHED
RO_FILL_DETACHED

BYPASS_FILL_PENDING
BYPASS_READY

TVD_CLEAN
TVD_DIRTY_WB_PENDING
TVD_DIRTY_WB_INFLIGHT
TVD_CLEAN_AFTER_WB
```

状态编码可以压缩，但协议语义必须可区分。

---

# 8. Request/Target Descriptor

256-entry shared descriptor pool。

每个 descriptor 建议包含：

```text
requester identity
warp/CTA/core destination
response route
access size/mask
next descriptor index
payload_id
transaction_id
issued/completed state
request type
```

每个 transaction/line chain：

```text
head
tail
count[4:0]   // up to 32
```

普通 MSHR transaction：

```text
MSHR entry owns descriptor chain
```

RO no-MSHR transaction：

```text
Payload Entry owns descriptor chain
```

## 8.1 Descriptor lifetime

```text
allocation
  ↓
waiting/merged
  ↓
lower read issued
  ↓
memory pending
  ↓
Fill/response
  ↓
requester completion
  ↓
free
```

Descriptor 不因 lower issue 而提前释放。

---

# 9. 普通非 RO MSHR 路径

普通 read/write/atomic 和未被证明为 read-only 的请求继续使用 conventional MSHR：

```text
Tag miss
  ↓
allocate resident tag/data policy state
  ↓
allocate/find 128-entry MSHR line entry
  ↓
append one of 256 request descriptors
  ↓
max 32 descriptors/address
  ↓
send one lower read
  ↓
Fill
  ↓
complete descriptor chain
```

普通路径仍负责：

```text
same-address coalescing
read/write ordering
atomic ordering
```

---

# 10. Certified RO no-MSHR 路径

## 10.1 Correctness eligibility

只有满足严格保证的地址才可进入：

```text
Certified Read-Only
```

保证范围内不得出现：

```text
GPU store
atomic
其他 coherent agent write
device-memory side effects
```

初期实验允许使用：

```text
Oracle read-only classification
```

最终可由已有 compiler/runtime/page/object annotation 提供。

当前工作不负责解决编译器 read-only 分析精度，但必须报告 coverage。

## 10.2 First RO miss A1

```text
RO Read A1
  ↓ Resident Tag miss
  ↓ certified read-only
allocate:
  Q1 request descriptor
  P1 Payload Entry
  T1 resident Tag way
  ↓
T1 = A, RO_PENDING, payload=P1
P1 = RO_FILL_ATTACHED, waiters=Q1
  ↓
send lower read(transaction_id=P1+generation)
```

不分配传统 MSHR line entry。

## 10.3 A2 arrives while T1 is still attached

```text
Tag lookup hits A + RO_PENDING
  ↓
allocate Q2
  ↓
append Q2 to P1 waiter list
  ↓
do not send another lower read
```

这是一种基于 attached pending tag 的小型 merge。

每 transaction 最多 32 个 descriptors。

## 10.4 T1 is selected as victim before Fill

```text
T1 invalidated/reused
  ↓
P1.attached_tag_valid = false
P1.state = RO_FILL_DETACHED
```

Q1/Q2 和 lower transaction 继续存在。

P1 仍保证 response 有 landing location。

## 10.5 A3 arrives after T1 is gone

```text
Resident Tag miss
  ↓
detached transaction P1 is intentionally not address-searched
  ↓
allocate Q3 + P2 + new RO_PENDING Tag T2
  ↓
send duplicate lower read A
```

因此同地址可能同时存在：

```text
P1 detached transaction
P2 attached transaction
```

但 resident Tag Array 中最多只有当前 T2 的 A tag。

## 10.6 Attached Fill

若 response 对应 Tag 仍满足：

```text
address + generation + payload owner match
```

则：

```text
write P
Tag RO_PENDING → VALID
Payload RO_FILL_ATTACHED → RESIDENT_CLEAN
complete waiters
```

## 10.7 Detached Fill

若 Tag 已不存在：

```text
write P
serve all waiters
after response completion:
    free request descriptors
    free Payload P
```

明确：

```text
不重新安装 Tag；
不重新选择 way；
不自动进入 TVD。
```

后续若希望 detached data机会式进入 TVD，必须作为单独 extension 评估，不属于第一版。

---

# 11. RO no-MSHR 的本质与边界

它不是：

```text
完全没有 transaction tracking
```

而是：

```text
绕过 address-indexed MSHR；
每笔独立 lower transaction 仍由
Payload Entry + request descriptor chain 跟踪。
```

建议论文术语：

```text
MSHR-bypassed read-only transaction
```

或：

```text
non-coalescing detached read-only miss
```

不建议只写：

```text
MSHR-free
```

除非同时解释 completion metadata 仍然存在。

---

# 12. RO_PENDING Tag replacement policy

当前尚未冻结最终 victim priority。

需要比较至少三种策略。

## P0：Aggressive

```text
所有 certified RO_PENDING Tag 均可替换
```

## P1：Waiter-aware

```text
只有 waiter_count == 1 的 RO_PENDING Tag 可优先替换
```

一旦已有第二个 same-line requester：

```text
reuse_seen = 1
```

暂时保护它。

## P2：Oracle low-overlap

只有已知在 Fill 前不会出现新的 same-line read 的 RO_PENDING Tag 可替换。

P2 用于上限，不是可直接实现的最终方案。

建议 replacement priority 初始实验：

```text
INVALID
  >
replaceable RO_PENDING
  >
normal clean LRU
  >
dirty resident
  >
non-replaceable pending/locked
```

但该优先级尚需 opportunity study 和性能实验确认，Codex不得直接作为最终 policy 固化。

---

# 13. RO no-MSHR 的关键性能风险

## 13.1 Duplicate-read amplification

```text
tag detached
  ↓
same address arrives
  ↓
new lower read
```

可能增加：

```text
DRAM read count
DRAM bytes
MissQ descriptors
Payload occupancy
L2→DRAM queue pressure
MC scheduler pressure
```

定义：

\[
ReadAmplification =
\frac{RO\ no\text{-}MSHR\ lower\ reads}
{conventional\ coalesced\ lower\ reads}
\]

## 13.2 Lower path saturation

如果 target baseline 的 lower path仍是 bottleneck：

```text
更多 outstanding
```

可能只会：

```text
增加排队，不提高吞吐。
```

因此必须配合：

```text
MissQ / L2→DRAM / DRAM scheduler / bandwidth sensitivity
```

## 13.3 Payload pressure

每个独立 RO transaction 预留一个 Payload。

大量 duplicate reads会消耗统一池，可能挤压：

```text
resident
bypass
TVD
normal fill
```

## 13.4 Descriptor pressure

每个 requester需要一个 256-entry descriptor。

即使 MSHR 被绕过，也不会绕过 descriptor capacity。

---

# 14. Unified Payload Pool

## 14.1 Baseline静态分池

```text
Resident payload quota: 1024
Bypass payload quota:    128
```

## 14.2 Proposed动态角色

```text
FREE
RESIDENT
NORMAL/RO FILL
BYPASS
TVD
WB-retained
```

## 14.3 Mandatory vs opportunistic

Mandatory：

```text
normal Fill landing
RO attached/detached Fill landing
bypass return landing
dirty victim required for pending/inflight WB
```

Opportunistic：

```text
clean TVD victim
WB-complete retained victim
```

任何 opportunistic entry 都不能阻塞 mandatory forward progress。

## 14.4 Allocation / reclaim priority

初始建议：

```text
new mandatory allocation:
  1. use FREE payload
  2. reclaim clean TVD
  3. reclaim WB-complete TVD
  4. evict clean resident if policy permits
  5. evict dirty resident only if WAD/WB resources available
```

需要额外保证：

```text
Fill landing credit
Bypass landing/progress guarantee
Dirty-WB progress guarantee
```

具体 watermark/credit 数尚未冻结，应由 occupancy opportunity study 决定。

---

# 15. Banking、端口与公平比较

## 15.1 Proposed

```text
4 banks
288 entries/bank
1 × 128B op/bank/cycle
```

同 bank 的以下操作竞争：

```text
resident hit read
TVD read
WB data readout
normal Fill write
RO Fill write
bypass Fill write
bypass response read
```

## 15.2 WB read 的定义

```text
dirty victim payload
  ↓
从 Unified Data RAM 读取128B dirty line
  ↓
构造下层 writeback packet
```

该 Payload RAM 读取即：

```text
WB read / writeback-data readout
```

## 15.3 Baseline与Proposed公平性

Baseline 两块 RAM：

```text
Resident: 1R1W
Bypass:   1R1W
```

Proposed：

```text
4 banks × 1 arbitrary op
```

二者 aggregate 上限都可达到4 ops/cycle，但允许的操作组合不同。

必须提供三种对照：

### Legacy-B0

```text
two physical arrays
static partition
```

### Bank-Matched-B0

```text
same 4-bank 1152-entry physical array as proposed
but logically enforce:
  1024 resident-only
  128 bypass-only
```

### Unified

```text
same 4-bank physical array
dynamic role allocation
```

这样可分别回答：

```text
银行结构改变的收益/代价
容量统一本身的收益
```

## 15.4 必须统计的 bank 指标

```text
per-bank read/write requests
bank conflict cycles
request type breakdown
resident vs bypass vs fill vs WB vs TVD
arbitration wait cycles
port utilization
```

---

# 16. WAD-backed TVD

## 16.1 Baseline WAD

```text
128 line-address entries
mandatory pending WB hazard tracking
release at WB response
```

## 16.2 Proposed TVD metadata

在原 entry 增加：

```text
11-bit data_ptr
victim state
retention/replacement age
optional dirty/valid metadata
```

如果 entry 数仍固定128：

```text
地址字段不是新增容量；
新增成本主要是 pointer + state + replacement bits。
```

## 16.3 Dynamic effective capacity

\[
C_{TVD}(t)=
\min\left(
128-N_{mandatory\ WAD}(t),
N_{borrowable\ payload}(t)
\right)
\]

TVD 不是固定拥有128个数据项。

## 16.4 Priority

```text
1. mandatory pending dirty WB
2. mandatory inflight dirty WB
3. WB-complete retained victim
4. clean opportunistic victim
```

当 WAD/TVD full 且新 mandatory WB 到来：

```text
evict clean TVD
  ↓
evict WB-complete retained TVD
  ↓
allocate mandatory WAD
```

不得删除：

```text
WB_PENDING
WB_INFLIGHT
```

## 16.5 TVD read hit：Serve-in-place

```text
Resident Tag miss
  ↓
WAD/TVD lookup hit
  ↓
read payload via data_ptr
  ↓
return requester
  ↓
keep TVD entry
  ↓
update TVD age
```

不立即安装 resident Tag。

## 16.6 Clean TVD + write/atomic

已确认使用保守方案：

```text
promote-to-resident
  ↓
resident Tag points to same Payload
  ↓
remove TVD metadata
  ↓
execute normal write/atomic path
```

需要统计：

```text
TVD clean write/atomic promotions
promotion wait cycles
promotion blocked by tag availability
promotion-triggered resident eviction/WB
```

若该路径成为瓶颈，再考虑更复杂的 directly-writable TVD。

## 16.7 Dirty TVD + WB inflight

Read：

```text
forward from retained latest Payload
```

Write/atomic：

```text
wait for WB response
then promote/execute
```

需要统计：

```text
read-forward count
write/atomic wait count
wait cycles
```

## 16.8 Single authoritative copy

必须保证：

```text
对可写数据：
Resident 与 TVD 不能同时存在两个 authoritative copy。
```

TVD promotion时：

```text
建立 resident Tag
删除 TVD metadata
不搬数据
```

---

# 17. Invalidate / Flush / Coherence要求

任何正式功能实现必须扩展以下操作：

```text
invalidate
cache flush
context/kernel boundary cleanup
coherence probe（若目标系统存在）
```

它们必须同时检查：

```text
Resident Tag
RO_PENDING attached transaction
RO detached Payload transaction
WAD/TVD
pending WB
```

Certified RO fast path不能绕过系统级 invalidate/epoch termination。

---

# 18. Graphics bypass方向

当前没有可直接使用的图形 trace，也不确定现有 trace 是否携带 bypass属性。

因此现阶段只能冻结结构语义：

```text
bypass请求：
不分配 resident Tag；
分配 Payload landing；
返回后由bypass路径消费并释放。
```

需要后续确认 bypass分类来自：

```text
graphics stage
request cache policy bit
address region
oracle annotation
或其他真实实现信号
```

没有真实图形 workload前，可以做：

```text
synthetic graphics-like bypass pressure
```

但不能将其写成完整图形实证。

---

# 19. 目标Baseline

## B0-Legacy：Target Conventional Baseline

```text
64 slices

L2:
64 sets × 16 ways
1024 resident Tag/data
128 bypass-only payload
two separate 1R1W RAMs

MSHR line entries        128
request descriptors      256
max chain/address        32
MissQ lifetime           until response
WAD                      128

L2→DRAM                  128
FR-FCFS                   128
DRAM ReturnQ              192

L1 primary:
64 KiB / 4 sets / 128 ways
4 banks / 20 cycles
```

## B0-Banked：Bank-matched Static Baseline

```text
same 4-bank 1152-entry RAM as proposed
but enforce static ownership:
1024 resident
128 bypass
```

无：

```text
TVD
RO pending replacement
RO MSHR bypass
dynamic borrowing
```

B0-Banked 是机制 attribution 的关键 baseline。

---

# 20. Ablation设计

## B1：Tag–Payload Decoupling Only

```text
增加 data_ptr
相同行为和静态配额
无动态借用
无 TVD
无 RO replacement
```

目标：

```text
证明 pointer化本身没有隐含性能收益或错误。
```

## B2：Unified Payload Pool

```text
1152 dynamic pool
无 TVD
无 RO replacement
```

目标：

```text
隔离 resident/bypass容量共享收益。
```

## B3：Replaceable RO Pending Tag + normal MSHR

```text
RO pending tag可替换
同地址请求仍由传统 MSHR合并
```

目标：

```text
隔离 transient Tag release 的贡献。
```

## B4：RO no-MSHR

```text
RO pending Tag attached时通过Tag/Payload chain merge
Tag detached后同地址请求独立发 lower read
```

目标：

```text
隔离 MSHR bypass 和 duplicate traffic。
```

## B4a：Waiter-aware / predictor policy

```text
只对低 in-flight same-line reuse 的RO transaction启用。
```

## B5：WAD-backed TVD

```text
serve-in-place read hits
dynamic payload retention
```

## B6：Full EP-L2

```text
Unified Pool
+
RO Pending Tag replacement
+
RO no-MSHR policy
+
TVD
```

---

# 21. Opportunity Study 1：RO no-MSHR / Early Tag Release

这是正式功能实现前优先级最高的机会分析之一。

## 21.1 目标

回答：

```text
多少请求可被严格证明为只读？
这些只读请求在Fill前是否有同地址复用？
Tag被detached后重复lower read会增加多少流量？
释放Tag/MSHR后是否真的解除目标baseline瓶颈？
```

## 21.2 Oracle只读定义

优先使用：

```text
per kernel/epoch address-region oracle
```

某地址区间在该 epoch 中：

```text
无store
无atomic
无外部write
```

则标记为 certified RO。

不得只因为当前指令是 load 就判定整条 line只读。

## 21.3 Timing-neutral shadow统计

第一阶段不改变 hit/miss/请求数量，只观察若启用机制会发生什么。

每个 conventional miss记录：

```text
block address
load PC
kernel/epoch
issue cycle
fill cycle
requester count
tag set/way
```

对 certified RO统计：

```text
RO requests / all L2 requests
RO misses / all L2 misses

in-flight same-line arrivals:
0
1
2–3
4–7
8–15
16–31
≥32

waiter count when RO_PENDING would be selected as victim

detached后、原Fill前的同地址新请求数
potential duplicate lower reads
potential duplicate bytes

RO_PENDING tag residency cycles
potential released tag cycles
set-local released-way distribution

traditional MSHR entries saved
merge targets/descriptors saved
extra descriptors required
extra Payload entries required
extra L2→DRAM transactions
```

## 21.4 Shadow policies

```text
RO-P0:
all certified RO pending tags replaceable

RO-P1:
only waiter_count == 1 replaceable

RO-P2:
oracle low-overlap replaceable

RO-P3:
merge first N requesters;
after detached/overflow allow independent read
```

其中 N 可测：

```text
1 / 2 / 4 / 8
```

## 21.5 关键指标

```text
Read Amplification
Useful Tag Release Rate
MSHR Occupancy Relief
Descriptor Pressure Increase
Payload Pressure Increase
Lower Traffic Increase
```

定义：

\[
UsefulTagReleaseRate=
\frac{真正被选为victim并让其他请求继续的RO\_PENDING}
{所有RO\_PENDING}
\]

## 21.6 进入功能实现的Gate

至少满足以下一类：

```text
A. Tag/set allocation pressure显著且RO release可解除；
或
B. MSHR/merge metadata成为目标baseline瓶颈，
   RO no-MSHR能以可接受流量放大解除。
```

若：

```text
duplicate read amplification很高
且Tag/MSHR relief很低
```

则不应实现 aggressive no-MSHR。

---

# 22. Opportunity Study 2：Shadow TVD

## 22.1 目标

回答：

```text
被淘汰数据在Payload需要被回收前是否会重访问？
128-entry WAD metadata与动态spare Payload能覆盖多少reuse？
```

## 22.2 Shadow结构

不改变真正 cache hit/miss。

每个 shadow entry：

```text
block address
clean/dirty
eviction cycle
WB state
payload-retention deadline/model
reuse age
```

模拟 metadata容量：

```text
8 / 16 / 32 / 64 / 128
```

模拟 payload可借容量：

```text
0 / 8 / 16 / 32 / 64 / 128
```

并支持真实动态上限：

```text
min(free WAD entries, borrowable payload)
```

## 22.3 统计

```text
clean victim re-reference
dirty victim re-reference

reuse before WB issue
reuse while WB inflight
reuse after WB response
reuse before payload reclaim

read reuse
write reuse
atomic reuse

reuse distance in accesses
reuse time in cycles

potential TVD hit
potential avoided lower read
potential avoided bytes

metadata hit but payload unavailable
payload available but WAD metadata unavailable
evicted TVD entry later reused
```

## 22.4 Serve-in-place模型

shadow opportunity应按第一版 policy估算：

```text
read:
serve-in-place

clean write/atomic:
promote-to-resident

dirty inflight read:
forward

dirty inflight write/atomic:
wait WB response
```

并统计 promotion / wait机会。

## 22.5 进入功能实现的Gate

TVD应至少满足：

```text
在合理metadata/payload预算下，
能够覆盖可观的post-eviction read reuse，
并减少lower reads/bytes。
```

如果 128-entry metadata + 128 spare payload 的潜在 hit率仍极低，TVD降级为次要或删除。

---

# 23. Opportunity Study 3：Payload角色互补性

图形trace准备好后进行；计算trace也可先测 resident/fill/WB/TVD。

目标：

```text
不同Payload角色的峰值是否错开？
静态128 bypass pool在compute中有多少空闲？
graphics bypass高峰时resident/reclaimable payload有多少？
```

统计：

```text
resident payload occupancy
RO fill occupancy
normal fill occupancy
bypass occupancy
dirty-WB retained occupancy
TVD occupancy
FREE occupancy

pairwise temporal correlation
sum-of-peaks vs peak-of-sum
borrow demand
reclaim demand
```

若：

```text
peak-of-sum << sum-of-peaks
```

说明统一池有明显统计复用价值。

---

# 24. 目标Baseline校准

正式机制实现前，必须先建立 B0-Legacy / B0-Banked。

## 24.1 需要核对的目标资源

```text
L1:
MSHR
MissQ
bank ports
write/allocation policy

L2:
ICNT→L2 FIFO
L2→ICNT FIFO
normal MSHR merge semantics
descriptor allocator
bank arbitration

Memory:
per-channel outstanding credits
NoC injection/ejection credits
scheduler throughput
DRAM timing
```

## 24.2 850MHz与1GHz

至少选择代表 workload比较：

```text
vectorAdd
scan
spmv
dwt2d
cfd
sgemm
btree
3mm/gemm
```

观察：

```text
per-channel bw_util
windowed bw_util
L2→DRAM full
scheduler blocking
MSHR lifetime
cycles
```

只有当1GHz有目标硬件依据时，才作为primary。

---

# 25. 当前进行中的 Round-2 Diagnostic 的作用

现有/计划的：

```text
merge 4→8
MissQ 32→64
L2→DRAM 64→128
FR-FCFS 64→128
```

仍应完成。

它们的作用是：

```text
解释Round-1 QV100瓶颈；
帮助确定target baseline；
不是最终EP-L2机制结果。
```

目标设计最终：

```text
128 MSHR line entries
256 shared descriptors
per-address cap 32
```

因此 4→8 仅是验证固定merge限制敏感性。

---

# 26. Kernel级分析

当前 Round-1 是 application-level aggregate。

机会分析应支持：

```text
kernel/epoch boundary reset or snapshot
```

原因：

```text
read-only classification必须有epoch；
同一application不同kernel可能访问角色不同；
temporal变化不能自动解释为single-kernel phase。
```

最低要求：

```text
per kernel:
requests
RO coverage
same-line overlap
duplicate-read opportunity
TVD opportunity
cycles
```

无需一开始把所有现有L2CHAR指标都复制成kernel级。

---

# 27. 关键正确性不变量

## Tag / Payload

```text
valid resident Tag 必须指向有效 Payload
一个 Payload最多有一个authoritative owner
stale response不得修改reused Tag
detached Fill不得安装Tag
```

## RO transaction

```text
response payload_id/generation必须匹配
descriptor链不超过32
所有waiters最终恰好完成一次
Payload在最后一个waiter完成前不得释放
```

## MSHR / Descriptor

```text
MSHR entries <=128
descriptors <=256
同一descriptor不能属于两个chain
```

## WAD/TVD

```text
mandatory WB不能被opportunistic TVD挤死
WB_PENDING/INFLIGHT entry不可被回收
promotion后TVD metadata必须失效
```

## Unified Pool

```text
Payload roles总和 =1152
无double allocation
mandatory landing已有credit后response不能无处落地
```

## Bank

```text
每bank每cycle最多1个128B op
冲突必须仲裁，不能隐式丢请求
```

---

# 28. 主要风险与应对

| 风险 | 结果 | 对应测量/策略 |
|---|---|---|
| RO duplicate reads过多 | lower path更堵 | read amplification shadow study |
| Tag release机会少 | 机制无收益 | useful release rate |
| Descriptor pool先满 | no-MSHR无效 | 256-entry occupancy/blocking |
| Payload先满 | detached/bypass/TVD互相挤压 | role occupancy与landing credit |
| TVD reuse低 | 成本无回报 | shadow TVD |
| TVD promotion频繁 | Tag瓶颈/额外淘汰 | promotion计数与wait |
| Dirty TVD write等待长 | write/atomic性能下降 | WB-inflight hazard统计 |
| Unified bank conflict | 合并后端口退化 | bank-matched baseline |
| WAD被TVD占满 | WB无法前进 | mandatory priority/invariants |
| L1成为真正瓶颈 | L2机制被掩盖 | L1 blocker closeout |
| DRAM成为绝对瓶颈 | 增加在飞只排更长队 | 850/1GHz + queue sensitivity |
| 图形无真实trace | bypass贡献无法实证 | synthetic仅作辅助，后续补trace |

---

# 29. 面积与成本核算框架

## 29.1 Resident Tag pointer

```text
1024 tags × 11 bits
= 11264 bits
= 1408 B / slice
≈ 88 KiB over 64 slices
```

## 29.2 WAD/TVD pointer

```text
128 entries × 11 bits
= 1408 bits
= 176 B / slice
≈ 11 KiB over 64 slices
```

## 29.3 其他成本

需要参数化计算：

```text
Payload role bits:
1152 × R bits / slice

Tag generation:
1024 × G bits / slice

WAD/TVD state:
128 × S bits / slice

Descriptor next pointer:
256 × 8 bits / slice

head/tail/count:
per MSHR / per RO transaction
```

不得在没有确定 R/G/S 位宽前给出伪精确面积。

真正大成本可能来自：

```text
4-bank RAM organization
cross-role mux
bank arbitration
TVD lookup timing
```

需要综合/CACTI/RTL估算。

---

# 30. 总体阶段规划

## Phase 0：冻结本文档

产物：

```text
EP_L2_ARCHITECTURE_AND_ROADMAP.md
open-decision register
source-to-structure mapping
```

## Phase 1：目标Baseline配置

建立：

```text
B0-Legacy
B0-Banked
```

完成：

```text
64×16 L2
128 MSHR
256 descriptors
32 cap/address
target queues
64KiB L1
bank model
```

验证机制全关闭时功能正确。

## Phase 2：目标Baseline Characterization

重新跑代表 workload，不必立刻51项全跑。

至少：

```text
vectorAdd4M
scan
spmv
convolution
cfd
dwt2d
sad
sgemm
btree
3mm
gemm
FWT7/21
FWT11/19
```

回答：

```text
bottleneck是否自然前移；
Tag/MSHR/descriptor/payload/lower各自压力。
```

## Phase 3：Opportunity Instrumentation

实现 timing-neutral：

```text
RO shadow study
TVD shadow study
Payload role complementarity
kernel/epoch snapshots
```

## Phase 4：Opportunity Runs

先跑代表集合。

Gate决定：

```text
RO no-MSHR是否值得
TVD是否值得
统一池容量互补是否真实
```

## Phase 5：Tag–Payload / Banked Pool基础实现

依次：

```text
B1 decoupling only
B2 unified pool
```

先不实现RO/TVD。

## Phase 6：RO Pending机制

```text
B3 replaceable RO pending + MSHR
B4 RO no-MSHR
B4a predictor/overflow policy
```

## Phase 7：TVD

```text
serve-in-place
promotion
dirty WB state
```

## Phase 8：Graphics bypass

准备真实trace/分类，验证：

```text
bypass borrowing
resident impact
```

## Phase 9：完整评估

```text
performance
traffic
resource blocking
area
energy
bank conflicts
sensitivity
ablation
```

---

# 31. Codex分支建议

不得修改任何 frozen Round-1 branch。

Core：

```text
hrl/ep-l2-target-baseline-v0
hrl/ep-l2-opportunity-v0
hrl/ep-l2-unified-payload-v0
hrl/ep-l2-ro-pending-v0
hrl/ep-l2-tvd-v0
```

Framework：

```text
hrl/ep-l2-exp-v0
```

建议基点：

```text
Instrumentation v1.1 frozen Core:
32f9b8d52490044f487c14811121ed0368e48a48

Instrumentation v1.1 Framework:
d24455a1981d7f099f641b5b6f17adb08d973a4a
```

每阶段从上一个已closeout阶段创建新分支，不在同一分支混入全部机制。

---

# 32. Codex提交拆分建议

## Target Baseline

```text
C1 config: define EP-L2 target hierarchy
C2 l1: configure 64KiB target L1
C3 l2: configure 64×16 tags and 128-MSHR/256-descriptor model
C4 mem: configure target lower queues and DRAM headroom variants
C5 data: add bank-matched static payload model
C6 test: target-baseline directed regressions
C7 docs: target-baseline closeout
```

## Opportunity Study

```text
O1 stats: add kernel/epoch snapshots
O2 stats: add oracle read-only coverage
O3 stats: add RO overlap/detach shadow model
O4 stats: add TVD shadow model
O5 stats: add payload role/complementarity statistics
O6 tools: analysis-ready parser
O7 test: opportunity instrumentation regressions
O8 docs: opportunity closeout
```

---

# 33. 立即下一步

正式功能实现前，建议按以下顺序：

```text
1. 完成当前Round-2 diagnostic；
2. 冻结目标baseline未决参数；
3. 建立B0-Legacy与B0-Banked；
4. 验证L1不是非容量型瓶颈；
5. 跑目标baseline代表workload；
6. 实现RO opportunity shadow；
7. 实现TVD opportunity shadow；
8. 根据Gate决定功能实现范围。
```

不要直接开始完整 EP-L2。

---

# 34. 当前仍未冻结的开放决策

以下项目本文不自行杜撰。

## 34.1 Memory primary

```text
850 MHz
或
1 GHz
```

需要真实目标依据和headroom实验。

## 34.2 L1内部资源

```text
L1 MSHR
L1 MissQ
L1 bank port
write/allocation policy
```

## 34.3 L2边界队列

```text
ICNT→L2
L2→ICNT
NoC credits
lower read credits
```

## 34.4 MissQ与descriptor是否物理同池

本文当前按：

```text
256-entry MissQ = 256 shared request/target descriptors
```

理解。

若真实实现是两套结构，需要用户确认并改文档。

## 34.5 RO victim policy

```text
Aggressive
waiter_count==1
history predictor
```

尚未选择。

## 34.6 Unified Pool reserves

```text
Fill reserve
bypass reserve
WB reserve
resident low watermark
```

需要opportunity数据定量。

## 34.7 TVD lookup timing

```text
与Tag串行
与Tag并行
tag miss后第二拍
```

尚未冻结。

## 34.8 TVD replacement policy

```text
LRU
FIFO
age
reuse-based
```

尚未冻结。

## 34.9 Graphics bypass标记

```text
trace/request如何标出bypass
```

尚未明确。

---

# 35. 研究叙事建议

当前最一致的论文逻辑是：

## Problem 1：Static Payload Partitioning

```text
resident data容量
与
bypass landing容量
静态分池
```

不同 workload 下，一类空闲时另一类可能受限。

## Problem 2：Transient Metadata Coupling

```text
RO pending transaction
长期占 resident tag/MSHR
```

即使它没有 resident reuse价值。

## Problem 3：Premature Payload Disposal

```text
逻辑淘汰后数据仍在片上
但传统结构立即丢弃
```

## Insight

```text
Tag visibility、transaction state和128B Payload
具有不同生命周期，
不应静态一一绑定。
```

## Solution

```text
Decoupled Tag–Payload
+
Unified banked Payload Pool
+
Replaceable certified-RO pending tags
+
WAD-backed TVD
```

---

# 36. 冻结结论

当前可以冻结的核心方案是：

```text
64-slice EP-L2

每slice：
64×16 Resident Tag
1152-entry unified 128B Payload
4×288 banks, 1 line-op/bank/cycle

128 MSHR line entries
256 persistent request descriptors
32 requesters/address

128-entry line-address WAD/TVD

Certified RO:
attached时通过Tag/Payload链表merge
detached后允许duplicate lower read
detached Fill只服务waiters并释放Payload

TVD:
read serve-in-place
clean write/atomic promote
dirty inflight read forward
dirty inflight write/atomic等待WB response
```

但是否把：

```text
RO no-MSHR
TVD
graphics bypass borrowing
```

全部作为最终论文核心，必须由 opportunity study 决定。

本阶段最重要的原则是：

> **先用目标 baseline 和 shadow opportunity 定量确认机会，再实现完整机制；不得为了保留原先故事而忽略 Round-1 与目标配置数据。**
