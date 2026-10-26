# Observer正确性与非干扰实证

结论：PROVEN，在本次精确同ELF Vector OFF/ON中，原有完整数值模型、请求/响应、缓存/队列及所有已纳入的scoped production counters等价。该证据限定给定trace/config与实际执行路径，不是所有协议交错的普遍正确性证明。生产身份见TAG_RESERVATION_OBSERVER_DESIGN.md。

## 实际执行的CPU控制

清洁V2 build实际22次组件执行、11组同fixture ELF OFF/ON：SECTOR_OVERLAP_REENTRY、RO_MERGE_PACKET_ONCE、REAL_TAGFAIL_PREVIEW32、GENERATION_DETACHED_OLD_RETURN、TVD_ZERO_DURATION、WAD_EARLY_NO_FAKE_ALLOC、TAGPRESSURE_CAPTURE_JOINT、PRESSURE_ELIGIBLE、RESPONSE_BACKPRESSURE、NATIVE_REQUESTER_RO_VICTIM、LIFETIME_SECTOR_REENTRY。最终receipt SHA6e86258fc3ccc3a614f96926e9ff2248f543b29c83cace794eadecf480c67839；B独立审查b0971e5c…、C独立wire/语义复核65e6d06d…见EVIDENCE_INDEX.json。

这些控制实际覆盖16路预约+第17新Tag真实失败、preview32不变、sector乱序及重入、generation/旧detach返回隔离、response背压前进、TVD同tick零寿命、WAD提前拒绝不制造Tag分配；面积/enter-exit/占用/censor闭合。CPU只有1slice、ROP0和显式synthetic lower返回，不能冒充真实DRAM或完整64slice应用。独立header数学/窗口测试与11组linked控制分开保留。精确逐路径未测边界见TAG_MUTATION_HOOK_COVERAGE.md。

ROP profile不匹配、preview比较时点和WAD drain harness的早期失败均保留；只修组件输入/断言范围，不改完整应用配置或协议保护。V1主ELF0090的Framework banner缺失被发现后未启动应用；修独立Git shallow元数据和短hash长度，清洁V2主ELF改为8d55。静态lib685逐字相同，V2仍实际重建并重跑22控制，不以旧结果代替新build资格。

## 两次完整应用

|指标|OFF|ON|
|---|---|---|
|UUID|718517d1-efa5-4dbd-8f9f-5124703a1ac0|5ee264d8-0ca2-4b06-8ff4-18e9f3e31454|
|cycles|75039|75039|
|instructions / CTA / slices|56000000 / 15625 / 64|56000000 / 15625 / 64|
|kernel / hardware drain|1 / true|1 / true|
|natural return / stop|0 / none|0 / none|
|lifetime开关|0|1|
|raw SHA256|c8c41b772fc254bfb7a9410f0c56f6bba98974b6d48bd4f1ad8ab0e0a1ea02ce|09d6d5a254cb80c387ef8d4901e44d13993f3b0f0ebd26d5f6531d97c78a75ce|
|约1Hz进程树RSS采样峰/B|578813952|591396864|
|host wall seconds|684.559848|700.124078|

同一个8d55 ELF、同source5身份、同输入内容、同原四配置与282个实际打印选项，旧detach/tagpressure诊断两边均1。只改变生产observer开关；ON另有已审查的host资源/SSHFS身份资格续接，未改模拟器参数、发射节奏或预算。实际native PID/maps/env/CPU16/nice10/AS9GiB和真实trace成功open通过syscall证据验证。

NI状态PASS_COMPLETE_OFF_ON_NONINTERFERENCE，receipt SHA66fe20cb02c582ab13fa7b45a4f15a83f79ef487f71896779709df6bd27f8b74。比较范围包括完整冻结数值model、所有64slice的R4/R5及phase、64个B0、64个M0、32个DRAM记录和全局L1；保留scope而非取最后一个被覆盖scalar。只排除规定的raw provenance字段，新增lifetime输出和host wall不要求相等。OFF已归档输出始终只读；两个归一化snapshot及NI都写于ON输出、在ON封存前完成。

ON严格wire实际9,171,562B<16MiB，64slice/4096set/40960 set-window/640 slice-window完整，无overflow/invalid。声明observer状态13,533,696B，加2MiB包络15,630,848B<16MiB。所有4096set的有限窗口面积与episode重叠、carry闭合，应用RIGHT=LEFT=0。500000个真实零时长episode保留，未为迎合旧tick统计滤掉事件。

RSS增加12MiB是采样观察，不是未采样峰的严格上界；host wall差异不是模拟cycles变化或性能收益。数值SASS输出/真实硬件正确性仍UNKNOWN，本轮未采GPU或新trace；不以统计闭合替代应用输出校验。全部两次预算已消耗、无重试退款、均CLOSED/reserve0及164双独立恢复。未自动合并accepted Core。
