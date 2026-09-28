# C16 LR07探索：174立即可下发 + 109串行队列

日期：2026-09-28。本文是任务分配/排队记录，不是实验已经开始或完成的证明。

文献本轮：`hrl/c16-chatgpt-literature-notes-v1@b0533583a6207a48cd4fa309e8dc4d925f20adce`，README与LR07。

## 调度表

| 优先级 | 节点 | Lane | 任务 | 状态 |
|---|---|---|---|---|
| 主线 | 174-new | 4 | 既有R0/M1/diagnostic reuse-window长跑 | 原样保持，不读partial，不修改/停止 |
| 当前GPU优先 | 109 | 7 | OLMoE routing provenance multiround | 按原协调合同完成，本轮不改任务 |
| CPU并行 | 174-new | 新8 | MoE warp request geometry screen | READY_TO_DISPATCH，可独立执行 |
| GPU下一项 | 109 | 7 | split-K × memory-state interaction | QUEUED_NOT_STARTED；当前OLMoE任务合法终止/发布/释放锁后才能执行 |

Lane6留给OLMoE新producer的后续独立consumer，不被Lane8占用。Lane1/2/3/5现有closure保持。新任务均不授权M1F或新的full timing simulation。

## 入口

- [Lane8 / 174-new handoff](LANE8_174NEW_WARP_REQUEST_GEOMETRY_HANDOFF.md)
- [Lane7 / 109 queued handoff](LANE7_109_SPLITK_MEMORY_STATE_QUEUED_HANDOFF.md)

### Lane8要回答什么

旧三lineage的weight/input各半是lane事件数；既有C16WARP1已保存mask/CTA/warp/addr[32]，先在CPU上检查广播、并集和32B sector覆盖。width不明就限G0，不造字节结论。不要重抓NVBit，不拼跨shard chronology。

### Lane7下一项为什么不是重做旧split-K

旧split8/split1全局H1保持失败。本轮固定原A/B binary，只新增执行前访存状态维度，一次做完两operator×两arm×两状态的timing和限定NCU。检验的是状态依赖，不扫描更多split参数，也不单凭scratch allocation证明L2容量瓶颈。

## 当前GPU任务锚点

`C16_OLMOE_ROUTING_PROVENANCE_MULTIROUND_109_V1`协调commit：
`378df585cba4c21ac5864c374976e271ae44e9a3`。

不要中途让Codex切换当前Goal、重新加载模型或拉取新文件覆盖旧runner。可以将本目录登记为下一任务；当前任务结束并释放`/data/c16/locks/c16_gpu_campaign.lock`后再续接。

## 证据与授权边界

source锚点：
- three-lineage consumer `08536be9940590be101c7f5bac2117ba82056db5`；
- native split-K producer `0e88faa28c9066b48e394dce657d7a16e6332a32`；
- work ledger `1f999e62000178feb7e657a79cdf9e5a64db182f`；
- LR07 notes/index `b0533583a6207a48cd4fa309e8dc4d925f20adce`。

所有summary均需回raw/source验证。输出的negative或partial同样保留。不得把本队列写入已完成的70条历史实验记录；结果回来后才由project review更新其终局。

本轮ChatGPT完成的是文献阅读、已提交数据的算术解释、合同发布和回读；没有SSH调度、实际GPU执行、模拟器执行或node164 raw重算。
