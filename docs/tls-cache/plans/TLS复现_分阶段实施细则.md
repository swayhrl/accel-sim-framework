# TLS-Cache 复现：分阶段实施细则（审阅稿）

> 状态：仅供审阅，尚未开始实现。  
> 上位约束：[TLS复现_执行契约与路线.md](TLS复现_执行契约与路线.md)。  
> 当前原则：先用已有 trace 把机制、守恒关系和竞争模型做正确；缺失 workload 后补，不因缺少九个论文负载而阻塞实现。

## 1. 本轮目标与完成定义

本轮复现分为三层，必须按顺序通过：

1. **机制正确**：请求路由、page home、CL1/RL1 归属、多级 fill、MSHR 合并、store/atomic、sector、返回 requester 全部满足不变量。
2. **时序可信**：endpoint bank/port、TLS crossbar、per-chip memory NoC、inter-chip ring 均有有限带宽和队列，不能靠固定延迟加无限吞吐得到结果。
3. **论文对照**：在论文规模和可信 workload 上复现 ICL、IPC、延迟与服务层级趋势。

“代码可以运行”不算阶段完成。每一阶段只有在 directed test、守恒统计、TLS-off 回归及 provenance 同时通过后才能进入下一阶段。

## 2. Git、源码和运行目录约定

实现获批后建立两个独立 worktree：

| 层次 | 分支 | 建议 worktree | 基线 |
|---|---|---|---|
| Accel-Sim framework、配置、脚本、文档 | `hrl/tls-cache-repro-v0` | `/workspace/worktrees/accel-sim-tls-cache` | framework `upstream/dev@3016c658` |
| GPGPU-Sim 核心 | `hrl/tls-cache-gpgpusim-v0` | `/workspace/worktrees/gpgpu-sim-tls-cache` | 当前匹配的 `dev@73774727` |

不得从 `hrl/decoupled-l2-exp-v0` 或 `hrl/decoupled-l2-v0` 继承实现代码。现有分支中的 trace 获取、筛选和 archive 脚本可以逐个审计后移植，但不整体 merge 实验历史。

顶层仓库忽略 `gpu-simulator/gpgpu-sim/`，因此顶层分支不能自动记录核心实现。顶层必须提交 `experiments/tls_cache/toolchain.lock`，至少包含：

- framework remote、branch、commit；
- GPGPU-Sim remote、branch、commit；
- 编译器、CUDA、构建类型；
- 默认配置文件 SHA-256；
- trace manifest revision。

运行数据仍放入忽略的 `hw_run/tls-cache-*`。任何脚本不得依赖“当前 shell 恰好指向哪个 GPGPU-Sim”；`scripts/setup_tls_cache_env.sh` 必须检查实际 root 和 commit，不匹配就退出。

### 建议提交边界

每个阶段至少一个可独立构建、可回退的提交：

1. `docs/infra: scaffold TLS reproduction and lock baselines`
2. `feat(tls): add default-off configuration and stats plumbing`
3. `feat(mgpu): add topology, placement and physical mapping`
4. `feat(mgpu): model private-L1 multi-chip baseline fabric`
5. `feat(tls): add ideal RDC and ICL characterization`
6. `feat(tls): add endpoint-owned Shared L1`
7. `feat(tls): add matched L1.5 RDC`
8. `feat(tls): add CL1/RL1 two-level shared cache`
9. `test(tls): add pressure, deadlock and workload gates`
10. `exp(tls): add paper-scale configurations and result pipeline`

禁止把多个尚未通过出口条件的阶段压成一个大提交。

## 3. 两套开发尺度

### 3.1 TLS-MINI：日常机制验证

建议使用 4 chip × 8 SM/chip，共 32 SM；每 chip 至少 2 个 TLS cluster，默认每 cluster 4 SM。这样能覆盖：

- 同 SM CL1；
- 同 cluster peer CL1；
- 同 cluster RL1；
- 跨 cluster RL1；
- ring 0/1/2-hop；
- 每 chip 独立 LLC/partition。

