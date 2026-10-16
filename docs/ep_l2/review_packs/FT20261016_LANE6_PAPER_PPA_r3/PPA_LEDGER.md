# PPA 差分账 r3

原科学合同 `6c136e2a`；续行审阅 `a41bfb55`。原冻结代码账版本：Core
`126394be46b15f55b9756d43eb9ca9a9baae1c84`、Framework
`37dec04d223ae65167c5584e56887c74f6540d27`，发布 `02982b65`。
该旧版本的应用资格已被撤回。本表只复用资源合同、字段清单及参数化算术，
不证明旧实现遵守物理端口上限；修复后需按准确新 release 复核 delta。
这是模型与参数化成本账，不是 RTL 综合结果。

## 数据 RAM、latch 和共同下层数据承载

| 配置 | payload bits/slice | 数据阵列 KiB/slice | copy latch B/slice | 阵列+latch KiB/slice | 全芯片 MiB（阵列+latch） |
|---|---:|---:|---:|---:|---:|
| B16 / U_WB16 | 1196032 | 146 | 128 | 146.125 | 9.1328125 |
| B8 / U_WB8 | 1187840 | 145 | 128 | 145.125 | 9.0703125 |

共同 latch 为 1024 bits/slice、8KiB/chip，B/U 两边一致；它不属于
1168/1160 项 payload 分配空间，不计为可借用槽。以上仍不包含 metadata、
ECC/宏周边、下层 queue、线网或仲裁。

Lane-1 生产账明确下层需要完整 dirty packet 数据承载：L2→DRAM FIFO 的
128×128B=16KiB/slice（1MiB/chip），scheduler 的 128×128B=16KiB/channel
（512KiB/chip），为共同上限承载模型。它们不因软件 queue 储存指针而消失；
同包在相邻阶段的指针引用不重复算成两份数据。ReturnQ 的 192 项/channel
与边界 FIFO 的作用域分开；实际 sector/line packing、真实电路存储复用与
有效位尚需物理映射。共同下层模型未变，不能从 EP-L2 delta 中扣除它们。

## 代码—参数—物理未知三列

