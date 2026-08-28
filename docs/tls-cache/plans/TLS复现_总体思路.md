## 结论

这项工作**可以基于 Accel-Sim 复现**，而且论文作者本身就是在 Accel-Sim 上完成实验的：他们扩展了 Accel-Sim，使其支持多芯片 GPU，并在此基础上实现 TLS-Cache。

但需要把“复现”分成三个层次：

| 复现目标                                      | 可行性             | 判断                                              |
| --------------------------------------------- | ------------------ | ------------------------------------------------- |
| 复现 TLS-Cache 的结构、访问流程和主要性能趋势 | 高                 | 架构描述已经足够实现                              |
| 复现 Fig. 8、Fig. 10、Fig. 11 的近似数值      | 中高               | 需要补齐网络、映射、benchmark 输入等参数          |
| 精确得到论文的 30.2%、77.2% 等全部数值        | 中低               | 缺少作者代码、精确 commit、trace 和若干微结构细节 |
| 复现 3.48 mm²、2.75 W 的硬件开销              | 不能只靠 Accel-Sim | 还要 RTL／综合或独立 NoC 功耗面积模型             |

论文的正式题目是 **“Exploiting intra-chip locality for multi-chip GPUs via two-level shared L1 cache”**。

------

# 一、这项工作究竟做了什么

## 1. 它解决的问题

在多芯片 GPU 中，每个芯片都有自己的 L2/LLC 和 DRAM。某个 SM 访问本芯片 DRAM 时是 local access，访问其他芯片 DRAM 时则是 remote access。

传统结构下：

```text
SM
 └─ Private L1
      └─ L1 miss
           └─ LLC / DRAM
```

当地址位于其他芯片时，L1 miss 必须跨芯片访问远端 LLC 或 DRAM，因此同时受到：

- 跨芯片额外延迟；
- inter-chip link 带宽竞争；
- 远端 LLC、内存控制器和链路排队；

的影响。论文认为这是 multi-chip GPU 的主要性能瓶颈之一。

此前一种典型方案是增加一个 **remote data cache，也叫 L1.5**：

```text
Private L1
   └─ remote miss
        └─ Remote Data Cache
             └─ remote LLC / DRAM
```

它能够缓存“从其他芯片取回的数据”，但有两个问题：

1. 要增加缓存容量，或者从 L2 中切一部分容量出来；
2. 所有 remote L1 miss 都要先经过 L1.5，即使数据实际上可以在附近 SM 的 L1 中获得。

TLS-Cache 的核心思路就是：

> 不再单独增加 L1.5，而是重新组织原来每个 SM 已经拥有的 L1，把它们分成两个层级。

------

# 二、TLS-Cache 的结构

## 1. 两类 L1

TLS-Cache 把每个芯片中的 SM 按组划分成若干 cluster。默认配置为：

```text
4 个 SM / cluster
```

每个 cluster 中原来有四个物理 L1，TLS-Cache 将其静态配置成：

```text
3 个 CL1：Cluster-shared L1
1 个 RL1：Remote-shared L1
```

论文第 3 页图 3 给出了完整结构：

```text
              chip 内所有 cluster
                     │
             Inter-cluster Xbar
                     │
        ┌────────────┼────────────┐
        │            │            │
  Intra-cluster  Intra-cluster  Intra-cluster
       Xbar           Xbar           Xbar
        │
   ┌────┼────┬────┐
   SM0  SM1  SM2  SM3
   CL1  CL1  CL1  RL1
```

这里需要特别注意：

- **CL1 是 cluster 内共享的第一级 L1；**
- **RL1 是整个芯片共享的远端数据缓存；**
- 它们都使用原有 SM 的物理 L1 容量；
- TLS 的两级交叉开关与原来 SM 到 L2 的 64×16 NoC 是两套不同网络。

论文明确说明，CL1 捕获 intra-cluster locality，RL1 捕获 inter-cluster locality，并且不需要增加额外 cache capacity。

------

## 2. CL1：cluster 内按地址分布

同一个 cluster 中的三个 CL1 并不是三个互相重复的 cache。

它们采用地址归属方式：

```text
某些地址 → CL1-0
某些地址 → CL1-1
其余地址 → CL1-2
```

三个 CL1 合起来覆盖整个地址空间。这样，同一个 cluster 中任意 SM 对同一个 cache line 的请求都会被路由到同一个 CL1，不会在四个 SM 的私有 L1 中保存四份重复数据。

例如：

```text
Cluster 0:
  SM0 请求 A ─┐
  SM1 请求 A ─┼──→ 同一个 home CL1
  SM3 请求 A ─┘
```