memory channel 和 LLC slice 按论文比例缩小，但所有容量、带宽和映射必须由配置给出，不能散落硬编码。MINI 结果只用于正确性和趋势预检，不与论文数值对比。

### 3.2 TLS-PAPER：论文规模

4 chip × 64 SM/chip，共 256 SM；每 chip 16 LLC slice、8 memory controller，1 GHz；4-SM TLS cluster；128 KB sector L1；论文给出的 LLC、DRAM、NoC 和 ring 参数全部进入独立配置。

论文未给出的 L1 组相联度、TLS xbar 细节和 ring 带宽解释放入 `assumptions.yml`。在作者回复前，主配置只能标记为 `public-description-reconstruction`。

## 4. 已有 workload 的分工

| 层级 | workload | 用途 | 每阶段是否必跑 |
|---|---|---|---|
| Unit | mapper/page/fabric/cache 独立测试 | 位映射、队列、仲裁、状态机 | 是 |
| Directed trace | 人工控制地址和 requester 的短 trace | 命中、miss、hop、fill、合并、store | 是，必须完整 drain |
| Smoke | SRAD 1/40 trimmed、PolyBench GEMM 1/40、FDTD2D 1/40 | 真实指令/sector/多 kernel 集成 | 是，选 1–2 个短项 |
| Functional workload | CFD 097K、完整 SRAD trimmed | 多 kernel、长期状态、page placement | 大阶段出口必跑 |
| Pressure | 2MM/3MM、CUTLASS、较大 CFD | MSHR、bank、网络拥塞、死锁 | M6/M8 才必跑 |
| Paper suite | SRAD、CFD、后补 SPMV/SHOC/Mars | 正式图表 | 机制完成后 |

开发期允许对真实 workload 设置 cycle/CTA 上限来快速发现崩溃，但任何守恒和完成性出口必须用能够完整 drain 的 directed trace；被截断的运行不能证明“无丢请求”。

每个 trace 在 `experiments/tls_cache/workloads.csv` 中记录：绝对来源、suite/app/input、kernel list、trace bytes、SHA-256、是否裁剪、裁剪规则及角色（directed/smoke/pressure/paper）。

## 5. 目标模块划分

核心逻辑集中在新增的 `src/gpgpu-sim/tls-cache.h/.cc`（最终命名可在实现时微调），避免把整个状态机堆进 `shader.cc`：

| 模块 | 职责 | 建议 owner |
|---|---|---|
| `tls_cache_config` | mode、topology、mapping、queue、latency、统计选项和合法性检查 | `gpgpu_sim_config` 持有 |
| `gpu_chip_topology` | `sid→chip/local_sid/TLS cluster`、partition 分组、ring hop | `gpgpu_sim` 持有 |
| `page_placement_table` | 4 KB dynamic first touch、frozen replay、dump/hash | multi-chip system 持有 |
| `multi_chip_address_decoder` | 一次性生成完整 physical mapping | multi-chip system 持有 |
| `multi_chip_memory_fabric` | per-chip request/response NoC、ring、有限队列和带宽 | `gpgpu_sim` 每周期驱动 |
| `tls_cache_endpoint` | endpoint 的 cache、bank pipeline、MSHR、fill/response 端口 | TLS system 持有 |
| `tls_cache_fabric` | CL1/RL1 mapping、intra/inter-cluster xbar、仲裁 | 每 chip 一个 |
| `tls_transaction` | root UID、requester、owner、home、阶段、waiter、时间戳 | 有界 sidecar 表 |
| `tls_cache_stats` | 守恒、service level、hop、latency、pressure、ICL | TLS system 持有 |

`gpgpu_sim` 只负责创建、逐周期调用和打印总统计。`ldst_unit` 只负责把可缓存 global request 提交给 TLS system，以及接收返回 requester 的 completion。

### 5.1 请求主路径

Shared/L1.5/TLS 模式下：