| 绑定当前代码字段/行为 | 参数化假设与可算成本 | 未知 RTL/工艺及差分规则 |
|---|---|---|
| `ep_l2_payload_store::slot`：allocation_role、status、owner、generation、pending_sector_mask、pins、ready_sector_mask | R0 有 3 种 allocation role、8 种 status；独立编码示例 2+3 bits，sector pending/ready 各 4；owner 若保存 full line key 为 A−7；generation G、pin K | 枚举 product 是否可压缩、owner 是否可复用 Tag/控制字段、读写端口；不可把容器布局当硬件编码 |
| `slot::versions[4]`、`ft_wb_record::expected[4]`、`m_ft_last_wb_versions` | 独立 version/reference 验证 sidecar，不属于重建的 128B payload 数值数组 | 软件审计不直接合成；真实数据 RAM 已在上表计数，ECC/版本化硬件若真实采用则另计 |
| Tag sidecar / `PayloadHandle {payload_id,generation}` | payload ID 11 bits，1024×11=11264 bits=1408B/slice；若实际储存 Tag generation 再加 1024G | B16 若同样 pointerized 则两侧共同；最终 Tag-array 合成映射和 generation 宽度未知 |
| `ft_wb_record {handle,born,expected}` 与 `m_ft_wb`，WAD 128、issue FIFO 128 | 每 WB 至少 P+G，取 G32 的保守表示为 43 bits/WB；128 项句柄字段 5504 bits=688B/slice；packet binding/state 另计 | `born` 是年龄统计、expected 是验证 sidecar；packet 控制 ID 宽度和状态编码待 RTL；不是无限 WB map，也不是 C 项控制上限 |
| `ft_replacement`：request/tag/phase/landing/victim/staging、dirty/wad/bound 等；每 slice 一笔前端 reservation | 若三句柄都显式保留：3(P+G)，再加 Tag index 10、phase 至少 2、标志及 key；128B copy latch 已单列 | saved slot 回滚可保留旧值或预览后延迟写；二者不能同时赠送免费 shadow RAM；具体寄存器和回滚实现未知 |
| slot pins / `m_ft_read_refs` | K=ceil(log2(max_refs+1))，每个 live payload 或实际消费者控制项计数；不是固定假设 6 就已证明 | 真实响应、fill 与 WB 引用最大值；公共描述符与 mem_fetch 控制 token 复用需要证明 |
| allocator：按 Bank class 选择、role/状态检查；相同 oldest-ready 四 Bank | bitmap N bits 或 free-list NP bits+control 为替代编码；不能无故同时相加；Bank token 为4Q_b(P+G+op+age+valid) | 多端口选择、仲裁 fan-in、队列深度和 critical path；C++ 扫描不是免费电路 |
| static source read / staging write / lower-send read | 每脏 line 三次 line-sized Bank 服务；合同要求同 Bank 按物理 GPU cycle 分拍；共享模式仅保留 send read，旧 R0 非零 memcpy offset 下曾违反该上限 | 实际能量需 macro read/write、latch/线网能量和各事件数；copy 消除不等于容量借用 |
| absorbed write、fill、descriptor response 的实际 Bank 请求 | 合同要求 B/U 同样支付；sector fill 占一次 line-sized 服务；新 physical_bank_clock 门槛需逐物理周期实测 | 最终 SRAM 端口/宽度与 pipeline 设计；不得赠送额外免费服务 |
| D512 描述符、普通 chain | 9-bit descriptor ID；显式 0..32 count 6 bits；链若 head/tail+valid 为 26 bits/chain | 请求路由/身份/sector/response state 共同保留；RO 不扣掉 requester descriptor 成本 |
| RO r3 `transactions::m_slots(payload_budget)`，按 payload_id 索引一 completion/物理项 | 绑定 `ddedbf0f` 模块配置 1168/1160 槽，示例 payload-sized 153-bit completion 已知字段为 22338B / 22185B/slice（G16、A48、E16 等算例）；不是 128 槽 | live transactions 同时受共享 D512 等边界限制，但不能将最大 live 数直接当已配置存储槽数。sparse 压缩须真实 allocator/lookup 设计；ordering、cursor、response fields 仍另计 |
| WAD/TVD 扩展（R0 尚未生产接入） | W=128；若每项加 P+G+state+sector+age，直接按字段计费；复用现有地址 key | TVD lookup 关联比较与额外读端口、retention，+1 cycle 非已证时序；served_sector_bytes 不是 DRAM avoided_bytes |
| RO whole-commandlist oracle | 离线分类、完整 commandlist/line 作用域、覆盖率与排除原因；epoch/key 表按真实容量另计 | 不当作免费硬件预知能力；并发/外部写边界和 compressed map 的代价仍需明确 |

## RO 容量修订与代际算例

r1 的 T_RO=128 仅为显式算例。当前已读的 r3 模块以 payload_budget 配置
completion vector，按 payload ID 索引；因此静态实现映射需按 N=1168/1160
项成本核算。最多同时存活多少实例是另一个约束，不能自动把数组压缩为
128 项或 512 项。该模块尚非已接入 R0 的功能；R0 的 RO completion 增量为零。

`PPA_BITS.json` 给出 G8/16/32、C8/16 的句柄算例和 N 项 completion 已知字段算例，
均明确排除未知字段。G 只是表示参数：软件 fail-on-wrap 不是物理最小位宽证明。
该算例不形成总面积，也不能作为对 R0 功能已开启的断言。

## 面积、功耗和时序结论范围

目前有历史 V3 RTL 与综合工具，但没有本轮 B16/U_WB/TVD/RO 的匹配 RTL、
同工艺 SRAM/标准单元库与同频率/IO 约束。尚无差分综合面积、静态时序或
功耗数字。原始 data bits 相等的结论有效；“面积相等”“耗能下降”“一拍 TVD
达到频率”均尚不能成立。

功耗应由实际 read/write/copy/lower bytes 与同工艺每事件能量估算。若 RAM
read/write 已计入，copy 的附加项只计线网/latch，避免重复计数。最终差分按
匹配 B/U field inventory 做新增/删除/复用，保留共同下层存储及活动时间。

## 修复后的成本接收

时钟来源修复、monotonic 断言与 version/reference 审计不自动增加数据 RAM 容量。
Host prefill 在唯一 allocator 中建立 owner，不能额外赠送 payload 存储。修复版
具体字段、warmup 暂存和 bank 控制 delta 需绑定 Lane-1 官方 R0.1 发布后重新审计；
未编译候选不计作已验证硬件实现。原146/145KiB和共同128B latch为不变预算。
