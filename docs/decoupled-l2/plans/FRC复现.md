问题：
目前第 1、2 阶段已完成。
第 3 阶段：FRC Baseline  要怎么做需要细化；另外这个baseline应该实现在哪个branch上


回答：可以。现在第 1、2 阶段已经完成后，第 3 阶段的目标应该非常明确：**不是“随便实现一个类似 FRC 的 Fill Buffer”，而是实现一个足够忠实于原论文、又适配我们 QV100/Accel-Sim 基线的 FRC reference design，作为后续 LateBind-L2 最重要的强 Baseline。**

先给结论：**FRC 机制应实现在 `swayhrl/gpgpu-sim` 的独立分支 `hrl/l2-frc-baseline-v1` 上；这个分支必须从第 1 阶段 Characterization 完成后的“stats-only、cycle-identical baseline commit”切出，而不是从第 2 阶段 Oracle 分支，也不要从原来的 `hrl/decoupled-l2-v0` 切。**

推荐的分支关系是：

```text
                     clean GPGPU-Sim baseline
                              │
                              ▼
                  Characterization stats-only
                  （功能/周期完全不变）
                              │
                 tag: l2-char-v1-done
                              │
         ┌────────────────────┼─────────────────────┐
         │                    │                     │
         ▼                    ▼                     ▼
hrl/l2-oracle-v1     hrl/l2-frc-baseline-v1   hrl/l2-latebind-v1
  已完成第2阶段             第3阶段                  第4阶段
```

这样最后论文里的：

```text
Baseline
FRC
LateBind
Oracle
```

全部拥有**同一个公共祖先和同一套 Characterization 统计代码**，不会出现“FRC 是从 Oracle 改出来的”“LateBind 又是从旧 Decoupled 后端改出来的”这种实验不可比问题。

------

# 一、先明确：我们到底要复现 FRC 的什么

你刚给的原文把 FRC 的机制写得很清楚。

它的核心不是扩大 L2，也不是替代 MSHR，而是：

> **每个 L2 bank 增加一个小型 Fetch and Replacement Cache；L2 miss 时如果 FRC 有空闲项，不立即处理 L2 victim，而是先把 incoming block 的 fetch 发往内存。等数据回来以后，再将 FRC 中的新块与 L2 victim 交换，之后从 FRC 中处理旧 victim 的 eviction。**

论文明确说 FRC 的两个直接目的就是：

1. L2 miss 一出现就启动 Main Memory Fetch，提高 MLP；
2. 把 invalidation/eviction 推迟到 fetch 完成以后，使 victim 在此期间继续留在 L2。

而且它特别规定：

- **一个 FRC 对应一个 L2 Bank**；
- FRC 本身也是 Set-Associative Cache；
- 每次 L2 Access 同时查 L2 和对应 FRC；
- 若请求命中一个仍在 Fetching 的 FRC Block，则请求等待并与该 Fetch 合并；
- 如果目标 FRC Set 没有 Free Entry，则**退化成传统 L2 Miss 流程，而不是因为 FRC 满直接阻塞**。

这几条是我们的 FRC Baseline 必须复现的“协议契约”。

------

# 二、FRC 最重要的行为：Victim 在 DRAM Fetch 期间仍然有效

这是实现时最容易做错的地方。

论文图 2 的核心区别其实不是“多一个 Buffer”，而是下面这个时序。

传统：

```text
Req B misses
     │
     ▼
选择 victim A
     │
     ▼
A → transient / invalidating / evicting
     │
     │ 很长时间
     ▼
fetch B
     │
     ▼
B进入L2
```

从 B Miss 开始，A 就不能作为普通 L2 Resident Block 使用。

因此后续访问：

```text
A
```

原本可能命中，却已经命不中了。

论文 Figure 2 明确指出，传统方式中 victim line 在 Replacement 开始时进入 Transient State，导致后来指向相同资源的替换被串行；而且由于真正最长的阶段是 Main-Memory Fetch，victim 被过早失效还降低了 L2 Hit Ratio。

FRC 则：

```text
Req B misses
     │
     ▼
FRC0 ← B的fetch事务
     │
     ├────────────→ DRAM fetch B
     │
     │
L2中的A仍然VALID
     │
     │
     ▼
B返回
     │
     ▼
swap:
L2 victim slot ← B
FRC0           ← A
     │
     ▼
从FRC0 Evict A
     │
     ▼
FRC0 free
```