```text
ldst_unit alloc request
  → determine requester sid/chip
  → accept into TLS/multi-chip fabric（失败则保留 accessq 并回压）
  → owner endpoint bank/tag/MSHR
  → lower endpoint or local/remote memory hierarchy
  → reverse fill chain
  → route completion to original requester sid
  → requester ldst_unit releases pending write/scoreboard exactly once
```

不能把 `m_L1D == NULL` 当成 TLS bypass。legacy/default-off 路径维持原判断；TLS 模式使用独立分支。

### 5.2 完成路径

现有 L1 hit 直接在 owner `ldst_unit::L1_latency_queue_cycle()` 中释放 requester scoreboard，这不适用于共享 endpoint。实现时抽取或新增统一的 requester completion helper，并先证明 default-off 统计完全不变。

每个 completion token 至少含 root UID、requester sid/wid、原始 `warp_inst_t`/`mem_fetch`、完成类型（load/store ack/atomic）和 sector。无论 hit、MSHR merge 还是多级 fill，同一个 leaf request 只能完成一次。

## 6. 配置契约

所有新选项默认关闭。建议配置面如下：

```text
-tls_cache_mode disabled|baseline|shared|l15|tls
-mgpu_num_chips N
-mgpu_sms_per_chip N
-mgpu_mem_channels_per_chip N
-mgpu_subpartitions_per_channel N
-mgpu_page_size 4096
-mgpu_page_placement dynamic-first-touch|frozen
-mgpu_page_map_file PATH

-tls_cluster_size 4
-tls_cl1_slices_per_cluster 3
-tls_rl1_slices_per_cluster 1
-tls_cl1_mapping selected-bits|modulo-line|xor
-tls_rl1_mapping selected-bits|modulo-line|xor

-tls_intra_xbar_latency N
-tls_inter_xbar_latency N
-tls_xbar_queue_depth N
-tls_xbar_request_bytes_per_cycle N
-tls_xbar_response_bytes_per_cycle N
-mgpu_ring_hop_latency 32
-mgpu_ring_queue_depth N
-mgpu_ring_request_bytes_per_cycle N
-mgpu_ring_response_bytes_per_cycle N
```

`disabled` 是旧版单芯片行为，必须逐周期兼容；`baseline` 是论文 multi-chip private L1；其余三项分别是 Shared L1、L1.5 和 TLS。

启动时必须拒绝以下非法配置：

- `num_shader != num_chips × sms_per_chip`；
- 每 chip SM 数不能被 TLS cluster size 整除；
- CL1+RL1 endpoint 数与 cluster size 不等；
- memory channel/subpartition 不能均匀分组到 chip；
- frozen 模式 page-map 缺失或 hash 不符；
- TLS mode 使用 disabled/zero queue、bandwidth 或未声明 mapping。

每次运行开头打印一条机器可解析的 `TLS_CONFIG`，结束时打印 `TLS_STATS_VERSION`；脚本对未知版本直接失败。

## 7. 分阶段实施

## P0：干净分支、基线锁定和 workload manifest

### 工作

- 建立双 worktree/双分支，不触碰仍在运行的 decoupled-L2 worktree。
- 迁移三份 TLS 文档，新增 `toolchain.lock`、`assumptions.yml`、`workloads.csv`。
- 建立 `TLS-MINI` 和 `TLS-PAPER` 配置目录，但此阶段不加入新模拟器选项。
- 从干净 baseline 构建 release/debug 两个二进制。
- 选择一个完整 drain 的短 trace和一个真实 smoke trace，保存 baseline stdout、cycles、instructions、L1/L2/DRAM 统计与二进制 hash。

### 出口

- 两个 worktree 均 clean，核心 commit 被顶层 lock 精确引用。
- 同一个 baseline 命令重复两次，关键统计一致。
- manifest 中不存在“路径存在但 trace 未核验”的 `ready` 状态。

## P1：default-off 配置骨架和零影响接线

### 工作

- 新增 `tls_cache_config`、option parser、统计版本和空的 TLS system 生命周期。
- 将新增 `.cc` 加入 Make/CMake 构建。
- mode 默认为 `disabled`；disabled 时不分配 endpoint、page table、fabric、sidecar，也不增加每周期循环。
- 加入环境脚本和最小 runner，保存双仓 revision。

