# 独立 CPU 分析辅助模块：未启动原 trace scan

`scripts/access_semantics.py` 是新增的独立只读分析辅助模块，只接受调用者传入的单条文本记录，没有文件打开、子进程、网络或模拟接口。没有修改冻结 decoder。`scripts/preflight_access_semantics.py` 使用合成文本和封存的CPU oracle摘要，运行于Python；未编译或执行C++、native或仿真工具。

代码依据 Framework `18a68dcccd795f1b6cda75504e9450d00c9cee02` 的 `trace_parser.cc` 和 `trace_parser.h`（源码片段4、7），访问分类依据 `trace_driven.cc`（片段5）。这些是被冻结consumer模型的语义依据，不是历史producer等价性证明。

预检覆盖六组边界：version0/3和可选lineinfo、signed stride/delta与非法地址拒绝、opcode width覆盖trace width及跨128B line/32B sector、已封存sparse-mask oracle、atomic/bypass/fence/CTA barrier分类、同warp记录先后和line alias/byte overlap区分。MAX_DST=1、MAX_SRC=4与冻结header一致。细节和模块SHA见 `CPU_ACCESS_SEMANTICS_PREFLIGHT.json`。

对非连续mask的base-stride记录，辅助诊断函数保持冻结consumer的原行为，以封存oracle的4个lane结果校验；正常分析入口明确拒绝该记录并产生 `ContractGap`。不把原decoder在mask间隙后的零地址纳入alias集合，不猜测或修补producer语义。该oracle比对仅覆盖现存摘要中的lane，不是完整parser等价性测试。

当前只支持reviewed version0/3和普通global/shared/local内存字段；新版本、TMA/LDGSTS等未评审opcode、未知address mode、字段缺失、地址溢出等直接拒绝，不静默跳过。PC、width和地址mask按冻结模型解释；不读取、保留或推断load返回值。跨行访问分为精确byte mask和粗粒度sector mask，不能把两者相交混为一谈。

`WarpWriteHistory` 仅服务单kernel，跨kernel必须创建新实例；key包含CTA/warp，无跨warp有序边。它报告先前同warp写PC的累计byte覆盖与后续读的相交，ordinal字段明确是该PC最后一次贡献记录，不能当作精确动态write/read配对。任何报告里的真实happens-before和返回值仍为UNAVAILABLE。跨warp及跨kernel候选需后续独立聚合，不由此模块生成。

此预检通过不表示原trace已被读取或访问语义扫描已完成。`stream_access_scan.py` 已加入有资源准入的单worker读取入口、逐kernel完整性核对和checkpoint；当前只用内存合成CTA流验证其结构逻辑，未以真实原trace验证。入口默认只准入检查，显式scan请求也必须通过同样检查。拒绝记录见 `SCAN_ADMISSION.json`，因持续高I/O压力及磁盘占用停在body open之前，无后台扫描任务。

stream入口仅访问已固定的Gaussian/GEMM原路径，不读取U raw。每个完整成员同时核对SHA、stat稳定性、kernel/版本、CTA/warp覆盖、完整指令与memory-path计数；合同缺口即停，不修复地址。不保留不完整kernel索引，已完成kernel索引只存放独立W scratch，身份不一致时不自动覆盖。限制4MiB/s输入、1GiB RSS峰值、每kernel30分钟、25万distinct lines/warp history keys、单索引128MiB、总索引2GiB；缺少字段或超过上限均为STOP，不伪造完成。

`cross_kernel_reuse.py` 提供已完整kernel索引间精确集合与byte/sector比较纯函数，另以合成集合预检。它不自动读取索引或把结果写入主报告。实际跨kernel批量归约及发布仍待完整原扫描后进行；目前原负载所有地址/PC结论仍为UNAVAILABLE。