论文强调，正是 Swap 保证了 L2 victim line 在 Fetch 阶段**不进入 Transient State**。

因此我们的 FRC 实现有一个绝对不能违反的不变量：

> **使用 FRC 路径的 Miss，在 Fill 返回之前绝不能调用 Baseline 的正常 `tag_array::access()` 去 Allocate/Reserve L2 Victim。**

否则只是：

```text
传统L2 +
一个额外Fill Buffer
```

而不是 FRC。

------

# 三、我们的 FRC 不应该照搬论文的容量配置，而应做“机制等价复现”

原论文平台是 AMD Southern Islands：

- 64-thread wavefront；
- 64B cache block；
- multi-banked L2；
- HD7770；
- 两个 16-way、128KB 的 L2 Bank。

我们现在的 QV100 Accel-Sim 配置却是：

```text
128B Cacheline
4 × 32B Sector
32 sets
24 ways
Sector Cache
192 MSHR
4 merges/MSHR
```

而且每个 `memory_sub_partition` 实际拥有一个自己的 `l2_cache` 实例。现有 QV100 配置也是每个 Subpartition 的 L2 为 32 Set × 24 Way × 128B。

所以不应该为了“复现论文”把我们的整个 QV100 改成：

```text
64B line
16-way
128KB
AMD Southern Islands
```

否则 FRC 与 LateBind 就不在同一个架构上了。

正式论文中需要的是：

> **FRC mechanism ported to the same QV100 baseline used by all evaluated designs.**

也就是：

```text
Baseline QV100 L2
+ 原论文FRC的miss/replacement机制
```

这样才是公平 Baseline。

------

# 四、FRC 在我们的架构中放在哪里

论文：

```text
每个 L2 Bank
    │
    └── 一个 FRC
```

我们：

```text
Memory Channel
   ├── memory_sub_partition 0
   │       └── L2 slice
   │             └── FRC
   │
   └── memory_sub_partition 1
           └── L2 slice
                 └── FRC
```

因此：

> **每个 `memory_sub_partition` 的 `l2_cache` 拥有一个独立 FRC。**

不要：

```text
整个GPU共享一个FRC
```

也不要：

```text
每个SM一个FRC
```

------

# 五、我建议的具体代码结构

不要再造一个像当前 `decoupled_l2_cache` 那样完全独立的 L2 Backend。

FRC 是一个 **Conventional L2 Miss Handling Enhancement**，最重要的是：

> Baseline 的 MSHR、Sector、Write Policy、Atomic、Data Port、Queue 等语义全部保持不变，只改变发生 Miss 后“何时分配 L2 victim”和“在哪里等待 Fill”的行为。

因此推荐：

```text
src/gpgpu-sim/
    gpu-cache.h
    gpu-cache.cc

    frc-cache.h       ← 新增
    frc-cache.cc      ← 新增
```

其中：

```cpp
class frc_cache
```

只负责：

```text
FRC Set/Way
FRC Tag
FRC State
FRC Sector masks
FRC Replacement
Incoming Fill → Victim swap
FRC eviction
```

而：

```cpp
class l2_cache
```

仍然负责：

```text
正常L2 lookup
MSHR
Write policy
Atomic
Sector semantics
Data port
Miss queue
Response
```

这会比建立：

```text
frc_l2_backend
```

干净得多。

------

# 六、FRC Entry 应该存什么

论文有一个容易产生误解的地方。

摘要说 FRC 在 Fetch 期间保存 incoming block 的 control/coherence information；但是具体流程明确要求：

> fetched block 被写入 FRC entry，然后与 L2 victim line swap。

因此它最终**必须有完整的数据 Payload 容量**，不是只有 Tag。

我们的抽象结构建议：

```cpp
enum frc_state {
    FRC_FREE,
    FRC_FETCHING,
    FRC_FETCHED,
    FRC_EVICTING
};

struct frc_entry {
    frc_state state;

    new_addr_type block_addr;

    mem_access_sector_mask_t pending_mask;
    mem_access_sector_mask_t valid_mask;
    mem_access_sector_mask_t dirty_mask;
    mem_access_byte_mask_t dirty_byte_mask;

    unsigned long long alloc_time;
    unsigned long long fetch_done_time;

    // after swap:
    new_addr_type victim_addr;
};
```