### 测试

- debug/release 编译。
- baseline golden trace、SRAD trimmed smoke。
- 比较 cycles、instructions、IPC、L1/L2/DRAM access/miss、interconnect packets、退出状态。

### 出口

- `disabled` 与 P0 golden 的全部关键整数统计精确一致；不能只要求“IPC 接近”。
- Valgrind/ASan 可选短测无新增泄漏；新配置非法值会明确报错。

## P2：拓扑、first-touch 和物理映射（尚不改时序）

### 工作

- 实现 `sid→gpu_chip/local_sid/tls_cluster/local_endpoint` 的纯函数。
- 实现 ring 最短 hop；4-chip directed test 覆盖 0/1/2-hop。
- 实现 dynamic first touch、dump、frozen replay。
- 新增原子化 `physical_mapping`：`home_chip`、chip-local/global memory channel、subpartition、完整 `addrdec_t`、`partition_addr` 一次生成并一起写入，禁止只改 `chip/sub_partition`。
- original core request 触发 first touch；sector child、writeback、fill 不得重新决定 page home。
- page table 在一次 application simulation 内跨 kernel 保留，下一 application run 重置。

### 实现注意

当前 `mem_fetch` 构造函数在创建时立即进行单芯片地址译码。应让 allocator 取得 multi-chip mapping，或向构造函数传入可选 `physical_mapping`；所有派生 `mem_fetch` 必须继承或重新计算完整 mapping。不得使用当前 `set_chip()`/`set_partition()` 作为最终方案，因为 `partition_addr` 会与之不一致。

### 测试

- 单元测试覆盖边界 sid、page 边界、非 2 次幂 mapping remap、同地址重复触碰和 frozen hash。
- 乱序访问同一页，验证第一次被接受的 original request 唯一决定 home。
- default-off golden 再跑。

### 出口

- 每个访问都满足 `global_subpartition = home_chip × subpartitions_per_chip + local_subpartition`。
- dynamic dump 后 frozen replay 的每个访问 home 完全一致。
- page assignment count 等于 page table size，无二次归属。

## P3：multi-chip private-L1 baseline

### P3A：功能拓扑

- `mode=baseline` 保留每 SM 私有 L1。
- L1 miss 按 page home 路由至本 chip 或 remote chip 的 LLC/subpartition。
- 将 32/64 个全局 memory partition 按 chip 连续分组；每组 LLC state 独立。
- request 保留 requester sid/tpc；reply 必须回到原 requester，而非 memory-home chip 的同号 SM。
- `perf_memcpy`、instruction/constant/texture/local memory是否参与 page placement逐项声明；首轮 ICL 只统计 global read。

### P3B：有限带宽网络

- 在请求进入现有 memory interconnect 前加入 per-chip memory-fabric 队列；remote request 依次消耗 source-chip NoC、ring hop、destination-chip NoC。
- memory reply 对称消耗 response 资源。
- request control bytes 与 response data bytes分开计费。
- 每条 ring link、每个方向、每 chip injection/ejection 独立仲裁；不可使用一个全局 token bucket。
- 初版可以复用现有 interconnect完成最终传输，但额外延迟/带宽不能重复隐藏；在正式结果前必须说明现有 ICNT 是承载层还是被旁路。

### Directed tests

1. local page：0 ring hop，只访问 source chip LLC。
2. 邻接 remote page：1-hop，remote LLC miss 后原路返回。
3. 对侧 remote page：2-hop。
4. 两个方向同时注入：只争用实际重叠的有向 link。
5. queue 满：requester backpressure，不丢请求。
6. remote LLC hit 与 DRAM miss：服务层级分别正确。

### 出口

- `accepted = completed + live`，结束时 `live=0`。
- 每个 memory request 只进入一个 subpartition；本 chip LLC 不可能命中 remote-home page 的同一物理副本。
- hop histogram 与 directed 预期完全一致。
- ring/link/queue 每周期消耗不超过配置。
- MINI 上 dynamic/frozen 均完整 drain，无死锁。

