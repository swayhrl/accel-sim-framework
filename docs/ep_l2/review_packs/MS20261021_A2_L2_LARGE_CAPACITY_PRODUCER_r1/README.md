# Lane A2：L2大容量／免费数据服务正式生产者交付

**已实现、构建并通过12项真实原生检查，可供E2独立资格验收。** A2没有启动完整应用。用户授权来自Framework提交49343880865edb22a17523790fc32dd55975966c的四文件；完整副本保留在此目录。入口为`RELEASE.json`；精确证据分别在`BUILD_PROVENANCE.json`、`NATIVE_EVIDENCE_INDEX.json`和`E_INDEPENDENT_QUALIFICATION_ENTRY.json`。

## 一键控制及准确身份

`-gpgpu_ep_l2_diag_l2_large_capacity 0|1`，默认0。

- OFF不干预既有显式诊断flag，保持原有限S尺寸、映射和时序路径。没有隐式扩容或大数组分配。
- ON仅允许传统S，自动选择L2_DATA_FREE及一组共同冻结的大容量；V/RO/MQ2/RG1、COPY_FREE、S64及旧ideal/强制命中/simple-DRAM组合明确拒绝。
- ON为**容量／服务诊断**，`hardware_P1_throughput_eligible=0`。保留真实hit/miss、DRAM/互连时序与带宽、同址顺序、sector版本、WB接受/完成生命周期及固定copy-latch。不是全命中，也不是保证可实现的硬件上界。

Core：`fe7e1fc1e8f40b5c4c6d0f232a528483891389c5`，从d010隔离派生，GitHub分支`hrl/ep-l2-ms20261021-a2-large-capacity-v1`。

Framework：`9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`；vendor：`f90c430c3a1ce8f08c09942a5a1c3a797bb2295b`。

main：`/workspace/build/ep-l2-ms20261021-a2-large-capacity-r1/accel-sim.out`，SHA256 `93a9f28ddb9c0c9ceb93409764a5664666589477778fe5d41d90a179704706eb`。

archive：`/workspace/build/ep-l2-ms20261021-a2-large-capacity-r1/gpgpu-sim/src/gpgpu-sim/libgpgpusim.a`，SHA256 `bed717ec2c4c5cd533c1a1fa15b79059907710885e61a61c1d70e0ace00be708`。

正式A公共入口新增显式spec及本任务用户授权分支，仍通过真实E `Coordinator.reserve_work`、原锁、原174、max-j2、原5GiB＋2GiB monitor reserve、RAM/Share/所有待写入资源检查和原owned-process监控。未自签E资格或伪造E审批；E中央API实际返回lease。r6构建和native各用新lease，均已释放。Release编译保留assertions；没有NDEBUG。生产main只链接新隔离构建的archive；旧d010 archive仅由独立reference test target链接。

## 五输入共同冻结向量

精确向量见`FROZEN_CAPACITY_VECTOR_FINAL.json`；五应用无逐输入调参或扫描。

| 每slice资源 | ON实际值 |
|---|---:|
| Tag sets × ways |4096 ×16 =65536|
| resident / bypass / WB payload |65536 /8192 /1024|
| payload总槽位 |74752|
| WAD / Line-MSHR |8192 /8192|
| descriptor / per-address |32768 /2048|
| MissQ |8192|
| ICNT→L2 / L2→DRAM |4096 /8192|
| DRAM→L2 / L2→ICNT |4096 /4096|

固定4 banks、128B line、4×32B sectors、1-cycle copy-latch不变。`result_fifo_entries`配置字段为4096，但它不是L2实际使用的另一条ready队列；真实ready响应仍受32768个descriptor约束，日志明确指出此范围。ROP storage保持原生动态队列，固定ROP延迟不变，新增实际事件高水位。**原memory-partition credit、DRAM scheduler/return/write队列没有随local FIFO放大**，不可把L2容量诊断说成整个memory path无约束。

原IPOLY helper不支持4096sets。ON保留原IPOLY64作为低6位，另用partition-line地址的高6位选择64组；支持原生linear用于资格fixture。实际应用原P选择绑定这一明确扩展；OFF完全走原映射。Tag／payload角色边界、Tag-handle向量、sector版本和generation存储一起扩展；PayloadHandle与mem_fetch ID为unsigned，WB ID73728已超过16-bit并经真实packet/版本检查。ON维护精确owner/role/pending索引，每次打印仍对完整存储做deep reconciliation。原有限模式guard继续保留；ON另用精确向量guard，未以删除guard或UINT_MAX代替实现。