逻辑含义：

### `FRC_FETCHING`

```text
Tag = incoming B
Data = 尚未/部分返回
```

允许：

```text
新请求B → FRC hit → merge
```

### `FRC_FETCHED`

```text
Tag = incoming B
Data = 已返回
尚未来得及完成swap
```

此时可以直接响应 B。

### `FRC_EVICTING`

Swap 后：

```text
L2里已经是B

FRC Entry:
Tag/Data = victim A
```

此时它不应该被当成普通 Victim Cache 使用。

这点非常重要，否则你实现出来的是：

> FRC + Victim Cache

性能会被高估。

------

# 七、FRC Lookup 怎么处理

每个 L2 Request：

```text
                Request
                   │
          ┌────────┴─────────┐
          ▼                  ▼
      L2 lookup           FRC lookup
          │                  │
          └────────┬─────────┘
                   ▼
                 classify
```

优先级建议：

```text
1. L2 HIT
2. FRC HIT_FETCHING / HIT_FETCHED
3. MSHR HIT
4. true L2+FRC MISS
```

实际上 FRC 与 MSHR Hit 的关系需要更精确：

```text
同一 Sector 已经有 lower read：
    → MSHR merge
    → FRC只提供该line的physical/transient location

同一 Line、不同 Sector：
    → 可以共享FRC line entry
    → 但各Sector仍保持Baseline MSHR语义
```

也就是说：

> **FRC 不替代 MSHR。**

原论文从来没有声称 FRC 去掉 MSHR。

这也是它与我们未来 TD/Physical Pool 工作的重要区别。

------

# 八、最关键的 Miss 流程

我建议第一版严格按下面的状态机实现。

## Case A：普通 L2 Hit

完全 Baseline：

```text
L2 HIT
 ↓
read data
 ↓
response
```

FRC 不介入。

------

## Case B：L2 Miss，但已有同地址 FRC_FETCHING

例如：

```text
Req0 → B miss → FRC0 FETCHING B

随后：

Req1 → B
```

应该：

```text
L2 miss
FRC hit B(FETCHING)
        │
        ▼
MSHR merge
        │
        ▼
不发送第二个DRAM read
```

论文明确规定，对正在 Fetch 的 FRC Block 的 Hit 要等待该 Fetch 完成。

必须有 Assertion：

```text
同一个{address,sector}
最多一个lower read
```

------

# 九、Case C：True Miss + FRC 有空闲 Entry

这是核心路径。

```text
L2 MISS
FRC MISS
   │
   ▼
检查Baseline MSHR
   │
   ├── MSHR不够 → Baseline reservation fail
   │
   ▼
FRC目标set有free entry?
   │
   ▼ YES
allocate FRC entry
state = FETCHING
   │
   ▼
allocate MSHR
   │
   ▼
立即把Read送入miss queue
   │
   ▼
DRAM
```

最关键的是：

```text
这里不碰 L2 victim
```

不做：

```cpp
m_tag_array->access(...)
```

不把任何 L2 Way 置为：

```text
RESERVED
```

不产生 Writeback。

这就是 Early Fetch。

论文 Figure 3 的 Yes Path 就是：

```text
Allocate free FRC
→ Fetch target block into FRC
→ Swap FRC and victim
→ Evict victim from FRC
→ Free FRC
```



------

# 十、Case D：True Miss + FRC Set Full

论文这一点必须严格复现：

> 如果目标 FRC Set 没有 Free Entry，FRC 方案就按照 conventional approach 工作。

所以不能：

```text
FRC Full
 ↓
RESERVATION_FAIL
```

而应该：

```text
FRC target set full
        │
        ▼
fallback to original l2_cache miss path
        │
        ▼
选择L2 victim
RESERVED
必要时writeback
发lower read
```

这个行为必须单独有统计：

```text
frc_set_full_fallback
```

否则无法解释 FRC Associativity 的敏感性。

论文实际上也发现 MatrixTranspose 会因为大量请求落到同一个 FRC Set，8-way FRC 仍然发生 Set Pressure。

------

# 十一、Fill 返回后怎么做，是实现第二关键点