## P4：Ideal RDC 与 ICL characterization

### 工作

- 增加 timing-neutral shadow RDC：每 chip 保存已从 remote hierarchy 取得的 read line/sector，容量设为无限或足够大。
- 只观察，不改变 hit/miss、latency、替换或网络流量。
- 固定统计原子：内部以 32 B sector request 为主，同时用 root UID 汇总 original coalesced transaction。
- 输出：remote read frequency、ideal RDC hit/miss、ICL、每 kernel/per app 值。

### 统计定义

```text
remote_read_frequency = remote-home global read requests / all global read requests
ideal_rdc_hit_rate    = repeat remote lines on same requester chip / remote-home reads
ICL                   = remote_read_frequency × ideal_rdc_hit_rate
```

第一次 remote fetch 在数据真正返回本 chip 时插入 shadow RDC；同一在途 line 的并发请求是否算 hit 必须单独计为 `inflight_merge_opportunity`，不能伪装成已缓存 hit。

### 出口

- observer 开/关的所有 timing 和 cache/DRAM 统计完全一致，只有新增 observer 统计不同。
- 手工地址序列的 hit/frequency/ICL 可人工算出并精确吻合。
- SRAD、CFD、GEMM/FDTD2D 给出第一版机会矩阵；此时只判断 workload 是否适合调试，不要求匹配论文 Table 2。

## P5：Shared L1（先建立共享 endpoint 基础）

### 工作

- `mode=shared`：每个 4-SM TLS cluster 有 4 个 CL1 endpoint，无 RL1。
- global address 直接映射到唯一 CL1；同 SM owner 直达，peer owner 经过 intra-cluster xbar。
- cache/tag/MSHR/bank/port 归 endpoint 所有，requester `ldst_unit` 不再拥有这笔访问的 cache pipeline。
- endpoint miss 进入 P3 multi-chip memory fabric；fill 回 owner endpoint，随后按每个 MSHR waiter 返回各 requester。
- 保留原 L1 sector、write、allocation、replacement 配置；不得先用理想 tag 或无限 MSHR跑真实 workload。
- flush/invalidate 遍历 endpoint一次；不能按4个 requester重复操作同一个 endpoint。

### Directed tests

1. requester 自己是 home CL1，miss→fill→hit。
2. peer CL1，验证一次 intra request 和一次 response。
3. 两 requester 同 line，owner MSHR 合并，两个 requester 各完成一次。
4. 同 line 不同 sector，验证 partial valid/fill。
5. store hit/miss/ack 与 baseline policy一致。
6. bank conflict、MSHR full、miss queue full 能正确回压。

### 出口

- cluster 内每个 line/sector 只有一个 CL1 owner；不存在 peer probing 或重复 tag copy。
- `endpoint_accept = hit + miss + reservation_fail`，重试不被重复计为新 logical request。
- `mshr_waiters_added = waiters_completed`（结束时 MSHR 空）。
- requester pending writes、store req、atomic count 全部归零。
- Shared L1 关闭后 default-off golden 仍精确一致。

## P6：L1.5 公平对照

### 工作

- `mode=l15` 保留每 SM 私有 128 KB L1。
- remote-home 的 private-L1 miss 路由到 chip-wide distributed RDC；local-home miss 直接到本 chip LLC。
- RDC 容量从 LLC 划出：每 chip 2 MB RDC、剩余 2 MB LLC（论文默认）；私有 L1仍为8 MB/chip。
- RDC slice 数、bank/port、mapping 和对外 xbar 带宽与 TLS RL1完全匹配。
- RDC 只填 remote-home line；local line 进入 RDC 立即 assert。

### Directed tests

- remote miss→remote memory→RDC→private L1；第二个 SM private miss能命中RDC。
- local miss不查询RDC。
- RDC MSHR merge、eviction、sector partial fill。
- 容量/带宽审计输出与 TLS RL1 配置相同。

### 出口

