# Lane V：冻结源码语义事件图

审查基准：Core `6fba0136f8465b59fe5858a950fa39efb265f654`；Framework **build** `18a68dcccd795f1b6cda75504e9450d00c9cee02`。Lane V 文档分支从该 build 提交建立，文档 HEAD 不冒充 build。源码只读，无 Core 修改、无完整模拟器运行。输入 blob/SHA256 与小型检查见 [SOURCE_SHA256.tsv](SOURCE_SHA256.tsv)、[CPU_CHECKS.json](CPU_CHECKS.json)。下列行号全部针对这两个冻结提交；`C:` 表示 Core，`F:` 表示 Framework，均为仓库相对路径。

**判定：冻结 Core 没有把 source-defined L1 invalidate 传入独立 DTC Tag/physical 状态。普通 store/atomic/bypass 也没有自动撤销 DTC Tag 的调用。写后 load 数值一致性是 UNPROVEN；不能用 ordinary flush、sidecar 完成或 PROXY_FENCE 退休补证。**

## 1. 冻结与 A/T/U 发布证据

仅通过 Framework Git 对象和远端 refs 审查其它 Lane，不进入其工作目录/raw/锁目录，不取得执行权。A/T/U 只是既有模型范围的证据，不是 K1 或全 ISA 正确性证明。

|证据|固定发布锚点|本次核对与边界|
|---|---|---|
|A|`f5c37d6edcce832a72cb0830021bffa78df6cc13`；`docs/dtc_l1/iscas2027/service_closure_174_v1/review_pack/final_closure_v1/`|README、integrity、source-policy/preservation、open-science 文件已读/哈希；原44行 41 numeric strict PASS、3 Hotspot HOLD，条件派生输入另列。保留原格式、modern、native/PPA边界。旧 checkpoint ACTIVE 字样是历史状态，不升级或重启。|
|T|`f520a445436b57c0a0f2494fb858a1636f04d2bc`；`docs/dtc_l1/review_packs/DTC_TAG_PILOT_V1/`|报告及 scope/发布回执已读/哈希；7点的 strict 与 T1-C 选型仅限 timing/accounting。内容回读回执绑定 `303019529edddd2727cdc88138fd1a9be262d23d`，不是伪称绑定最终元数据 HEAD。数值 load 正确性/PPA 未提供。|
|U|`16e56912cfd02f2311a1603a29415dee829fd495`；`docs/dtc_l1/review_packs/DTC_T1C_HOLDOUT_V1/`|保留真实后台 admission：authority PID2132794/start_ticks898867525，passive monitor PID2238870/start_ticks899502188；这是历史证据，不是本次检查其存活。发布报告已含 DWT2D/BICG 两点终态；内容回执绑定 `2071c6e582de1a9ab2afe1b517b28bcb4f6066ee`。PUBLICATION_CONTRACT 仍把最终外部收据另列，本审计没有进入该 raw root 重做终态验收。|

远端 `ls-remote` 首次读到 U=`d38e362d8cfd058484c7dc17a9a1887defd1bc56`，随后正常 fetch 读到上表 U；固定使用 fetched `16e56912…`，没有把移动中的 HEAD 当静态身份。A/T 远端与上表一致。U 的 SOURCE_IDENTITY 与 FAST64_OO 配置明确绑定上述 Core/build；其配置 `-gpgpu_flush_l1_cache 1`、`-gpgpu_gmem_skip_L1D 0`、ordinary `S:32:128:4,L:T:m:L:L,A:512:8,16:0,32`。配置存在不证明 DTC 失效已经生效。

## 2. 三类不同的边界事件

|ID|入口与条件|调用链/作用域|冻结行为与不能推断的内容|
|---|---|---|---|
|E-KERNEL|C:shader.cc:5484–5527，CTA 最后线程退出，`dec_running()` 后 `!kernel_more_cta_left(kernel) && !kernel->running()`|`set_kernel_done(kernel)` → C:gpu-sim.cc:1027–1043，写 end_cycle、finished queue、清 running slot|这里没有 `cache_invalidate()`；实际 kernel 退场与下行排空、cache失效是不同事件。|
|E-IDLE-CLUSTER|C:gpu-sim.cc:799–801 注册 `gpgpu_flush_l1_cache`，默认 **0**；cycle:2515–2527 在 issue_block2core/decrement_kernel_latency **之后**|开关=1 且 **该 cluster** `get_not_completed()==0` 才调用其 `cache_invalidate()`；shader.cc:7471–7475 是该 cluster 所有 SM 的 not_completed 求和|不是按退场 kernel ID 广播；同 cluster 其它 kernel/SM 未完成会阻止该 cluster 条件；别的 cluster 可先触发。idle 条件可逐 cycle 重复触发，甚至不是刚发生 kernel end。条件本身不检查 DTC/ordinary inflight 排空。|
|E-CONFIG|C:gpu-sim.cc:1741–1755|`set_cache_config` → `change_cache_config`；所选 cache status 不同时遍历所有 clusters → invalidate，然后初始化配置|与 flush_l1 开关条件不同；不是任意两个 kernel 之间必触发。|
|E-MEMBAR|C:shader.cc:1134–1135、6875–6889|普通 MEMORY_BARRIER_OP 设置 warp membar；等待函数见 `!scoreboard.pendingWrites(warp)`，clear_membar，且 `flush_l1()` 才调用本 SM `cache_invalidate()`|这是源实现的判据；注释声称等 ack，但代码查询 scoreboard，不能据注释证明所有 store ACK 已收到。它不是 PROXY_FENCE。|

