# 可信 Weight Segment 的软件/运行时合同

本合同是 C8 对未来硬件模型的**最低需求**，不是对冻结实现的修改建议，也不授权启动
C5。它避免让 simulator object map、identity `SimPA` 或“永远 immutable”成为未说明的
硬件事实。

## 角色和 trust boundary

| 角色 | 可做的事 | 不可做的事 |
| --- | --- | --- |
| 模型 loader / framework | 报告已加载 Weight allocation 的候选 VA range、size、access intent 与生命周期事件 | 不能自行赋予“Weight”绕过翻译或保护的权限。 |
| privileged GPU driver / VM manager | 验证 allocation ownership、context、permissions、mapping form，安装/撤销 descriptor，驱动 TLB/Segment shootdown | 不能安装未验证、跨 tenant 或不具生命周期同步的范围。 |
| hardware descriptor table | 以 context+VA match，检查 valid/epoch/permission，产生已定义的 PA 或受控间接 translation | 不从 simulator object label 推断对象语义；不能在 epoch stale 时命中。 |
| telemetry object map | 离线 attribution 与审计 | 不是硬件 classification source，也不替代安全 provenance。 |

## descriptor 安装记录

每个 descriptor 必须由 driver 创建并原子绑定以下信息：

```
{valid, context_id/ASID/PASID, VA_base, VA_limit, granularity,
 mapping_kind, PA_base | mapping_root, permissions/attributes,
 epoch/generation, ownership, priority}
```

安装前的检查：

1. range 属于该 context 的经验证、已 pin 或受控的 Weight allocation；相邻对象、尾页和
   request-crossing 的行为明确（不能凭 object name 放宽范围）。
2. 选择并证明 mapping kind。若 `PA_base`，整个范围须有连续物理映射及适当 alignment；若
   mapping root，root 的访问时延、coherence、权限和失效必须建模。
3. descriptor permissions 不得比普通 GPU PTE 更宽；read/write/execute、privilege、memory
   attribute/ownership 的确切字段由目标 VM ABI 定义。
4. 为 context 发出不可复用的 epoch。匹配时 context、valid、epoch 和 permissions 都是
   hit 条件。

## lookup、端口与顺序

硬件应把 range match 看成普通 translation 的一个可计时前级，而不是免费 metadata read。
实现必须选择：

- per-SM replicas（每个 C4 cluster 至少 1 request/cycle）或共享多-bank/多port table；
- `Tsegment_service`、bank conflict、queue capacity 和 backpressure；
- L1-first、Segment-first、或真正并行时 L1 hit 是否可无等待返回；
- 请求在 Segment/ordinary path 间的唯一 completion ownership，防止重复 data/store/atomic
  side effect。

若按当前并行语义等待两者，`ready=max(TL1,Tsegment_service+queue_delay)`；因此 queue
对 L1 hit 也可见。若改为 L1-first/cancel，必须重新定义哪一个 PA/permission 结果有权
完成，以及 cancel 与 descriptor update 的竞态。这是 architecture decision，不能由一次
replay 隐式选择。

## 必须同步的 lifecycle / invalidation protocol

以下事件均先停止对相关 descriptor 的新有效命中，再 broadcast invalidate 或改变 epoch；
旧 epoch request 必须 drain、retry 或被安全拒绝，ack 后才可完成映射变化或 context reuse：

| 事件 | 运行时动作 | 硬件可观察保证 |
| --- | --- | --- |
| map/unmap/free 或 model unload | invalidate descriptor、Segment cache 和相关 TLB | 已释放 VA/PA 不被旧 descriptor 命中。 |
| PTE permission change | 更新 PTE 与 descriptor permissions，shootdown | descriptor hit 不比普通 PTE 宽松。 |
| page migration/remap | 停止命中，解除或更新 contiguous invariant/indirection，epoch bump | 不返回旧 PA。 |
| UVM CPU/GPU ownership / fault | revoke 或 pending 状态；普通 VM protocol 成功后再 install | ownership/复用与普通 VM 一致。 |
| context switch / ASID-PASID reuse | context-tag lookup，旧 epoch flush/ack 后才 reuse | tenant/context isolation。 |
| descriptor replacement / table resize | serialize update，优先保证 concurrent lookup 的 old/new atomicity | 一次 lookup 不混合两个 descriptor 版本。 |
| TLB shootdown | Segment table/cache 同属 shootdown domain 或有等价 epoch protocol | conventional TLB 与 segment path 不产生不一致翻译。 |

## 多模型、多租户扩展

descriptor capacity `N=1/4/16/64` 必须按 context 分配、quota/eviction 与权限检查，不能让
global table 用无 context tag 的 VA range 交叉匹配。每个 tenant 的 admission 应报告：
descriptor count、range coverage、mapping kind、pinning成本、lookup placement、更新传播和
overflow fallback。overflow/unknown 必须走普通 paging，不能静默复用另一 tenant 的 descriptor。

## C5 前可验证证据

在任何 architecture-labeled C5 replay 之前，至少需要书面批准并在模型中可观察：

1. 一种 PA mapping form 与对 range contiguity/indirection 的证据；
2. context/permission/epoch 字段和 map/remap/unmap/shootdown sequencing；
3. driver-controlled classification provenance，object map 仅 telemetry；
4. placement、ports、replication、queue/backpressure 和 L1-hit ordering；
5. N=1/4/16/64 capacity policy，以及 unknown/overflow fallback。

未满足时，现有回放可以继续作为 `SPECULATIVE_CANDIDATE` 的软件状态机探索，但不能回答
“合理、可实现且公平的 GPU translation architecture”这一 C8 问题。