- 总容量按论文比较口径可打印并自动校验。
- L1.5 没有比 TLS 多出的 injection、lookup 或 fill port。
- `rdc_local_home_fill=0`，所有 waiter 完成且 sidecar 归零。

## P7：TLS 两级共享 L1

### 工作

- `mode=tls`：每 cluster 3 CL1 + 1 RL1物理角色；每 chip 16 个 RL1 slice 组成 chip-wide remote cache。
- requester 地址在本 cluster 的3个CL1中选择唯一home。
- CL1 miss：local-home page→本 chip LLC；remote-home page→按地址选择本 chip 的唯一 RL1 slice（可能在本 cluster，也可能在另一cluster）。
- RL1 hit：经反向 TLS fabric填入发起CL1并完成其waiter。
- RL1 miss：经P3 memory fabric访问remote LLC/DRAM，返回后先fill RL1，再唤醒一个或多个CL1 fill，最后返回各requester。
- CL1/RL1 均使用 endpoint-owned MSHR；sidecar显式记录 `AT_CL1`、`TO_RL1`、`AT_RL1`、`TO_MEMORY`、`FILL_RL1`、`FILL_CL1`、`TO_REQUESTER`。

### 关键合并场景

多个cluster请求同一remote line时，可能在同一RL1 MSHR合并；RL1完成后，每个waiter对应不同CL1 MSHR。实现不能只保存一个“上一级owner”，而要为每个RL1 waiter保存目标CL1和root UID。

### Directed tests

1. CL1 hit。
2. local-home CL1 miss→local LLC/DRAM，不访问RL1。
3. remote-home，same-cluster RL1 hit/miss。
4. remote-home，other-cluster RL1 hit/miss。
5. 两CL1→同RL1 line合并，分别fill两个CL1。
6. RL1 eviction、CL1 eviction、不同sector交错返回。
7. request/response xbar同时拥塞，验证独立带宽。
8. store/atomic保持已声明baseline语义。

### 出口

- `rl1_local_home_lookup=0`、`rl1_local_home_fill=0`。
- 每个root transaction阶段单调前进，不循环、不跳过必需fill。
- `remote_memory_fetches ≤ rl1_misses`，合并时严格小于；无重复remote fetch。
- 所有intra/inter-cluster路径计数与owner位置吻合。
- MINI 下 TLS、L1.5、Shared、baseline 四模式均完整drain。

## P8：压力、死锁、资源与回归封板

### 工作

- 建立统一 watchdog，只有request完成、queue移动、MSHR释放、network传输或core提交算结构性进展。
- deadlock dump输出每个endpoint tag/MSHR、每级queue、ring link、live transaction阶段和最老年龄。
- 运行同line fanout、不同sector、满MSHR、满fill queue、双向ring拥塞、writeback压力和多kernel flush/invalidate。
- 用CFD、2MM/3MM、CUTLASS等较长trace做压力测试。

### 出口

- 所有 directed/real trace 正常退出，无live transaction、MSHR、network flit和pending scoreboard。
- 请求、response、fill、completion、write ack逐层守恒。
- 不允许以扩大到“几乎无限”的queue/MSHR通过测试；压力配置使用论文值或明确缩小值。
- debug assert与release结果的架构统计一致。

## P9：已有 workload 机制矩阵与论文规模

### P9A：已有 workload 机制矩阵

在TLS-MINI上运行：baseline、Shared、L1.5、TLS × dynamic/frozen placement，至少覆盖SRAD trimmed、CFD 097K、GEMM、FDTD2D。

输出：

- cycles/IPC；
- CL1/RL1/RDC hit与MSHR merge；
- local/remote hierarchy频率；
- ring bytes/hops/queue occupancy；
- request read latency直方图；
- final service level；
- ICL与性能提升相关性。

此阶段只验证机制趋势和异常：不设置逐应用必须 `TLS>L1.5>Shared>baseline` 的硬门槛。若结果反常，先用路径/压力统计解释，不能调参数追论文数字。

### P9B：TLS-PAPER

