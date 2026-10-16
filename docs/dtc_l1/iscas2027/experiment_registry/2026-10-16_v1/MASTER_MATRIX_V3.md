# DTC实验总表V3：Hotspot语义HOLD与多Codex分工

来源：主执行`e3dbe3dbf2abb49b923244538d2a3d1828024d4f`，`review_pack/checkpoint_20261016T094353Z/SUMMARY.json`，时间2026-10-16 09:43:54 UTC；不是服务器此刻实时状态。V1/V2保留。

## 当前准确计数

44个原注册新行：**5个terminal/invariant PASS，其中2个Hotspot scientific HOLD；8运行；3 admission HOLD；28未启动。** 三个未被此次编码问题影响的完成行是Btree IO/OO/TRAD96。3个禁止启动行是Hotspot TRAD96、IO128、WAIT128。所有原baseline与旧Hotspot结果不删除，但Hotspot相应科学解释/比较同样HOLD。

全629正文审计核对171982 CTA、1368212 warp、4693978494 active-thread instructions；12负载合计匹配。global load最多32个128B引用、没有cacheable local-load形式，支持此固定集合的有限引用服务上界，不证明任意ISA或整个GPU前进性。90792条Hotspot shared mode1+稀疏mask记录存在历史编码分歧；其他11个输入未出现同类组合。

## 完整研究任务

| ID | 内容 | 最新状态/下一步 | 负责人 |
|---|---|---|---|
| E00 | 原输入、Core、配置与629正文审计 | 完成正文/身份核对；Hotspot共享地址语义单独HOLD | A |
| E01 | 有限服务与正确性资格 | R1 V2保持；输入内global引用上界得到补证 | A |
| E02 | B16-N传统参照 | 原复用收据保留；Hotspot分母科学推广HOLD，其余按原范围使用 | A |
| E03 | TC80-N传统容量参照 | 同E02；不重开TC80矩阵 | A |
| E04 | 4程序×IO/OO主试点8行 | 4 terminal（Btree2、Hotspot2 HOLD）；BICG/2D共4运行 | A |
| E05 | 4程序增强传统试点 | Btree通过，BICG/2D运行，Hotspot admission HOLD | A |
| E06 | WAIT128控制4行 | 3个非Hotspot按单程序gate补位；Hotspot HOLD | A |
| E07 | IO128控制4行 | 同E06，复用主OO128；不新增同深度矩阵 | A |
| E08 | 余8程序×3arm共24行 | GESUMMV IO/OO已运行；其余22按原gate滚动 | A |
| E09 | 局部服务敏感性 | 仍有条件；先完成主配对与必要粗筛定义，不扩矩阵 | A |
| E10 | 接纳/保留定向机制 | 复用既有测试；与有限服务/时间指标合并收口 | A |
| E11 | 109原生12诊断 | 已完成，native-only，不重跑 | 原109 |
| E12 | SpMV原生与SASS准入 | native有效；SM89 dispatcher HOLD；D仅给隔离候选与验证 | D/A |
| E13 | LayerNorm | native有效；trace NOT_ADMITTED，不做CALL省略或重构 | 保留 |
| E14 | 4080传统baseline-only | 4个原terminal通过；其中Hotspot scientific HOLD，另3保持原旧SASS反事实范围 | A |
| E15 | 固定128KiB布局/支持域 | 已有容量审计不重做；C提交最小可实施方案或明确不做建议 | C |
| E16 | 4080同预算DTC | 仍HOLD、0行；C的提案不等于准入 | A（批准后） |
| E17 | 3070 | 未启动，最低优先级条件项 | A |
| E18 | 面积与关键时序 | 等用户实际硬件证据，辅助Codex不猜面积 | 用户 |
| E19 | 论文图表与配置 | v0.6 setup保留；Hotspot不入无条件主结果或GM12 | ChatGPT |
| E20 | 旧SG3 queue/DRAM/ICNT | 关闭，不再扫 | 无 |
| E21 | FAST64/Lane-E/TC80/SG0/logical80 | 冻结保留；编码问题只加适用性注记，不覆盖原证据 | 无 |
| E22 | Hotspot历史地址格式闭合 | 新增最高优先级CPU调查，先来源再补丁再局部重验决策 | B |

A是现有原174主窗口；B/C是原174独立新窗口；D是109新的CPU-only窗口。具体任务见[multi_codex_v1/README.md](multi_codex_v1/README.md)。辅助任务准备就绪，尚未因本次提交自动启动。

## 统计/科学状态分开

执行完成与科学可用是两个字段。Hotspot旧/新行可维持自然退出、指令守恒、ownership/drain等通过记录，同时因输入解释未闭合而禁止性能推广。不能删除这两行后把其余集合仍称GM12；也不能因各设计用了相同错误解释，就假定加速比误差相消。若最终需要改输入或正式删一项，需单独决定、披露，而不是调度器自动替换。

## 流水要点

GESUMMV慢行已在运行，不重复发；空槽滚动放行原注册的长行、配对参照和快速机制控制，不设全pilot屏障。Hotspot/现代容量/SpMV独立调查不阻塞其他原任务。主调度唯一负责仿真启动和结果受理，多窗口只分离问题与候选，不复制44行。
