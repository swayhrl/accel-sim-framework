# 支持域、反例和验证边界

## 现有平台与候选域分别陈述

原 4080 模型统一 data/shared 为 128KiB；shared 选项 0/8/16/32/64/100KiB，每 CTA 上限 48KiB。原 native/baseline-only 证据保留原支持域。当前全域 fixed80 DTC 无合法布局：S=64 已使 L1=64<80；S=100 时 L1=28<80，尚未为普通路径留一字节。无论分多少 bank/端口，该矛盾都成立。

A 的字节可行域为 S∈{0,8,16,32}，C=48-S≥16；128 mappings、640 physical lines、IO PIB256/OO PIB128、whole-line128B、LD/ST multiplier1。可复用 R1 内存生命周期及原路由；不能将 R1 的原平台资格自动移植到 76-SM 现代平台。合法性还要求完成下面的 epoch、服务和现有 ISA gates。**本报告没有准入任何现代 DTC kernel。**

629 个固定成员全部满足 A 的字节条件；这不授权把平台 shared 最大值改成 32KiB。六个已审计 pilot kernel 中 BICG×2、Btree×2、2DConvolution 无 shared，80/48/0；Hotspot1 为 80/16/32，其原 CTA cap=6、resident shared=18KiB。BICG 的 grid clamp 后 cap=1。算式不改变这些 CTA cap；Hotspot 的格式/语义 HOLD 保持，不能用容量 PASS 放行。没有读取新 trace，也未推断未审计程序或新的输入形状。

## 候选 A 的 epoch 前提

每个 SM 一个分区描述符，含 pool 范围、尾部各 bank 的 C/S 行界限、active C ways、mode、epoch identity。现有 `max_cta` 是配置级变更，不能直接作为每 SM 的完整所有权分配器。

首次构造必须限制普通 cache 的最大可用容量为尾部 48KiB，而不是保留 128KiB 普通容量加 80KiB 池。每 epoch 的普通有效行数为 4×ways，DTC 固定640行；尾部的 inactive conventional rows 实际成为 shared rows，不能在普通 cache 中仍可命中。对 `tag_array` 最大几何/析构使用同一上界，避免构造/销毁范围不一致。`set_assoc` 会改变 set/way 索引步幅，因此切换前的状态处理不能省略。

重新分区前必须证明该 SM 没有活的 PIB、部分分配、lower candidate/inflight、响应 FIFO、普通 MSHR/latency queue、未确认 store/atomic、未结束 shared CTA 或 pending writeback；若尚有请求，维持原 epoch 并反压，不迁移身份。不仅仅检查 PIB=0：tag-visible retained data 可以继续占据物理槽。缓存清退/初始化要与原 kernel 边界、flush/write policy 一起验证，不能在活返回时重建 frontend。现有 `ldst_unit::flush/invalidate` 不重建 DTC frontend，此处需要新增且审核清退语义。

单 epoch 的 CPU 地址检查没有证明混合 kernel 同 SM、跨 SM 同时不同 S、连续 kernel 分区切换或 preferred-cache-config 的正确性。不得把它们默认为合法；也不得擅自关闭 concurrency、固定 shared reservation 或清空缓存来掩盖问题。任何执行范围限制必须显式登记并批准，未满足则留在 baseline-only。

## 唯一备选 B：动态缩池，不推荐本轮实现

为不删除 64/100KiB shared，尝试保留 C≥16KiB，并令 P=min(80,112-S)：

| S KiB | P KiB / physical lines | C KiB | 变化 |
|---|---|---|---|
| 0/8/16/32 | 80 /640 | 48/40/32/16 | 与 A 字节相同 |
| 64 | 48 /384 | 16 | 缩池；R1 进度资格不可继承 |
| 100 | 12 /96 | 16 | 缩池；原128 mappings下已有阻塞反例 |

CPU oracle 使用 Core6fba0136 原类及 finite_service=true。串行访问 line0..95（address=line×128），每次返回、退休后再开始下一个；每 set 3 个映射，96 个槽全为 tag-visible，无活引用/在途请求。line96 的 set0 有空闲第4 way。IO 的 `access` 在选择/替换 Tag 前要求 free slot；OO 在没有 free slot 时只能回收**有效且 ref_count=0 的被选 victim**，空闲 logical way 不满足这个条件。因此两者都返回 NO_FREE_LINE，后续相同访问不改变状态。640 行对照成功。

这说明 B 不能只缩 `physical_lines` 并继承原支持域。缩 Tag（例如96以下）、强制驱逐其他映射、改变 victim 选择、降低 PIB、全或无分配/rollback、绕过 DTC 都会分别改变覆盖/替换、生命周期或路由；即便缩 Tag 也仍需单独验证部分分配和 IO 前进条件。384 行未在本轮证明安全；96 反例也不能被反向表述为“至少128/129/160行就足够”。B 需要新 pool/Tag/PIB/progress 共同合同与独立验证，不作为本轮短期工程。

## 不能自动采用的处理

- 额外208KiB：已被固定容量决定拒绝。
- 将 `unified_l1d_size` 改成48：破坏真实统一预算的意义和64/100 shared；原128KiB cache字符串与新max-size比例还涉及解析断言。
- 删除普通数组或把所有写/atomic改走DTC：原路由/存储/响应所有权改变。
- S>32 自动 fallback/off：改变被测机制覆盖，不能合并为统一 DTC 行；现有授权没有自动混合模式。
- 将最大 shared/CTA cap 降低：改变原平台合法输入及 occupancy。
- 将4×1R DTC bank 当4个任意地址读口：232/256分布违反R1；若增加冲突必须重新注册服务时序。

## 获批后最小验证顺序（本轮未执行）

1. 默认 OFF：检查 Core/framework source diff，默认参数和布局分支完全隔离；复用原 NN OFF 等价基准，并新增一个 shared baseline 以覆盖新 allocator 的默认旁路。
2. CPU geometry/ownership：扩展本包地址检查到分区对象，覆盖每个合法 S、边界 slot、set/way 重索引及构造/析构上界。非法 S 必须在配置/工作负载准入时明确拒绝，不能启动后 fallback。
3. 最坏端口和计数：同 bank 四个 DTC sector read+一个 refill，普通 data/fill 和 shared 同 word bank 的并行；新增普通访问尝试和fill每cycle各一次的显式配额，覆盖FIFO内多个普通返回与四个bank同时就绪，所有配对modern arms采用同服务版本；重复LD/ST调用不刷新配额、失败不消耗完成ownership、WB重试不重复collect。保留R1 lookup/readiness/waiter/retire时序及 Ref/generation 负测。
4. 分区边界：从 S0→S32→S0 切换，包含 retained mappings、晚返回、dirty普通行、full MSHR、store ACK、atomic和旁路；活 epoch 不可被覆盖。混合 kernel 并发若仍属目标支持域，必须有定向压力检查，不能跳过后宣称支持。
5. 原路由与完成：cacheable load→DTC；store/atomic/`.cg`/shared 保持各自源路由；每条完成一次，Ref/事务/返回守恒、CTA共享分配不减、无额外读写丢失。SASS只有结构/时序不能提供的返回值验证需另有证据，不能用退出0替代。
6. 仅在资源/域合同获批、上述局部检查通过且格式/ISA独立准入通过后，由A登记新的 future attempt identities、端口/metadata向量和baseline可比性，再考虑单个pilot；性能行不由本窗口启动。不能复用新旧binary为同一attempt。
