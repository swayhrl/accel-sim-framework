# r2 claim–evidence map

正文只放研究问题、方法、限定范围与真实观测；本表保存阶段/来源细节。
准确 SHA 与文件 hash 在 SOURCE_EVIDENCE_MANIFEST，非正文中的新性能结论。

| Claim | 绑定实现/记录 | 验证与数据 | 成熟度 / 限定 |
|---|---|---|---|
| B16/U_WB16 是有限资源生产实现 | R0 Core126394be / FW37dec04d / binary0b504f55 | Lane-1 release02982b65；Lane-5资格221c7f65及九组 gate→checks digest | INDEPENDENTLY_QUALIFIED，仅该两向量，非 TVD/RO |
| static copy 与原位 WB 的服务不同 | R0 ep-l2-ft-cache.inc / gpu-cache.h | STORAGE_AND_PORT_LEDGER；独立生产 Bank/lifecycle 范围 | 已实现；应用 copy/Bank 减少的性能归因仍待 pair |
| 数据预算一致且另有共同 latch | R0 pool参数与端口账 | B/U 同1168/1160项，另128B/slice；PPA_BITS | 原始bits与模型服务，非等面积/等功耗结论 |
| 容量共享有系统收益 | b47b721d sad pair的角色/借用、staging、copy、Bank与周期 | 110593/110573基本持平，峰值1且无C16压力 | 首点支持copy/Bank减少，不支持capacity benefit；其余四点缺失 |
| 历史 locality 的 line/sector 差异 | Streaming runtime db1c9018 / Coreca3e7bc0 | 原聚合器a38ce9c5重验13行、raw/status/config/masks闭合 | HISTORICAL_LOCALITY；非TVD hits/borrow收益 |
| 单点乐观读参考1.721259× | 历史 Core6c5dc9f8 / FW992ed2d7 / binaryc0405d83 | 两行 CEILING_RESULTS、实际run_key/raw/summary；73873/42918 | HISTORICAL_DIAGNOSTIC；非R0/R1 B16、非严格上界/平均 |
| TVD 服务与减少 DRAM 传输不同 | Lane-2接线扩展，与R0分开 | served_sector_bytes仅服务量，saved必须matched lower/DRAM差分 | 扩展未生产资格；+1cycle非STA |
| RO oracle 与 completion 有真实成本 | ddedbf0f模块 m_slots(payload_budget) | configured N=1168/1160与live上限分开；whole-commandlist closed-world | 模块/设计范围；不是免费CAM、128项或已集成R0 |
| 模型内数据正确性 | R0独立sector/reference与requester源汇 | 资格scope与原生终态；SASS numeric不可观测 | 不等价full-byte/atomic应用输出 |
| R1 ideal 与 R0 实现分离 | Lane-4 be21c95d handoff / 新候选b8b3d55b | R1须自身B16/binary；18格缺失保留 | 诊断集成pending，不阻R0实验 |

后续读取 Lane-5 原生 RESULTS.csv/PAIR_RECEIPT，按准确 publication 映射并校验；
每完整 pair 可更新图，五点前不求全组均值。不改生产 CSV、历史 pack 或运行锁。