它同时带来两点效果：

- 利用跨 SM 的共享；
- 去除 cluster 内重复副本，弥补“拿出一个物理 L1 作为 RL1”造成的 CL1 容量减少。

论文第 4 页图 4 展示了 CL1 和 RL1 的地址空间划分。CL1 只在本 cluster 内共享，而同一个地址在不同 cluster 的 CL1 中仍然可能有多个副本。

------

## 3. RL1：全芯片分布式远端缓存

每个 cluster 中还有一个 RL1。

默认每芯片 64 个 SM、每 cluster 4 个 SM，因此：

```text
64 / 4 = 16 个 cluster
→ 每芯片 16 个 RL1
```

这 16 个 RL1 分别负责不同的 remote address segment：

```text
remote address segment 0 → cluster 0 的 RL1
remote address segment 1 → cluster 1 的 RL1
...
remote address segment 15 → cluster 15 的 RL1
```

所有 RL1 合起来覆盖整个 remote memory address space，并允许本芯片全部 SM 访问。

所以 RL1 不是一个集中式 2 MB cache，而是：

```text
16 个 128 KB 的分布式 cache slice
```

通过两级交叉开关访问。

------

## 4. 按论文参数推算的容量分配

论文默认每个 SM 有 128 KB L1，每芯片 64 个 SM。

因此每芯片原始 L1 总容量为：

```text
64 × 128 KB = 8 MB
```

TLS-Cache 默认 3:1 分配后：

```text
CL1 总容量：
48 × 128 KB = 6 MB

RL1 总容量：
16 × 128 KB = 2 MB

总容量：
6 MB + 2 MB = 8 MB
```

所以它确实没有增加 L1 总容量，只是把原有 L1 从：

```text
64 个 private L1
```

变为：

```text
48 个 cluster-shared CL1
+
16 个 chip-shared RL1
```

论文最终采用 cluster size=4、每 cluster 三个 CL1 和一个 RL1。

------

# 三、一条请求在 TLS-Cache 中怎样流动

论文第 5 页图 5、图 6 给出了 request router 和完整访问路径。

可以概括为：

```text
LD/ST Unit
    │
    ▼
Request Router
    │
    ▼
地址映射到本 cluster 的一个 CL1
    │
    ├─ CL1 hit
    │     └─ 返回原请求 SM
    │
    └─ CL1 miss
          │
          ▼
    Page / Memory Classifier
          │
          ├─ 目标页属于本芯片
          │     └─ 直接访问 local LLC / DRAM
          │          不访问 RL1
          │
          └─ 目标页属于其他芯片
                │
                ▼
          映射到本芯片某个 RL1
                │
                ├─ RL1 hit
                │     ├─ 填充原 CL1
                │     └─ 返回请求 SM
                │
                └─ RL1 miss
                      └─ 经过 inter-chip link
                           → remote LLC / DRAM
                           → 填充 RL1
                           → 填充 CL1
                           → 返回请求 SM
```

其中：

- 访问同一 SM 所在的目标 CL1，可以直接访问；
- 访问同 cluster 其他 SM 上的 CL1，要经过 intra-cluster crossbar；
- 访问其他 cluster 上的 RL1，要经过 intra-cluster 和 inter-cluster 两级网络；
- 本地内存请求在 CL1 miss 后直接去 LLC，不应经过 RL1。

这里最重要的是：

> TLS-Cache 不是先查询本地私有 L1、再查询邻居 L1，而是根据地址直接确定唯一的 home CL1。

因此不需要广播探测或目录查询，也不会出现“逐个检查多个 L1”的问题。

------

# 四、为什么 TLS 比 Shared L1 和 L1.5 更好

论文把数据复用分为几类：

- 同一 SM 内复用；
- 同一 cluster 内不同 SM 之间复用；
- 同一芯片不同 cluster 之间复用；
- 跨芯片复用。

三种方案能力如下：

| 结构       | 同 SM | 同 cluster 跨 SM | 跨 cluster | 缓存远端数据 |
| ---------- | ----- | ---------------- | ---------- | ------------ |
| Private L1 | 是    | 否               | 否         | 否           |
| Shared L1  | 是    | 是               | 否         | 否           |
| L1.5       | 是    | 较高层级捕获     | 是         | 是           |
| TLS-Cache  | 是    | CL1 捕获         | RL1 捕获   | 是           |

TLS 的优势不只是“多了一个 RL1”，而是把复用放在了不同距离：

