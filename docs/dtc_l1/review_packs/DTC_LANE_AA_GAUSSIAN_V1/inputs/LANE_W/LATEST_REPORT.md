# DTC_LANE_W_TRACE_ACCESS_RISK_174_V1

状态：**DEFERRED_SAFE_STOP — 身份及既有访问分布已固定；地址/PC 流式 scan 因高 I/O 压力暂停。** 审阅始于2026-10-17，封存日期2026-10-18（Asia/Shanghai）。主机 `huangrulin-174`，账户 uid0/root。独立 Framework 分支 `hrl/iscas2027-dtc-lane-w-trace-semantics-174-v1`，基线18a68dcc；不改 Core、decoder、trace 或旧 raw。

Gaussian **具备值得研究的结构性可能，但“确有跨 kernel 可查询 Tag 复用”尚未证实**。原510个kernel由255个 Fan1和255个 Fan2组成，既有 CPU proof 记录557,456条cacheable global load、186,200条store。冻结OO实现保留有效Tag，传统L1 invalidate路径未清除DTC映射。这些事实支持候选研究；没有扫描地址，无法确认任一跨kernel R∩R、W∩R、可复用distinct lines，或映射在下一kernel仍位于同SM且可查询。对应字段全部UNAVAILABLE。

**目前不能点名任何实际暴露旧DTC映射的PC。** 四个指定负载均有cacheable reads和stores，可列为风险筛查对象；Gaussian/DWT2D/BICG有跨kernel候选范围，GEMM原输入仅1个kernel，跨kernel对不存在。真正可能暴露旧映射的读PC需同时具备：读到此前DTC映射的line、相关store/atomic/invalidate未使映射失效、映射仍驻留且属于同一DTC查询域。byte重叠才是比line别名更强的写读候选；依然不证明读到旧值或native错误。逐PC字段UNAVAILABLE。

**原输入目前不能支持K1性能外推。** K1合同/机制身份未固定；既有完整指令覆盖只能支持冻结consumer模型的输入范围。即便后续scan证实地址复用，也不能据此外推出Tag命中率、时序、性能或值正确性。四个负载本包都只作为风险筛查；本包不授予新模拟或自动晋升。Hotspot HOLD、2D新输入STOP及LUD不追加边界继续保留。

| 原输入 | kernels | active-thread instructions | cacheable read记录 | store记录 | list中的HtoD |
|---|---:|---:|---:|---:|---:|
| Gaussian | 510 | 283,685,120 | 557,456 | 186,200 | 3 |
| GEMM | 1 | 739,246,080 | 8,396,800 | 4,202,496 | 3 |
| DWT2D（U封存身份补充） | 10 | 148,684,429 | 210,558 | 246,240 | 1 |
| BICG（U封存身份补充） | 2 | 145,666,048 | 2,097,152 | 1,048,832 | 5 |

访问计数单位为动态warp instruction records，不是active lanes、事务数或distinct lines。所选四负载atomic/bypass load/fence均为0，依据完整既有opcode目录及冻结cache分类；DWT2D另有1,253,574条shared记录。BAR.SYNC不等于全局fence。

原list重新逐字节/SHA验真；成员SHA与既有body proof逐个一致，当前成员只stat尺寸，未重新读取大文件做SHA。Gaussian原list SHA `6dc7caba6733657293e8c517467bac28890ae4eb97c732ffd245d7fd1c479fb9`；GEMM `fd9a9430fc95eb0af4c73b9710db271f8e32bff4ea2f5dd08a4e8e17c9b02057`。Core `6fba0136f8465b59fe5858a950fa39efb265f654`；parser/Framework `18a68dcccd795f1b6cda75504e9450d00c9cee02`。冻结parser SHA `f63db893d39bfcd4cbf679ea1158fd9a0594211181333e13b2fdbb478d60ddb7`，源码/proof当前小文件SHA均通过。

T输入源提交 `f520a445436b57c0a0f2494fb858a1636f04d2bc`；U只读提交 `16e56912cfd02f2311a1603a29415dee829fd495`；A完整body proof源 `f5c37d6edcce832a72cb0830021bffa78df6cc13`。所有输入内容来自不可变git对象；未读取U raw或干预其后台活动。U提交身份不暗示授予本轮运行U工作负载的权限。

交付索引：

- `TRACE_SCOPE_SHA256.tsv`：四个原list、523个成员的来源/SHA与本轮核对级别。
- `ACCESS_CLASS_COUNTS.tsv`：逐kernel及ALL汇总；`inputs/OPCODE_FORMS.tsv`、`MEMORY_WIDTHS.tsv`保留分类依据。
- `COMMAND_SEQUENCE.tsv`、`KERNEL_ORDER_AND_COVERAGE.tsv`：完整原list顺序、memcpy及kernel覆盖；不建立执行全序。
- `SOURCE_DEFINED_INVALIDATE.tsv`、`inputs/SOURCE_EXCERPT_*.txt`：源码事件类型、条件和可审查锚点；动态调用次数UNAVAILABLE。
- `CROSS_KERNEL_ALIAS_AND_REUSE.tsv`、`WRITE_READ_RISK.tsv`：逐段待查范围及明确UNAVAILABLE，不冒充已发现候选pair。
- `MEASURED_VS_INFERRED.md`、`SCAN_CONTRACT.md`：证据边界、暂停点及后续CPU扫描要求。
- `RESOURCE_PREFLIGHT.json`、`CPU_READONLY_CHECKS.json`、`PROVENANCE_SHA256.tsv`、`FILES_SHA256.tsv`：资源、身份与内容完整性。
- `scripts/build_readonly_pack.py`、`scripts/verify_pack.py`：只读整理和独立包校验；没有仿真启动路径。

零新模拟attempt；零GPU/native工具执行；零trace body open；零旧raw读写；零后台scan或自动恢复任务。地址/PC、byte/sector mask、distinct lines和任何性能外推仍未完成，不能将本包称为完整trace访问语义扫描报告。