假设：

```text
FRC0 = FETCHING B
L2 victim candidate仍然可能是A
```

当 B 从 DRAM 返回：

```text
B arrives
   │
   ▼
FRC0.valid_sector |= returned_sector
   │
   ▼
原始请求可以ready
```

然后才：

```text
重新访问目标L2 set
   │
   ▼
此时选择victim
```

注意是：

> **Fill 时才选 Victim。**

绝不能保存 Miss 时的 Victim ID。

否则 FRC 延长 Victim Lifetime 的一半意义就丢了。

------

# 十二、Fill 时 Victim 是 Clean

最简单：

```text
FRC0:
B FETCHED

L2:
A CLEAN
```

执行：

```text
FRC0.B  ↔  L2.A
```

结果：

```text
L2:
B VALID

FRC0:
A CLEAN
```

Clean A 无需写回：

```text
FRC0 → FREE
```

论文所谓 `Evict FRC entry` 对 clean victim 可以视作直接丢弃。

------

# 十三、Fill 时 Victim 是 Dirty

这是我们后续 LateBind 最关心的路径。

Swap 后：

```text
L2:
B VALID

FRC0:
A DIRTY / EVICTING
```

然后：

```text
FRC0(A)
   │
   ▼
generate L2_WRBK_ACC
   │
   ▼
L2 → DRAM queue
   │
   ▼
下层接受
   │
   ▼
FRC0 FREE
```

注意：

> FRC Entry 必须一直占用到 Dirty Victim 的 Payload 已经安全交给下层。

否则会丢数据。

这一步也正好为以后比较：

```text
FRC:
新Fill和旧Victim都必须在额外FRC Data Entry中搬动/交换

LateBind:
原Resident Dirty Entry可以直接变成WB_PENDING
```

提供非常清晰的对比。

------

# 十四、一个需要比论文额外处理的问题：Fill 返回时暂时没有可替换 Way

比如：

```text
FRC中B已经返回

但目标L2 Set：
way0 RESERVED
way1 RESERVED
...
way23 RESERVED
```

此时不能丢 B。

所以需要：

```text
FRC_FETCHED
```

状态。

行为：

```text
FRC中保留B
请求B的数据已经可以返回上层
但B暂时还没有swap进L2
```

以后每个 Cycle 重试：

```text
target L2 set
```

一旦出现可替换 Way：

```text
swap
```

这实际上是非常自然的 FRC 实现。

同时：

```text
后续请求B
```

可以直接命中：

```text
FRC_FETCHED
```

并使用数据。

这也符合论文“L2 lookup 同时搜索 L2 和 FRC”的描述。

------

# 十五、Sector Cache 怎么适配

这是我们的实现比原论文复杂的地方。

原论文：

```text
64B block
```

是 Block 粒度。

我们的 QV100：

```text
128B line
├── sector 0 = 32B
├── sector 1 = 32B
├── sector 2 = 32B
└── sector 3 = 32B
```

而当前 GPGPU-Sim 本身就是 Sector Cache，并且会跟踪每个 Sector 的：

- INVALID；
- RESERVED；
- VALID；
- MODIFIED；
- Dirty Byte Mask。

因此建议：

> **FRC Entry 仍然按 128B Physical Line 计算容量，但内部保存 4-bit Sector State/Valid/Pending Mask。**

例如：

```text
FRC Entry tag = B

pending = 0101
valid   = 0010
```

而不是把 FRC 做成：

```text
4个独立32B FRC Entry
```

否则面积和论文的“额外 Cache Line”定义就变了。

第一版可以：

```text
一个Line第一次Sector返回
→ 完成line-level swap
→ 其余pending Sector后续直接Fill到已经安装好的L2 Line
```

这样与现有 Sector Cache 更容易结合。

------

# 十六、MSHR 应该完全保留

这是 FRC Baseline 公平性的一个关键点。

当前 Baseline MSHR 是有限的全相联结构，并限制：

```text
number of entries
max merged requests
```

所以：

```text
FRC free
```

并不意味着：

```text
MSHR可以无限
```

正确顺序是：

```text
Request
  │
  ▼
L2/FRC lookup
  │
  ▼
MSHR probe
  │
  ├── MSHR hit → merge
  │
  ├── MSHR full → reservation fail
  │
  └── new MSHR
          │
          ▼
       FRC path
```