三个 source invalidate 入口的后半链：C:shader.cc:7553–7555（cluster 全部 SM）→ 6553（SM）→ 4012–4014（LDST）→ **`m_L1D->invalidate()`**。E-MEMBAR 从 SM 入口进入。此版本没有 DTC invalidate/flush API，也没有在该调用链重建 frontend。

ordinary 两阶段：C:gpu-cache.cc:1268–1285 的 invalidate **请求**先置 `m_invalidate_pending`；只有 `!conventional_miss_lifecycle_active()` 才执行 Tag invalidate。C:gpu-cache.h:1474–1476 只查 ordinary miss_queue、extra_mf_fields、MSHR；ordinary `cycle()` 在 gpu-cache.cc:1265 重试退休请求。这不是 DTC drain gate，也不是收到请求时立即关闭所有 ordinary 命中的证明。

另一条 `cache_flush()` → LDST `flush()`（C:shader.cc:7548、6551、4007–4009）只调 ordinary `m_L1D->flush()`。C:gpu-cache.h:1361 转 `tag_array::flush`；gpu-cache.cc:464–476 只把 modified entries invalid，保留 TODO writeback；`invalidate`（478–486）遍历所有 sector 状态。不能把这两种 API 或其中任意一种与 DTC 清空等同。LDST 两入口都未检查 `m_L1D` 空指针；禁用/空 L1D 组合不据此宣称受支持。

## 3. cacheable load 与独立 IO/OO 生命周期

入口 C:shader.cc:3880–3931：非空 global/local/param_space_local，有 active/access；CACHE_GLOBAL (`.cg`)、L1D空、global skip 且非 CACHE_L1 划入 bypass。atomic 优先于 generic load 分类，不进入 DTC mergeable read。DTC frontend 在 LDST constructor 的 4350–4359 独立创建；ordinary L1D 是另一个对象。grid初始化 C:gpu-sim.cc:1499–1522 → cluster reinit（shader.cc:7462–7464）→ core reinit（518–542）仅重置线程/warp/占用状态，不重建LDST/frontend；没有逐 kernel 的 DTC reset 调用。另有强制stop路径 gpu-sim.cc:1046–1052 也调用set_kernel_done，不能把一个finished记录当作自然完成或失效证据。

|状态转移|IO（C:dtc-l1-common.h）|OO（同文件）|
|---|---|---|
|admit/partial|181–185 admit，237–295 access；已拿到的 reference 保留，无 rollback|567–622 access，attach_reference:888–899；每个 live PIB 每个 distinct physical reference +1，不按 lane 加计数|
|visible hit|243–254 记旧 identity，ready/pending 命中，不新建 lower|573–578 附加 Ref；若 pending 则加入 `{slot,slot_generation}` waiter 并加 pending_dependencies|
|new miss/tag victim|273–289 找 free physical；旧 victim physical 放入**替换者** `release_on_retire`，旧请求不取消；新 allocation generation++、ready=false、安装新 Tag|594–618 旧 physical.tag_valid=false；Ref=0 即 release，否则延期；新 physical 置 allocated/visible、ready=false、generation++，再 attach Ref|
|return|298–335 旧 identity 检查；finite 时排入 cycle+1 队列再 ready|628–685 generation/allocated 检查；finite metadata 每 cycle 最多4 waiter；未处理完保持 ready=false；中途 late merge 追加同 generation waiter；全部完成才 ready=true|
|retire|354–360 FIFO head ready，释放其 release_on_retire，再 pop；没有 OO 数字 Ref 或 waiter 表|724–748 selected UID ready，逐引用 Ref--；仅 `!tag_valid && Ref==0` release；否则 Tag-visible 数据可继续保留|

IO 的 TagValid 是 m_tags[].valid；它没有 physical.tag_valid/Ref 字段，不能照抄 OO 的 clear-bit+Ref==0 算法。其 FIFO 保护依赖“替换者退休晚于旧消费者”，source invalidate 没有天然替换者，见 [K1合同](K1_SEMANTIC_CONTRACT.md)。