```text
同 cluster 复用 → 尽量在 CL1 完成
跨 cluster 的远端复用 → 再进入 RL1
```

这样不会让本来可以在第一级处理的请求全部进入 L1.5。

------

# 五、论文结果应该怎样理解

论文报告：

- TLS 相对 Baseline 平均提升 30.2%，最高提升 77.2%；
- Shared L1 相对 Baseline 平均提升 9.3%；
- L1.5 相对 Baseline 平均提升 19.7%；
- TLS 相对 Shared L1 再提升 19.6%；
- TLS 相对 L1.5 再提升 8.8%。

平均读延迟方面：

```text
Baseline       100%
Shared L1       76.7%
L1.5            49.3%
TLS-Cache       36.9%
```

TLS 中约 42.6% 的请求由 RL1 服务，并将 L1 命中率从 L1.5 下的 18.3% 提高到约 30.0%。

但这个 30.2% 不能理解成“所有 GPU workload 平均提升 30.2%”。论文明确说明，它选择的是具有较高 intra-chip locality 的应用，包括 SS、SRAD、FFT、SPMV、SORT、CFD、GEMM、ST2D 和 REDC。

因此在复现时，首先应该复现的是：

```text
高 remote-access frequency
+
高 intra-chip remote-data reuse
```

的应用，而不是先拿一套任意 workload 求总体平均。

------

# 六、这项工作本身有哪些值得注意的限制

## 1. 默认是整块 L1 静态分角色

论文不是在每个 L1 内部按 bank 做 3:1，而是：

```text
整个物理 L1 → CL1
或
整个物理 L1 → RL1
```

默认四个 SM 中三个 SM 的物理 L1 是 CL1，一个 SM 的物理 L1 是 RL1。

这意味着那个配置为 RL1 的 SM 自己发出的普通 global request，也不能先访问自己的“本地 L1”，而是要根据地址去访问另外三个 CL1 中的一个。

这正是实现时容易做错的地方。

------

## 2. cluster size 实验同时改变了两件事

论文规定每个 cluster 始终只有一个 RL1，因此：

| Cluster size | CL1:RL1 | RL1 占总 L1 比例 |
| ------------ | ------- | ---------------- |
| 2            | 1:1     | 1/2              |
| 4            | 3:1     | 1/4              |
| 8            | 7:1     | 1/8              |

cluster size=8 性能下降到约 20.2%，论文主要归因于 RL1 容量只剩总 L1 的八分之一。

所以这个实验实际上同时改变了：

- cluster 共享范围；
- RL1 总容量；
- CL1/RL1 容量比例；
- inter-cluster 网络负载。

复现时必须严格跟随“每 cluster 一个 RL1”，否则不能与 Fig. 13 对齐。

------

## 3. 三个 CL1 的地址映射没有交代完整

论文说使用：

```text
ceil(log2 N)
```

个 tag bits 选择 N 个 CL1。

当 Shared L1 中 N=4 时没有问题，但 TLS 默认 N=3：

```text
ceil(log2 3) = 2 bits
```

两个 bit 会产生四种编码，论文没有说明第四种编码如何映射，也没有给出具体 bit 位置或 modulo/hash 规则。

这是精确复现中一个比较关键的缺口。

建议实现时提供可切换策略：

```text
tls_cl1_mapping = modulo
tls_cl1_mapping = tag_bits_remap
tls_cl1_mapping = xor_hash
```

初始采用：

```cpp
home_cl1 = cl1_list[(block_addr >> line_bits) % num_cl1];
```

保证三个 CL1 均匀分布，同时把它明确记录为“复现假设”。

------

## 4. TLS 两级 crossbar 的时序参数不完整

论文给出了硬件数量：

```text
16 个 4×4 intra-cluster crossbar
1 个 16×16 inter-cluster crossbar
```

但没有完整给出：

- 每级 latency；
- 每端口每周期带宽；
- request/response flit 大小；
- input/output queue 深度；
- arbitration policy；
- 是否支持 request/response 同时传输；
- RL1 response 如何经过两级网络返回。

论文只说明这些性能开销已经被模拟，并报告了综合后的面积和功耗。

这会直接影响精确 IPC。

------

## 5. coherence、store 和 atomic 描述偏简略

论文声称：

- cluster 内同一个 line 只有一个 CL1 副本，因此无需新的 cluster 内 coherence；
- 不同 cluster 之间的重复与传统 private L1 类似；
- 默认 GPU coherence 机制足以处理。

但实现时仍然必须明确：