`EPL2LARGEV1`打印requested/effective总开关、实际几何和容量、服务模式、每资源高水位／拒绝检查及覆盖范围。Tag occupancy是含懒清理身份的保守resident bound；payload与ready-response也明确使用保守上界。不能把它们冒称精确连续占用。除授权的拒绝0／高水位≤50%条件外，Tag还必须无timed有效victim替换、无host预填充有效替换，才能标近非绑定。native stress故意触发2次dirty替换＋1次untimed prefill替换，实测Tag标签为0。该门仅限制科学标签；**允许有效large-finite应用结果，不禁止执行，也不自动重试。** 五个完整输入的非绑定状态须由E实际终验，A没有预称全应用“基本无限”。

## 实际生产定向结果

`NATIVE_RESULTS.csv`的12项全部真实exit0，逐项ELF、原生退出回执、raw SHA和命令已冻结。

- retained d010 archive reference、新binary默认OFF、显式OFF：同一20请求激励，均74cycles、20responses、两笔真实WB接受及完成、完全drain，语义签名逐字相同。
- ON linear、实际P扩展、64slice几何三端：真实600条同时在途Line-MSHR与600descriptor，单地址64请求；超过原128／512／32边界。600个真实lower返回逆序交付，实际校验sector版本、每请求exact-once及闭合。
- ON保留copy read/write及固定latch、同址WAD等待；两笔dirty WB均经实际lower接受及set_done完成，最终0 transient／MSHR／descriptor／WAD／WB；物理bank grant为0。
- 实际host预填充17条同set clean line，确认1次有效Tag替换被单独计数，未推进GPU周期，未换算为GPU停顿。
- 拒绝COPY_FREE、RO、非法master2及forced-hit；同时执行受影响默认OFF stale-sector与physical-clock生产fixture。
- 64slice原生实例化峰值RSS为1,429,504KiB，约1.36GiB；slot实际sizeof80B。这是小型资格负载的主机成本证据，不是完整应用RSS或walltime保证，E仍独立保留每端资源与监控门禁。

ON资格激励额外执行664请求和17条untimed prefill，不能拿ON的1407cycles与OFF74cycles计算性能收益。数据检查是既有模型的symbolic sector-version生产路径范围，不冒充全应用数值／性能PASS。

## E2可直接消费的入口

`APPLICATION_CONFIG_MANIFEST.json`包含Conv、CFD、DWT、SAD、Vector的10套准确有序配置资产。保留各accepted S基础字节，最后只追加一个master0/1配置；已有base中的历史空白也保留以维持SHA。它们不是launch spec、E qualification或run key。原五输入trace SHA／selection／完整指令数均与授权逐项相符，未重扫或复制大型trace。

E须区分raw options与总开关派生后的有效配置：raw S字段仍可显示原尺寸和`diag_l2_data_free0`，master1实际选择本向量及data_free1。终验必须以准确的raw资产身份、该确定转换和原生effective输出闭合；不可照用main61的固定1024／1168解析断言。按`E_INDEPENDENT_QUALIFICATION_ENTRY.json`独立审查新版本，再由唯一E中央控制器执行同新binary五对完整OFF/ON；每对接收后及时交D。旧main61任何S/F数值不能替代新OFF。

最终快照已见原中央36/46、10GiB新增／24GiB旧＋新及北京时间2026-10-22 18:00启动／22:00接收截止采用，旧36次及原T0保留。A未改中央预算、runner、资格判定或接受结果。正式发布不意味着E已授予独立资格，亦不意味着新版本应用已PASS。

## 历史证据

旧main61 SHA61aad…和旧archive SHA3c6ce…在交付时重新核验一致；旧E006/E007、r39–r42及其他失败／撤回／INCOMPLETE不变。此次新隔离工程历史也完整保留：r1编译修复；r2/r3旧archive reference激励的lower-WB采样／第二笔WB收尾修复；r4全部12项PASS；r5新增host计数的旧header reference编译修复；r6最终全部12项PASS。旧失败与中间PASS的回执、SHA清单及相关未资格ELF/main均保留，没有reset、clean或删除历史结果。