返回路由：C:shader.cc:3140–3176 / 3451–3483 用 request UID，必要时 original/root UID 查 inflight；核 line address/expected sector/new sector，whole-line 收齐0xF（sector模式用自己的 mask）才对**保存的** record.physical 完成并关闭 lower credit、erase inflight。不重查当前地址 Tag。response FIFO 先按 DTC ownership 分派（5013–5046），再 ordinary fill/WRITE_ACK。有限 refill 接纳、lower credit 归还和 frontend metadata ready 是不同时间点，不能 erase inflight 后就认为无 pending service。

退休还要经过全引用接纳、finite collect、operand collector writeback grant，才关闭 pending-write/scoreboard，最后 frontend retire/release（3217–3266、3523–3589）。WB失败保持引用，不可提前回收。generation 保护重用身份；它不表示数据版本/coherence epoch。

## 4. store / atomic / bypass / fence

M4 admission（C:shader.cc:2621–2655）给独立 PIB sidecar **一个 external dependency，零地址引用**；complete（2658–2680）只标 source_completed、撤销 external dependency。IO按FIFO、OO按ready与fence过滤退休 sidecar；不重复执行 store/atomic/load。

* Store：memory_cycle 走 ordinary cache 或 bypass。ordinary WB/WT/WE 分别改自己的 modified/byte mask、发送write、或自身sector invalidate（C:gpu-cache.cc:1551–1631）；no-write-allocate miss 只发 write（1919–1932）。它们没有修改独立 DTC Tag。**sidecar completion 在 store退出 dispatch pipeline 的 5307–5310**；真正 WRITE_ACK 由5083–5089→6937–6943减 outstanding store 计数，不能把前者说成每笔 ack 后退休或数据全局可见。
* Atomic：3913 优先分类，不走 IO/OO read merge；保留原 cache/bypass 与下层 atomic 路径。ordinary read-hit atomic 置自身 MODIFIED（gpu-cache.cc:1939–1955），不能使 DTC 同地址 Tag 无效。全局写回减少 atomic count（shader.cc:4582–4585）；sidecar在 source writeback_complete 后完成。F:trace_driven.h:65–75 显式 `should_do_atomic=false`，trace replay 不提供完整数据副作用/数值证明。
* Bypass：`.cg`/skip/空L1路径发原 mem_fetch（3933–3981），不查询/分配 DTC Tag，load在原写回路径关闭 external dep（4523–4529、4617–4618）。bypass 完成本身不会刷新旧 DTC cacheable 同地址映射。
* PROXY_FENCE：5205–5228 只支持 async proxy，PIB admit 成功才入 LDST pipeline，满时保持 dispatch backpressure。shader.h:2032–2036 设置 `m_fence_async`；1833–1839 阻 shmem/SYNCS/TMA load 的 source issue，非全局 load/store coherence gate。WB_CLIENT_FENCE（4656–4678）在无后续 pipeline async fence 时清 flag；随后 source WB成功→observe_complete 关闭 external dep；sidecar退休再移除其 OO同warp阻挡。
* OO过滤：2683–2707 对 ready candidate 搜索**仍在PIB内的 older same-warp PROXY_FENCE**，有则不选择。它不等价于阻所有年轻指令接纳/发下行，不阻其它 warp，也没有“fence自身必须等待所有更老DTC消费者”的对称条件。不同warp可继续退休；IO自然FIFO。regular FENCE_OP 在此 LDST路径 assert不支持，不与 MEMORY_BARRIER_OP 混称。

F:trace_driven.cc:715–720 只明确解析 `FENCE.VIEW.ASYNC.S` 为 ASYNC_SHARED_CTA；不能从枚举存在外推所有proxy kind均可由冻结trace到达。F:trace_driven.cc:1115、1126–1155 从trace设置PC/地址并生成访存，不能证明architectural load读值。

## 5. 审查结论的层级

**结构身份安全（有界支持）**：Tag victim后旧physical/generation、OO Ref/shadow、waiter slot generation、有限late merge、最后引用回收与对应小型测试相互支持；尚无 source invalidate 的 DTC 实现或验收。

**时间模型（有界支持）**：Tag 1cycle/II1、有限refill/4 waiter更新/collect/单退休、sidecar lifecycle是明确软件模型。失效遍历/带宽/与同cycle lookup线性化尚未实现；不能由软件接口推真实端口/PPA/同频。

**architectural load 数值正确性（UNPROVEN / STOP-CLAIM）**：header只存地址映射和ready/引用元数据，没有数据payload；trace replay没有逐load期望值比较。`L(x)→S(x)→L(x)`、atomic写同址、跨kernel producer-consumer、多SM共享、release/acquire等不能由 balance/terminal strict/PROXY_FENCE代证。矩阵逐项见 [WRITE_VISIBILITY_RISK_MATRIX.tsv](WRITE_VISIBILITY_RISK_MATRIX.tsv)。
