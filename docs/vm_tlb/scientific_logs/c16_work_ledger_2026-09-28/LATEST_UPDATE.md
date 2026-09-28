# C16最新增量：Lane 8结果审查与Lane 7派发状态

日期：2026-09-28。

本文件补充原工作总账快照`1f999e62000178feb7e657a79cdf9e5a64db182f`，不重写原实验或历史负结果。原`WORK_LEDGER.tsv`保留70条；本次新增记录EXP06见`WORK_LEDGER_ADDITIONS.tsv`。两表合并为71条逻辑工作记录，不是71次独立实验。原VALIDATION.json只适用于其注明的历史内容版本，不代表本增量重新运行了历史实验。

## 1. Lane 8：接受并关闭

- 节点：174-new，CPU-only。
- 任务：`C16_MOE_WARP_REQUEST_GEOMETRY_SCREEN_174NEW_V1`。
- 分支：`hrl/c16-moe-warp-request-geometry-screen-174new-v1`。
- Commit：`2afdf832273f31df496d7424ec6b426c6aabdfc3`。
- Tree：`304f14bfadbf2feb60d3c553a3cdf680411b01ac`。
- Parent：`08536be9940590be101c7f5bac2117ba82056db5`（accepted three-lineage consumer）。
- Git比对：准确前进1 commit、behind=0；报告分支与结果commit相同。

接受的标签：

```text
WARP_REQUEST_GEOMETRY_CHARACTERIZED_SCOPED
ROLE_EVENT_SHARE_DIFFERS_FROM_SECTOR_PROXY_SHARE
FAMILIAR_BROADCAST_WITH_NO_NEW_OPPORTUNITY
```

状态：`ACCEPTED_SCOPED / CLOSED / NO_NEW_NATIVE_AUTHORIZATION`。

### 结果与计算口径

L是同一动态warp record内的lane逻辑字节之和；U是该record的字节区间并集；C32是32乘以该record所覆盖的sector数。跨record/跨shard只能累计明确标记的几何量，不形成虚构的时间序列或VA并集。

| lineage | input的full-warp结构 | weight的full-warp结构 | weight/input sector-proxy份额 |
|---|---|---|---|
| Q30 | 32个不同U16起始地址，覆盖32 sectors | 同样为32个不同U16地址、32 sectors | 49.9675% / 49.9675% |
| DeepSeek | 32 lanes、16个U16起始地址，覆盖1 sector，L/U=2 | 32个U16起始地址，覆盖2 sectors，L/U=1 | 66.4151% / 33.2075% |
| OLMoE | 32 lanes、16个U16起始地址，覆盖1 sector，L/U=2 | 32个U16起始地址，覆盖2 sectors，L/U=1 | 66.3212% / 33.1607% |

剩余为output份额，因此表内两列不要求合计100%。旧weight/input lane-event约各半的结论仍成立，本次补充的是它们并不必然具有相同请求几何。

### 不能扩写的结论

- Q30的U/C32=6.25%是单record sector覆盖填充率，不是DRAM有效带宽利用率，不能写成93.75%的DRAM浪费。
- DeepSeek/OLMoE的重复地址是两lane共享同一U16地址的熟悉模式；该项没有提供新broadcast机制的动机。这个说明不把Q30也称为broadcast。
- C32不是实际L1/L2请求数、cache miss数或DRAM字节数；没有时序与命中证据就不将覆盖proxy升级为瓶颈。
- 三模型仍耦合于cuBLAS gemvx家族；DeepSeek/OLMoE为template parameter 6、Q30为7。几何差异不等于已证明由该参数单独引起。
- 全部243 selected paths/lineage具有width authority，G1在当前静态集合和动态记录中覆盖100%；并不代表完整模型所有访存路径都被覆盖。
- G2未执行：`G2_NOT_AUTHORIZED_BY_AVAILABLE_SCOPE`。不能把G0/G1完成写成跨warp共享分析也完成。
- 关闭的是本screen作为新native/broadcast机制的推进依据，不是证明Q30或所有MoE不再有优化空间。

### 本轮审查深度

ChatGPT本轮读取了commit差异、Git parent/tree、README、SCIENTIFIC_INTERPRETATION、计算代码中的width/interval-union/sector计数与streaming路径，以及validation记录。没有SSH验证109/174/164现场，也没有重新读取全部node164 raw、重新运行单元测试或重算全部shards。raw/ACK/manifest/历史计数闭合采用此次consumer已提交的receipt；不把源码审查冒充第二次全量raw重算。

## 2. Lane 7：用户明确尚未下发下一任务

最新用户说明：`LANE7_109_SPLITK_MEMORY_STATE_QUEUED_HANDOFF.md`尚未发给109上的Codex，等待当前OLMoE任务完成后由用户发入。

因此调度状态是：

| 节点/Lane | 任务 | 状态 |
|---|---|---|
| 174-new / Lane 4 | 既有R0/M1/diagnostic长跑 | 保持原任务；不读取partial，不更改运行 |
| 174-new / Lane 8 | warp request geometry screen | 已接受并STOP，不自动新增实验 |
| 174-new / Lane 6 | 后续OLMoE独立consumer | 保留窗口；等待producer交付及新指令，不视为已启动 |
| 109 / Lane 7 | OLMoE routing provenance multiround | 用户报告的当前任务；本轮没有现场查询运行状态 |
| 109 / Lane 7 | split-K × memory-state interaction | `HANDOFF_PREPARED_NOT_DISPATCHED`，不是已排入Codex自动执行队列 |

不向Lane 7插入新Goal，不因为GPU lock暂时可用就启动下一任务。当前OLMoE结果合法发布且锁释放后，用户再下发后续指令。所有未来CUDA执行仍须使用既有`/data/c16/locks/c16_gpu_campaign.lock`。

## 3. 新来源S43（均为固定commit读取）

Repository：`swayhrl/accel-sim-framework`；ref：`2afdf832273f31df496d7424ec6b426c6aabdfc3`。

- `docs/vm_tlb/review_packs/C16_MOE_WARP_REQUEST_GEOMETRY_SCREEN_174NEW_V1/README.md`；Git blob `24a24ae12ecc4b561f7e921ed05edc848f5fcedb`。
- `docs/vm_tlb/review_packs/C16_MOE_WARP_REQUEST_GEOMETRY_SCREEN_174NEW_V1/SCIENTIFIC_INTERPRETATION.md`；Git blob `ffe0fd84ba827bb9a63617a32100b8aab89ecced`。
- `docs/vm_tlb/review_packs/C16_MOE_WARP_REQUEST_GEOMETRY_SCREEN_174NEW_V1/AUTHORITY_AND_VALIDATION.json`；Git blob `6997287653bbd33217b07341844eb6d0d58967c4`。
- `util/vm_tlb/c16/warp_request_geometry/analyze.py`；Git blob `5c1e982380503f4137f1d1fd7541ce758c7466a7`，已读计算、width、authority与streaming相关段落。

调度状态另以本轮用户明确说明为来源，不从远端存在handoff推断已经派发或执行。此增量不授权新GPU实验、重抓、缓存机制或full timing，不改变Lane 4/M1F gate。