- 切换4×64 SM论文配置。
- 用短trace和裁剪trace先验证资源规模、内存占用、无数组越界。
- 再运行完整可信workload；缺失SPMV/SHOC/Mars不阻塞已有项，但汇总必须标注样本数，不能与论文九应用平均值直接比较。
- dynamic first touch为主结果，frozen baseline map为控制结果。

### 出口

- Fig.8/10/11 的统计定义和脚本固定、可重跑。
- per-app normalized IPC平均方法和paired 95% CI明确。
- 所有图表可回溯到双仓commit、配置、trace/page-map hash和原始输出。

## 8. 全阶段不变量和守恒式

### 8.1 请求生命周期

```text
logical_requests_accepted
  = logical_requests_completed + logical_requests_live

结束时：logical_requests_live = 0
```

reservation failure只是未接受的重试，不进入accepted；同一request重试不能产生多个sidecar。

### 8.2 Cache/MSHR

```text
mshr_waiters_added = mshr_waiters_completed + mshr_waiters_live
fills_accepted     = fills_consumed + fills_queued
```

每个endpoint独立统计tag access、data/fill port、bank、MSHR和miss queue占用。

### 8.3 网络

```text
injected_flits = delivered_flits + queued_flits + in_flight_flits
```

request/response、方向、link和fabric分别守恒；不能只检查全局总和，因为方向错路由可能仍满足全局相等。

### 8.4 服务层级

每个完成的global read只能归入一个最终层级：CL1、RL1/RDC、local memory hierarchy、remote memory hierarchy。endpoint距离另行统计为self/intra-cluster/inter-cluster，不与page home混在一起。

### 8.5 容量

每次运行打印并校验：

- baseline：8 MB private L1/chip + 4 MB LLC/chip；
- Shared：8 MB CL1/chip + 4 MB LLC/chip；
- L1.5：8 MB private L1/chip + 2 MB RDC/chip + 2 MB LLC/chip；
- TLS：6 MB CL1/chip + 2 MB RL1/chip + 4 MB LLC/chip。

若开发用MINI按比例缩放，输出同时标出绝对值和相对论文比例。

## 9. 统计与日志约束

- 默认只保存聚合counter和有界histogram，不保存无界per-request日志。
- directed/debug模式允许指定UID范围或前N笔transaction详细trace。
- latency时间戳至少含：core accept、CL1 lookup、RL1 lookup、memory inject、memory return、RL1 fill、CL1 fill、requester complete。
- 同时输出sector-level和root-transaction-level计数；图表脚本必须显式选择一种。
- page-map dump、live transaction dump和deadlock dump均带版本号。
- 任何counter名称变更都递增`TLS_STATS_VERSION`并同步解析器测试。

## 10. 已知假设与推迟项

首轮机制实现允许以下显式假设：

- CL1/RL1先以`modulo-line`映射，保留selected-bit/xor接口；作者给出bit mapping后切换主配置。
- store/atomic沿用当前baseline策略，不自行发明新coherence协议。
- inter-chip 768 GB/s先按配置的bytes/cycle解释，并至少做“每链路每方向”和“聚合”两种敏感性；未获作者确认前不隐藏选择。
- 面积/功耗不作为Accel-Sim阶段出口。

以下内容推迟到机制封板之后：

- 下载/采集缺失的SPMV、SHOC、Mars trace；
- 6/8 chip XY网络敏感性；
- 64/256 KB L1和2/8-SM cluster敏感性；
- 精确面积、功耗和物理时序。

## 11. 审阅时需要确认的决策

开始实现前确认以下四点即可：

1. 同意双分支/双worktree，从干净framework和GPGPU-Sim `dev`起步。
2. 同意先TLS-MINI机制封板，再TLS-PAPER；MINI数字不与论文对比。
3. 同意首轮CL1/RL1使用显式标注的`modulo-line`，dynamic first touch为主、frozen map为控制。
4. 同意当前主开发集为directed + SRAD trimmed + CFD 097K + PolyBench GEMM/FDTD2D，缺失workload后补。

在本审阅稿获批前，不创建实现分支、不修改模拟器、不启动TLS仿真。