这点对后续 LateBind 特别重要，因为我们的 Transaction Directory 可能会真正改变传统 MSHR 组织。

所以 FRC 必须保持：

> **MSHR 和 Baseline 一样。**

否则后面：

```text
LateBind vs FRC
```

无法知道收益来自 FRC 还是来自更大的 Miss Tracking Capacity。

------

# 十七、Write 应该怎么处理

建议分两步。

### FRC-v1

只优化：

```text
需要真正Lower Read Fetch的Miss
```

例如：

```text
Read Miss
Atomic Read phase
Partial Write需要Fetch旧数据
```

如果 Write 已经覆盖整个 Sector/Line，不需要 Lower Read：

```text
Full Write Miss
```

继续走 Baseline，因为：

> FRC 的核心收益来自把长延迟 Fetch 从 Victim Eviction 的后面移到前面。

没有 Fetch，自然没有多少东西可以提前。

### FRC-v2

正式论文版本再完整支持：

- partial write；
- lazy-fetch-on-read；
- fetch-on-write；
- same-line RAW/WAR/WAW。

不要直接把当前抽象 `decoupled_l2_cache` 中“Write Miss 直接安装 Dirty Line”的做法搬过来；当前 Baseline 对部分写已经有 Byte Mask、Readable-on-fill 和 Read-after-Write Pending 语义。

------

# 十八、Atomic 应该如何处理

正式 FRC Baseline 最终要保持 Baseline Atomic 语义。

Baseline 在 Atomic Fill 返回后会：

```text
mark MSHR ready
mark corresponding line MODIFIED
set dirty byte mask
```

因此：

```text
Atomic miss
→ 可以Early Fetch进入FRC
→ Fill
→ swap/install
→ Atomic执行
→ L2 line = MODIFIED
```

第一轮 bring-up 可以临时：

```text
atomic → conventional baseline path
```

先确保普通 Read FRC 完全正确。

但最终跑论文结果之前不能一直这么做，因为那会让 FRC 在 Atomic-heavy Workload 上被人为削弱。

------

# 十九、FRC Timing 怎么建模

原论文在这一点上比较理想化。

他们明确说：

> 为比较不同配置，保守地假定所有分析过的 L2 配置具有相同 Access Time。

也就是说论文没有认真惩罚：

- FRC 额外 Tag Lookup；
- Swap；
- FRC Data SRAM；
- Crossbar。

我们最好提供两个模式。

### Paper-faithful FRC

用于和原论文机制对应：

```text
FRC lookup 与 L2 lookup 并行
额外lookup latency = 0
swap latency = 0或1 cycle
```

### Conservative FRC

最终论文主结果：

```text
FRC lookup +0/+1 cycle sensitivity
swap占用内部Data Port
dirty victim需要真实WB带宽
```

这样以后审稿人问：

> “是不是你故意把 FRC 模拟得太慢？”

可以回答：

```text
No.
We reproduce the paper-style timing first,
and additionally evaluate a more conservative implementation.
```

------

# 二十、FRC 必须增加哪些统计

这里直接对齐原论文。

论文的三类核心分析指标是：

- OPC；
- L2 MPKO；
- L2 Miss Delaying Latency；
- Percentage of Misses Served by FRC。

我们不必照抄 OPC，但至少要有：

```text
frc_access
frc_hit_fetching
frc_hit_fetched

frc_alloc
frc_set_full_fallback

frc_fetch_complete
frc_swap

frc_clean_victim
frc_dirty_victim

frc_evict_stall
frc_ready_wait_swap

frc_occupancy_avg
frc_occupancy_max

frc_misses_served
frc_misses_served_ratio

frc_fetch_lifetime

frc_victim_lifetime_extension

frc_pre_memory_delay
frc_post_memory_delay

l2_mpko
average_outstanding_lower_reads
```

其中我特别建议把论文所谓：

> L2 miss delaying latency excluding actual main memory access

拆成两个更清楚的指标：

# [ T_{\text{pre}}

## T_{\text{DRAM issue}}

T_{\text{L2 miss}}
]

以及：

# [ T_{\text{post}}

## T_{\text{upper ready}}

T_{\text{DRAM return}}
]

于是：