- global store 是否 write-through；
- 是否 write-allocate；
- store 是否进入 RL1；
- atomic 是否绕过 CL1/RL1；
- kernel boundary 是否 invalidate；
- RL1 和多个 CL1 中存在副本时如何处理写操作。

第一版可以先让 atomic 绕过 TLS cache，并严格沿用 baseline L1 的 global store policy，但完整实验前必须把这些路径补齐。

------

# 七、基于你们当前 Accel-Sim 仓库，代码应该放在哪里

我检查了你们当前 `accel-sim-framework` 的结构。`gpu-simulator/setup_environment.sh` 会在运行时拉取独立的 `gpgpu-sim_distribution`，也就是说：

```text
accel-sim-framework
    └─ 配置、trace、实验脚本、trace-driven frontend

gpgpu-sim_distribution
    └─ shader、L1/L2、NoC、DRAM、mem_fetch 等微结构模型
```

真正的 TLS-Cache 代码应该主要修改后一个仓库，而不是只在 framework 中改配置。

当前 Accel-Sim 的官方 CI 也采用 framework 与 `gpgpu-sim_distribution` 同名分支配套检出的方式，因此建议你们在两个 fork 中建立同名 TLS 分支。([GitHub](https://github.com/accel-sim/accel-sim-framework/blob/dev/.github/workflows/main.yml))

推荐分支组织：

```text
swayhrl/accel-sim-framework
  hrl/tls-cache-exp-v0

swayhrl/gpgpu-sim_distribution
  hrl/tls-cache-exp-v0
```

你们现有的：

```text
hrl/decoupled-l2-exp-v0
```

不建议直接作为 TLS 的起点。

更合理的是：

1. 从相同 baseline commit 建立干净的 TLS 分支；

2. 只 cherry-pick 已经验证过的通用 multi-chip、chip-id、remote-path 代码；

3. 暂时关闭 decoupled-L2 优化；

4. TLS 完成后再建立：

   ```text
   hrl/tls-cache-plus-decoupled-l2
   ```

   研究两者组合。

这样不会把 TLS 的收益和你们已有 L2 改动混在一起。

------

# 八、推荐的 Accel-Sim 实现架构

## 1. 不要简单让多个 `ldst_unit` 共用一个 `m_L1D` 指针

这是最容易想到、但容易产生错误的实现。

当前每个 LD/ST unit 除了拥有 `m_L1D`，还拥有：

- L1 bank latency queue；
- response FIFO；
- pending register writes；
- warp/scoreboard completion；
- 与本 SM 对应的 memory interface。

如果四个 SM 直接共享某个 `l1_cache*`，可能出现：

- 每个 SM 都有独立 bank queue，等效把 cache bank 带宽放大四倍；
- cache miss response 被送回 requester，但 fill 应发生在 cache owner；
- target SM 错误地完成 requester SM 的 warp；
- MSHR 和 response routing 不匹配；
- 同周期多个 requester 无仲裁地调用同一个 cache。

因此建议建立一个明确的 **TLS cache fabric**。

------

## 2. 建议新增的对象

```cpp
class tls_cache_fabric {
 public:
  void push_from_sm(mem_fetch *mf);
  void cycle();
  void accept_memory_response(mem_fetch *mf);

 private:
  std::vector<tls_l1_endpoint *> m_endpoints;
  std::vector<tls_cluster_xbar *> m_intra_xbars;
  tls_inter_cluster_xbar *m_inter_xbar;
};
```

每个原始物理 L1 对应一个 endpoint：

```cpp
class tls_l1_endpoint {
 public:
  enum role_t {
    PRIVATE_L1,
    CL1,
    RL1
  };

 private:
  role_t m_role;
  l1_cache *m_cache;

  // 必须跟 cache endpoint 绑定，而不是跟 requester SM 绑定
  std::vector<std::deque<mem_fetch *>> m_bank_pipeline;

  std::deque<mem_fetch *> m_request_queue;
  std::deque<mem_fetch *> m_fill_queue;
  std::deque<mem_fetch *> m_response_queue;
};
```

不同实验配置只改变 endpoint role：

```text
Baseline:
  每个 endpoint = PRIVATE_L1

Shared L1:
  cluster 内 4 个 endpoint 全部 = CL1

TLS:
  cluster 内 3 个 endpoint = CL1
  cluster 内 1 个 endpoint = RL1

L1.5:
  endpoint 保持 PRIVATE_L1
  另外增加 remote-data-cache slices
```

这样四个比较结构可以共用同一套路由和统计框架。

------

## 3. TLS cluster 不要复用 GPGPU-Sim 原有的 `simt_core_cluster`

GPGPU-Sim 的 `simt_core_cluster` 本身承担：

- TPC／SM concentration；
- core-to-memory interconnect node；
- response routing；
- CTA scheduling 的部分组织关系。

论文中的 TLS cluster 只是：

```text
用于 L1 共享的 4-SM 逻辑组
```

二者语义不同。

建议单独增加：

```cpp
unsigned num_chips;
unsigned sms_per_chip;
unsigned tls_cluster_size;
unsigned rl1_per_tls_cluster;
```

以及：

```cpp
unsigned sid_to_chip(unsigned sid);
unsigned sid_to_local_sm(unsigned sid);
unsigned sid_to_tls_cluster(unsigned sid);
unsigned sid_to_tls_lane(unsigned sid);

unsigned map_cl1(new_addr_type addr, unsigned requester_sid);
unsigned map_rl1(new_addr_type addr, unsigned requester_chip);
```

不要通过把：

```text
n_simt_cores_per_cluster = 4
```

来代替 TLS cluster size，否则会同时改变原有 NoC concentration 和 baseline 结构。

------

## 4. `mem_fetch` 中要增加 TLS 路由元数据

至少需要保存：

```cpp
enum tls_stage_t {
  TLS_TO_CL1,
  TLS_CL1_TO_LOCAL_LLC,
  TLS_CL1_TO_RL1,
  TLS_RL1_TO_REMOTE_MEMORY,
  TLS_RETURN_TO_RL1,
  TLS_RETURN_TO_CL1,
  TLS_RETURN_TO_REQUESTER
};

struct tls_metadata {
  bool valid;

  unsigned requester_sid;
  unsigned requester_chip;

  unsigned cl1_owner_sid;
  unsigned rl1_owner_sid;
  unsigned home_chip;

  tls_stage_t stage;
  uint64_t transaction_id;
};
```

这里必须区分：

```text
requester_sid：最终要完成 warp 的 SM
cache_owner_sid：负责 cache tag/MSHR/fill 的物理 L1 endpoint
```

否则远端 CL1 或 RL1 命中后，很容易错误更新 owner SM 的 scoreboard。

------

## 5. MSHR 应属于目标 cache endpoint

例如 cluster 内三个 SM 同时请求同一个 line：

```text
SM0 ─┐
SM1 ─┼─→ CL1-2 miss
SM3 ─┘
```

应当在 CL1-2 的 MSHR 中合并成一个下行请求，并保留三个 requester。

类似地，不同 cluster 的 CL1 同时 miss 到同一个 remote line：

```text
CL1-A ─┐
CL1-B ─┼─→ RL1-7 miss
CL1-C ─┘
```

应当在 RL1-7 的 MSHR 中合并，远端数据返回后再 fan-out 到多个 CL1。

因此完整返回链应当是：

```text
Remote memory response
        │
        ▼
   fill target RL1
        │
        ├─ 唤醒多个 waiting CL1 miss
        ▼
   fill target CL1(s)
        │
        ├─ 唤醒多个 requester
        ▼
 requester LD/ST writeback
```

这部分是整个实现中最容易出现功能错误和死锁的位置。

------

# 九、建议修改的主要文件

| 模块            | 建议文件                                  | 主要改动                                     |
| --------------- | ----------------------------------------- | -------------------------------------------- |
| 配置参数        | `gpu-sim.h/.cc`、`shader.h/.cc`           | 注册 chip/TLS/network 配置                   |
| Chip/SM 分组    | `gpu-sim.h/.cc`                           | `sid_to_chip`、TLS cluster 映射              |
| 请求入口        | `shader.h/.cc`                            | global request 从 private L1 改为 TLS router |
| Cache endpoint  | `gpu-cache.h/.cc` 或新增 `tls-cache.*`    | CL1/RL1 tag、MSHR、bank pipeline             |
| 请求元数据      | `mem_fetch.h/.cc`                         | requester、owner、stage、transaction ID      |
| Page placement  | `addrdec.h/.cc` 或新增 `page-placement.*` | 4 KB first-touch／round-robin                |
| 本地与远端路由  | `gpu-sim.*`、`icnt_wrapper.*`             | chip-aware LLC/DRAM 路径                     |
| Inter-chip ring | 新增 `mcm-network.*` 或扩展 Intersim      | hop、带宽、buffer、backpressure              |
| 统计            | `shader_core_stats`、`memory_stats_t`     | CL1/RL1、local/remote latency/traffic        |

推荐新增独立文件：

```text
src/gpgpu-sim/tls-cache.h
src/gpgpu-sim/tls-cache.cc
src/gpgpu-sim/mcm-network.h
src/gpgpu-sim/mcm-network.cc
src/gpgpu-sim/page-placement.h
src/gpgpu-sim/page-placement.cc
```

不要把所有逻辑直接堆进 `shader.cc`。

------

# 十、分阶段复现方案

## Phase 0：固定 baseline 和 artifact

首先固定：

```text
framework commit
gpgpu-sim commit
CUDA / tracer version
trace version
benchmark suite commit
benchmark input
GPU configuration
```

建立：

```text
docs/reproduction_manifest.md
```

至少记录：

```text
benchmark
suite/version
input
kernel name
trace checksum
instruction count
memory instruction count
CTA count
```

论文的 Data Availability 只写了“可按请求提供”，并没有在正文中给出完整 artifact。

在正式大改前，应向作者索取：

- Accel-Sim 和 GPGPU-Sim commit；
- simulator patch；
- config 文件；
- benchmark input；
- trace；
- CL1/RL1 地址映射；
- TLS xbar latency、queue、带宽；
- L1.5 的具体容量和 banking；
- store/atomic policy。

这是精确复现能否成功的决定性因素。

------

## Phase 1：先完成 multi-chip NUMA baseline

不要先实现 TLS。先让 Baseline 正确支持：

```text
4 chips
64 SM / chip
16 L2 slices / chip
8 memory controllers / chip
4 KB first-touch pages
4-chip ring
768 GB/s
32 cycles / hop
```

论文完整配置见 Table 1。

建议逻辑映射：

```cpp
chip_id = sid / 64;
local_sid = sid % 64;

memory_chip =
    page_home_chip[addr >> 12];

local_l2_slice =
    original_addr_decoder(addr) % 16;

global_l2_slice =
    memory_chip * 16 + local_l2_slice;
```

### First-touch 建议

增加：

```cpp
std::unordered_map<uint64_t, unsigned> page_home;
```

首次访问某 4 KB 页时：

```cpp
page_home[page] = requester_chip;
```

为了保证 Baseline、Shared L1、L1.5、TLS 的页面放置完全一致，最好：

1. 用一个 placement pre-pass 生成 page map；
2. 四个结构共同 replay 同一份 page map。

否则不同结构的执行时序变化可能改变“谁先访问页面”，进而使 page placement 也发生变化，混入额外变量。

### Phase 1 验收

必须能够区分并统计：

```text
local L2 access
remote L2 access
local DRAM access
remote DRAM access
inter-chip request bytes
inter-chip response bytes
hop count
link queue delay
```

并通过强制 page-home 的微基准验证 1-hop、2-hop 路径。

------

## Phase 2：实现 Shared L1，而不是直接上完整 TLS

这一阶段每个 4-SM cluster 的四个 L1 都作为 CL1：

```text
4 CL1 + 0 RL1
```

地址映射：

```cpp
home = cluster_base +
       hash(block_addr) % 4;
```

所有 global request 直接去 home CL1。

这一步主要验证：

- requester 与 cache owner 分离；
- cluster 内路由；
- endpoint bank bandwidth；
- shared MSHR；
- remote CL1 hit response；
- cluster 内单副本。

论文中 Shared L1 相对 Baseline 平均提升约 9.3%，可以作为第一项性能 sanity check。

若 Shared L1 的命中率和性能都没有明显增加，不应继续实现 RL1，而应先检查：

- CTA 分布是否产生跨 SM 共享；
- 地址映射是否均匀；
- target cache 是否正确填充；
- requester response 是否正确；
- cache bank 带宽是否被无意放大或压低。

------

## Phase 3：实现 L1.5 对照组

论文中的 L1.5 是：

```text
Private L1
+
从 LLC 容量中切出的 remote data cache
```

并要求其 remote cache size 和 bandwidth 与 TLS 中的 RL1 相同。

按默认参数推算：

```text
TLS RL1 总容量 = 2 MB / chip
```

一个合理的复现解释是：

```text
L1.5:
  16 个 remote-cache slice × 128 KB = 2 MB

LLC:
  原 16 × 256 KB = 4 MB
  改为 16 × 128 KB = 2 MB
```

这样：

```text
Private L1 8 MB
+ Remote cache 2 MB
+ LLC 2 MB
= 12 MB
```

与 Baseline/TLS 的总 cache capacity 一致。

但论文没有明确说明 L1.5 的具体 slice 组织，所以这一点应当列为待作者确认项。

------

## Phase 4：实现完整 TLS-Cache

默认配置：

```text
tls_cluster_size = 4
cl1_per_cluster = 3
rl1_per_cluster = 1
```

建议固定 lane 3 为 RL1：

```cpp
role(local_sid % 4) =
    local_sid % 4 == 3 ? RL1 : CL1;
```

### CL1 映射

```cpp
cl1_index =
    hash(block_addr) % 3;

cl1_owner_sid =
    chip_base +
    tls_cluster_id * 4 +
    cl1_index;
```

### RL1 映射

每芯片有 16 个 RL1：

```cpp
rl1_cluster =
    hash(block_addr) % 16;

rl1_owner_sid =
    chip_base +
    rl1_cluster * 4 +
    3;
```

### CL1 miss classifier

```cpp
if (page_home_chip(addr) == requester_chip)
    send_to_local_llc();
else
    send_to_rl1();
```

### RL1 miss

```cpp
send_to_memory_chip(page_home_chip(addr));
```

### 需要模拟的延迟和竞争

至少应显式建模：

```text
requester → intra-cluster xbar
intra-cluster xbar → CL1
CL1 → inter-cluster xbar
inter-cluster xbar → target cluster
target intra-cluster xbar → RL1
response reverse path
endpoint bank conflict
endpoint MSHR full
xbar input/output queue full
```

第一版可以使用可配置的 bounded delay queue，而不是立即接入完整 BookSim：

```text
tls_intra_xbar_latency
tls_inter_xbar_latency
tls_xbar_queue_depth
tls_xbar_flit_bytes
tls_xbar_bandwidth
```

等功能和 backpressure 正确后，再升级为更详细的 crossbar arbitration。

------

## Phase 5：补齐 store、atomic 和 coherence

推荐实现顺序：

1. global load；
2. global store，沿用 baseline write policy；
3. write-allocate/write-through corner cases；
4. atomic 绕过 CL1/RL1；
5. kernel boundary invalidate；
6. eviction/writeback；
7. sector miss 和 partial-sector merge。

在这一阶段之前可以运行只读微基准，但不应宣称完成了论文 workload 的完整复现。

------

# 十一、必须准备的微基准

在运行 CFD、GEMM 等大 workload 前，至少需要七个定向测试。

| 微基准                           | 预期行为                                   |
| -------------------------------- | ------------------------------------------ |
| 同一 SM 重复读同一 line          | 第二次 CL1 hit                             |
| 同 cluster 不同 SM 读同一 line   | 后续请求 remote-CL1 hit                    |
| 不同 cluster 读本地页            | 各自 CL1 miss 后进入 local LLC，不访问 RL1 |
| 不同 cluster 读远端页            | 第一次 RL1 miss，随后其他 cluster RL1 hit  |
| 多 SM 同周期读同一 line          | CL1 MSHR merge                             |
| 多 cluster 同时请求同一远端 line | RL1 MSHR merge并 fan-out                   |
| store/atomic 后重新读取          | 不出现 stale CL1/RL1 hit                   |

一个非常关键的序列应当是：

```text
1. chip 1 首次触碰 page P，使 P 位于 chip 1
2. chip 0 / cluster 0 读取 P
      CL1 miss → RL1 miss → remote memory
3. chip 0 / cluster 0 再次读取
      CL1 hit
4. chip 0 / cluster 1 读取同一 line
      CL1 miss → RL1 hit
```

计数应严格是：

```text
remote memory access = 1
RL1 miss             = 1
RL1 hit              = 1
CL1 hit              = 1
```

这比直接比较 IPC 更能发现请求路径错误。

------

# 十二、需要新增的统计量

为了复现论文图表，至少增加：

```text
CL1 local access / hit / miss
CL1 remote access / hit / miss
CL1 MSHR merge
RL1 access / hit / miss
RL1 MSHR merge

local LLC requests
remote LLC requests
local DRAM requests
remote DRAM requests

intra-cluster xbar requests / bytes / stalls
inter-cluster xbar requests / bytes / stalls
inter-chip requests / bytes / hops / queue latency

read issue-to-completion latency
request final service level
```

其中“request final service level”应分类为：

```text
CL1
RL1 / L1.5
Local memory partition
Remote memory partition
```

用来直接画论文 Fig. 11。

还应记录每个请求：

```text
issue_cycle
CL1_arrive_cycle
RL1_arrive_cycle
memory_arrive_cycle
complete_cycle
```

这样才能定位性能差异来自：

- cache hit；
- cache queue；
- TLS xbar；
- inter-chip link；
- 远端 memory system；

中的哪一部分。

------

# 十三、实验复现顺序

## 第一批：主结果

优先只做论文默认配置：

```text
4 chips
64 SM/chip
cluster size=4
128 KB L1/SM
first-touch
```

运行四种结构：

```text
Baseline
Shared L1
L1.5
TLS-Cache
```

第一轮目标只复现：

1. Fig. 8：normalized IPC；
2. Fig. 10：normalized read latency；
3. Fig. 11：请求服务层级分布。

论文的参考目标为：

| 指标                         | Shared L1 | L1.5     | TLS      |
| ---------------------------- | --------- | -------- | -------- |
| 平均 normalized IPC          | 约 1.093  | 约 1.197 | 约 1.302 |
| 平均 normalized read latency | 0.767     | 0.493    | 0.369    |

不应一开始就做 6/8 chips、80/96 SM 和面积功耗。

------

## 第二批：per-kernel 分析

复现 Fig. 9：

```text
x = intra-chip locality
y = normalized IPC
```

需要按 kernel，而不是只按整个 application 汇总。

这一步能够检查：

- 高 locality 但低性能收益：可能不 memory-sensitive；
- 高 locality 且高性能收益：TLS 理想 workload；
- 低 locality 且 L1.5 回退：可能是 LLC 容量缩减造成；
- TLS 是否在低 locality kernel 中避免明显回退。

------

## 第三批：敏感性

依次做：

```text
SM/chip:    64 / 80 / 96
chip count: 4 / 6 / 8
L1 size:    64 / 128 / 256 KB
placement:  first-touch / round-robin
cluster:    2 / 4 / 8
```

论文在 8-chip 配置下报告 TLS 平均提升约 42%，并且 6/8-chip 使用 X-Y routing，而不是四芯片配置中的 ring。

因此 6/8-chip 复现还需要明确：

- 2×3 或其他 6-chip mesh 形状；
- 2×4 或其他 8-chip mesh 形状；
- gateway 布置；
- 每 link 带宽；
- router latency。

论文对此交代也不够完整，所以应放在主结果稳定之后。

------

# 十四、最终验收标准

## 功能验收

必须满足：

```text
TLS disabled 时与 upstream baseline 结果一致
每芯片物理 L1 总容量始终为 8 MB
每 cluster 同一 line 至多存在一个 CL1 copy
RL1 只缓存 remote-memory data
local-memory CL1 miss 不访问 RL1
所有完成信号返回原 requester SM
MSHR merge 后能够正确 fan-out
不存在 request/response network deadlock
```

## 趋势验收

在高 intra-chip locality workload 上应观察到：

```text
Shared L1:
  L1 hit rate 上升
  但 remote traffic 仍较高

L1.5:
  remote traffic 下降
  低 locality kernel 可能因 LLC 减小而回退

TLS:
  CL1 hit rate高于 L1.5
  remote traffic低于 Shared L1
  read latency最低
```

性能排序通常应为：

```text
TLS > L1.5 > Shared L1 > Baseline
```

但不要求每个 kernel 都严格满足这一顺序。

------

# 十五、推荐的最短落地路线

第一轮不要直接实现全部论文内容，建议按下面的最小闭环推进：

```text
M0  固定两个仓库和全部 trace/config commit
M1  实现 4-chip NUMA、4 KB page ownership 和 remote ring
M2  实现 cache-owner/requester 分离
M3  实现 cluster-4 Shared L1
M4  实现 2 MB/chip 的 L1.5 对照组
M5  实现 3CL1+1RL1 的完整 TLS
M6  跑定向微基准并关闭所有路径错误
M7  复现 Fig. 8、Fig. 10、Fig. 11
M8  再做 cluster size 和 chip count sensitivity
```

其中真正最难的不是 CL1/RL1 的 tag mapping，而是：

1. **multi-chip page placement 与 inter-chip network；**
2. **cache owner 和 requester 分离后的 MSHR/fill/response；**
3. **共享 cache endpoint 的真实 bank bandwidth；**
4. **RL1 miss → RL1 fill → CL1 fill → requester completion 的多级返回链。**

因此总体判断是：

> **机制复现完全可行，而且适合建立在 Accel-Sim/GPGPU-Sim 上；但它不是“改几个 cache 参数”就能完成，而是一项需要重构 L1 请求归属、fill 路径和 multi-chip NoC 的中等偏大模拟器工程。最合理的起点是先完成独立、可验证的 multi-chip baseline 和 Shared L1，再添加 RL1。**