# DTC_LANE_AE_BANK_PRESERVING_TAG_HASH_174_V1

2026-10-18，原 `huangrulin-174` / root。**PASS_BOUNDED_CPU_FRONTEND_READY_FOR_AG**。仅一个预先固定bank-preserving hash，默认OFF；137项CPU检查通过，C++编译恰好2次。完整sim、native应用、GPU运行和应用trace读取均0。未修改其它Lane源/运行或旧论文数据。

固定父Core/X2：`e32afdcf44be3374ff36d22568ed01a075459b6f`。AE Core：**`ae83cc510f301cfe7937ad77318e332b2ab324e8`**，独立分支`hrl/iscas2027-dtc-lane-ae-tag-hash-core-174-v1`，已push/fetch-back精确一致。Framework独立分支`hrl/iscas2027-dtc-lane-ae-tag-hash-174-v1`，基于X2审查`631eb6418f6e7f1f548afd33351cbc0d98d27145`。来源/blob/GCC11.4/flags/CPU ELF/hash见`SOURCE_AND_TOOLCHAIN.json`，完整SHA见`SHA256SUMS`。

实现 `-gpgpu_dtc_l1_tag_hash_bankrow` 默认0。ON仅PAPER_OO whole-line、finite1、B=4且S为>=4的2次幂；不支持明确STOP。ON使用用户指定的`set=4*(((L>>2)^(L>>s))&((S/4)-1))+(L&3)`，完整logical line key及所有数据/身份字段不变。OO bank服务/find_tag/victim统一到同一helper；K1全目录遍历原样。`will_new_miss`的旧LRU副作用在ON/OFF均保留，没有replacement cleanup。ordinary C+、80KiB physical、OO128、原Tag延迟/所有quota均未修改。

|主要证据|结果|
|---|---|
|新omitted/0与固定X2每请求输出|56组精确相同；另4组旧nonpower/small geometry OFF等价|
|S32/64、ways4/8|全部通过；每种ON/OFF固定S×ways，没有扩Tag/ways|
|bank与冲突|地址bank不变，same-bank quota和全局窄quota拒绝保留；whole-line原一reference/调用源体不变|
|4096B stride|96请求下，四geometry miss均96→32，bank不变|
|neutral/固定负控|neutral均32→32；反例三个geometry更差，一个持平，完整保留|
|LRU / late merge / K1|probe后victim顺序保留；旧7 Ref在E后保留，同址新physical，旧最后Ref才释放；map-loss守恒|
|非法geometry/mode/finite|13个指定STOP + -6；真实parser omitted/0/1与未知option检查通过|
|静态源码边界|四个既有生产文件移除明确AE增量可逐byte恢复X2，ordinary和既有K1源体相同|

资格范围是**实际production frontend/header及option parser的有界CPU测试**。两次编译产物不链接libcudart；没有构建完整Core/trace simulator，没有验证完整shader/LDST翻译单元或新动态库绑定。生产注册/构造配置传递是静态审核，不能提升为完整ABI运行通过。应用性能、完整ISA数值、coherence、PPA仍未证明。

XOR功能量级为S32的3个或S64的4个二输入XOR，外加可能的enable mux/控制/布线；固定Tag延迟是假定能装入原时序预算，不是零面积/硬件零延迟证明。XOR placement有既有研究，本轮不声称DTC首次发明；未来若声称超越C+必须有传统cache对等hash控制。详见`HARDWARE_COST_ESTIMATE.md`和`RELATED_WORK_BOUNDARY.md`。

交付：`Core_SHA`、`HASH_MAPPING_SPEC.md`、`INDEX_POINT_AUDIT.md/json`、`CPU_CASES.md/json`、`K0_EQUIVALENCE.md`、成本/相关工作边界、`VALIDATION_GATE.json`及`AG_HANDOFF.md`。原始CPU输出/两个ELF只在`/workspace/dtc-lane-ae-tag-hash-174-v1/cpu_final_v1/`（约3MB输出、整个external约3.7MiB）。本Goal编译闩已锁2，不应重置以绕过预算。

`PUBLICATION_RECEIPT.json`给出Core发布收据及Framework最终提交定位；最终双仓push/fetch-back/clean精确SHA在外部`/workspace/dtc-lane-ae-tag-hash-174-v1/FINAL_FETCH_BACK.json`和最终交接消息，避免自引用。AG接收的是上述有限CPU资格与明确未测项，本包不建立新执行authority、不自动启动任何模拟。