# [ T_{\text{management}}

T_{\text{pre}}+T_{\text{post}}
]

FRC 的理论作用正是：

```text
Tpre ↓↓↓
```

因为 Victim Eviction 被移出 Fetch Critical Path。

这会比原论文 Figure 6 更容易解释。

------

# 二十一、配置怎么设计

建议不要给 FRC 增加太多不必要参数。

最小集合：

```text
-gpgpu_l2_frc_enable
-gpgpu_l2_frc_entries
-gpgpu_l2_frc_assoc
-gpgpu_l2_frc_lookup_latency
-gpgpu_l2_frc_swap_latency
```

默认：

```text
enable = 0
```

这样：

```text
enable = 0
```

必须保证和 Characterization Baseline：

```text
cycle-exact
traffic-exact
hit/miss-exact
```

------

# 二十二、容量 sweep 直接跟论文对齐

论文测试：

```text
4
8
16
32
64
128
256
512
```

FRC Entries，而且除了 4-entry 外，其余都是 8-way。

我们完全可以做同样的 Sweep：

```text
frc_4e
frc_8e
frc_16e
frc_32e
frc_64e
frc_128e
frc_256e
frc_512e
```

其中：

```text
4e  → 4-way × 1 set
8e  → 8-way × 1 set
16e → 8-way × 2 sets
32e → 8-way × 4 sets
...
```

论文发现多数 workload 在约 32～64 Entries 已接近最佳性能，而且 FRC 相比直接把 L2 增大到 256KB/512KB 更有效。

所以我们的正式主配置可先候选：

```text
32e
64e
```

但最终应由 QV100 Characterization 和 Sweep 决定，而不是照搬论文。

------

# 二十三、必须做一个 Figure 2 的定向复现测试

这是 FRC 实现是否正确的最好测试。

写一个微型 Cache-level Test：

初始：

```text
L2 target set:
A resident
```

然后：

```text
cycle 0:
Req B

cycle 90:
Req C

cycle 240:
Req D
```

并强制：

```text
B/C/D → 同一目标L2 set / victim pressure
```

Baseline 应看到：

```text
B replacement
→ target line transient
→ C waiting
→ D waiting
```

FRC 应看到：

```text
B → FRC0 fetch

C arrives:
FRC1 free
→ C fetch并行开始

B returns
→ swap
→ FRC0 recycle

D arrives
→ FRC0 fetch
```

这正是论文 Figure 2 的行为。

不需要周期数完全等于原论文，因为：

```text
Multi2Sim HD7770 ≠ Accel-Sim QV100
```

但是**事件依赖关系必须相同**。

------

# 二十四、第 3 阶段的验证矩阵

我建议最终做到下面这一套：

| Test                        | 必须看到                                                     |
| --------------------------- | ------------------------------------------------------------ |
| FRC disabled                | Cycle/traffic/cache stats 与 Characterization Baseline 完全一致 |
| Single read miss            | FRC alloc → early fetch → fill → swap → free                 |
| Victim reuse before fill    | Fill 返回前对 victim 地址仍然 L2 Hit                         |
| Secondary same-address miss | FRC/ MSHR merge，只发一个 lower read                         |
| FRC set full                | 自动 fallback conventional path                              |
| Clean victim                | swap 后 FRC 立即释放                                         |
| Dirty victim                | swap 后 FRC 保留直到 WB 可安全交给下层                       |
| Lower queue full            | FRC 不丢请求、不死锁                                         |
| Fill burst                  | 多个 FRC Entry 支持并行 lower reads                          |
| Sector miss                 | Sector masks 保持正确                                        |
| Multi-sector same line      | 同一 FRC line 正确聚合                                       |
| Partial write               | 与 Baseline Byte/Readable 语义一致                           |
| Atomic                      | Functional result、Dirty State、WB 与 Baseline 一致          |
| Flush/invalidate            | 最终 FRC/ MSHR/queue 全部排空                                |
| 4-entry/8-entry boundary    | 不越界、不死锁                                               |
| 32/64-entry performance     | FRC served ratio、MLP、miss delay 有合理变化                 |

------

# 二十五、建议按 6 个 Commit 实现，不要一次改完

这是我建议的开发顺序：

```text
FRC-R0
config + empty FRC structure
enable=0 cycle exact

FRC-R1
FRC lookup / set / way / free-list
无行为改变

FRC-R2
Read miss early-fetch
MSHR保持Baseline
FRC FETCHING merge

FRC-R3
Fill-time victim selection
swap
clean victim recycle

FRC-R4
dirty victim eviction
WB progress
deadlock assertions

FRC-R5
sector semantics
partial write
atomic

FRC-R6
timing + stats + capacity sweep
paper Figure-2 directed test
```

每个 Round 都做：

```text
baseline preservation
directed
small regression
postcheck
```

这样一旦性能异常，很容易定位是哪一步导致的。

------

# 二十六、branch 到底怎么放：最终推荐

## GPGPU-Sim

FRC 机制代码放：

```text
swayhrl/gpgpu-sim

branch:
hrl/l2-frc-baseline-v1
```

**起点必须是：**

```text
第1阶段 Characterization 完成后的最后一个
“只加统计、不改行为”的 commit
```

不是：

```text
hrl/decoupled-l2-v0
```

因为当前这个分支的自定义后端已经：

- 用全局 `m_lines` 抽象 Resident；
- 没有真实 Set/Way；
- 没有真实 Data Array；
- 简化 Write；
- 简化 Atomic；

不能拿它做 FRC。

也不是：

```text
hrl/l2-oracle-v1
```

因为 Oracle 已经故意引入理想化行为。

------

## Accel-Sim Framework

运行脚本、配置 Overlay、结果收集继续放在**整个 LateBind 项目的共同 Experiment Branch**：

```text
hrl/l2-latebind-exp-v1
```

不建议再长期维护一个：

```text
hrl/l2-frc-exp-v1
```

除非开发期间临时切分。

最终 Framework 应该能统一跑：

```text
baseline
frc-4
frc-8
frc-16
frc-32
frc-64
oracle-...
latebind-...
```

这样实验脚本、Trace 和统计解析完全共享。

------

# 二十七、最关键的一点：FRC 实现出来以后，不要立刻拿 Speedup 判断成功

FRC-R6 完成后的第一件事不是：

```text
看性能提升多少
```

而是验证三条机制曲线：

### 1. FRC Entry 增加 → FRC-served Miss 比例应该上升

原论文 Figure 7 就是这个趋势；64 Entries 在很多应用上已经能承担约 75% 的 Miss。

### 2. FRC Entry 增加 → L2 Miss Management Delay 应总体下降

这是 Figure 6 的核心结果。

### 3. Victim lifetime 应明显增加

而且要能实际看到：

```text
原来Baseline中在Miss时就RESERVED/被替换的A

FRC中直到B真正回来才被替换
```

只有这三条都成立，才能确认：

> “我们实现的是 FRC。”

如果只是：

```text
IPC提高了
```

但 Victim Lifetime、Early Fetch 和 Set-full Fallback 不对，那么很可能只是实现了一个不同的 Buffer。

------

# 最后把第 3 阶段压缩成一句执行方案

> **从 Characterization 完成后的 cycle-identical GPGPU-Sim Baseline 切出 `hrl/l2-frc-baseline-v1`；保持原 L2 的 Set/Way、Sector、MSHR、Write、Atomic 和 Queue 语义不变，每个 L2 Subpartition 增加一个 Set-associative FRC。FRC 仅改变 Miss 生命周期：有空闲 FRC Entry 时先 Early Fetch、不提前占用 L2 Victim；Fill 返回后才重新选择 Victim 并 Swap，旧 Victim 在 FRC 中完成 Writeback；FRC Set Full 时无条件回退 Baseline conventional path。先做 Read/clean victim，再做 dirty WB、Sector、Write/Atomic，最后用 Figure 2 定向测试、4–512 Entry Sweep、FRC-served ratio、victim lifetime 和 miss-management latency 验证实现。**

这会给第 4 阶段 LateBind 一个非常干净的对照关系：

```text
Conventional:
Resident storage固定 + early victim reservation

FRC:
Resident storage固定 + 专用transient data storage
+ delayed victim replacement

LateBind:
Resident / transient不再固定分区
+ transaction-payload decoupling
+ late physical binding
+ in-place dirty retirement
```

这个三层递进关系本身就已经开始形成论文中非常有说服力的设计演进图。